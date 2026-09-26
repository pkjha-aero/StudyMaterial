---
title: Aerodynamics
status: solid
tags: [pillar-1, aerospace, airfoils, lifting-line, compressibility]
updated: 2026-09-26
---

# Aerodynamics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Lift comes from **circulation**: \(L' = \rho U \Gamma\). The Kutta condition is what selects \(\Gamma\) for a given shape and incidence.
    - Thin airfoil theory gives \(c_\ell = 2\pi\alpha\) and the quarter-chord aerodynamic centre — good to within a few percent below stall, useless above it.
    - **Induced drag is the price of finite span**: \(C_{D_i} = C_L^2/(\pi e \mathrm{AR})\). It falls with speed while profile drag rises, which sets minimum-drag speed.
    - **Prandtl–Glauert** corrects for compressibility until it does not — it is singular at \(M=1\) and unusable transonically.
    - Potential-flow methods cannot predict separation or maximum lift. Those need viscous physics.

## Key results

**Kutta–Joukowski**, and thin airfoil theory for a cambered section:

<div class="result" markdown>

\[
L' = \rho U_\infty \Gamma,
\qquad
c_\ell = 2\pi(\alpha - \alpha_{L=0}),
\qquad
x_{ac} = \frac{c}{4}
\]

</div>

The lift-curve slope \(2\pi\) per radian (\(\approx 0.11\) per degree) is the reference every real airfoil is measured against; real sections reach 90–95% of it.

**Finite wing — Prandtl lifting line:**

\[
C_L = \frac{C_{L_\alpha,\,2\mathrm{D}}}{1 + \frac{C_{L_\alpha,\,2\mathrm{D}}}{\pi e \mathrm{AR}}}\,\alpha,
\qquad
C_{D_i} = \frac{C_L^2}{\pi e\, \mathrm{AR}},
\qquad
\alpha_i = \frac{C_L}{\pi e\,\mathrm{AR}}
\]

Elliptical loading gives \(e = 1\) and minimum induced drag; typical wings reach \(e \approx 0.7\text{–}0.85\).

**Drag decomposition:**

| Component | Scales as | Dominant when |
|---|---|---|
| Induced | \(C_L^2/\mathrm{AR}\), so \(\propto 1/V^2\) | slow, heavy, high \(C_L\) |
| Profile (skin friction + form) | \(\propto V^2\) | fast, low \(C_L\) |
| Wave | onset above \(M_{crit}\) | transonic and above |

Minimum drag occurs where induced equals profile drag — which is also where \(L/D\) is maximum.

**Drag polar:**

\[
C_D = C_{D_0} + \frac{C_L^2}{\pi e \mathrm{AR}},
\qquad
\left(\frac{L}{D}\right)_{\max} = \frac{1}{2}\sqrt{\frac{\pi e \mathrm{AR}}{C_{D_0}}}
\]

**Compressibility.** Prandtl–Glauert for subsonic flow:

\[
c_p = \frac{c_{p,0}}{\sqrt{1-M_\infty^2}}
\]

Critical Mach \(M_{crit}\) is where local flow first reaches sonic; drag divergence follows shortly after. Sweep delays both by acting on the normal component: \(M_{\text{eff}} \approx M_\infty\cos\Lambda\).

**Reynolds effects.** \(C_{L,\max}\) and stall behaviour depend strongly on \(\mathrm{Re}\) — transition location changes, and a laminar separation bubble at low \(\mathrm{Re}\) can halve maximum lift. Wind-tunnel data at \(\mathrm{Re}=10^6\) does not transfer to flight at \(10^7\).

## Mental model

A wing deflects air downwards; the reaction is lift. The downwash it generates at its own location tilts the local flow, so the effective incidence is less than the geometric one, and the lift vector tilts backwards by that angle — that backward component *is* induced drag. Nothing is lost to friction; the energy goes into the trailing vortex system.

