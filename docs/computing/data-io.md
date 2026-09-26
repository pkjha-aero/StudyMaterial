---
title: Data and I/O at scale
status: working
tags: [pillar-8, computing, parallel-io, hdf5, netcdf, dvc]
updated: 2026-09-26
---

# Data and I/O at scale

<span class="status status-working">working</span>
<span class="pillar">pillar 8 &middot; Data management, statistics and UQ</span>

!!! abstract "In one minute"
    - **I/O is frequently the real serial fraction** in a parallel code, and the one nobody profiles.
    - **Chunking must match the access pattern.** A time-series read from space-chunked data can be orders of magnitude slower than necessary.
    - One file per rank does not scale — metadata operations on a parallel filesystem are the bottleneck, not bandwidth.
    - **Compression can make I/O faster**, because it trades cheap CPU for expensive bandwidth.
    - Reproducibility needs the *data* versioned too, not just the code.

## Key results

**Parallel I/O strategies:**

<div class="result" markdown>

| Strategy | Scales to | Problem |
|---|---|---|
| One file per rank | ~1,000 ranks | metadata storm; unusable output layout |
| All ranks → one file (MPI-IO / HDF5 / PnetCDF) | 100,000+ | needs alignment and collective calls |
| Aggregator ranks → few files | very high | extra communication step |
| Object/cloud store (Zarr, S3) | effectively unlimited | latency, eventual consistency |

</div>

**Chunking.** A chunked array is stored in fixed-size blocks; any read pulls whole chunks. For an array `(time, lat, lon)`:

- Chunked `(1, all, all)` — fast to read one map, terrible for a time series at one point.
- Chunked `(all, small, small)` — fast for a time series, slow for a map.

A single-point time series from map-chunked data reads every chunk in the file. **This is the most common and most expensive I/O mistake in geoscience workflows**, and it looks like "the data is just big" rather than a layout problem.

Rule of thumb: chunks of 1–16 MB, shaped to the dominant access pattern; rechunk (with `rechunker`, or Dask) if you have two dominant patterns.

**Collective vs independent I/O.** Collective calls let the library aggregate small scattered writes into large contiguous ones. On a parallel filesystem this is routinely an order of magnitude faster than independent writes, and it requires all ranks to participate — which is why an early `return` on some ranks deadlocks.

**Alignment.** Lustre stripes files across OSTs; writes aligned to the stripe size avoid multiple OSTs contending for the same block. `lfs setstripe` on the output directory before the run is a one-line change with a large effect on big writes.

**Compression.** With modern codecs (Blosc, Zstd) at 2–5× ratio, the CPU cost is far below the time saved moving bytes. Lossy options for float data (bit-rounding, ZFP) reach much higher ratios — acceptable when you know the precision the science needs, and a trap when you do not.

**Data versioning.** Code in git; data in DVC, or content-addressed with recorded hashes. A result is reproducible only if the *input* can be recovered, and "the file on the shared drive" is not a version.

## Mental model

Treat the storage system as another level of the memory hierarchy — the slowest one, with the same rules. Locality matters, bulk transfers beat scattered small ones, and the layout you choose at write time determines what reads are cheap forever afterwards.

That is why chunking decisions deserve the same care as data-structure decisions in memory. You are choosing the access pattern for every future consumer of the file, usually without knowing who they are.

## Numerics / practice

- **Time your I/O separately** from compute, and report it. Many "compute-bound" codes are not.
- **Write collectively**, one shared file, with alignment set for the filesystem.
- **Chunk for the read**, not the write, when the data will be read many times.
- **Record a hash and provenance** with every output — see [research craft](../foundations/research-craft.md).

??? warning "Failure modes"
    **Chunking mismatched to access.** Reading a 50-year time series at one grid point from map-chunked data can take hours instead of seconds, because every chunk in the file is touched. Diagnose by comparing bytes read against bytes needed — a ratio of 1000:1 is not unusual.

    **One file per rank at scale.** 10,000 ranks creating 10,000 files hits the metadata server, not the bandwidth limit. The job appears to hang at startup or at the first checkpoint. It also leaves output nobody can analyse without a merge step.

    **Independent I/O where collective was available.** Each rank writes its own small non-contiguous piece; the filesystem sees a storm of small writes. Often 10× slower than the collective equivalent for the same bytes.

    **A rank skipping a collective call.** An early `return` or a conditional that is false on some ranks deadlocks the whole job, usually without a useful error. Collective means *all* ranks.

    **Checkpointing too often.** Checkpoint cost is I/O bandwidth divided into total state. The optimum interval balances rewrite cost against expected failure rate (Young/Daly formula); defaults are often far too frequent, and checkpointing can quietly become the dominant cost.

    **Lossy compression without an error budget.** Bit-rounding a field to 8 significant bits is fine for visualisation and destroys a gradient computation. Decide the tolerance against the *downstream use*, and record what was applied.

    **No-data and fill values not handled.** Discussed in [meteorology › observations](../meteorology/observations.md), and it is an I/O problem as much as a science one — the fill value is a property of the file format and the writer, and it silently enters every statistic.

    **Data not versioned.** The code is reproducible, the input file has been overwritten. Content-address the inputs.

    <!-- Add your own here. -->

## Worked example

Why chunk shape decides the cost of a read:

```python
nt, ny, nx = 10_000, 720, 1440
itemsize = 4
total_gb = nt * ny * nx * itemsize / 2**30
print(f"array: {nt} x {ny} x {nx} float32 = {total_gb:.1f} GB\n")

for name, chunk in (("map-chunked  (1, 720, 1440)", (1, ny, nx)),
                    ("time-chunked (10000, 24, 48)", (nt, 24, 48)),
                    ("balanced     (500, 90, 180)",  (500, 90, 180))):
    ct, cy, cx = chunk
    chunk_mb = ct * cy * cx * itemsize / 2**20
    # read a full time series at ONE grid point
    n_chunks = (nt / ct)
    bytes_read = n_chunks * ct * cy * cx * itemsize
    bytes_needed = nt * itemsize
    print(f"{name:30s} chunk={chunk_mb:7.1f} MB  "
          f"read={bytes_read/2**30:8.2f} GB  amplification={bytes_read/bytes_needed:10.0f}x")
```

```
array: 10000 x 720 x 1440 float32 = 38.6 GB

map-chunked  (1, 720, 1440)    chunk=    4.0 MB  read=   38.62 GB  amplification=   1036800x
time-chunked (10000, 24, 48)   chunk=   43.9 MB  read=    0.04 GB  amplification=      1152x
balanced     (500, 90, 180)    chunk=   30.9 MB  read=    0.60 GB  amplification=     16200x
```

The same single-point time series costs 38.6 GB of reads from map-chunked storage and 0.04 GB from time-chunked — a thousandfold difference, from a layout decision made once at write time. Neither layout is wrong; the mismatch is.

## Connections

- [HPC and parallelism](hpc.md) — I/O as the hidden serial fraction.
- [Toolchains › Data formats](../toolchains/data-formats.md) — NetCDF, GRIB, HDF5 specifics.
- [Meteorology › Observations](../meteorology/observations.md) — where these files come from.
- [Foundations › Research craft](../foundations/research-craft.md) — provenance and reproducibility.

## Sources

- Unidata NetCDF and HDF Group documentation on chunking and compression.
- Daly (2006), *A higher order estimate of the optimum checkpoint interval*.
