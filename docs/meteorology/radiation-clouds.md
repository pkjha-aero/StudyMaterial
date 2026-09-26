---
title: Radiation and clouds
status: working
tags: [pillar-1, meteorology, radiation, microphysics, parameterization]
updated: 2026-09-26
---

# Radiation and clouds

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Solar and terrestrial radiation barely overlap in wavelength, so they are treated as two nearly independent problems — shortwave and longwave.
    - The **greenhouse effect** is an emission-height argument: adding absorbers raises the level from which radiation escapes, and that level is colder.
    - **Clouds are the largest uncertainty in climate projection**, because they both reflect sunlight and trap infrared, and the two nearly cancel.
    - Microphysics schemes are **bulk** (moments of an assumed distribution) or **bin** (resolved spectrum). Bulk is affordable; bin is what you validate against.
    - The **independent column approximation** ignores horizontal photon transport, which matters increasingly as grids get finer.

## Key results

**Two spectral regimes:**

<div class="result" markdown>

| | Shortwave | Longwave |
|---|---|---|
| Source | Sun, \(T\approx5780\) K | Earth/atmosphere, \(T\approx255\) K |
| Peak | 0.5 µm | 10 µm |
| Main absorbers | \(\mathrm{O_3}\), \(\mathrm{H_2O}\), clouds | \(\mathrm{H_2O}\), \(\mathrm{CO_2}\), \(\mathrm{O_3}\), clouds |
| Scattering | dominant (Rayleigh, Mie) | mostly negligible |

</div>

**Energy balance and emission height:**

\[
\frac{S_0(1-\alpha)}{4} = \sigma T_e^4
\qquad\Longrightarrow\qquad
T_e \approx 255\ \mathrm{K}
\]

Surface temperature is ~288 K. The 33 K difference is the greenhouse effect: \(T_e\) is the temperature at the *effective emission level* (around 5 km), and the surface is warmer by the lapse rate times that height. Adding CO₂ raises the emission level into colder air, reducing outgoing radiation until the whole column warms.

**Two-stream approximation.** Reduce the angular problem to upward and downward fluxes:

\[
\frac{dF^\uparrow}{d\tau} = \gamma_1 F^\uparrow - \gamma_2 F^\downarrow - \text{source},
\qquad
\frac{dF^\downarrow}{d\tau} = \gamma_2 F^\uparrow - \gamma_1 F^\downarrow + \text{source}
\]

Cheap enough for every column every timestep, which is the binding constraint. Correlated-\(k\) methods (RRTMG) handle the spectral integration by grouping absorption coefficients rather than resolving thousands of lines.

**Cloud radiative effect:**

\[
\mathrm{CRE} = F_{\text{all-sky}} - F_{\text{clear-sky}}
\]

Globally, shortwave CRE \(\approx -45\) W/m² (cooling) and longwave \(\approx +30\) W/m² (warming), netting about \(-20\) W/m². Low clouds cool; high thin cirrus warm. Since the two terms are large and opposite, small errors in cloud amount or height produce large net errors.

**Microphysics.** Bulk schemes predict moments of an assumed size distribution \(N(D) = N_0 D^\mu e^{-\lambda D}\):

| Scheme | Predicts | Cost |
|---|---|---|
| Single-moment | mass mixing ratio only | cheapest |
| Double-moment | mass + number concentration | standard for research |
| Bin / spectral | the distribution itself, 30–100 bins | 10–100× more expensive |

Key parameterised processes: **nucleation** (CCN/IN activation), **condensation/deposition**, **autoconversion** (cloud → rain, the most uncertain step), **accretion**, **riming**, **melting**, **sedimentation**.

**Cloud overlap.** A model column has cloud fraction per layer and must assume how layers overlap: maximum, random, or **maximum-random** (adjacent layers maximally, separated layers randomly) — the usual compromise. The choice changes total cloud cover by several percent globally.

## Mental model