That picture explains why span matters more than area for induced drag, why gliders have enormous aspect ratio, and why formation flight saves fuel.

## Numerics / practice

- **Panel methods** (vortex/source/doublet) solve potential flow cheaply and are excellent for attached, thin-boundary-layer cases. Coupled to an integral boundary-layer method (as XFOIL does) they predict separation onset reasonably.
- **Report \(\mathrm{Re}\) and \(M\)** with any aerodynamic coefficient. Without both, the number is not interpretable.
- **Check \(e\)** against the planform rather than assuming 1. Taper, twist and fuselage interference all reduce it.
- For CFD, see [fluids › CFD](../fluids/cfd/index.md); the failure modes there apply directly.

??? warning "Failure modes"
    **Thin airfoil theory near stall.** \(c_\ell = 2\pi\alpha\) has no maximum — extrapolate it past about 10–12° and it predicts lift a real wing cannot produce. It is a linear theory with no viscous physics.

    **Prandtl–Glauert approaching \(M=1\).** The \(1/\sqrt{1-M^2}\) factor diverges. Above roughly \(M=0.7\) it is already poor and transonically it is meaningless. Symptom: pressure coefficients growing without bound as the design Mach rises.

    **Lifting line at low aspect ratio.** The theory assumes high \(\mathrm{AR}\) and small sweep. Below \(\mathrm{AR}\approx4\), or on strongly swept or delta wings, it is wrong in kind — those wings generate lift partly through leading-edge vortices, a mechanism the theory does not contain.

    **2D section data applied directly to a 3D wing.** Ignores downwash, so it overpredicts lift-curve slope and omits induced drag entirely. The correction is not small: at \(\mathrm{AR}=8\) the 3D slope is about 80% of 2D.

    **Reynolds number mismatch.** Sub-scale tunnel data at \(\mathrm{Re}\sim10^5\)–\(10^6\) can show laminar separation bubbles absent at flight \(\mathrm{Re}\). \(C_{L,\max}\) is the most affected quantity and the one most often transferred uncorrected.

    **Potential-flow methods asked to predict separation.** They will return an answer — a smooth, attached, plausible one — at 25° incidence. There is no mechanism in the formulation for the flow to leave the surface.

    **Ignoring trim drag.** The tail download to trim reduces effective lift and adds drag. Cruise polars built from wing-alone data are optimistic.

    <!-- Add your own here. -->

## Worked example

Where minimum drag sits, and why it is also best \(L/D\):

```python
import numpy as np

CD0, e, AR = 0.022, 0.80, 9.0
k  = 1.0 / (np.pi * e * AR)
CL = np.sqrt(CD0 / k)                    # induced drag == profile drag
LD = CL / (CD0 + k * CL**2)
print(f"k            = {k:.5f}")
print(f"CL at min drag = {CL:.3f}")
print(f"(L/D)max       = {LD:.2f}")
print(f"check formula  = {0.5*np.sqrt(np.pi*e*AR/CD0):.2f}")
```

```
k            = 0.04421
CL at min drag = 0.705
(L/D)max       = 16.03
check formula  = 16.03
```

Best \(L/D\) occurs at exactly the \(C_L\) where the two drag contributions are equal — which is why a clean, high-aspect-ratio wing flies its best-range speed slower than intuition suggests.

## Connections

- [Flight mechanics](flight-mechanics.md) — the drag polar feeds range and climb directly.
- [Fluids › Compressible flow](../fluids/compressible.md) — transonic and supersonic behaviour.
- [Fluids › Turbulence](../fluids/turbulence/index.md) — boundary layers, transition, separation.
- [Rotorcraft](rotorcraft.md) — the same section aerodynamics on a rotating blade.

## Sources

- Anderson, *Fundamentals of Aerodynamics*.
- Katz & Plotkin, *Low-Speed Aerodynamics* — panel methods.
- Archive: see the [course archive](../resources/course-archive.md) for the Aerospace folders.
