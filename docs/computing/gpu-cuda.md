---
title: GPU and CUDA
status: working
tags: [pillar-6, computing, parallelism, performance]
updated: 2026-09-26
---

# GPU and CUDA

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - A GPU is a **latency-hiding throughput machine**: thousands of threads, and the scheduler covers memory latency by switching between them.
    - **Coalesced access is the single biggest performance factor.** Consecutive threads must read consecutive addresses, or you pay a transaction per thread.
    - Threads execute in **warps of 32 in lockstep**; a branch that diverges within a warp serialises both paths.
    - **Occupancy is a means, not an end.** High occupancy helps hide latency; past a point more registers per thread is worth less occupancy.
    - **PCIe transfer often dominates.** A kernel that is 50× faster is worthless if the data movement costs more than the original computation.

## Key results

**Execution model:**

<div class="result" markdown>

| Level | Unit | Notes |
|---|---|---|
| Thread | one lane | has private registers |
| Warp | 32 threads | lockstep, the real scheduling unit |
| Block | up to 1024 threads | shares shared memory, can synchronise |
| Grid | all blocks | no inter-block synchronisation within a kernel |

</div>

**Memory hierarchy**, fastest to slowest:

| Memory | Scope | Latency | Notes |
|---|---|---|---|
| Registers | thread | ~1 cycle | limited per thread; spilling is expensive |
| Shared | block | ~20 cycles | programmer-managed cache; watch bank conflicts |
| L2 | device | ~200 cycles | |
| Global | device | ~400–800 cycles | the thing to coalesce |
| Host (over PCIe) | system | microseconds | the thing to avoid |

**Coalescing.** A warp's 32 global-memory accesses are serviced in as few 32-byte transactions as possible. Consecutive threads reading consecutive `float`s → 4 transactions. Strided by 32 → 32 transactions, **8× the traffic for the same data**. This is why array-of-structures layouts perform badly on GPUs and structure-of-arrays is the standard fix.

**Warp divergence.** `if (threadIdx.x % 2)` splits a warp; both branches execute with half the lanes masked, so the cost is the sum. Divergence *between* warps is free — only within one is it a problem.

**Occupancy** = active warps / maximum warps per SM, limited by registers per thread, shared memory per block, and block size. 50–75% is usually plenty; chasing 100% by cutting registers often makes things slower because of spilling.

**Arithmetic intensity, again.** GPUs have higher peak FLOPs *and* higher bandwidth than CPUs, but the ratio is similar — so the [roofline](hpc.md) argument transfers directly. A memory-bound kernel on a GPU is still memory-bound.

**Streams and overlap.** Copy-compute overlap using multiple streams and pinned host memory is what makes PCIe cost tolerable: transfer chunk \(n+1\) while computing on chunk \(n\).

**When not to write CUDA.** cuBLAS, cuFFT, cuSPARSE, Thrust, and library-backed frameworks (CuPy, PyTorch, JAX) are faster than hand-written kernels for anything standard. Write CUDA for a fused custom kernel that no library provides.

## Mental model

A CPU minimises latency for one thread; a GPU maximises throughput across many. When a GPU thread stalls on memory, the scheduler swaps in another warp — so latency is hidden rather than reduced, provided there is enough parallelism to swap to. That is the whole design, and it explains why GPUs need huge problems to be efficient and why occupancy matters at all.

The corollary is that the GPU's advantage is bandwidth, not cleverness. Roughly an order of magnitude more memory bandwidth than a CPU socket, and that is most of the speedup on memory-bound scientific code.

## Numerics / practice

- **Profile with Nsight Compute / Nsight Systems**, not by timing. The metrics that matter are achieved occupancy, memory throughput as a fraction of peak, and the coalescing efficiency.
- **Use structure-of-arrays**, always, for GPU-resident data.
- **Keep data resident.** The right pattern is transfer once, run many kernels, transfer back.
- **Use pinned memory** for transfers; pageable memory forces an extra staging copy.

