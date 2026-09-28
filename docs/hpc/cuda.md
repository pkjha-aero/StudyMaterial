---
title: CUDA
status: working
tags: [pillar-6, hpc, parallelism, performance]
updated: 2026-09-28
---

# CUDA

<span class="status status-working">working</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! warning "The code on this page was not executed"
    Unlike the [MPI](mpi.md) and [OpenMP](openmp.md) pages, whose timings come from real
    runs, there is no CUDA toolkit or GPU on the machine this site is built from. The code
    below is written to compile and is standard, but **no output on this page is
    measured** — where numbers appear they are labelled as expectations, not results.

    Treat it as a starting point to run yourself, not as verified output. That distinction
    is the whole reason the other pages quote timings and this one does not.

!!! abstract "In one minute"
    - **A kernel is a function run by thousands of threads**, indexed by their position in a grid of blocks.
    - **Always check the launch and the API calls.** CUDA fails asynchronously and silently by default; an unchecked kernel launch that failed just produces wrong answers.
    - **Coalescing first.** Consecutive threads must read consecutive addresses; this dominates every other optimisation.
    - **Synchronise before timing.** Launches are asynchronous, so timing without `cudaDeviceSynchronize` measures the launch, not the work.
    - Reach for **cuBLAS, cuFFT, Thrust or CuPy** before writing a kernel. Hand-written kernels are for fusion no library offers.

## Anatomy of a kernel

<div class="result" markdown>

```cuda
__global__ void saxpy(int n, float a, const float *x, float *y) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;   // global thread index
    if (i < n) y[i] = a * x[i] + y[i];               // guard: n is rarely a multiple
}
```

Launched as `saxpy<<<blocks, threads>>>(...)`, with `blocks = (n + threads - 1) / threads`.
The guard matters: the last block almost always has idle threads.

</div>

## A complete, checked program

The error checking is not optional decoration — it is the difference between a bug you
find in seconds and one you chase for a day.

```cuda
#include <cstdio>

#define CUDA_CHECK(call)                                                      \
    do {                                                                      \
        cudaError_t err__ = (call);                                           \
        if (err__ != cudaSuccess) {                                           \
            fprintf(stderr, "%s:%d %s\n", __FILE__, __LINE__,                 \
                    cudaGetErrorString(err__));                               \
            exit(1);                                                          \
        }                                                                     \
    } while (0)

__global__ void saxpy(int n, float a, const float *x, float *y) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = a * x[i] + y[i];
}

int main(void) {
    const int n = 1 << 24;
    size_t bytes = n * sizeof(float);

    float *hx = (float *)malloc(bytes), *hy = (float *)malloc(bytes);
    for (int i = 0; i < n; i++) { hx[i] = 1.0f; hy[i] = 2.0f; }

    float *dx, *dy;
    CUDA_CHECK(cudaMalloc(&dx, bytes));
    CUDA_CHECK(cudaMalloc(&dy, bytes));
    CUDA_CHECK(cudaMemcpy(dx, hx, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(dy, hy, bytes, cudaMemcpyHostToDevice));

    int threads = 256, blocks = (n + threads - 1) / threads;

    cudaEvent_t t0, t1;
    CUDA_CHECK(cudaEventCreate(&t0)); CUDA_CHECK(cudaEventCreate(&t1));
    CUDA_CHECK(cudaEventRecord(t0));
    saxpy<<<blocks, threads>>>(n, 2.0f, dx, dy);
    CUDA_CHECK(cudaGetLastError());          // catches a bad launch configuration
    CUDA_CHECK(cudaEventRecord(t1));
    CUDA_CHECK(cudaEventSynchronize(t1));    // the synchronisation timing needs

    float ms; CUDA_CHECK(cudaEventElapsedTime(&ms, t0, t1));
    CUDA_CHECK(cudaMemcpy(hy, dy, bytes, cudaMemcpyDeviceToHost));

    printf("n=%d  kernel %.3f ms  effective BW %.1f GB/s  y[0]=%.1f\n",
           n, ms, 3.0 * bytes / (ms * 1e6), hy[0]);

    cudaFree(dx); cudaFree(dy); free(hx); free(hy);
    return 0;
}
```

`3.0 * bytes` because saxpy reads `x`, reads `y` and writes `y` — three streams. Comparing
that effective bandwidth against the device's peak is the first thing to do with any
kernel: most scientific kernels are memory-bound, so the fraction of peak bandwidth *is*
the efficiency.

```bash
nvcc -O3 -arch=sm_80 saxpy.cu -o saxpy    # match -arch to your device
./saxpy
nvidia-smi                                 # device, driver, memory
```

## Coalescing, in one experiment

The single most valuable thing to measure on a new kernel.

```cuda
__global__ void coalesced(const float *in, float *out, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) out[i] = in[i] * 2.0f;                   // consecutive threads, consecutive addresses
}

__global__ void strided(const float *in, float *out, int n, int stride) {
    int i = (blockIdx.x * blockDim.x + threadIdx.x) * stride;
    if (i < n) out[i] = in[i] * 2.0f;                   // each thread a different cache line
}
```

