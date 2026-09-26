---
title: Toolchains
status: working
tags: [pillar-7, toolchains]
---

# Toolchains

<span class="status status-working">working</span>
<span class="pillar">pillar 7</span>

The codes you are expected to arrive already knowing, rather than to learn on the job.
These pages are **cheatsheets and gotcha-lists, not tutorials** — the commands worth
remembering and the failures worth recognising.

## Pages

| Page | Covers |
|---|---|
| [CFD codes](cfd-codes.md) | OpenFOAM case structure and schemes, FLUENT batch, AMReX |
| [Weather and climate models](weather-models.md) | WRF/WPS workflow and namelists, MPAS, ERF, RRTMG |
| [Astrophysics codes](astro-codes.md) | FLASH, Athena++, Gadget, ZEUS-MP, analysis with yt |
| [Meshing tools](meshing.md) | Gmsh size fields, snappyHexMesh stages, quality targets |
| [Visualization tools](visualization.md) | ParaView client-server and batch, colormaps, filters |
| [Geospatial tools](geospatial.md) | GDAL, rioxarray, GeoPandas, CRS traps |
| [Data formats](data-formats.md) | NetCDF, GRIB, HDF5, Zarr — packing, chunking, fill values |

## The working rule

**Write the page the day you fight the tool**, while the workaround is still in your shell
history. A gotcha recorded six months later is a vague memory; one recorded the same
afternoon is a precise instruction.

Most pages here are marked `seed` deliberately. They carry the baseline that applies to
everyone — the entries that will make them valuable are the ones only you can write, and
each failure-modes block ends with an invitation to add them.

## What these pages are for

This is the least intellectually deep section on the site and one of the most practically
expensive to lack. Not knowing that `snappyHexMesh` silently inserts fewer prism layers
than requested, or that WRF stores perturbation pressure, or that `gdalwarp` defaults to
nearest-neighbour while rioxarray does not, costs hours — and none of it is in a textbook,
because it is not knowledge about the world, it is knowledge about a program.

That is exactly the kind of thing a personal reference should hold.

## Connections

- [Fluids › CFD](../fluids/cfd/index.md) · [Meteorology › NWP](../meteorology/nwp.md) · [Astrophysics](../astrophysics/index.md) — the physics being configured.
- [Computing](../computing/index.md) — running these at scale.
- [Course archive](../resources/course-archive.md) — the offline material.
