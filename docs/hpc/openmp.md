---
title: OpenMP
status: working
tags: [pillar-6, hpc, parallelism, performance]
updated: 2026-09-28
---

# OpenMP

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - **Shared memory, fork-join.** Directives turn serial loops parallel without restructuring the program — which is the appeal and the trap.
    - **`reduction` and `private` are the two clauses that matter.** Most races are a variable that should have been one and was left shared.
    - **False sharing is the silent killer**: correct results, and parallel code slower than serial. Measured at 5.6× below.
    - **Schedule choice is a load-balance decision.** `static` for uniform work, `dynamic` or `guided` when iterations cost differently.
    - **Pin your threads.** Unpinned threads migrate across NUMA domains and lose a factor of two for free.

## The directives worth knowing

<div class="result" markdown>

| Directive / clause | Does |
|---|---|
| `#pragma omp parallel` | fork a team of threads |
| `#pragma omp for` | distribute loop iterations across the team |
| `#pragma omp parallel for` | both at once, the common case |
| `reduction(+:x)` | private copy per thread, combined at the end |
| `private(x)` / `firstprivate(x)` | uninitialised / initialised copy per thread |
| `schedule(static|dynamic|guided[,chunk])` | how iterations are handed out |
| `collapse(2)` | fuse nested loops into one iteration space |
| `nowait` | skip the implicit barrier at the end of a `for` |
| `critical` / `atomic` | serialise a region / a single update |
| `simd` | request vectorisation |
| `task` / `taskwait` | irregular and recursive parallelism |

</div>

**Environment:**

```bash
export OMP_NUM_THREADS=8
export OMP_PROC_BIND=close      # or spread
export OMP_PLACES=cores         # threads, cores, sockets
export OMP_DISPLAY_ENV=true     # print the resolved settings at startup
```

`OMP_DISPLAY_ENV` is worth setting once on any new machine — it tells you what the runtime
actually decided, which is often not what you assumed.

## A reduction, correctly

```c
#include <omp.h>
#include <stdio.h>

int main(void) {
    const long N = 100000000L;
    double sum = 0.0;

    #pragma omp parallel for reduction(+:sum)
    for (long i = 0; i < N; i++)
        sum += 1.0 / ((double)i + 1.0);

    printf("threads=%d  sum=%.10f\n", omp_get_max_threads(), sum);
    return 0;
}
```

```bash
gcc -O2 -fopenmp reduce.c -o reduce
for t in 1 4 8; do OMP_NUM_THREADS=$t ./reduce; done
```

Complete source: [`reduce.c`](code/reduce.c).

```
threads=1  sum=18.9978964139
threads=4  sum=18.9978964138
threads=8  sum=18.9978964139
```

Look at the last digit. A floating-point reduction is **not bit-reproducible** across
thread counts, because the summation order changes — and here four threads differs from
one and eight in the tenth decimal place. That is expected behaviour, not a bug, and it is
why bitwise comparison against a serial run is the wrong test. Compare against a tolerance.
See [research craft](../foundations/research-craft.md).

## False sharing, measured

Each thread updates its own small histogram. In the first version the per-thread
histograms sit adjacent in memory, so neighbouring threads write to the **same cache
lines** and the hardware ping-pongs them between cores. The results are correct either way.

```c
#define NBIN 8                      /* 8 longs = 64 B = exactly one cache line */

/* (a) adjacent per-thread histograms — false sharing */
long *packed = calloc((size_t)T * NBIN, sizeof *packed);
#pragma omp parallel
{
    long *mine = packed + (long)omp_get_thread_num() * NBIN;
    #pragma omp for
    for (long i = 0; i < N; i++) mine[idx[i]]++;
}

/* (b) padded so each thread owns its own cache lines */
const int PAD = 64 / sizeof(long);
long *padded = calloc((size_t)T * (NBIN + PAD), sizeof *padded);
#pragma omp parallel
{
    long *mine = padded + (long)omp_get_thread_num() * (NBIN + PAD);
    #pragma omp for
    for (long i = 0; i < N; i++) mine[idx[i]]++;
}
```

Complete source: [`hist.c`](code/hist.c) — the fragments above are excerpts from it.