**Expected** behaviour, not measured here: the strided version at `stride = 32` moves the
same useful bytes while issuing roughly 32× the memory transactions, so it runs close to
an order of magnitude slower. If you run it and the gap is small, suspect the cache is
absorbing a too-small array.

## Shared memory tiling

Shared memory is a programmer-managed cache. The pattern is load a tile cooperatively,
`__syncthreads()`, compute from shared memory, repeat.

```cuda
#define TILE 32

__global__ void transpose(const float *in, float *out, int w, int h) {
    __shared__ float tile[TILE][TILE + 1];    // +1 pads away bank conflicts

    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;
    if (x < w && y < h) tile[threadIdx.y][threadIdx.x] = in[y * w + x];

    __syncthreads();

    x = blockIdx.y * TILE + threadIdx.x;      // transposed block indices
    y = blockIdx.x * TILE + threadIdx.y;
    if (x < h && y < w) out[y * h + x] = tile[threadIdx.x][threadIdx.y];
}
```

The `TILE + 1` is the whole trick: with a stride of exactly 32, every thread in a warp hits
the same shared-memory bank and the access serialises 32-fold. One element of padding
shifts each row into a different bank.

## Streams, to hide the transfer

```cuda
const int nstream = 4, chunk = n / nstream;
cudaStream_t s[nstream];
for (int k = 0; k < nstream; k++) cudaStreamCreate(&s[k]);

for (int k = 0; k < nstream; k++) {
    int off = k * chunk;
    cudaMemcpyAsync(dx + off, hx + off, chunk * sizeof(float),
                    cudaMemcpyHostToDevice, s[k]);
    saxpy<<<(chunk + 255) / 256, 256, 0, s[k]>>>(chunk, 2.0f, dx + off, dy + off);
    cudaMemcpyAsync(hy + off, dy + off, chunk * sizeof(float),
                    cudaMemcpyDeviceToHost, s[k]);
}
cudaDeviceSynchronize();
```

This requires **pinned** host memory (`cudaMallocHost`) — pageable memory forces a staging
copy and the overlap does not happen.

## Profiling

```bash
nsys profile -o report ./app        # timeline: kernels, transfers, gaps
ncu --set full -o prof ./app        # per-kernel counters
ncu --metrics gpu__time_duration.sum,\
dram__bytes.sum,\
sm__warps_active.avg.pct_of_peak_sustained_active ./app
```

The three numbers worth reading first: achieved occupancy, DRAM throughput as a fraction of
peak, and the ratio of transfer time to kernel time on the timeline.

## Mental model

A GPU hides latency rather than reducing it. When a warp stalls on memory, the scheduler
runs another — so performance depends on having enough parallelism to switch to, and on
not asking for more memory traffic than necessary.

That is why coalescing dominates and why occupancy matters only up to a point: both are
about keeping the memory system busy with useful bytes.

??? warning "Failure modes"
    **Unchecked errors.** CUDA calls return status codes and kernel launches fail asynchronously. Without `CUDA_CHECK` and `cudaGetLastError()` after a launch, a kernel that never ran produces plausible stale output. This is the first thing to add and the most commonly missing.

    **Timing without synchronising.** Launches are asynchronous, so a host timer around a kernel measures the launch overhead and reports an absurd speedup. Use CUDA events, or `cudaDeviceSynchronize()` before stopping the clock.

    **Uncoalesced access.** The dominant performance bug. A kernel at a few percent of peak bandwidth is almost always reading strided or through an array-of-structures layout.

    **Counting the kernel and not the transfer.** A kernel 50× faster than the CPU is irrelevant if the round trip over PCIe costs more than the original computation — see [computing › GPU and CUDA](../computing/gpu-cuda.md) for the arithmetic. GPUs win by keeping data resident across many kernels.

    **`-arch` mismatched to the device.** Compiling for the wrong compute capability either fails to launch or falls back to JIT with a startup cost. Set it explicitly rather than relying on the default.

    **Shared-memory bank conflicts.** A tile with stride 32 serialises 32-fold. The `[TILE][TILE+1]` padding is standard and easy to omit.

    **Assuming inter-block synchronisation.** There is none within a kernel launch. Code that depends on block ordering works on small grids and fails on large ones.

    **Expecting bitwise agreement with the CPU.** Different summation order and fused multiply-add mean the results differ in the last bits. Decide the tolerance in advance.

    <!-- Add your own here — and replace the expectations above with your measurements. -->

## Connections

- [Computing › GPU and CUDA](../computing/gpu-cuda.md) — the memory hierarchy and the transfer-cost arithmetic.
- [OpenMP](openmp.md) · [MPI](mpi.md) — the CPU-side models, and what a hybrid GPU code still needs.
- [Running jobs](running-jobs.md) — requesting GPUs from a scheduler.
- [DL › PyTorch patterns](../dl/pytorch-patterns.md) — where most people's GPU time is actually spent.

## Sources

- NVIDIA *CUDA C++ Programming Guide* and *Best Practices Guide*.
- Kirk & Hwu, *Programming Massively Parallel Processors*.
