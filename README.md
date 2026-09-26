# StudyMaterial

Notes and recaps in computational physics, aerospace, meteorology, and machine learning —
published as a [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) site at
**<https://pkjha-aero.github.io/StudyMaterial/>**.

## What this is

A *recap surface*, not a textbook. Pages are written for a reader who already has the
skills and needs to reload a topic quickly — equations and failure modes up front, no
pedagogy. Some areas (meteorology, ML/DL, computer vision) are under active expansion and
grow continuously.

Start at the **Skills Map** on the site: ten competency pillars, each page tagged with the
pillar it serves.

## What is *not* in this repo

The source course archive (~11 GB of PDFs, notes, and lecture recordings) lives on
external storage and is never committed. The site publishes a generated **catalog** of it
instead — see `catalog/` — so pages can point into the archive without carrying it.

Keep it that way:

| Tier | What | Where |
|---|---|---|
| A | Authored notes, notebooks, figures | `docs/`, `notebooks/` — committed |
| B | Small own artifacts, < 5 MB each | `material/` — committed selectively |
| C | Course archive, textbooks, lecture media | External drive — **never committed** |

## Local development

This repo lives on an NTFS volume, which does not carry the execute bit — a virtualenv
created *inside* the repo will fail with `Permission denied`. Put it on a native
filesystem instead:

```bash
python3 -m venv ~/.venvs/studymaterial
source ~/.venvs/studymaterial/bin/activate
pip install -r requirements.txt
mkdocs serve          # http://127.0.0.1:8000
```

`mkdocs build --strict` is what CI runs, and warnings are errors there; run it before
pushing.

For the same reason, shell scripts in `scripts/` carry their execute bit in the git index
rather than on disk (`git update-index --chmod=+x`). Invoke them as `bash scripts/x.sh`
locally.

## Regenerating the course catalog

The archive is indexed at **course** granularity — what each course covers and how much
material there is, plus the path to open it. No filenames, no instructor attribution: the
site publishes what the material *covers*, not what files it contains.

```bash
python3 catalog/build_catalog.py     # scan the drive -> catalog/coursework_index.yml
python3 catalog/render_catalog.py    # + course_titles.yml -> docs/resources/course-archive.md
```

`build_catalog.py` refuses to run when the drive is not mounted rather than emitting an
empty index over a good one. Course names and topics are hand-maintained in
`catalog/course_titles.yml`, which the scan never touches — fill entries in there and
re-render.

## Branching

- `main` — the published site. Protected: direct pushes are rejected, so every change
  arrives through a pull request with a green build.
- `feature/*` — branched from `main`, merged back by PR.

There is no long-lived integration branch. Pages deploys from `main` via the Actions
artifact path, so there is no `gh-pages` branch either — deploy history lives under the
repository's Deployments tab rather than as commits.

## Writing a new page

```bash
python3 scripts/new_note.py <section>/<slug> --title "Topic" --pillar <n>
```

Every page follows one template: a one-minute abstract, key results, mental model,
numerics, **failure modes** (mandatory), a worked example, connections, and sources.
Page conventions are documented on the site under *How to use this site*.

## Licence

Dual-licensed, because prose and code want different terms:

- **Prose, notes and figures** in `docs/` — [CC BY 4.0](LICENSE). Reuse freely with
  attribution.
- **Code** in `scripts/`, `catalog/` and `notebooks/` — [MIT](LICENSE-CODE).

Third-party course material is referenced by course name only, never redistributed and
never reproduced here.
