---
title: MPI
status: working
tags: [pillar-6, hpc, parallelism, performance]
updated: 2026-09-28
---

# MPI

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - **Distributed memory, explicit messages.** Nothing is shared; every byte another rank needs, you send.
    - **Post receives before sends.** It costs nothing and removes a whole class of deadlock and unexpected-message buffering.
    - **Non-blocking plus overlap is the single structural win** — measured at 1.1–1.4× below, on one node where messages are already cheap.
    - **Collectives are synchronisation points.** Load imbalance shows up as time spent *inside* `MPI_Allreduce`, not in the slow rank.
    - Every rank must call every collective. A conditional that is false on one rank hangs the job with no error.

## Core API

<div class="result" markdown>

| Call | Use |
|---|---|
| `MPI_Init` / `MPI_Finalize` | bracket everything |
| `MPI_Comm_rank` / `MPI_Comm_size` | who am I, how many of us |
| `MPI_Send` / `MPI_Recv` | blocking point-to-point |
| `MPI_Sendrecv` | paired exchange, deadlock-free |
| `MPI_Isend` / `MPI_Irecv` + `MPI_Waitall` | non-blocking — the one to reach for |
| `MPI_Bcast` / `MPI_Reduce` / `MPI_Allreduce` | collectives |
| `MPI_Scatter` / `MPI_Gather` / `MPI_Alltoall` | data redistribution |
| `MPI_Barrier` | almost never needed; usually a symptom |
| `MPI_Type_create_subarray` | strided halo faces without manual packing |
| `MPI_Cart_create` | Cartesian topology, gives you neighbour ranks |

</div>

## Hello, rank and a reduction

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size, len;
    char host[MPI_MAX_PROCESSOR_NAME];
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Get_processor_name(host, &len);

    double local = rank + 1.0, total;
    MPI_Reduce(&local, &total, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    printf("rank %d of %d on %s\n", rank, size, host);
    if (rank == 0) printf("sum over ranks = %.0f\n", total);
    MPI_Finalize();
    return 0;
}
```

```bash
mpicc -O2 hello.c -o hello
mpirun -np 4 ./hello          # add --oversubscribe to exceed physical cores
```

Complete source: [`hello.c`](code/hello.c).

```
rank 0 of 4 on <host>
rank 1 of 4 on <host>
rank 2 of 4 on <host>
rank 3 of 4 on <host>
sum over ranks = 10
```

Output order across ranks is **not** deterministic — stdout from four processes interleaves
however the runtime flushes it. Sort before comparing, or write per-rank files.

## The halo exchange, done two ways

This is the pattern most structured-grid codes live or die by. Both versions are correct;
only the second overlaps communication with computation.

```c
/* blocking: communicate, then compute */
MPI_Sendrecv(&u[HALO], HALO, MPI_DOUBLE, left,  0,
             &u[HALO+NINT], HALO, MPI_DOUBLE, right, 0,
             MPI_COMM_WORLD, MPI_STATUS_IGNORE);
MPI_Sendrecv(&u[NINT], HALO, MPI_DOUBLE, right, 1,
             &u[0],    HALO, MPI_DOUBLE, left,  1,
             MPI_COMM_WORLD, MPI_STATUS_IGNORE);
work(u, HALO, HALO + NINT);
```

```c
/* overlapped: post, compute the interior, wait, compute the edges */
MPI_Request req[4];
MPI_Irecv(&u[0],         HALO, MPI_DOUBLE, left,  1, MPI_COMM_WORLD, &req[0]);
MPI_Irecv(&u[HALO+NINT], HALO, MPI_DOUBLE, right, 0, MPI_COMM_WORLD, &req[1]);
MPI_Isend(&u[HALO],      HALO, MPI_DOUBLE, left,  0, MPI_COMM_WORLD, &req[2]);
MPI_Isend(&u[NINT],      HALO, MPI_DOUBLE, right, 1, MPI_COMM_WORLD, &req[3]);

