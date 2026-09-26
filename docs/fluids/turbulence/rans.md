---
title: RANS closures
status: solid
tags: [pillar-1, fluids, turbulence, rans, wall-functions]
updated: 2026-09-26
---

# RANS closures

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - RANS replaces six unknown Reynolds stresses with a model. Almost all production models use the **Boussinesq hypothesis**: stress aligned with mean strain, via a scalar eddy viscosity.
    - That single assumption is the source of most RANS failures — it cannot represent anisotropy, curvature, rotation or secondary flows.
    - **k–ε** is robust in free shear, poor near walls and in adverse pressure gradient. **k–ω SST** blends ω near the wall with ε outside and is the sane default for aerodynamics.
    - **\(y^+\) decides your wall treatment**, and the buffer layer \(5 < y^+ < 30\) is the one place you must not put the first cell.
    - RANS is calibrated on attached, equilibrium, near-isotropic flows. Massive separation is outside its domain of validity, not merely hard for it.

## Key results

**Boussinesq hypothesis:**

<div class="result" markdown>

\[
-\overline{u_i'u_j'} = \nu_t\left(\frac{\partial \overline{u}_i}{\partial x_j} + \frac{\partial \overline{u}_j}{\partial x_i}\right) - \frac{2}{3}k\,\delta_{ij}
\]

</div>

One scalar \(\nu_t\) now carries all six stress components. The trace term keeps the identity \(k = \tfrac{1}{2}\overline{u_i'u_i'}\) consistent.

**k–ε**, with \(\nu_t = C_\mu k^2/\varepsilon\), \(C_\mu = 0.09\):

\[
\frac{Dk}{Dt} = P - \varepsilon + \nabla\cdot\left[\left(\nu + \frac{\nu_t}{\sigma_k}\right)\nabla k\right],
\qquad
\frac{D\varepsilon}{Dt} = \frac{\varepsilon}{k}\left(C_{1}P - C_{2}\varepsilon\right) + \nabla\cdot\left[\left(\nu + \frac{\nu_t}{\sigma_\varepsilon}\right)\nabla\varepsilon\right]
\]

with \(C_1 = 1.44\), \(C_2 = 1.92\), \(\sigma_k = 1.0\), \(\sigma_\varepsilon = 1.3\). The \(\varepsilon\) equation is largely empirical — it is not derived from anything.

**k–ω SST** uses \(\nu_t = a_1 k/\max(a_1\omega,\; S F_2)\). Two ideas matter:

1. A blending function activates k–ω near the wall and k–ε in the free stream, removing k–ω's notorious free-stream sensitivity.
2. The **shear-stress limiter** caps \(\nu_t\) in adverse pressure gradient, which is what makes SST predict separation onset far better than k–ε.

**Spalart–Allmaras** solves one transport equation for \(\tilde{\nu}\). Cheap, robust, well-tuned for attached aerodynamic boundary layers; not intended for free shear or massive separation.

**Law of the wall**, with \(u_\tau = \sqrt{\tau_w/\rho}\), \(y^+ = y u_\tau/\nu\), \(u^+ = \overline{u}/u_\tau\):

\[
u^+ = y^+ \quad (y^+ \lesssim 5),
\qquad
u^+ = \frac{1}{\kappa}\ln y^+ + B \quad (y^+ \gtrsim 30)
\]

\(\kappa \approx 0.41\), \(B \approx 5.0\).

| First-cell \(y^+\) | Treatment | Notes |
|---|---|---|
| \(\lesssim 1\) | resolve to the wall | needs a low-\(\mathrm{Re}\) model; 10–20 cells inside \(y^+<20\) |
| \(5\)–\(30\) | **avoid** | buffer layer: neither asymptote is valid |
| \(30\)–\(300\) | wall functions | valid only for attached equilibrium flow |

## Mental model

Eddy viscosity says: turbulent mixing behaves like a much larger molecular viscosity, and momentum flux points down the mean velocity gradient. That is a good picture for a simple shear layer, where the largest eddies genuinely do scramble momentum across the gradient.

