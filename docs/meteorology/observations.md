---
title: Observations and datasets
status: working
tags: [pillar-8, meteorology, radar, satellite, reanalysis, grib]
updated: 2026-09-26
---

# Observations and datasets

<span class="status status-working">working</span>
<span class="pillar">pillar 8 &middot; Data management, statistics and UQ</span>

!!! abstract "In one minute"
    - **Reanalysis is not observation.** ERA5 is a model constrained by observations — excellent, and wrong in specific, documented ways.
    - Radar measures a **beam volume that grows with range and rises above the surface**. Most radar artefacts follow from that geometry.
    - Satellites measure **radiances**, not geophysical variables. Everything else is a retrieval with assumptions baked in.
    - **GRIB2 is lossy by design.** Packing precision is a per-field choice, and it can be coarser than the signal you are looking for.
    - Every dataset has a **representativeness scale**. Comparing a point gauge to a 13 km grid cell is comparing different quantities.

## Key results

**Observation types and what they actually measure:**

<div class="result" markdown>

| Platform | Measures | Representativeness | Main limitation |
|---|---|---|---|
| Surface station | point, 2 m / 10 m | metres | siting, exposure, urban heat |
| Radiosonde | a drifting profile, ~2/day | a slanted curtain | sparse in time and over ocean |
| Radar | backscattered power in a beam volume | 0.5–4 km, range-dependent | geometry, clutter, attenuation |
| Geostationary satellite | radiance, 0.5–2 km, 1–15 min | column or cloud top | retrievals, no vertical resolution |
| Polar orbiter | radiance, higher spatial res | swath | twice-daily revisit |
| Aircraft (AMDAR) | along flight path | point | concentrated near airports and cruise levels |
| Reanalysis | model state | grid cell | **not an observation** |

</div>

**Radar.** Reflectivity factor in dBZ, related to rain rate by an empirical Z–R relation:

\[
Z = a R^{b},\qquad a \approx 200,\ b \approx 1.6 \ \text{(Marshall–Palmer)}
\]

That relation is a fit, varies by precipitation type, and is a leading source of QPE error. Dual polarisation (\(Z_{DR}\), \(K_{DP}\), \(\rho_{HV}\)) constrains drop shape and improves both classification and rainfall estimation substantially.

Beam geometry sets most of the artefacts: the beam widens with range (about 1° beamwidth, so ~1.7 km at 100 km) and rises with Earth curvature plus refraction, roughly

\[
h \approx r\sin\phi + \frac{r^2}{2\cdot(4/3)R_\oplus}
\]

**Satellite channels** (GOES-R ABI as the reference case): visible (0.64 µm) for cloud and albedo; near-IR (1.6, 2.2 µm) for phase and particle size; water vapour (6.2, 6.9, 7.3 µm) for mid/upper tropospheric moisture and flow; window IR (10.3, 11.2 µm) for cloud-top temperature.

**Reanalysis.** ERA5: ~31 km global, hourly, 1940–present, 137 levels. MERRA-2 and JRA-3Q are the main alternatives; regional reanalyses exist for some domains. Key properties to keep in mind:

- It is a **model forecast constrained by observations**, so in data-sparse regions and eras it is mostly model.
- The **observing system changes over time** — satellites arrive in 1979 and again in the 2000s — so trends across those boundaries can be artefacts.
- Different variables have very different reliability: upper-air winds and temperature are well constrained; precipitation and surface fluxes are model products.

**Data formats:**

| Format | Used for | Watch out for |
|---|---|---|
| GRIB2 | operational NWP output | lossy packing; template complexity |
| NetCDF4/HDF5 | research, reanalysis, satellite | chunking affects read speed by orders of magnitude |
| BUFR | observation exchange | tabular, needs decoding tables |
| Zarr | cloud-native array storage | increasingly standard for large datasets |

## Mental model