work(u, 2*HALO, NINT);                    /* interior needs no halo */
MPI_Waitall(4, req, MPI_STATUSES_IGNORE);
work(u, HALO, 2*HALO);                    /* now the edges */
work(u, NINT, HALO + NINT);
```

Note the ordering in the non-blocking version: **receives are posted before sends**, and the
send/recv tags are crossed so each rank's left-send matches its neighbour's right-receive.

## Running it

Complete source: [`overlap.c`](code/overlap.c) — the fragments above are excerpts from it.

```bash
mpicc -O2 overlap.c -o overlap
mpirun --oversubscribe -np 4 ./overlap
```

Measured on an 8-core laptop, so message latency is shared-memory and already small — on
a real interconnect the gap is wider. **Five repetitions per rank count**, because a single
run of this is not a measurement:

```
ranks=2   1.05x  1.18x  1.08x  1.22x  1.10x
ranks=4   1.28x  1.39x  0.59x  1.62x  1.44x
ranks=8   1.22x  1.48x  1.26x  1.43x  2.08x
```

Overlap won in **14 of 15 runs**, typically by 1.1–1.5×. The one reading below 1.0 is
noise — at 4+ ranks on 8 cores the ranks contend, and `MPI_Waitall` busy-waits by default,
so an unlucky scheduling decision can cost more than the overlap saves.

Reporting this as a single row of a table, which is what I first did, would have been
tidier and would have hidden both the spread and the outlier. The spread *is* the result
on a shared machine: quote a range and the number of repetitions, or do not quote a
timing. See [research craft](../foundations/research-craft.md).

## Mental model

Think in terms of who owns which data and what each rank must be told. A parallel
decomposition is a partition of ownership; the messages are the seams. Everything else —
topologies, derived types, neighbourhood collectives — is convenience over that.

The overlap idea follows directly: the interior of a subdomain depends only on data the
rank already owns, so it can be computed while the seams are in flight. The only reason
not to is that it complicates the loop bounds.

## Practice

- **Post receives first**, then sends, then compute, then wait.
- **Use `MPI_Sendrecv`** for simple paired exchanges rather than hand-ordering send/recv.
- **Derived datatypes** for non-contiguous faces; manual pack/unpack buffers are a common source of subtle bugs.
- **Time with `MPI_Wtime` and reduce with `MPI_MAX`** — the slowest rank is the one that matters.

??? warning "Failure modes"
    **Deadlock from symmetric blocking sends.** Every rank calls `MPI_Send` to its neighbour, then `MPI_Recv`. For small messages this works, because the runtime buffers eagerly; above the eager threshold it hangs. So the bug appears only when the problem gets big — the worst possible time. `MPI_Sendrecv` or non-blocking avoids it entirely.

    **A collective not called by every rank.** An early `return`, or a collective inside `if (rank == 0)`. The job hangs with no error message, usually blamed on the interconnect. Every rank in the communicator must participate.

    **Buffer reused before `MPI_Wait`.** After `MPI_Isend` the buffer belongs to MPI until the request completes. Modifying it early gives silently corrupted data that depends on timing — the hardest class of bug to reproduce.

    **Load imbalance hiding inside a collective.** Every rank waits at `MPI_Allreduce`, so a profile shows time in the reduction rather than in the slow rank. Time a `MPI_Barrier` immediately before it to separate wait from work.

    **`MPI_Barrier` sprinkled to "fix" things.** It almost always hides a real ordering bug and costs synchronisation. If a barrier fixes it, find out why.

    **Tag or communicator mismatch.** Sends and receives that never pair up. With wildcards (`MPI_ANY_SOURCE`, `MPI_ANY_TAG`) this becomes a race rather than a hang, which is worse.

    **Assuming rank 0 is special for I/O.** Funnelling all output through rank 0 serialises the job at scale — see [running jobs](running-jobs.md) for parallel I/O.

    <!-- Add your own here. -->

## Connections

- [OpenMP](openmp.md) — the shared-memory half of a hybrid code.
- [Running jobs](running-jobs.md) — schedulers, binding, profiling.
- [Computing › HPC and parallelism](../computing/hpc.md) — Amdahl, roofline, and the surface-to-volume argument behind decomposition.
- [Fluids › CFD](../fluids/cfd/index.md) — the halo exchange in its native habitat.

## Sources

- Gropp, Lusk & Skjellum, *Using MPI*.
- The MPI Standard — genuinely readable as a reference.
- Archive: `Others/ParallelProgramming`, `Aerospace/AERSP590`, `Aerospace/AOE5984`.