It breaks wherever stress and strain are *not* aligned. In a square duct, the secondary flow in the corners is driven entirely by Reynolds stress anisotropy — a quantity Boussinesq sets to zero by construction. k–ε predicts no secondary flow at all. Not inaccurately: none.

## Numerics / practice

- **Check the realised \(y^+\)** after the run, not before. It depends on the solution.
- **Free-stream turbulence values matter.** k–ω without SST blending is sensitive to inlet \(\omega\); results can shift by percent-level on a value nobody measured.
- **Production limiters** are standard for a reason — see the stagnation anomaly below.
- **Grid convergence with wall functions is not meaningful** in the usual sense: refining the near-wall mesh moves \(y^+\) out of the valid range. Refine everywhere else, or switch to wall-resolved.

??? warning "Failure modes"
    **Stagnation point anomaly.** At a bluff-body leading edge, \(P = \nu_t S^2\) with large normal strain produces enormous spurious \(k\). That turbulence convects downstream and suppresses separation. Symptom: unrealistically high heat transfer at a leading edge, and a separation bubble that will not appear. Fix: a production limiter (Kato–Launder or \(P \le C\varepsilon\)). This is the single most common silent RANS error in external aerodynamics.

    **k–ε in adverse pressure gradient.** Over-predicts \(\nu_t\), so the boundary layer stays attached far past where it should separate. Symptom: pressure recovery too good, drag too low. SST's shear-stress limiter exists specifically for this.

    **First cell in the buffer layer.** \(5 < y^+ < 30\) satisfies neither the viscous sublayer nor the log law. Most codes blend, but the blend is a fit, not physics. Symptom: wall shear stress that changes with mesh refinement in a non-converging way.

    **Round-jet / plane-jet anomaly.** Standard k–ε gets the round jet spreading rate wrong by about 15% in the opposite direction to the plane jet. A calibration artefact: the constants cannot satisfy both.

    **Wall functions on separated flow.** The log law assumes attached equilibrium. At and near a separation point \(u_\tau \to 0\), so \(y^+ \to 0\) and the formulation degenerates. Results near reattachment are not trustworthy.

    **Boussinesq where anisotropy is the answer.** Secondary flows in non-circular ducts, strongly curved or rotating flows, and swirl. Linear eddy viscosity predicts zero effect. A Reynolds-stress model or a nonlinear/explicit algebraic closure is the fix, at a robustness cost.

    **Treating RANS convergence as validation.** A tightly converged residual on a model outside its calibration range is a precise answer to the wrong equations.

    <!-- Add your own here. -->

## Worked example

Sizing the first cell — do this before meshing, and check after solving:

```python
import numpy as np

rho, U, L, mu = 1.225, 50.0, 2.0, 1.8e-5
nu = mu / rho
Re = U * L / nu

cf     = 0.058 * Re**-0.2            # flat-plate turbulent skin friction
u_tau  = U * np.sqrt(cf / 2.0)
for target in (1.0, 30.0, 300.0):
    y = target * nu / u_tau
    print(f"y+ = {target:5.0f}  ->  first cell height = {y*1e3:.4f} mm")
```

```
y+ =     1  ->  first cell height = 0.0083 mm
y+ =    30  ->  first cell height = 0.2497 mm
y+ =   300  ->  first cell height = 2.4967 mm
```

A factor of 300 in first-cell height between wall-resolved and wall-function meshes — which is why the choice is made at meshing time, not afterwards.

## Connections

- [Turbulence](index.md) — scales, cascade, and the closure problem.
- [LES](les.md) — the alternative when the mean is not enough.
- [Meshing](../cfd/meshing.md) — boundary-layer meshing and growth ratios.

## Sources

- Wilcox, *Turbulence Modeling for CFD* — model equations and their calibration history.
- Menter (1994), *Two-equation eddy-viscosity turbulence models for engineering applications* — SST.
- Archive: `Others/Turbulence_JCM`, `Others/UMD_Turb`.
