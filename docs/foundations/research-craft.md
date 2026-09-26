---
title: Research craft
status: working
tags: [pillar-10, foundations, reproducibility, writing, communication]
updated: 2026-09-26
---

# Research craft

<span class="status status-working">working</span>
<span class="pillar">pillar 10 &middot; V&V, research craft and communication</span>

!!! abstract "In one minute"
    - "Physics insight — knowing when and why a model breaks" is listed as a *skill*, not a by-product of knowing the equations. It is trainable, and the training is deliberate scepticism.
    - **Reproducibility is a property of the record, not the intention.** If you cannot rerun a result in six months, it is an anecdote.
    - A figure makes an argument. Truncated axes, dual y-axes and rainbow colormaps make dishonest ones, usually by accident.
    - Write the **claim** first, then the evidence for it. A paper organised around what you did rather than what you found is unreadable.
    - Different audiences need different *claims*, not the same claim at different volumes.

## Key results

**The reproducibility record.** A result is reproducible when someone — including future you — can regenerate it from what was stored. Minimum viable record:

<div class="result" markdown>

| Item | Why |
|---|---|
| Code version (git SHA, not "v2 final") | the code changed and you will not remember how |
| Full input deck / config | defaults change between versions |
| Environment (container, lockfile, module list) | library versions alter results at the margin |
| Random seeds | otherwise "similar" is the best you can claim |
| Hardware + compiler flags | `-ffast-math` and GPU reductions are not bit-reproducible |
| Post-processing scripts | usually the least-recorded and most-forgotten step |

</div>

**Bit-reproducibility is often impossible** — parallel reductions sum in nondeterministic order, and that is fine. What matters is *statistical* reproducibility plus a recorded provenance chain. Say which one you are claiming.

**Literature strategy.** Forward citation search (who cited this foundational paper?) finds the current state faster than keyword search. Read in this order: abstract → figures → conclusions → methods, and only then the introduction. Most papers can be rejected at the figures.

**Figures that do not lie:**

- **Start bar-chart axes at zero.** Line plots may be truncated when showing change, but say so.
- **Avoid dual y-axes** — the apparent correlation is set by where you choose to put the scales.
- **Use perceptually uniform colormaps** (viridis, cividis). Jet/rainbow creates false banding at the yellow-cyan transition and is unreadable in greyscale or for colour-blind readers.
- **Label units on everything**, and state \(\mathrm{Re}\), \(\mathrm{Ma}\) and the grid on any CFD figure.
- **Show the data density.** A regression line over 8 points and over 8000 look identical.

**Structuring a claim.** For each result: what is claimed, what evidence supports it, what would falsify it, what its domain of validity is. A result whose falsification condition you cannot state is not yet a result.

**Audience calibration.** The same work supports different claims:

| Audience | Leading claim |
|---|---|
| Specialists | what is new relative to the prior method |
| Adjacent technical | what it enables that was not possible |
| Management | what decision it changes, and the confidence |
| Public | what question it answers |

## Mental model

Treat your own result as the strongest available adversary would. Before believing a simulation, ask what would have to be true for it to be wrong, then go and check that thing specifically. Most spurious results survive because nobody asked the one question that would have killed them — usually about resolution, about the boundary conditions, or about whether the comparison data means what it appears to.

The same discipline applies to writing. A reader is a hostile compiler: any ambiguity will be resolved in the least favourable way.

## Numerics / practice

- **Log the provenance automatically.** A solver that writes git SHA, input hash, environment and timestamp into every output file costs an hour once and saves entire re-runs.
- **Keep a lab notebook** with negative results. The configuration that did not work is the expensive knowledge, and it is never written down.
- **Write the figure captions first.** If the caption cannot state a finding, the figure has no job.
- **Give the talk before the paper is finished.** Questions expose the weak claim faster than rereading.

??? warning "Failure modes"
    **Results that cannot be regenerated.** Six months later the script has moved, the config was edited in place, and the library upgraded. Symptom: being unable to reproduce your own published number. This is normal and preventable only by recording provenance at generation time — never retroactively.

    **Truncated axes exaggerating an effect.** A bar chart from 0.95 to 1.00 makes a 2% difference look like a factor of five. Usually not deliberate; the plotting library did it by default.

    **Rainbow colormap.** Creates visual boundaries where the data is smooth, and hides real gradients in the green band. Still the default in several CFD post-processors, which is why it persists.

    **Comparing against digitized literature data without saying so.** Points read off a printed figure carry several percent of extraction error. Reporting agreement to 1% against digitized data is not meaningful.

    **Overclaiming the domain of validity.** A model validated on one geometry at one Reynolds number, presented as general. The fix is one sentence stating the range tested — cheap, and it is what makes the work usable by others.

    **Burying the finding in chronology.** Organising a report by what was done in what order, rather than by what was found. The reader has to reconstruct the argument.

    **Presenting uncertainty only when it is small.** Selectively reporting error bars trains readers to distrust all of them.

    <!-- Add your own here: the review comments you keep receiving. -->

## Worked example

A provenance stamp worth writing into every output file:

```python
import hashlib, json, platform, subprocess, sys

def provenance(config: dict) -> dict:
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    except Exception:
        sha, dirty = "unknown", True
    blob = json.dumps(config, sort_keys=True).encode()
    return {
        "git_sha": sha,
        "dirty_tree": dirty,          # the field people forget, and the one that matters
        "config_sha256": hashlib.sha256(blob).hexdigest()[:16],
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }

print(json.dumps(provenance({"Re": 4e6, "scheme": "MUSCL", "cfl": 0.8}), indent=2))
```

The `dirty_tree` flag is the important one: a recorded SHA is worthless if the working tree had uncommitted edits when the run started, and that is the usual case during active work.

## Connections

- [Verification and validation](verification-validation.md) — the evidence this reports on.
- [Uncertainty quantification](uncertainty-quantification.md) — what the error bars mean.
- [Probability and statistics](probability-statistics.md) — not overstating significance.
- [Skills Map](../skills-map.md) — pillar 10 in context.

## Sources

- Tufte, *The Visual Display of Quantitative Information*.
- Crameri, Shephard & Heron (2020), *The misuse of colour in science communication*.
- Wilson et al. (2017), *Good enough practices in scientific computing*.
