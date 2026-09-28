---
title: HPC
status: working
tags: [pillar-6, hpc, parallelism, performance]
---

# HPC

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

Hands-on parallel programming: the three models, working code, and how to run it.

## Pages

| Page | Covers |
|---|---|
| [MPI](mpi.md) | Distributed memory, halo exchange with overlap, collectives, deadlock modes |
| [OpenMP](openmp.md) | Shared memory, reductions, false sharing measured, scheduling and affinity |
| [CUDA](cuda.md) | Kernels, error checking, coalescing, shared-memory tiling, streams |
| [Running jobs](running-jobs.md) | SLURM scripts for pure MPI, hybrid and GPU; profiling and debugging tools |

## How this differs from Computing

[Computing › HPC and parallelism](../computing/hpc.md) and
[GPU and CUDA](../computing/gpu-cuda.md) are the **reasoning** pages: Amdahl and Gustafson,
the roofline, arithmetic intensity, the surface-to-volume argument, why a GPU offload does
or does not pay. They answer *should this be faster, and what is stopping it*.

These pages are the **doing**: the code, the compile line, the run command, the batch
script. They answer *how do I write and launch it*.

Read the Computing pages to decide what to optimise; read these to implement it.

## Choosing a model

| You have | Reach for |
|---|---|
| One node, shared memory, a loop to parallelise | [OpenMP](openmp.md) |
| More memory or cores than one node has | [MPI](mpi.md) |
| A large node and a memory-bandwidth-bound kernel | [CUDA](cuda.md) |
| Many nodes, each with several sockets | MPI + OpenMP hybrid |
| Many nodes with GPUs | MPI + CUDA, one rank per GPU |
| A standard operation | a library — cuBLAS, FFTW, PETSc, Trilinos |

That last row is the one most often skipped. A tuned library beats hand-written parallel
code for anything standard, and the time saved is better spent on the part no library
covers.

## A note on what is measured here

The MPI and OpenMP pages quote **timings from real runs** on an 8-core machine — including
a false-sharing case where going from one thread to two makes the code *slower*, which is
more convincing than any description of the effect.

The CUDA page quotes **nothing measured**, because this machine has no GPU, and says so at
the top. That asymmetry is deliberate: a page that presents plausible invented numbers as
results is worse than one that admits it cannot run the code.

## The code is downloadable

The fragments on these pages come from complete programs, kept beside them so they can
actually be run rather than retyped:

| File | Page |
|---|---|
| [`hello.c`](code/hello.c) | [MPI](mpi.md) — rank, size, reduction |
| [`overlap.c`](code/overlap.c) | [MPI](mpi.md) — blocking vs overlapped halo exchange |
| [`reduce.c`](code/reduce.c) | [OpenMP](openmp.md) — reduction and bit-reproducibility |
| [`hist.c`](code/hist.c) | [OpenMP](openmp.md) — false sharing |
| [`Makefile`](code/Makefile) | builds and runs all of them |

```bash
cd docs/hpc/code && make run
```

## Connections

- [Computing](../computing/index.md) — performance reasoning, memory hierarchy, profiling philosophy.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — what usually dominates the runtime.
- [Fluids › CFD](../fluids/cfd/index.md) — the halo exchange in its native habitat.
- [Toolchains](../toolchains/index.md) — the codes that run on all this.
