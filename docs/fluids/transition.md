---
title: Stability and transition
status: working
tags: [pillar-1, fluids, turbulence, boundary-layer, numerical-stability]
updated: 2026-09-28
---

# Stability and transition

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Transition is the gap between [laminar flow](governing-equations.md) and [turbulence](turbulence/index.md), and the site's other pages assume one or the other.
    - **Linear stability tells you when a disturbance grows**, not when the flow becomes turbulent. Those are different questions separated by a long nonlinear stage.
    - **An inflection point is the strong instability.** Adverse pressure gradient creates one; favourable pressure gradient removes it.
    - **Bypass transition skips the linear stage entirely** when freestream turbulence is high — and that is the common case on turbomachinery blades.
    - Transition location controls drag and heat transfer by factors, not percentages. Assuming fully turbulent is a choice with a cost.

## Key results

**Orr–Sommerfeld.** Linearise about a parallel base flow \(U(y)\) with disturbance \(\hat{v}(y)e^{i(\alpha x - \omega t)}\):

<div class="result" markdown>

\[
(U - c)\left(\frac{d^2}{dy^2} - \alpha^2\right)\hat{v} - U''\hat{v}
= \frac{1}{i\alpha \mathrm{Re}}\left(\frac{d^2}{dy^2}-\alpha^2\right)^2\hat{v}
\]

</div>

An eigenvalue problem: complex \(c = \omega/\alpha\) with \(c_i > 0\) means growth. The inviscid limit is the Rayleigh equation, and **Rayleigh's criterion** follows — an inflection point in \(U(y)\) is *necessary* for inviscid instability, and Fjørtoft's condition sharpens it.

That single result organises the subject. A Blasius boundary layer has no inflection point, so it is only viscously unstable — weakly, above \(\mathrm{Re}_\delta^* \approx 520\). Add an adverse pressure gradient and an inflection point appears, giving a far more violent inviscid instability. This is why separation bubbles transition almost immediately and why favourable pressure gradients keep flow laminar.

**Critical Reynolds numbers**, as orientation rather than prediction:

| Flow | Critical | Note |
|---|---|---|
| Blasius boundary layer | \(\mathrm{Re}_{\delta^*}\approx520\) (\(\mathrm{Re}_x\approx9\times10^4\)) | linear onset, not transition |
| Flat plate, low freestream turbulence | \(\mathrm{Re}_x \sim 3\times10^6\) | transition completes far downstream |
| Plane Poiseuille | \(\mathrm{Re}\approx5772\) | linear; observed transition ~1000 |
| Pipe (Hagen–Poiseuille) | linearly stable at all \(\mathrm{Re}\) | transition ~2300 anyway |

Those last two rows are the point: **linear stability is neither necessary nor sufficient for transition.** Pipe flow is linearly stable forever and still transitions, through transient growth of non-normal modes.

**The route, when it is orderly** (low freestream turbulence, natural transition):

1. **Receptivity** — external disturbance enters the boundary layer.
2. **Linear growth** — Tollmien–Schlichting waves amplify exponentially.
3. **Secondary instability** — three-dimensional Λ-structures.
4. **Breakdown** — turbulent spots.
5. **Merging** — fully turbulent boundary layer.

**Bypass transition** skips stages 2–3. Above roughly 1% freestream turbulence, streamwise streaks grow algebraically (transient growth, non-modal) and break down directly. This is the normal mechanism in turbomachinery, where inflow turbulence is several percent.

**\(e^N\) method.** Integrate the linear growth rate and declare transition when the amplitude ratio reaches \(e^N\):

\[
N = \int_{x_0}^{x} -\alpha_i \, dx,
\qquad N \approx 9 \text{ for low-disturbance environments}
\]

\(N\) is a calibration against the disturbance environment, not a physical constant: wind tunnels with higher turbulence correlate to \(N\approx4\)–6, quiet flight to \(N\approx11\). Using \(N=9\) universally is the usual misuse.

**Transport-equation models.** \(\gamma\)–\(\mathrm{Re}_\theta\) and \(\gamma\)-only models add an intermittency equation to a RANS solver, correlating transition onset locally so the model works on unstructured meshes without a boundary-layer march. Practical and thoroughly empirical.

## Mental model

Think of the boundary layer as an amplifier with a gain that depends on frequency and Reynolds number, driven by whatever noise the environment supplies. Linear stability gives the gain curve. The environment gives the input. Transition happens when output reaches a threshold.

That picture explains why transition prediction is so environment-dependent: the same wing transitions at different places in a noisy tunnel and in flight, with identical gain. It also explains bypass — raise the input enough and you skip the amplifier entirely, because the disturbance is already large.