```bash
gcc -O2 -fopenmp hist.c -o hist
for t in 1 2 4 8; do OMP_NUM_THREADS=$t ./hist; done
```

```
threads=1  false-shared  0.063 s   padded  0.062 s   speedup 1.01x
threads=2  false-shared  0.137 s   padded  0.037 s   speedup 3.68x
threads=4  false-shared  0.117 s   padded  0.021 s   speedup 5.58x
threads=8  false-shared  0.099 s   padded  0.044 s   speedup 2.23x
```

Three things in that table:

1. **At one thread there is no difference** (1.01×). False sharing is a cache-coherence
   effect between cores, so a single-threaded test cannot detect it — which is exactly why
   it survives development.
2. **Going from 1 to 2 threads makes the false-shared version slower** — 0.063 s to
   0.137 s. Adding a core more than doubled the runtime. That signature, negative scaling
   at low thread counts, is close to diagnostic.
3. **Padding recovers real scaling**: 0.062 → 0.021 s from 1 to 4 threads.

Run-to-run magnitude varies on a shared laptop — repeated runs gave **4.1× to 6.7×** at
four threads — but the direction and the negative-scaling signature are stable across every
run. Quote a range and the repetition count, not a single number.

## Mental model

OpenMP hides the threads but not the memory. The directives make it easy to forget that
every core has its own cache and that the coherence protocol is what keeps them agreeing.
False sharing is the bill for forgetting.

That is also the practical rule: think about **which thread touches which cache line**,
not which thread runs which iteration. Two threads writing different variables in the same
64-byte line are, as far as the hardware is concerned, fighting over one variable.

## Practice

- **Prefer `reduction` to a hand-rolled per-thread array.** It is faster, correct, and immune to the padding problem by construction.
- **Pad or privatise** any per-thread accumulator you do write by hand.
- **`schedule(static)`** when iterations cost the same; **`dynamic,chunk`** when they do not — but a too-small chunk adds scheduling overhead.
- **First-touch matters on NUMA.** Memory is placed on the node whose thread first writes it, so initialise arrays with the *same* parallel loop pattern you will use to compute.

??? warning "Failure modes"
    **False sharing.** Correct answers, and parallel slower than serial. Nothing in the language warns you. Diagnostic: scaling that is flat or negative at 2–4 threads, with per-thread writes to adjacent memory.

    **A shared variable that should be private.** A loop-local temporary declared outside the parallel region is shared by default in C. Symptom: results that change run to run. Declare inside the region, or list it `private`.

    **`reduction` omitted on an accumulator.** A data race, and often the answer is only slightly wrong — which is worse than badly wrong, because it passes a smoke test.

    **Assuming thread count.** `omp_get_max_threads()` is what *could* run; `omp_get_num_threads()` inside the region is what *is* running, and outside a parallel region it returns 1. Code that sizes arrays from the wrong one overflows.

    **Threads unpinned.** Without `OMP_PROC_BIND`, the OS migrates threads between NUMA domains and memory access becomes remote. Silent, and routinely a factor of two.

    **First touch in a serial loop.** Initialising an array serially places all of it on one NUMA node; the parallel compute loop then reaches across the interconnect for most of it. Initialise in parallel, with the same access pattern.

    **Nested parallelism by accident.** A parallel region calling a library that is itself threaded oversubscribes badly. Set `OMP_NESTED=false` or the library's own thread count explicitly.

    **Bitwise comparison across thread counts.** Reduction order changes, so results differ in the last bits. Compare against a tolerance, not exactly.

    <!-- Add your own here. -->

## Connections

- [MPI](mpi.md) — the distributed half; one rank per NUMA domain with threads inside is the usual hybrid.
- [Running jobs](running-jobs.md) — binding, `--cpus-per-task`, and profiling.
- [Computing › HPC and parallelism](../computing/hpc.md) — roofline, and why most of this is memory-bound.
- [Computing › C++ and Fortran](../computing/cpp-fortran.md) — memory order, which decides whether threading helps at all.

## Sources

- Chapman, Jost & van der Pas, *Using OpenMP*.
- The OpenMP specification and the examples document.
- Archive: `Others/ParallelProgramming`, `Aerospace/AERSP590`.