Radiation is an energy transport problem with two almost separate spectral halves, and clouds are the switch that connects them. Water droplets are nearly perfect reflectors in the shortwave and nearly black in the longwave, so a cloud flips the local radiation balance depending on its height: high and cold means weak reflection but strong trapping (net warming); low and warm means strong reflection and trapping that barely matters because it emits at nearly surface temperature (net cooling).

Microphysics is where the small scales assert themselves. Whether a cloud rains out in twenty minutes or persists for hours depends on droplet-size distributions determined by aerosol at submicron scales — and the model has to represent that with two numbers per species.

## Numerics / practice

- **Call radiation infrequently** (every 10–30 model minutes) because it is expensive; interpolate between calls. Be aware this introduces a lag in the diurnal cycle.
- **Match the microphysics scheme to the question.** Single-moment is fine for precipitation totals in a synoptic model; aerosol-cloud interaction needs at least double-moment.
- **Check the saturation adjustment** — how the scheme removes supersaturation. Instant adjustment is standard and is itself an approximation.
- **Cloud fraction must be consistent** between the radiation and microphysics schemes. They are often developed separately.

??? warning "Failure modes"
    **Independent column approximation at fine resolution.** ICA treats each column as an infinite horizontal slab, so no photon crosses column boundaries. At grid spacings below ~1 km, cloud sides and shadows matter and ICA misses both. Symptom: surface shortwave that is too uniform, missing the bright edges and deep shadows real cloud fields produce.

    **Autoconversion threshold tuning.** The cloud-to-rain conversion is the least constrained process in bulk microphysics, and it is routinely tuned to fix precipitation biases. That buries a model-structure error in a microphysical constant — see the calibration warning in [UQ](../foundations/uncertainty-quantification.md).

    **Cloud overlap assumption unexamined.** Maximum overlap and random overlap can differ by 10%+ in total cloud cover for the same profile. Whichever a model uses, the radiation responds strongly to it.

    **Double counting cloud effects.** When convection, microphysics and cloud-fraction schemes all produce condensate, the same cloud can be represented twice unless the coupling is careful. Symptom: excessive cloud radiative effect with reasonable-looking individual schemes.

    **Fixed droplet number in a single-moment scheme.** Effectively fixes the aerosol environment. Any conclusion about aerosol-cloud interaction from such a run is a property of the setting, not the physics.

    **Radiation timestep too long.** A 1-hour radiation call in a model with a strong diurnal cycle produces stepped surface heating and a phase-lagged boundary layer. Visible as staircase artefacts in surface temperature time series.

    <!-- Add your own here. -->

## Worked example

Why the emission-height argument, not "heat trapping", is the right picture:

```python
import numpy as np

S0, sigma, alpha, lapse = 1361.0, 5.670374419e-8, 0.30, 6.5e-3

Te = (S0 * (1 - alpha) / (4 * sigma))**0.25
print(f"effective emission temperature = {Te:.1f} K")

for z_emit in (5000.0, 5200.0):                  # raise the emission level 200 m
    Ts = Te + lapse * z_emit
    print(f"emission height {z_emit:6.0f} m  ->  surface T = {Ts:.2f} K")
print(f"warming from a 200 m rise in emission height = {lapse*200:.2f} K")
```

```
effective emission temperature = 254.6 K
emission height   5000 m  ->  surface T = 287.08 K
emission height   5200 m  ->  surface T = 288.38 K
warming from a 200 m rise in emission height = 1.30 K
```

Raising the effective emission level by 200 m warms the surface by 1.3 K, with no change to the amount of energy absorbed. The greenhouse effect is geometry plus a lapse rate, not a blanket.

## Connections

- [Thermodynamics](thermodynamics.md) — saturation, latent heat, the lapse rate used above.
- [NWP](nwp.md) — where these schemes are coupled together.
- [Astrophysics › Radiative transfer](../astrophysics/radiative-transfer.md) — the same transfer equation, different opacities.
- [Observations](observations.md) — satellite radiances are this equation inverted.

## Sources

- Petty, *A First Course in Atmospheric Radiation*.
- Lamb & Verlinde, *Physics and Chemistry of Clouds*.
- Archive: `METEO 511` material; see the [course archive](../resources/course-archive.md).