Every dataset is an instrument plus a processing chain, and both leave fingerprints. The useful habit is to ask, for any field: *what was physically measured, and what was inferred?* For a radiosonde temperature, almost all measured. For satellite-derived precipitation, almost all inferred. For reanalysis precipitation, entirely model.

That question also settles most comparison disputes. A model and an observation disagreeing may simply be reporting different quantities over different volumes.

## Numerics / practice

- **Read the dataset documentation on known issues** before using it. ERA5, HRRR and GOES all publish them, and they are specific and useful.
- **Chunk NetCDF/Zarr to match the access pattern.** A time-series read from space-chunked data can be 100× slower than necessary.
- **Check GRIB2 packing precision** when differencing fields or computing gradients — the quantisation step can exceed the signal.
- **Use `xarray` + `dask`** for anything larger than memory, and `cfgrib`/`pygrib` for GRIB. `MetPy` for unit-aware meteorological calculations.

??? warning "Failure modes"
    **Reanalysis used as ground truth.** Verifying a model against ERA5 partly verifies it against another model — and if they share physics or assimilate the same observations, the agreement is not independent. For precipitation and surface fluxes especially, ERA5 is a model product.

    **Radar bright band.** Melting snow produces a layer of strongly enhanced reflectivity near the freezing level. A radar beam intersecting it reports rain rates several times too high in a characteristic ring around the site. Well known, still routinely forgotten in QPE.

    **Beam overshoot at long range.** At 150 km the beam centre is above 2 km, so shallow precipitation is missed entirely. Apparent precipitation gradients in a radar climatology often trace radar geometry rather than weather.

    **Trends across observing-system changes.** A "trend" in reanalysis that begins in 1979 is very likely the arrival of satellite data. Any long-term analysis must check whether the change coincides with an observing-system transition.

    **Satellite retrieval assumptions ignored.** Cloud-top height from IR brightness temperature assumes an opaque cloud and a known temperature profile; for thin cirrus both fail, and heights are biased low by kilometres.

    **Point-to-grid comparison.** A rain gauge measures ~0.02 m²; a 3 km grid cell is \(9\times10^6\) m². Their variances differ by construction, so RMSE against gauges includes a representativeness component that no model improvement can remove.

    **Station metadata changes.** Instrument swaps, relocations and changes in observation time produce step changes that look meteorological. Homogenisation exists for this, and raw records need it.

    <!-- Add your own here. -->

## Worked example

Radar beam height, and why distant coverage is not coverage:

```python
import numpy as np

Re_eff = (4.0/3.0) * 6371e3            # effective Earth radius for standard refraction
beamwidth = np.deg2rad(0.95)           # WSR-88D

for r_km in (25.0, 60.0, 120.0, 200.0):
    r = r_km * 1e3
    for elev_deg in (0.5,):
        h = r*np.sin(np.deg2rad(elev_deg)) + r**2/(2*Re_eff)
        width = r * beamwidth
        print(f"range {r_km:5.0f} km   beam centre {h:6.0f} m AGL   "
              f"beam width {width/1e3:5.2f} km")
```

```
range    25 km   beam centre    255 m AGL   beam width  0.41 km
range    60 km   beam centre    735 m AGL   beam width  0.99 km
range   120 km   beam centre   1895 m AGL   beam width  1.99 km
range   200 km   beam centre   4100 m AGL   beam width  3.32 km
```

At 200 km the lowest beam is 4 km up and 3.3 km wide — it cannot see shallow precipitation at all, and what it does see is smeared over a volume larger than a convection-permitting grid cell.

## Connections

- [Data assimilation](data-assimilation.md) — how these observations enter a model.
- [NWP](nwp.md) — verification and its pitfalls.
- [Toolchains › Data formats](../toolchains/index.md) — GRIB, NetCDF and their gotchas.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — representativeness as a variance term.

## Sources

- Rinehart, *Radar for Meteorologists*.
- Hersbach et al. (2020), *The ERA5 global reanalysis*.
- ECMWF and NOAA dataset documentation — the known-issues pages are worth reading in full.
