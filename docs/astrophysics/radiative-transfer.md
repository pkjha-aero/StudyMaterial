---
title: Radiative transfer
status: solid
tags: [pillar-1, astrophysics, radiation, opacity]
updated: 2026-09-26
---

# Radiative transfer

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - The transfer equation is a **balance along a ray**: emission adds, absorption and scattering remove.
    - **Optical depth \(\tau\) is the organising variable.** \(\tau \gg 1\) is diffusive and local; \(\tau \ll 1\) is free-streaming and global. Methods that work in one regime fail in the other.
    - Radiation is a **6D problem** (3 space, 2 angle, 1 frequency) plus time — which is why almost everything practical is an approximation.
    - **LTE** makes the source function the Planck function and the problem tractable. It fails in thin, fast, or strongly irradiated gas.
    - Coupling radiation to hydrodynamics is stiff: photons move at \(c\), the fluid does not.

## Key results

**The transfer equation** along a ray of path length \(s\):

<div class="result" markdown>

\[
\frac{dI_\nu}{ds} = \underbrace{j_\nu}_{\text{emission}} - \underbrace{\alpha_\nu I_\nu}_{\text{extinction}}
\qquad\Longleftrightarrow\qquad
\frac{dI_\nu}{d\tau_\nu} = S_\nu - I_\nu
\]

with \(d\tau_\nu = \alpha_\nu\,ds\) and source function \(S_\nu = j_\nu/\alpha_\nu\).

</div>

**Formal solution:**

\[
I_\nu(\tau_\nu) = I_\nu(0)e^{-\tau_\nu} + \int_0^{\tau_\nu} S_\nu(t)\,e^{-(\tau_\nu - t)}\,dt
\]

Read directly: the background attenuated, plus emission from each layer attenuated by what lies in front of it. The \(e^{-\tau}\) weighting is why you "see" to about \(\tau\approx1\) and no deeper — the photosphere.

**LTE.** When collisions dominate, \(S_\nu = B_\nu(T)\), the Planck function:

\[
B_\nu(T) = \frac{2h\nu^3}{c^2}\frac{1}{e^{h\nu/kT}-1}
\]

**Regimes and their methods:**

| Regime | Physics | Method |
|---|---|---|
| \(\tau \gg 1\) | diffusion, local | Rosseland-mean diffusion |
| \(\tau \sim 1\) | neither | full transport, or flux-limited diffusion |
| \(\tau \ll 1\) | free streaming | ray tracing, Monte Carlo |

**Diffusion limit.** For \(\tau\gg1\) the radiation flux becomes

\[
\mathbf{F} = -\frac{c}{3\kappa_R\rho}\nabla E_r
\]

Unmodified, this permits \(|\mathbf{F}| > cE_r\) in thin regions — faster than light. **Flux-limited diffusion** patches it with a limiter \(\lambda(R)\) that recovers free streaming as \(\tau\to0\). It is a patch, not a derivation: FLD gets the two limits right and the transition region wrong, and it cannot cast shadows.

**Mean opacities.** Rosseland (harmonic, flux-weighted) for optically thick; Planck (arithmetic, emission-weighted) for optically thin. They differ by orders of magnitude when opacity is line-dominated, and using the wrong one is a quiet disaster:

\[
\frac{1}{\kappa_R} = \frac{\int \kappa_\nu^{-1}\,\partial B_\nu/\partial T\,d\nu}{\int \partial B_\nu/\partial T\,d\nu},
\qquad
\kappa_P = \frac{\int \kappa_\nu B_\nu\,d\nu}{\int B_\nu\,d\nu}
\]

**Moment methods.** Take angular moments of the transfer equation and close the hierarchy: M1 closure assumes a single dominant direction and can cast shadows (unlike FLD) but handles crossing beams incorrectly. Variable Eddington tensor solves a reduced transport problem for the closure — accurate, expensive.

## Mental model

Follow a photon. It travels until it is absorbed or scattered, a distance of order one mean free path \(1/(\kappa\rho)\). In a stellar interior that distance is centimetres, so radiation random-walks and behaves exactly like heat conduction — hence diffusion. In a nebula it crosses the whole object, so what happens here depends on sources everywhere else at once — a global, non-local problem.

