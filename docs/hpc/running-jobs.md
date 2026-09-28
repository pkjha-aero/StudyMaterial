---
title: Running jobs
status: working
tags: [pillar-6, hpc, parallelism, reproducibility]
updated: 2026-09-28
---

# Running jobs

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - **`--ntasks` is MPI ranks, `--cpus-per-task` is threads per rank.** Getting the pair inconsistent with the code oversubscribes the node, and nothing errors.
    - **Bind processes and threads explicitly.** The default is often adequate and occasionally halves your performance.
    - **Load the same modules in the batch script** that you built with. A login-shell environment is not inherited.
    - **Write to scratch, not home.** Home is small, often not on the parallel filesystem, and sometimes not mounted on compute nodes.
    - Profile before optimising, and profile the thing you actually run.

## SLURM, the parts that matter

<div class="result" markdown>

| Directive | Means |
|---|---|
| `--nodes=N` | nodes |
| `--ntasks=N` | total MPI ranks |
| `--ntasks-per-node=N` | ranks on each node |
| `--cpus-per-task=N` | cores per rank — set `OMP_NUM_THREADS` to match |
| `--gpus-per-node=N` | GPUs |
| `--time=HH:MM:SS` | wallclock; the job is killed at it |
| `--mem=` / `--mem-per-cpu=` | memory; exceeding it kills the job |
| `--exclusive` | whole node, no sharing |

</div>

The invariant to hold in your head: **`ntasks × cpus-per-task ≤ cores per node × nodes`**.

## Pure MPI

```bash
#!/bin/bash
#SBATCH --job-name=solver
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --output=%x-%j.out        # jobname-jobid, so runs do not overwrite

module purge
module load gcc/13 openmpi/4.1     # the same modules you built with

srun ./solver input.json           # srun knows the allocation; no -np needed
```

## Hybrid MPI + OpenMP

One rank per NUMA domain, threads inside it, is the usual shape.

```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=2        # 2 ranks per node = 1 per socket
#SBATCH --cpus-per-task=16         # 16 threads each = 32 cores per node
#SBATCH --time=04:00:00

module purge && module load gcc/13 openmpi/4.1

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK    # never hard-code this
export OMP_PROC_BIND=close
export OMP_PLACES=cores

srun --cpu-bind=cores ./solver
```

Deriving `OMP_NUM_THREADS` from `$SLURM_CPUS_PER_TASK` rather than hard-coding it is the
single most useful line in the script: change the allocation and the threading follows.

## GPU job

```bash
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00

module purge && module load cuda/12 openmpi/4.1
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun --gpus-per-task=1 ./gpu_solver
```

## Day-to-day commands

```bash
sbatch job.sh                       # submit
squeue -u $USER                     # queued and running
scontrol show job <id>              # why is it not running
sacct -j <id> --format=JobID,Elapsed,MaxRSS,State    # after the fact
seff <id>                           # efficiency summary — cheap and revealing
scancel <id>
salloc -N1 -t 00:30:00 --pty bash   # interactive node for debugging
```

`seff` is under-used: it reports CPU and memory efficiency for a finished job, and a run at
15% CPU efficiency tells you something is wrong before any profiler does.

## Profiling and debugging

| Tool | For |
|---|---|
| `perf stat` / `perf record` | node-level hotspots, cache and branch counters |
| `nsys` / `ncu` | GPU timeline and per-kernel counters |
| HPCToolkit, Score-P, TAU | sampling profiles across MPI ranks |
| mpiP | lightweight MPI communication summary |
| Intel VTune / Advisor | node performance, roofline |
| `gdb` / `cuda-gdb` | stepping; attach to one rank |
| `valgrind --tool=memcheck` | leaks and invalid access (slow) |
| `-fsanitize=address,undefined` | fast checks at build time |
| MUST / `mpi-checker` | MPI correctness — mismatched calls, leaks |

A practical first pass costs almost nothing:

```bash
perf stat -e cycles,instructions,cache-misses,cache-references ./app
```

A cache-miss rate above a few percent on a supposedly cache-friendly kernel is the signal
to look at data layout rather than arithmetic.

## Mental model

A batch script is a reproducibility artifact as much as a launcher. It records the
allocation shape, the environment, and the exact command — which is precisely what you
need six months later when the result has to be regenerated. Treat it as source, commit
it, and stamp the job ID into the output.

## Practice

- **Test at small scale interactively** with `salloc` before submitting a large job.
- **Name outputs with `%x-%j`** so reruns do not overwrite each other.
- **Record the module list** (`module list 2>&1`) into the output file — see [research craft](../foundations/research-craft.md).
- **Check `seff`** on every long job; the cheapest performance feedback available.

??? warning "Failure modes"
    **`--cpus-per-task` inconsistent with `OMP_NUM_THREADS`.** Asking for 4 cores per rank and spawning 16 threads oversubscribes by 4×. The job runs, slowly, and nothing warns. Always derive one from the other.

    **Modules not loaded in the batch script.** The login shell's environment is not inherited by the job. Symptom: a binary that runs interactively and fails in batch with a missing shared library. `module purge` first, then load explicitly.

    **Writing to home from every rank.** Home is usually small, often on NFS rather than the parallel filesystem, and sometimes read-only on compute nodes. Thousands of ranks opening files there is also a metadata storm — see [computing › data and I/O](../computing/data-io.md).

    **Wallclock too short.** The job is killed mid-write and the checkpoint is corrupt. Request margin, and make checkpoints atomic (write to a temporary name, then rename).

    **No process binding.** Threads migrate across NUMA domains and memory access becomes remote. Silent, and routinely a factor of two.

    **Benchmarking on a shared node.** Without `--exclusive`, another job on the same node perturbs your timings. Scaling studies need exclusive allocation or they measure your neighbours.

    **Timing the first iteration.** First-touch allocation, lazy MPI connection setup and cold caches make iteration one unrepresentative. Discard warm-up and say how many.

    **Job ID not recorded with the results.** Without it, `sacct` cannot tell you later what the run actually used, and the result becomes unreproducible for a reason that had nothing to do with the science.

    <!-- Add your own here — scheduler quirks are extremely site-specific. -->

## Connections

- [MPI](mpi.md) · [OpenMP](openmp.md) · [CUDA](cuda.md) — what the scripts launch.
- [Computing › HPC and parallelism](../computing/hpc.md) — scaling studies and what to report.
- [Computing › Data and I/O](../computing/data-io.md) — parallel I/O and checkpoint cost.
- [Foundations › Research craft](../foundations/research-craft.md) — the batch script as provenance.

## Sources

- SLURM documentation — `sbatch`, `srun` and the cpu-binding pages especially.
- Your site's own user guide; scheduler configuration is highly site-specific.
- Archive: `Aerospace/AERSP590`, `Others/ParallelProgramming`.
