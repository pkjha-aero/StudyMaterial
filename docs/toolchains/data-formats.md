---
title: Data formats
status: working
tags: [pillar-7, toolchains, data-formats]
updated: 2026-09-26
---

# Data formats

<span class="status status-working">working</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! abstract "In one minute"
    - **NetCDF4 is HDF5 underneath**, with a self-describing convention layered on top.
    - **GRIB2 is lossy by design** — packing precision is a per-field choice and can be coarser than your signal.
    - **Chunking decides read performance**, permanently, at write time.
    - **Zarr is the cloud-native answer**: chunks as separate objects, no file locking, parallel writes.
    - Always check the **fill value and scale/offset** before doing arithmetic.

## Quick reference

| Format | Underlying | Strength | Watch |
|---|---|---|---|
| NetCDF4 | HDF5 | self-describing, CF conventions | chunking, unlimited-dimension cost |
| NetCDF3 | flat | simple, portable | 2 GB limits, no compression |
| HDF5 | — | general hierarchical arrays | complexity, file locking on parallel FS |
| GRIB2 | — | compact operational NWP | lossy packing, template complexity |
| Zarr | object store | cloud, parallel write | many small objects if chunked badly |
| BUFR | — | observation exchange | needs decode tables |

## Commands worth remembering

```bash
ncdump -h file.nc                    # header only — always start here
ncdump -v time file.nc | head        # inspect one variable
ncinfo file.nc                       # netCDF4-python's summary

cdo sinfo file.nc                    # structure summary
cdo griddes file.nc                  # grid description
nccopy -d5 -c time/100,lat/50,lon/50 in.nc out.nc   # rechunk + deflate

grib_ls file.grib2                   # list messages
grib_dump -O file.grib2 | head -50   # full key dump for one message
wgrib2 file.grib2 -s                 # concise inventory

h5ls -r file.h5                      # hierarchy
h5dump -H file.h5                    # header
```

## Python

```python
import xarray as xr

ds = xr.open_dataset("f.nc")                      # single file
ds = xr.open_mfdataset("f*.nc", combine="by_coords",
                       chunks={"time": 100})      # lazy, dask-backed
ds = xr.open_dataset("f.grib2", engine="cfgrib",
                     backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface"}})
```

`filter_by_keys` is usually necessary for GRIB: a file with multiple level types cannot be
opened as one dataset, and the error message does not say so clearly.

**`mask_and_scale`** is on by default in xarray — it applies `scale_factor`/`add_offset`
and converts `_FillValue` to NaN, promoting integers to float. Turn it off when you need
the raw packed values, and know that it is happening.

## Chunking

Chunks of roughly 1–16 MB, shaped for the dominant read. See
[computing › data and I/O](../computing/data-io.md) for the full argument — the summary is
that a single-point time series from map-chunked data can read the entire file.

```python
import rechunker   # or ds.chunk({...}).to_zarr(...) for smaller cases
```

??? warning "Failure modes"
    **GRIB packing precision below the signal.** GRIB2 stores values with a specified number of bits. A temperature field packed to 0.1 K resolution makes a 0.02 K gradient pure quantisation noise. Check `numberOfBits` / the decimal scale before differencing fields.

    **Fill values entering statistics.** `_FillValue` of \(-9999\), \(0\), or \(65535\) looks like data to a mean. Always mask explicitly; do not assume the array is clean because it loaded without error.

    **Scale/offset applied twice, or not at all.** Reading with one library that auto-applies and writing with another that also applies gives silently wrong magnitudes. Check whether your reader has already unpacked.

    **Unlimited dimension performance.** A NetCDF unlimited dimension forces a chunk layout that is often terrible for reading, and appending along it can be very slow. Use a fixed dimension unless you genuinely need to append.

    **HDF5 file locking on a parallel filesystem.** HDF5's locking can hang or fail on Lustre/GPFS. `HDF5_USE_FILE_LOCKING=FALSE` is the usual workaround, with the understanding that you are now responsible for not writing concurrently.

    **Zarr with too many tiny chunks.** Every chunk is an object; a million 10 KB chunks means a million requests. Latency, not bandwidth, becomes the limit.

    **CF conventions assumed rather than checked.** Time units, calendars (`360_day`, `noleap`), and coordinate names vary. A `units = "hours since 1900-01-01"` with a non-standard calendar silently misdates everything.

    <!-- Add your own here — the ones that cost you a day. -->

## Connections

- [Computing › Data and I/O](../computing/data-io.md) — chunking, parallel I/O, compression.
- [Geospatial](geospatial.md) — CRS and raster handling on top of these.
- [Meteorology › Observations](../meteorology/observations.md) — where these files come from.

## Sources

- Unidata NetCDF documentation; HDF Group HDF5 docs; ECMWF ecCodes (GRIB) documentation.
- Zarr specification; CF Conventions document.
