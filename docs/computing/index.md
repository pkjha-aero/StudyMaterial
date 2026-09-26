---
title: Computing
status: working
tags: [pillar-5, pillar-6, pillar-8, computing, hpc]
---

# Computing

<span class="status status-working">working</span>
<span class="pillar">pillars 5, 6, 8</span>

Making code run, run fast, and run on someone else's machine.

## Pages

| Page | Pillar | Covers |
|---|---|---|
| [HPC and parallelism](hpc.md) | 6 | Amdahl and Gustafson, roofline, MPI patterns, surface-to-volume, SLURM |
| [GPU and CUDA](gpu-cuda.md) | 6 | Execution model, memory hierarchy, coalescing, divergence, transfer cost |
| [Data and I/O at scale](data-io.md) | 8 | Parallel I/O, chunking, compression, checkpointing, data versioning |
| [Python performance](python-performance.md) | 5 | Vectorisation, temporaries, Numba, JAX, the GIL, profiling |
| [C++ and Fortran](cpp-fortran.md) | 5 | Memory order, aliasing, interop, build systems |
| [MLOps and deployment](mlops.md) | 5 | Containers, Apptainer on HPC, Kubernetes, CI/CD, serving |

## The theme

**Every page here is about data movement.** The roofline says most scientific kernels are
memory-bound. Coalescing is data movement within a GPU. Chunking is data movement from
disk. Loop order is data movement through cache. NumPy temporaries are extra passes over
memory. Halo exchange is data movement between nodes.

Compute has been cheap for a long time; moving bytes has not. When a code is slower than
expected, the productive first question is almost never "how many operations?" — it is
**"how many bytes, and how far?"**

## A second theme: measure

Each page repeats the same instruction in its own vocabulary — profile before optimising,
time I/O separately, check arithmetic intensity, look at p99 rather than the mean, use
`py-spy` on the running process. Intuition about performance is unreliable in a way that
intuition about correctness is not, because the hardware behaviour that dominates is
invisible in the source.

## Connections

- [Foundations › Linear solvers](../foundations/linear-solvers.md) — usually the runtime.
- [Toolchains](../toolchains/index.md) — the codes this runs.
- [DL › PyTorch patterns](../dl/pytorch-patterns.md) — the ML-side equivalent.