The hard part is always the transition. Almost every real object has both regimes, and the interface between them is where the interesting physics (photospheres, ionisation fronts, shock breakout) lives — and where every approximate method is at its worst.

## Numerics / practice

- **Compute \(\tau\) across your domain first.** It tells you which method is defensible.
- **Monte Carlo** converges as \(1/\sqrt{N}\) but handles arbitrary geometry and scattering naturally. Discrete ordinates (\(S_N\)) is cheaper but suffers ray effects.
- **Check the opacity table's range.** Extrapolation off the edge of a tabulated \(\kappa(\rho,T)\) is a common and silent failure.
- **Subcycle or use implicit coupling** for radiation hydrodynamics; the explicit light-crossing timestep is unusable.

??? warning "Failure modes"
    **LTE assumed where it does not hold.** Requires collisions to dominate radiative rates. It fails in low-density, rapidly expanding, or strongly irradiated gas — stellar winds, nebulae, supernova ejecta. Symptom: line ratios and ionisation states that cannot be reconciled with observation whatever the temperature.

    **Flux-limited diffusion in the optically thin regime.** FLD is a diffusion approximation with a speed limit bolted on. It cannot cast a shadow: a beam behind an opaque obstacle diffuses in and illuminates the shadowed region. If shadows matter, FLD is the wrong tool regardless of how the limiter is tuned.

    **Wrong mean opacity.** Rosseland weights by \(1/\kappa\) and is dominated by *transparent* frequencies; Planck weights by emission. In a line-dominated regime they can differ by orders of magnitude, and the error looks like a temperature error.

    **Ray effects in discrete ordinates.** \(S_N\) with a finite angular quadrature produces unphysical striping in optically thin regions around localised sources — an artefact of the angular discretization, and it does not vanish under spatial refinement.

    **Opacity table extrapolation.** Densities or temperatures outside the tabulated range often return the edge value or a wild extrapolation. Symptom: a suspiciously smooth, flat opacity in the most extreme region of the run.

    **Explicit radiation-hydrodynamics coupling.** The radiation timescale is \(\Delta x/c\), the hydro timescale \(\Delta x/v\). Coupling them explicitly at \(v \ll c\) is unaffordable; a run that appears to proceed is probably violating its own stability limit.

    <!-- Add your own here. -->

## Worked example

Why \(\tau \approx 1\) defines what you see:

```python
import numpy as np

for tau in (0.1, 0.5, 1.0, 2.0, 5.0, 10.0):
    transmitted = np.exp(-tau)
    print(f"tau={tau:5.1f}   transmitted={transmitted:7.4f}   "
          f"cumulative emission fraction={1-transmitted:7.4f}")
```

```
tau=  0.1   transmitted= 0.9048   cumulative emission fraction= 0.0952
tau=  0.5   transmitted= 0.6065   cumulative emission fraction= 0.3935
tau=  1.0   transmitted= 0.3679   cumulative emission fraction= 0.6321
tau=  2.0   transmitted= 0.1353   cumulative emission fraction= 0.8647
tau=  5.0   transmitted= 0.0067   cumulative emission fraction= 0.9933
tau= 10.0   transmitted= 0.0000   cumulative emission fraction= 1.0000
```

By \(\tau=5\) more than 99% of what you observe originated in front of that point — the photosphere is not a surface, it is the depth at which the exponential runs out.

## Connections

- [MHD](mhd.md) — radiation-MHD in accretion and stellar interiors.
- [Plasma](plasma.md) — emission and absorption mechanisms.
- [Meteorology › Radiation](../meteorology/index.md) — the same equation, different opacity sources.
- [Foundations › Numerical methods](../foundations/numerical-methods.md) — stiffness and operator splitting.

## Sources

- Mihalas & Mihalas, *Foundations of Radiation Hydrodynamics*.
- Rybicki & Lightman, *Radiative Processes in Astrophysics*.
- Archive: see the [course archive](../resources/course-archive.md) for the Astro folders.
