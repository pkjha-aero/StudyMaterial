---
title: HPC and parallelism
status: working
tags: [pillar-6, computing, parallelism, performance, scaling]
updated: 2026-09-26
---

# HPC and parallelism

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - **Amdahl bounds strong scaling**; Gustafson describes weak scaling. Which one applies depends on whether your problem size grows with the machine.
    - **The roofline tells you what to optimise**: memory-bound code needs better access patterns, compute-bound code needs better instructions. Most scientific code is memory-bound.
    - **Communication is the scaling limit**, and surface-to-volume ratio is why: halo exchange grows as \(N^{2/3}\) while work grows as \(N\).
    - **Overlap communication with computation** — non-blocking sends, interior-first ordering. This is the single biggest structural win available.
    - Measure before optimising. The bottleneck is almost never where intuition puts it.

## Key results

**Scaling laws.** With serial fraction \(s\) and \(p\) processors:

<div class="result" markdown>

\[
\text{Amdahl (fixed problem):}\quad S(p) = \frac{1}{s + (1-s)/p} \xrightarrow{p\to\infty} \frac{1}{s}
\]

\[
\text{Gustafson (scaled problem):}\quad S(p) = s + p(1-s)
\]

</div>

Amdahl is brutal: 1% serial work caps speedup at 100×, no matter the machine. The escape is Gustafson's observation that people usually *grow the problem* with the machine, so the serial fraction shrinks in relative terms.

| Metric | Definition | Good |
|---|---|---|
| Strong scaling | fixed total problem, more ranks | \(>70\%\) efficiency at target rank count |
| Weak scaling | fixed problem *per rank* | near-flat time as ranks grow |
| Parallel efficiency | \(T_1/(p\,T_p)\) | report it, not just speedup |

**Roofline model:**

\[
P = \min\left(P_{\text{peak}},\ I \times B\right),
\qquad
I = \frac{\text{FLOPs}}{\text{bytes moved}}
\]

The ridge point \(I^* = P_{\text{peak}}/B\) separates the regimes. On a modern node \(P_{\text{peak}}/B\) is roughly 10–50 FLOP/byte, while a stencil update is around 0.5 — **an order of magnitude or more below the ridge, so almost all scientific kernels are memory-bound.** Vectorising a memory-bound loop buys nothing; improving locality buys everything.

**Communication scaling.** For a 3D domain of \(N\) cells decomposed over \(p\) ranks:

\[
\frac{\text{communication}}{\text{computation}} \sim \frac{(N/p)^{2/3}}{N/p} = \left(\frac{p}{N}\right)^{1/3}
\]

Halo exchange scales with surface, work with volume. Strong scaling eventually fails because the subdomains get small enough that surface dominates.

**MPI essentials:**

| Pattern | Use |
|---|---|
| `MPI_Isend`/`Irecv` + `Waitall` | halo exchange, overlappable |
| `MPI_Allreduce` | global sums, norms — a synchronisation point |
| `MPI_Barrier` | almost never needed in production; usually a symptom |
| Derived datatypes | strided halo faces without manual packing |
| Neighbourhood collectives | cleaner Cartesian halo exchange |

**MPI + OpenMP hybrid.** One rank per NUMA domain, threads within it. Reduces rank count (so fewer, larger messages) and shares memory for read-only data. Requires care: pin threads, and check the MPI thread-support level actually granted by `MPI_Init_thread`.

**Schedulers.** SLURM is the common case: `sbatch` a script, `srun` inside it, `squeue`/`sacct` to inspect. The distinctions that matter are `--ntasks` (MPI ranks) versus `--cpus-per-task` (threads per rank) versus `--nodes`, and getting them inconsistent is the most common cause of a job that runs at a fraction of expected speed.

## Mental model

Parallel performance is a bookkeeping problem about **where data is** and **who needs it**. Compute is cheap; moving data is not, at every level — register to cache, cache to DRAM, node to node. The roofline and the surface-to-volume argument are the same statement at two different scales.

That framing settles most optimisation questions. Before rewriting a kernel, ask how many bytes it must move; if that number cannot go down, neither can the runtime.

## Numerics / practice