## Numerics / practice

- **Decide transition treatment deliberately** and state it. Fully-turbulent, fully-laminar, fixed-trip, and a transition model give materially different drag and heat transfer.
- **Trip the boundary layer explicitly** in a simulation if the experiment was tripped — comparing a natural-transition computation to tripped data is comparing different flows.
- **Report the \(N\)-factor and its basis** when using \(e^N\). Without the disturbance environment it is a tuned parameter presented as a prediction.
- Resolving transition in LES/DNS needs the receptivity and the streak spacing resolved — see [LES](turbulence/les.md) for the cost.

??? warning "Failure modes"
    **Assuming fully turbulent everywhere.** The safe-sounding default. On a laminar-flow aerofoil or a low-Reynolds-number rotor it can overpredict skin-friction drag by a factor of two and miss the laminar separation bubble entirely. "Conservative" in drag is not conservative in heat transfer, where it overpredicts too.

    **Linear onset reported as transition.** \(\mathrm{Re}_{\delta^*}=520\) is where TS waves *start growing*, typically far upstream of where the flow becomes turbulent. Quoting it as transition location is off by a large factor.

    **\(N=9\) used universally.** The \(N\)-factor encodes the disturbance environment. Applying the quiet-flight value to a conventional wind tunnel predicts transition much too far downstream; the error is systematic and the method gives no warning.

    **Bypass mechanism ignored at high freestream turbulence.** Above ~1% turbulence intensity the linear route is irrelevant, so an \(e^N\) prediction is not just inaccurate but modelling the wrong physics. Turbomachinery is the standard case.

    **Roughness neglected.** Surface roughness, steps and gaps trip transition well before any natural mechanism. A polished computation against a real, slightly rough surface will disagree, and the surface is usually right.

    **Transition model run on a mesh that cannot support it.** \(\gamma\)–\(\mathrm{Re}_\theta\) needs \(y^+ < 1\) and good streamwise resolution through the transition region. On a wall-function mesh it returns a transition location determined by the grid.

    **Comparing tripped experiment with untripped computation.** Extremely common, and it looks like a turbulence-model deficiency rather than a boundary-condition mismatch.

    <!-- Add your own here. -->

## Worked example

What assuming fully turbulent actually costs:

```python
import numpy as np

def cf_lam(Re):  return 1.328 / np.sqrt(Re)              # Blasius, plate-averaged
def cf_turb(Re): return 0.074 * Re**-0.2                 # fully turbulent from LE

def cf_mixed(Re, Re_tr):
    """Turbulent from the trip, with the usual transition correction."""
    return 0.074 * Re**-0.2 - (0.074 * Re_tr**-0.2 - 1.328 * Re_tr**-0.5) * Re_tr / Re

Re = 5e6
print(f"{'transition Re_x':>18}{'Cf mixed':>12}{'vs fully turb':>16}")
for Re_tr in (1e5, 5e5, 1e6, 2e6, 3e6):
    cm = cf_mixed(Re, Re_tr)
    print(f"{Re_tr:18.0e}{cm:12.5f}{cm/cf_turb(Re):15.2f}x")
print(f"\nfully laminar at Re=5e6 : {cf_lam(Re):.5f}  ({cf_lam(Re)/cf_turb(Re):.2f}x turbulent)")
print(f"fully turbulent          : {cf_turb(Re):.5f}")
```

```
   transition Re_x    Cf mixed   vs fully turb
             1e+05     0.00332           0.98x
             5e+05     0.00304           0.90x
             1e+06     0.00272           0.80x
             2e+06     0.00213           0.63x
             3e+06     0.00160           0.47x

fully laminar at Re=5e6 : 0.00059  (0.18x turbulent)
fully turbulent          : 0.00338
```

Moving transition from \(\mathrm{Re}_x=10^5\) to \(3\times10^6\) halves the skin-friction drag. Assuming fully turbulent when half the plate is laminar overpredicts it by nearly a factor of two — and on a natural-laminar-flow section, by much more.

## Connections

- [Governing equations](governing-equations.md) — the base flow being perturbed.
- [Turbulence](turbulence/index.md) — where transition ends up.
- [RANS closures](turbulence/rans.md) — transition models bolt onto these.
- [Aerospace › Aerodynamics](../aerospace/aerodynamics.md) — Reynolds effects on maximum lift.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — Orr–Sommerfeld is an eigenvalue problem.

## Sources

- Schmid & Henningson, *Stability and Transition in Shear Flows*.
- Drazin & Reid, *Hydrodynamic Stability*.
- Archive: `Aerospace/AERSP514`, `Mechanical/ME522`; see the [course archive](../resources/course-archive.md).
