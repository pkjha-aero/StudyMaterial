---
title: Meteorology
status: working
tags: [pillar-1, pillar-8, meteorology]
---

# Meteorology

<span class="status status-working">working</span>
<span class="pillar">pillars 1, 8</span>

Atmospheric physics, the models that forecast it, and the observations that constrain them.
An **active growth area** — these pages are marked `working` rather than `solid` because
they will keep expanding, not because they are incomplete as recaps.

## Pages

| Page | Covers |
|---|---|
| [Atmospheric thermodynamics](thermodynamics.md) | \(\theta\) and \(\theta_e\), moisture variables, Clausius-Clapeyron, CAPE and CIN |
| [Atmospheric dynamics](dynamics.md) | Rossby number, geostrophy, thermal wind, PV, QG omega, Rossby waves |
| [Atmospheric boundary layer](boundary-layer.md) | Monin-Obukhov similarity, log profile, diurnal cycle, low-level jet |
| [Radiation and clouds](radiation-clouds.md) | Two-stream transfer, emission height, cloud radiative effect, microphysics |
| [Numerical weather prediction](nwp.md) | Dynamical cores, physics suites, the convective grey zone, ensembles |
| [Data assimilation](data-assimilation.md) | 3D/4D-Var, EnKF, localization and inflation, observation error |
| [Observations and datasets](observations.md) | Radar geometry, satellite radiances, reanalysis caveats, GRIB and NetCDF |
| [Fire weather](fire-weather.md) | Fuel moisture, Rothermel, plume-dominated vs wind-driven, coupled modelling |

## Reading order

**[Thermodynamics](thermodynamics.md)** and **[dynamics](dynamics.md)** are the physics;
**[boundary layer](boundary-layer.md)** and **[radiation and clouds](radiation-clouds.md)**
are the processes models must parameterize; **[NWP](nwp.md)** assembles them;
**[data assimilation](data-assimilation.md)** and **[observations](observations.md)** supply
and constrain the state. **[Fire weather](fire-weather.md)** is the applied end.

## A theme worth naming

Meteorology is unusual among the sections here in that **the observation is often the
least certain element**. In fluids or structures you compare a model to a measurement and
suspect the model. Here:

- **Reanalysis is a model**, so verifying against it is partly model-to-model comparison.
- **Radar and satellite measure proxies** — backscattered power, radiance — and everything
  geophysical is a retrieval.
- **Representativeness error usually dominates** instrument error, so a point observation
  and a grid cell are not the same quantity even when both are perfect.

That inverts the usual V&V posture and it shapes how [data assimilation](data-assimilation.md)
is set up: the observation error covariance is doing at least as much work as the model.

## Connections

- [Fluids](../fluids/index.md) — the atmosphere is a rotating, stratified fluid.
- [Foundations › UQ](../foundations/uncertainty-quantification.md) — ensembles and uncertainty.
- [CV › Scientific imagery](../cv/scientific-imagery.md) — satellite observation.
- [Toolchains › Weather models](../toolchains/weather-models.md) — running WRF and MPAS.

## Sources

Per page. See the [course archive](../resources/course-archive.md) — the METEO course
folders are indexed there.
