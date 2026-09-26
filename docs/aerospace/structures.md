---
title: Structures and aeroelasticity
status: solid
tags: [pillar-1, aerospace]
updated: 2026-09-26
---

# Structures and aeroelasticity

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Aerospace structures are **stiffness- and stability-driven**, not strength-driven. Thin-walled sections fail by buckling long before the material yields.
    - **Shear centre, not centroid**, is where a transverse load produces no twist. Open thin-walled sections have it well outside the section.
    - **Aeroelasticity is a coupling problem**: aerodynamic loads deform the structure, deformation changes the loads. Divergence and control reversal are static; flutter is dynamic.
    - **Flutter cannot be found from modes in isolation** — it is the coalescence of two modes under aerodynamic coupling.
    - Fatigue and damage tolerance, not static strength, size most of the airframe life.

## Key results

**Beam bending and torsion:**

<div class="result" markdown>

\[
\sigma = \frac{M y}{I},
\qquad
\tau = \frac{VQ}{It},
\qquad
\theta = \frac{TL}{GJ}
\]

For a closed thin-walled section, Bredt–Batho gives shear flow \(q = T/(2A_m)\) with \(A_m\) the enclosed area. A closed section is dramatically stiffer in torsion than an open one of the same material — often by two or three orders of magnitude.

</div>

**Euler buckling**, and its validity limit:

\[
P_{cr} = \frac{\pi^2 EI}{(KL)^2},
\qquad
\sigma_{cr} = \frac{\pi^2 E}{(KL/r)^2}
\]

Valid only while \(\sigma_{cr} < \sigma_y\), i.e. above the critical slenderness \((KL/r)_{crit} = \pi\sqrt{2E/\sigma_y}\). Below it, inelastic buckling (Johnson parabola) or crippling governs.

\(K\): 1.0 pinned–pinned, 0.5 fixed–fixed, 0.7 fixed–pinned, 2.0 cantilever.

**Aeroelastic phenomena:**

| Phenomenon | Type | Mechanism |
|---|---|---|
| Divergence | static | aerodynamic moment outgrows torsional stiffness |
| Control reversal | static | surface deflection twists the wing the other way |
| Flutter | dynamic | two modes coalesce, extracting energy from the flow |
| Buffet | dynamic, forced | separated-flow excitation |
| LCO | nonlinear | limit-cycle oscillation, bounded amplitude |

**Divergence speed** for a simple typical section:

\[
q_{\text{div}} = \frac{K_\theta}{e\,S\,C_{L_\alpha}},
\qquad
V_{\text{div}} = \sqrt{\frac{2q_{\text{div}}}{\rho}}
\]

with \(K_\theta\) torsional stiffness and \(e\) the distance from elastic axis to aerodynamic centre. Moving the elastic axis forward (or the AC aft) raises it.

**Flutter.** The classic binary flutter mechanism is bending and torsion coalescing: as speed rises their frequencies approach, and at \(V_f\) the damping of one mode goes negative. Determined by V-g or p-k analysis, not by looking at modes separately.

**Fatigue.** Basquin/Miner for crack initiation, Paris law for propagation:

\[
\frac{da}{dN} = C(\Delta K)^m,
\qquad
\Delta K = \Delta\sigma\,\beta\sqrt{\pi a}
\]

Damage tolerance assumes cracks exist and sets inspection intervals so they are found before reaching critical length.

## Mental model

A wing is a cantilever beam that must be as light as possible, so every part is thin, so everything is a stability problem. A flat panel in compression does not crush — it buckles, and then carries load only near its stiffened edges. That is why skins are stiffened by stringers and ribs at spacings chosen to keep buckling above limit load, and why "effective width" appears everywhere in airframe sizing.

Aeroelasticity is a feedback loop. Static aeroelasticity asks whether the loop gain exceeds one at zero frequency — that is divergence. Flutter asks whether at some frequency the aerodynamic forces are phased so they do positive work on the structure over a cycle. Phase, not magnitude, is what makes flutter possible.

## Numerics / practice

- **Check the slenderness ratio before applying Euler.** Short columns fail inelastically at loads well below the Euler prediction.
- **Locate the shear centre** for any open section carrying transverse load. Applying load at the centroid of a C-section twists it.
- **Flutter needs coupled aero-structural analysis.** A modal analysis alone gives frequencies, not stability.
- **Run the V-g diagram across the full envelope**, including altitude — flutter speed varies with density and Mach.

??? warning "Failure modes"
    **Euler buckling applied to a short column.** Beyond the slenderness limit the formula predicts a critical stress above yield, which is physically impossible. Symptom: a predicted buckling load higher than the squash load — an obvious tell, and still a recurring error.

    **Load applied at the centroid of an open section.** Produces unintended torsion that a bending-only analysis never sees. Thin-walled open sections are extremely torsionally soft, so the resulting twist is large.

    **Flutter inferred from mode frequencies alone.** "The modes are well separated so it will not flutter" is not an argument — frequencies migrate with airspeed, and coalescence is exactly what happens as \(V\) increases. Only a coupled analysis answers it.

    **Linear flutter analysis in the transonic dip.** Flutter speed drops sharply near \(M \approx 0.8\text{–}0.9\) where shock motion couples with structural modes. Linear aerodynamics misses the dip entirely — and the dip is where the minimum sits.

    **Stress concentration ignored at cutouts.** A hole raises local stress by roughly \(3\times\) for an infinite plate in tension. Fatigue cracks start at fastener holes and cutouts, essentially always.

    **Composite treated as isotropic.** Laminate stiffness is directional and bend-twist coupling can be deliberately designed in (aeroelastic tailoring) or accidentally introduced. Using an isotropic equivalent loses the effect that matters most.

    **Static strength taken as life.** Meeting ultimate load says nothing about fatigue. Most airframe structure is fatigue- or damage-tolerance-sized.

    <!-- Add your own here. -->

## Worked example

The slenderness limit, and what happens if you ignore it:

```python
import numpy as np

E, sigma_y = 71e9, 350e6            # aluminium
slend_crit = np.pi * np.sqrt(2 * E / sigma_y)
print(f"critical slenderness KL/r = {slend_crit:.1f}")

for s in (40.0, 80.0, 150.0):
    sig_euler = np.pi**2 * E / s**2
    governs = "Euler" if sig_euler < sigma_y else "INELASTIC (Euler invalid)"
    print(f"KL/r={s:5.0f}  sigma_euler={sig_euler/1e6:8.1f} MPa   {governs}")
```

```
critical slenderness KL/r = 63.3
KL/r=   40  sigma_euler=   438.0 MPa   INELASTIC (Euler invalid)
KL/r=   80  sigma_euler=   109.5 MPa   Euler
KL/r=  150  sigma_euler=    31.1 MPa   Euler
```

At \(KL/r = 40\) the Euler formula predicts a critical stress 25% above yield — the column would have squashed first. The formula gives a number regardless; the slenderness check is what tells you whether to believe it.

## Connections

- [Aerodynamics](aerodynamics.md) — the loads being carried.
- [Flight mechanics](flight-mechanics.md) — load factors and the manoeuvre envelope.
- [Rotorcraft](rotorcraft.md) — rotating-blade dynamics and ground resonance.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — eigenvalue problems behind buckling and flutter.

## Sources

- Megson, *Aircraft Structures for Engineering Students*.
- Hodges & Pierce, *Introduction to Structural Dynamics and Aeroelasticity*.
- Archive: see the [course archive](../resources/course-archive.md).