- **Profile first.** `perf`, Intel VTune, HPCToolkit, or even coarse MPI timers. Optimising by intuition wastes more time than profiling costs.
- **Report parallel efficiency with a baseline rank count**, and state whether the study is strong or weak scaling. "Scales to 10,000 cores" without efficiency is not a claim.
- **Overlap**: post non-blocking receives, compute the interior, then wait and compute boundaries.
- **Pin processes and threads** (`--cpu-bind`, `OMP_PROC_BIND=close`, `OMP_PLACES=cores`). Unpinned threads migrating between NUMA domains can cost 2× silently.

??? warning "Failure modes"
    **Scaling claimed without efficiency.** A run that is 200× faster on 1,000 cores is 20% efficient — usually a bad result presented as a good one. Always divide.

    **Load imbalance hidden behind a collective.** Every rank waits at `MPI_Allreduce`, so the time appears *in the reduction* rather than in the slow rank. Symptom: a profile showing most time in a collective that does almost no work. Diagnose by timing the barrier immediately before it.

    **Strong scaling past the surface-to-volume limit.** Beyond a point, subdomains are so small that halo exchange dominates and adding ranks makes the run slower. There is an optimum rank count for a given problem size, and it is worth finding rather than assuming more is better.

    **Unpinned threads.** Without affinity, the OS migrates threads across NUMA domains and memory access becomes remote. Silent, and routinely a factor of two.

    **`--ntasks` and `--cpus-per-task` inconsistent with the code.** Asking SLURM for 64 tasks and then spawning 8 OpenMP threads each on a 64-core node oversubscribes by 8×. The job runs, slowly, and nothing errors.

    **Optimising FLOPs on a memory-bound kernel.** Vectorising, unrolling, or reducing arithmetic in code that is waiting on DRAM changes nothing. Compute the arithmetic intensity first; if it is below the ridge point, work on data movement.

    **Benchmarking the first iteration.** First-touch page allocation, cache warm-up and lazy MPI connection setup make iteration one unrepresentative. Discard warm-up iterations and say how many.

    <!-- Add your own here. -->

## Worked example

Amdahl's ceiling, which is why "parallelise the hot loop" has a limit:

```python
for s in (0.10, 0.01, 0.001):
    print(f"serial fraction {s:6.3f}  ->  max speedup {1/s:8.1f}x")
    for p in (16, 128, 1024, 8192):
        S = 1.0 / (s + (1 - s) / p)
        print(f"     p={p:6d}   speedup={S:8.1f}x   efficiency={100*S/p:5.1f}%")
```

```
serial fraction  0.100  ->  max speedup     10.0x
     p=    16   speedup=     6.4x   efficiency= 40.0%
     p=   128   speedup=     9.3x   efficiency=  7.3%
     p=  1024   speedup=     9.9x   efficiency=  1.0%
     p=  8192   speedup=    10.0x   efficiency=  0.1%
serial fraction  0.010  ->  max speedup    100.0x
     p=    16   speedup=    13.9x   efficiency= 87.0%
     p=   128   speedup=    56.4x   efficiency= 44.1%
     p=  1024   speedup=    91.2x   efficiency=  8.9%
     p=  8192   speedup=    98.8x   efficiency=  1.2%
serial fraction  0.001  ->  max speedup   1000.0x
     p=    16   speedup=    15.8x   efficiency= 98.5%
     p=   128   speedup=   113.6x   efficiency= 88.7%
     p=  1024   speedup=   506.2x   efficiency= 49.4%
     p=  8192   speedup=   891.3x   efficiency= 10.9%
```

At 1% serial, efficiency is already below 50% at 128 ranks. Getting to thousands of ranks usefully requires the serial fraction below 0.1% — which is a statement about I/O, setup and global reductions, not about the main loop.

## Connections

- [GPU and CUDA](gpu-cuda.md) — the same memory-bandwidth argument, sharper.
- [Data and I/O](data-io.md) — often the real serial fraction.
- [C++ and Fortran](cpp-fortran.md) — where the kernels live.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — what usually dominates the runtime.

## Sources

- Williams, Waterman & Patterson (2009), *Roofline: an insightful visual performance model*.
- Hager & Wellein, *Introduction to High Performance Computing for Scientists and Engineers*.
- Archive: `Others/ParallelProgramming`.
