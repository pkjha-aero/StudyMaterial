---
title: Tags
status: working
---

# Tags

<span class="status status-working">working</span>

The navigation tree can only put a topic in one place, but topics do not respect it.
Tags are the second way in — and to be useful they have to be a **small controlled
vocabulary**, not free-form keywords.

!!! info "Why controlled"
    An earlier version of this site had 205 tags, 177 of which appeared on exactly one
    page. A tag used once cross-links nothing, which is the entire purpose. The
    vocabulary below is 36 tags, every one on at least two pages and most on four or
    more.

    Specific terms — `openfoam`, `betz`, `skew-t` — are deliberately *not* tags. Press
    <kbd>/</kbd> and search for those; search is better at specifics than tags ever are.

## The vocabulary

### Pillar

`pillar-1` … `pillar-10`, from the [Skills Map](skills-map.md). The primary competency
comes first and matches the badge under the page title; a second appears only where a
page genuinely spans two.

### Section

Mirrors the navigation, for filtering within an area:

`aerospace` · `astrophysics` · `computer-vision` · `computing` · `deep-learning` ·
`fluids` · `foundations` · `machine-learning` · `meteorology` · `resources` · `sciml` ·
`thermal` · `toolchains`

### Cross-cutting concept

The tags that earn their place — each one connects pages the navigation tree separates:

| Tag | Connects |
|---|---|
| `boundary-layer` | aerodynamics, wind turbines, RANS wall treatment, the atmospheric surface layer, fire weather |
| `conservation` | governing equations, finite volume, MHD, N-body |
| `data-formats` | parallel I/O, satellite products, NetCDF/GRIB, geospatial rasters |
| `discretization` | numerical methods, finite volume, time integration, NWP cores, N-body |
| `extrapolation` | the shared weakness of trees, forecasts, surrogates, PINNs and neural operators |
| `inverse-problems` | adjoints, data assimilation, PINNs |
| `mesh` | grid quality, meshing tools, graph networks on unstructured grids |
| `neural-networks` | architectures through to scientific ML and vision |
| `numerical-stability` | von Neumann analysis, CFL, MHD positivity, learned-closure blow-up |
| `optimization` | adjoint design optimization, model training |
| `parallelism` | MPI, GPUs, distributed training |
| `performance` | roofline, memory traffic, profiling — the whole computing section |
| `radiation` | atmospheric and astrophysical transfer, the same equation twice |
| `remote-sensing` | scientific imagery, satellite observation, geospatial tooling |
| `reproducibility` | provenance, containers, data versioning, figures |
| `scaling` | nondimensional groups, Amdahl, disk loading, Kolmogorov, Rossby |
| `spectral-methods` | Fourier analysis, from image sampling to FNO to POD |
| `statistics` | estimation, UQ, ML evaluation, data assimilation |
| `surrogates` | reduced-order models and emulators |
| `turbulence` | closures, the boundary layer, learned subgrid models |
| `uncertainty` | UQ, ensembles, observation error |
| `validation` | V&V, grid convergence, ML evaluation, detection metrics |
| `wildfire` | fire weather and fire detection from orbit |

## Browse

<!-- material/tags -->

## Adding a tag

Don't, unless it will land on **three or more pages across at least two sections** — and
then add it to the list above and to the `CONCEPT` set in
[`scripts/audit_pages.py`](https://github.com/pkjha-aero/StudyMaterial/blob/main/scripts/audit_pages.py),
which rejects tags outside the vocabulary. The gate is deliberate: the previous taxonomy
decayed because adding a tag was free.
