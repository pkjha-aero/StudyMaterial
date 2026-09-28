---
title: Aeroacoustics
status: working
tags: [pillar-1, aerospace, turbulence, scaling, discretization]
updated: 2026-09-28
---

# Aeroacoustics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - **Lighthill's analogy** rearranges Navier–Stokes exactly into a wave equation with a source term. Nothing is approximated; the approximation enters when you estimate the source.
    - **Velocity scaling separates the mechanisms**: monopole \(U^4\), dipole \(U^6\), quadrupole \(U^8\). That exponent tells you which one you are hearing.
    - Acoustic energy is a **tiny fraction** of the flow energy — around \(10^{-4}\) of jet power — so any numerical dissipation comparable to it destroys the answer.
    - **Hybrid CFD + FW-H is the practical method**: resolve the source region, propagate analytically to the observer.
    - Noise is a *perceived* quantity. A-weighting and tonality mean two fields with equal acoustic power can be rated very differently.

## Key results

**Lighthill's acoustic analogy** — exact, by construction:

<div class="result" markdown>

\[
\frac{\partial^2 \rho'}{\partial t^2} - a_0^2\nabla^2\rho'
= \frac{\partial^2 T_{ij}}{\partial x_i \partial x_j},
\qquad
T_{ij} = \rho u_i u_j + \left(p' - a_0^2\rho'\right)\delta_{ij} - \tau_{ij}
\]

</div>

The left side is sound in a uniform medium at rest; everything else is pushed into \(T_{ij}\), the Lighthill stress tensor. The physics has not been simplified — the difficulty has been *relocated* into knowing \(T_{ij}\), which requires the turbulent flow field.

**Ffowcs Williams–Hawkings** extends this to moving surfaces, and splits the radiated sound into three physically distinct terms:

| Term | Source | Physically | Scales as |
|---|---|---|---|
| Monopole | surface displacement (thickness) | volume the body pushes aside | \(U^4\) |
| Dipole | surface loading | unsteady force on the fluid | \(U^6\) |
| Quadrupole | volume (Lighthill stress) | turbulence itself | \(U^8\) |

**Lighthill's eighth-power law** for jet noise, \(P_{ac} \sim \rho_0 U^8 D^2 / a_0^5\), is the single most consequential scaling in the subject: halving jet velocity cuts acoustic power by a factor of 256. That is why high-bypass turbofans are quiet — the same reasoning as [propulsive efficiency](propulsion.md), arriving at the same design from a different direction.

**Acoustic efficiency** is minuscule:

\[
\eta_{ac} = \frac{P_{ac}}{P_{mech}} \sim 10^{-4}\ \text{for a jet}
\]

which is why aeroacoustics is numerically brutal: the quantity of interest is four orders of magnitude below the flow energy, so a scheme that loses even a fraction of a percent per wavelength destroys it.

**Rotor noise**, the rotorcraft and propeller case:

- **Thickness noise** — monopole, blade volume displacement, in-plane, low frequency.
- **Loading noise** — dipole, unsteady blade lift, dominant below the rotor.
- **Blade–vortex interaction (BVI)** — impulsive loading when a blade strikes a previous tip vortex; the characteristic slap, and the reason descent is the noisiest flight condition.
- **High-speed impulsive** — transonic tip effects, delocalised shock.
- **Broadband** — turbulence ingestion and trailing-edge noise.

**Metrics.** SPL in dB re 20 µPa; OASPL integrates over frequency; **A-weighting** approximates human sensitivity and heavily discounts low frequency; EPNdB adds tone and duration corrections for certification. Decibels are logarithmic, so two equal incoherent sources give +3 dB, not double.

## Mental model

Sound is the small compressible remainder of a flow that is mostly doing something else. The analogy formalises that: write the exact equations, move everything that is not a simple wave to the right-hand side, and call it a source.

That framing explains both the method's power and its trap. Power, because you can compute the source with a method suited to the flow and propagate it with a method suited to waves. Trap, because the analogy is only as good as the source field — an under-resolved or over-dissipated CFD solution produces a confident, quiet, wrong answer.

## Numerics / practice

- **Hybrid is the default**: LES or DES of the source region, FW-H surface integral to the far field. Direct computation of both flow and far field is affordable only at small scale.
- **Place the FW-H surface** where the flow is still resolved, and check the answer is insensitive to its position. A surface through a region of coarsening grid contaminates the result.
- **Use low-dissipation schemes and resolve the acoustic wavelength**, not just the turbulence. Acoustic wavelengths are typically much longer than eddies, but they must survive propagation — see the [modified wavenumber notebook](../notebooks/modified-wavenumber.ipynb) for what a scheme does to a wave over distance.
- **Non-reflecting boundaries are mandatory.** A reflected wave is indistinguishable from a source.

??? warning "Failure modes"
    **Numerical dissipation swamping the acoustics.** Acoustic energy is ~\(10^{-4}\) of the flow energy. A second-order upwind scheme at 8 points per wavelength loses a quarter-wavelength of phase in 2.5 wavelengths of travel and attenuates as it goes — so the far-field signal is the scheme's, not the flow's. The symptom is a spectrum that decays with distance faster than the geometric \(1/r\).

    **Acoustic analogy fed a bad source.** The analogy is exact; the source is not. An under-resolved LES gives a smooth, quiet quadrupole field and a plausible-looking result. Validate the source statistics before trusting the radiated field.

    **Reflections from the domain boundary.** A reflected wave arrives at the observer as a spurious source. Symptom: tones at frequencies corresponding to domain dimensions divided by sound speed. Characteristic or sponge boundaries, and check by varying the domain size.

    **Near field mistaken for far field.** Within roughly a wavelength, hydrodynamic pressure fluctuations vastly exceed acoustic ones and do not radiate. Sampling "noise" there measures turbulence, not sound. The far field begins beyond several wavelengths and several source dimensions.

    **Decibel arithmetic.** Two incoherent equal sources give +3 dB; ten give +10 dB. Averaging dB values directly is wrong — convert to intensity, average, convert back. This error is common and always in the flattering direction when summing.

    **A-weighted and unweighted compared.** dB(A) discounts low frequency heavily, so a change that reduces broadband high-frequency noise looks large in dB(A) and small unweighted. Quote the weighting, always.

    **FW-H surface inside the nonlinear region.** The formulation assumes the surface encloses all sources, with linear propagation outside. Placed too close, quadrupole sources outside the surface are omitted; too far, it sits in a coarse grid. Both fail quietly.

    <!-- Add your own here. -->

## Worked example

Why the velocity exponent identifies the mechanism, and what it means for design:

```python
import numpy as np

U_ref = 300.0                      # reference jet velocity, m/s
print(f"{'U (m/s)':>9}{'U/Uref':>9}{'monopole U^4':>15}{'dipole U^6':>13}{'quadrupole U^8':>17}")
for U in (150, 200, 250, 300, 400):
    r = U / U_ref
    print(f"{U:9.0f}{r:9.2f}{r**4:15.3f}{r**6:13.3f}{r**8:17.3f}")

print()
for U in (150, 250):
    r = U / U_ref
    print(f"halving-ish to {U:3.0f} m/s: quadrupole power x{r**8:.3f} "
          f"= {10*np.log10(r**8):+.1f} dB")
```

```
  U (m/s)   U/Uref   monopole U^4   dipole U^6   quadrupole U^8
      150     0.50          0.062        0.016            0.004
      200     0.67          0.198        0.088            0.039
      250     0.83          0.482        0.335            0.233
      300     1.00          1.000        1.000            1.000
      400     1.33          3.160        5.619            9.989

halving-ish to 150 m/s: quadrupole power x0.004 = -24.1 dB
halving-ish to 250 m/s: quadrupole power x0.233 = -6.3 dB
```

Halving jet velocity removes 24 dB of quadrupole noise — a factor of 256 in acoustic power. Nothing else in the designer's control comes close, which is why bypass ratio rather than acoustic treatment did most of the work in making jets quieter.

## Connections

- [Propulsion](propulsion.md) — bypass ratio, arrived at from efficiency rather than noise.
- [Rotorcraft](rotorcraft.md) — BVI and the descent noise problem.
- [Wind energy](wind-energy.md) — trailing-edge noise is the binding siting constraint.
- [Fluids › LES](../fluids/turbulence/les.md) — the source field, and why numerical dissipation matters.
- [Modified wavenumber notebook](../notebooks/modified-wavenumber.ipynb) — what a scheme does to a wave over distance.

## Sources

- Lighthill (1952), *On sound generated aerodynamically I: General theory*.
- Ffowcs Williams & Hawkings (1969), *Sound generation by turbulence and surfaces in arbitrary motion*.
- Goldstein, *Aeroacoustics*.
- Archive: `Aerospace/AERSP511`; see the [course archive](../resources/course-archive.md).
