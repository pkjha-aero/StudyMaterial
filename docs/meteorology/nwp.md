---
title: Numerical weather prediction
status: working
tags: [pillar-1, pillar-7, meteorology, discretization, uncertainty]
updated: 2026-09-26
---

# Numerical weather prediction

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - An NWP model is a **dynamical core plus a physics suite**. The core is well-posed numerics; the physics is where the modelling judgement — and most of the error — lives.
    - **Predictability is finite.** Deterministic skill runs out around 10–14 days regardless of model quality, which is why ensembles exist.
    - The **convective grey zone** (roughly 1–10 km) is genuinely awkward: too fine for convective parameterization, too coarse to resolve convection.
    - **Terrain-following coordinates** degrade over steep topography — a recurring problem in exactly the complex terrain people most want to forecast.
    - Model output is a **realisation, not a truth**. Post-processing and calibration are part of the forecast, not an afterthought.

## Key results

**Anatomy of a model:**

<div class="result" markdown>

| Component | What it does | Typical choices |
|---|---|---|
| Dynamical core | solves the resolved-scale equations | hydrostatic vs non-hydrostatic; grid; time scheme |
| Microphysics | cloud and precipitation | single/double moment |
| Radiation | SW and LW transfer | RRTMG |
| Boundary layer | vertical mixing | YSU, MYJ, MYNN |
| Surface layer | fluxes | MOST-based |
| Land surface | soil, vegetation | Noah-MP |
| Cumulus | subgrid convection | Kain–Fritsch, Grell — off below ~4 km |

</div>

**Resolution regimes:**

| \(\Delta x\) | Convection | Approach |
|---|---|---|
| \(> 10\) km | fully parameterized | global models |
| 1–10 km | **grey zone** | scale-aware schemes, or neither option is right |
| 0.1–1 km | convection-permitting | no cumulus scheme; updrafts marginally resolved |
| \(< 100\) m | LES regime | boundary-layer scheme must also be replaced |

"Convection-permitting" is a carefully chosen word: at 3 km, storms form and organise realistically, but individual updrafts are 2–3 grid points across and are not converged.

**Operational systems**, as a rough orientation:

| Model | \(\Delta x\) | Domain | Notes |
|---|---|---|---|
| ECMWF IFS | ~9 km | global | spectral, generally the skill benchmark |
| GFS | ~13 km | global | FV3 core |
| HRRR | 3 km | CONUS | hourly, convection-permitting, radar assimilation |
| WRF | configurable | limited area | research workhorse |
| MPAS | variable-resolution | global | unstructured, avoids nesting |

**Predictability.** Error growth is exponential at small scales and saturates:

\[
\frac{dE}{dt} = \alpha E\left(1 - \frac{E}{E_\infty}\right)
\]

Doubling time is roughly 1.5–2 days at synoptic scales and hours at convective scales — so a convection-permitting forecast of individual storm placement has skill for hours, not days, however good the model.

**Ensembles** sample initial-condition uncertainty (perturbed analyses) and model uncertainty (stochastic physics, multi-physics, multi-model). The ensemble mean beats any member on average; the spread is the useful product, and a well-calibrated ensemble has spread matching RMSE.

## Mental model

A forecast model is a coupled system in which the dynamics are largely settled and the physics is where competing approximations meet. The dynamical core can be verified against analytic solutions — it is a [V&V](../foundations/verification-validation.md) problem with right answers. The physics cannot: every scheme is a different defensible approximation, and switching one changes the forecast in ways that are hard to attribute.

That asymmetry explains a great deal about how the field works — why physics suites are named and tracked, why ensembles perturb physics as well as initial conditions, and why model intercomparison is a discipline of its own.

## Numerics / practice

- **Spin-up matters.** A cold-started limited-area run needs hours before its boundary layer and clouds are consistent with its own physics. Verification during spin-up measures the initialisation.
- **Nest ratios of 3:1 or 5:1**, and keep the parent domain large enough that the lateral boundary is far from the region of interest.
- **Do not mix a cumulus scheme with a 2 km grid.** Either resolve convection or parameterize it; doing both double-counts.
- **Verify against the right thing.** Point verification of a convection-permitting forecast penalises realistic storms in slightly the wrong place — neighbourhood and object-based methods (FSS, MODE) are the appropriate tools.

??? warning "Failure modes"
    **Running a cumulus scheme in the grey zone.** At 3–4 km with Kain–Fritsch active, the scheme and the resolved dynamics both produce convection. Symptom: too much light precipitation, suppressed organised storms, and a damped diurnal cycle. Conversely, switching cumulus off at 8 km leaves convection entirely unrepresented.

    **Terrain-following coordinate errors over steep slopes.** Horizontal pressure-gradient terms become the small difference of two large terms on sloping coordinate surfaces. Symptom: spurious circulations and temperature errors locked to topography that do not disappear with refinement. Hybrid or step-terrain coordinates mitigate it.

    **Verifying during spin-up.** The first 3–6 hours of a cold-start run reflect the initialisation, not the model. Including them makes physics look worse (or better) than it is.

    **Lateral boundary contamination.** Errors propagate inward from the boundary at the advective speed. A small domain at high resolution can be boundary-dominated within a few hours — the nest is then reproducing its parent, not adding value.

    **Ensemble spread mistaken for uncertainty.** Under-dispersive ensembles are the norm: spread is often smaller than RMSE, so the ensemble is overconfident. Check the spread-skill relationship before using percentiles as probabilities.

    **Point verification of convection-permitting output.** A forecast storm 20 km from the observed one scores worse than a smooth forecast with no storm at all — the "double penalty". It rewards blurry forecasts, which is exactly the wrong incentive.

    **Physics timestep coupling.** Schemes are usually called sequentially and each sees the state left by the last. The ordering is a modelling choice with real consequences, and it differs between models.

    <!-- Add your own here. -->

## Worked example

Why convective-scale forecasts have skill for hours, not days:

```python
import numpy as np

E0, E_inf = 0.01, 1.0                 # initial error, saturation

for scale, doubling_h in (("synoptic (1000 km)", 40.0),
                          ("mesoscale (100 km)",  8.0),
                          ("convective (10 km)",  2.0)):
    alpha = np.log(2) / doubling_h
    # logistic growth solved for time to reach 50% of saturation
    t50 = np.log((0.5*E_inf/E0) * (E_inf - E0)/(E_inf - 0.5*E_inf)) / alpha
    print(f"{scale:22s} doubling={doubling_h:4.0f} h   "
          f"time to 50% saturation = {t50:6.1f} h ({t50/24:.1f} days)")
```

```
synoptic (1000 km)     doubling=  40 h   time to 50% saturation =  265.2 h (11.0 days)
mesoscale (100 km)     doubling=   8 h   time to 50% saturation =   53.0 h (2.2 days)
convective (10 km)     doubling=   2 h   time to 50% saturation =   13.3 h (0.6 days)
```

Roughly the observed limits: about ten days for synoptic patterns, half a day for individual storms. No improvement in model or observations moves the convective number much — it is set by the dynamics.

## Connections

- [Dynamics](dynamics.md) — what the dynamical core solves.
- [Radiation and clouds](radiation-clouds.md) · [Boundary layer](boundary-layer.md) — the physics suite.
- [Data assimilation](data-assimilation.md) — where initial conditions come from.
- [Toolchains › Weather models](../toolchains/index.md) — running WRF, MPAS and friends.

## Sources

- Kalnay, *Atmospheric Modeling, Data Assimilation and Predictability*.
- Warner, *Numerical Weather and Climate Prediction*.
- Archive: see the [course archive](../resources/course-archive.md).