??? warning "Failure modes"
    **Uncoalesced access.** The dominant GPU performance bug. A kernel achieving 5% of peak bandwidth is almost always reading strided or via an AoS layout. Symptom: profiler shows huge global memory transaction counts relative to data actually needed.

    **PCIe transfer dominating.** Copying an array to the device, running one cheap kernel, copying it back. The kernel is fast; the round trip is slower than the CPU version. Diagnose by timing the copies separately — they are frequently 90% of the wall time and are invisible in kernel-only benchmarks.

    **Warp divergence inside a hot loop.** A branch on thread index or on data serialises the warp. Often fixable by sorting or partitioning the work so branches align with warp boundaries.

    **Chasing occupancy.** Reducing registers per thread to increase occupancy causes register spilling to local memory, which is global memory latency. Net slower, with a better occupancy number.

    **Shared memory bank conflicts.** Shared memory has 32 banks; threads hitting the same bank with different addresses serialise. Classic case is a 2D tile with stride 32 — padding the row by one element fixes it.

    **Assuming inter-block synchronisation.** There is none within a kernel launch. Code that relies on block A finishing before block B works by accident on small grids and fails on large ones — a genuinely nasty heisenbug.

    **Silent numerical differences.** GPU reductions sum in nondeterministic order, and fused multiply-add changes rounding. Bitwise agreement with a CPU run is not achievable; decide what tolerance means before comparing — see [research craft](../foundations/research-craft.md).

    **Benchmarking without synchronisation.** CUDA kernel launches are asynchronous. Timing without `cudaDeviceSynchronize()` measures the launch, not the kernel, and reports an absurd speedup.

    <!-- Add your own here. -->

## Worked example

Whether a GPU offload can pay for itself, before writing the kernel:

```python
bw_pcie, bw_gpu, bw_cpu = 25e9, 2000e9, 200e9      # bytes/s

for name, bytes_moved, arith_intensity in (
        ("tiny vector add",   8e6,   0.08),
        ("large stencil",     8e9,   0.50),
        ("dense matmul",      8e8,  50.00)):
    t_cpu = bytes_moved / bw_cpu
    t_gpu_kernel = bytes_moved / bw_gpu
    t_transfer = 2 * bytes_moved / bw_pcie          # over and back
    print(f"{name:18s} CPU={t_cpu*1e3:8.2f} ms   "
          f"GPU kernel={t_gpu_kernel*1e3:7.2f} ms   "
          f"+transfer={(t_gpu_kernel+t_transfer)*1e3:8.2f} ms   "
          f"net {'WIN' if t_gpu_kernel+t_transfer < t_cpu else 'LOSS'}")
```

```
tiny vector add    CPU=    0.04 ms   GPU kernel=   0.00 ms   +transfer=    0.64 ms   net LOSS
large stencil      CPU=   40.00 ms   GPU kernel=   4.00 ms   +transfer=  644.00 ms   net LOSS
dense matmul       CPU=    4.00 ms   GPU kernel=   0.40 ms   +transfer=   64.40 ms   net LOSS
```

Every single case loses **once the round-trip transfer is counted**. That is the real lesson: a one-shot offload almost never pays. GPUs win by keeping data resident across many kernels, so the transfer is amortised — the large stencil run 1,000 times costs 4 s of kernel plus one 0.64 s transfer, against 40 s on CPU.

## Connections

- [HPC and parallelism](hpc.md) — the roofline and scaling arguments.
- **[HPC › CUDA](../hpc/cuda.md)** — kernels, error checking, tiling and streams, with compile and profile commands.
- [Python performance](python-performance.md) — CuPy, JAX, and GPU without CUDA.
- [DL › PyTorch patterns](../dl/pytorch-patterns.md) — where most GPU time is actually spent.

## Sources

- NVIDIA *CUDA C++ Programming Guide* and *Best Practices Guide*.
- Kirk & Hwu, *Programming Massively Parallel Processors*.
