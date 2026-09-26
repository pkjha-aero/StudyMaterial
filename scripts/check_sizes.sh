#!/usr/bin/env bash
# Size guard. The 11 GB course archive lives on external storage and must never
# be committed; the failure mode this prevents is casually `cp`-ing a lecture
# folder into the repo, which is easy to do and annoying to undo once pushed.
#
# Install as a pre-commit hook:
#   ln -s ../../scripts/check_sizes.sh .git/hooks/pre-commit
# Or run over the staged set directly:
#   ./scripts/check_sizes.sh

set -uo pipefail

HARD_LIMIT=$((5 * 1024 * 1024))   # reject
SOFT_LIMIT=$((1 * 1024 * 1024))   # warn

fail=0

while IFS= read -r file; do
    [ -f "$file" ] || continue
    size=$(stat -c%s "$file" 2>/dev/null || echo 0)
    if [ "$size" -gt "$HARD_LIMIT" ]; then
        printf 'BLOCKED  %6s MB  %s\n' "$((size / 1048576))" "$file"
        fail=1
    elif [ "$size" -gt "$SOFT_LIMIT" ]; then
        printf 'warning  %6s KB  %s\n' "$((size / 1024))" "$file"
    fi
done < <(git diff --cached --name-only --diff-filter=ACM)

if [ "$fail" -ne 0 ]; then
    cat >&2 <<'MSG'

Commit blocked: file(s) above 5 MB are staged.

Large source material belongs on the external drive, not in this repo. The site
references it through the generated catalog (catalog/). If this file really is
Tier B material that must be versioned, commit it with --no-verify and say why
in the commit message.
MSG
    exit 1
fi

exit 0
