---
title: Weather and climate models
status: seed
tags: [pillar-7, toolchains, wrf, mpas, erf, rrtm]
updated: 2026-09-26
---

# Weather and climate models

<span class="status status-seed">seed</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! note "Cheatsheet page"
    Gotchas, not tutorials. Write the entry the day you fight the tool.

## WRF

**Workflow:** `WPS` (geogrid → ungrib → metgrid) → `real.exe` → `wrf.exe`.

```bash
./geogrid.exe          # static fields onto your domain
./link_grib.csh /path/to/GRIB/
./ungrib.exe           # decode driving data
./metgrid.exe          # horizontally interpolate onto the domain
./real.exe             # vertical interpolation, IC/BC
mpirun -np 256 ./wrf.exe
```

**`namelist.wps` and `namelist.input` must agree** on domain dimensions, nest ratios,
projection and start/end times. Most WRF failures are a mismatch between the two, and the
error messages point at the symptom rather than the inconsistency.

**Settings that decide the answer:**

| Setting | Note |
|---|---|
| `dx`, `dy` | below ~4 km, turn the cumulus scheme **off** (`cu_physics = 0`) |
| `time_step` | ~6× `dx` in km as a starting point; reduce if unstable |
| `e_vert` | more levels near the surface for boundary-layer work |
| `parent_grid_ratio` | 3 or 5; even ratios are discouraged |
| `num_metgrid_levels` | must match what ungrib produced |
| `bl_pbl_physics` / `sf_sfclay_physics` | must be a compatible pair |

The PBL/surface-layer pairing is a real constraint — not all combinations are valid, and
an invalid one may run and produce nonsense rather than stopping.

## MPAS

Unstructured centroidal Voronoi mesh, global with a smoothly variable-resolution region —
which avoids the abrupt nest boundaries that WRF has. Mesh files are downloaded or
generated, not defined in a namelist. Output is on an unstructured grid, so standard
lat/lon tooling needs a conversion step (`convert_mpas`).

## ERF

Energy Research and Forecasting — an [AMReX](cfd-codes.md)-based atmospheric model,
GPU-first, with WRF-like physics. Relevant here as the modern rewrite of that lineage on
block-structured AMR.

## Radiation

**RRTMG** is the standard broadband scheme in WRF and many others: correlated-\(k\),
separate longwave and shortwave. **libRadtran** is the reference line-by-line/DISORT
toolkit — far more accurate, far too slow for inline use, and the right thing to validate
against.

## Post-processing

```bash
cdo sinfo wrfout_d01_*            # structure
ncl_filedump wrfout_d01_*         # WRF-aware dump
```

```python
import wrf, netCDF4
nc = netCDF4.Dataset("wrfout_d01_2026-09-26_00:00:00")
slp = wrf.getvar(nc, "slp")               # diagnostics computed correctly
lats, lons = wrf.latlon_coords(slp)
```

Use `wrf-python` rather than reading raw variables: WRF stores perturbation fields, and
several diagnostics require adding a base state that is easy to forget.

??? warning "Failure modes"
    **Cumulus scheme left on in the grey zone.** At 3–4 km with `cu_physics` active, the scheme and the resolved dynamics both produce convection. Too much light rain, suppressed storms. See [NWP](../meteorology/nwp.md).

    **Raw WRF fields read without the base state.** Geopotential is `PH + PHB`, pressure is `P + PB`, potential temperature is `T + 300`. Reading `T` alone gives a field 300 K too cold, which is obvious; reading `P` alone gives a small perturbation that looks plausible.

    **Namelist mismatch between WPS and WRF.** Domain sizes, `num_metgrid_levels`, or time range disagreeing. `real.exe` may succeed and `wrf.exe` fail much later with an unrelated message.

    **Timestep too large for the grid.** CFL violation appears as `cfl` warnings then a segfault, often after hours. The 6×`dx`(km) rule is a start, not a guarantee — steep terrain needs less.

    **Spin-up included in verification.** The first few hours reflect the initialisation, not the model.

    **Nest boundary too close to the feature of interest.** Lateral boundary errors propagate inward; keep the region of interest well inside.

    **Terrain smoothing insufficient for steep topography.** Produces the pressure-gradient error described in [NWP](../meteorology/nwp.md) — spurious circulations locked to the terrain.

    <!-- Add your own here. -->

## Connections

- [Meteorology › NWP](../meteorology/nwp.md) — the physics being configured.
- [Data formats](data-formats.md) — GRIB input, NetCDF output.
- [Geospatial](geospatial.md) · [Visualization](visualization.md)
