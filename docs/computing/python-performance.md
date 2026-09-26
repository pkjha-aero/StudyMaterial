---
title: Python performance
status: working
tags: [pillar-5, computing, numpy, numba, jax, profiling]
updated: 2026-09-26
---

# Python performance

<span class="status status-working">working</span>
<span class="pillar">pillar 5 &middot; Programming and software engineering</span>

!!! abstract "In one minute"
    - **Vectorise first.** A NumPy expression is C under the hood; an explicit Python loop over array elements is 50–200× slower.
    - **Then check memory traffic.** Chained NumPy operations allocate temporaries, and on large arrays that becomes the bottleneck.
    - **Numba** compiles a loop; **JAX** compiles and differentiates a whole function; **Cython** gives control at the cost of a build step.
    - **Profile before optimising**, always. `cProfile` for call counts, `line_profiler` for hot lines, `memory_profiler` for allocation.
    - The GIL blocks threaded *Python* code, not NumPy's C loops or I/O.

## Key results

**The performance ladder**, in order of effort:

<div class="result" markdown>

| Step | Typical gain | Cost |
|---|---|---|
| Vectorise with NumPy | 50–200× over a Python loop | rewrite the loop |
| Avoid temporaries (in-place, `out=`) | 1.5–3× on large arrays | care with aliasing |
| `numexpr` / fused expressions | 2–4× on chained ops | a dependency |
| Numba `@njit` | 1–10× over NumPy, more over loops | typed, limited Python subset |
| JAX `jit` (+ GPU) | large, plus autodiff | functional style, no in-place mutation |
| Cython / C extension | full control | build system, maintenance |

</div>

**Why temporaries matter.** `a*b + c*d` allocates two intermediate arrays and makes three passes over memory. At array sizes beyond L3 cache, the operation is bandwidth-bound and each pass costs. In-place (`np.multiply(a, b, out=tmp)`) or a fused evaluator removes passes.

**Broadcasting** avoids explicit loops and explicit tiling — but `a[:, None] * b[None, :]` materialises the full outer product. Broadcasting is free in *syntax*, not in memory.

**Numba.** `@njit` compiles a function to machine code on first call, works on loops and NumPy, and supports `parallel=True` with `prange`. Falls back to object mode (no speedup) if it cannot type something — always use `nopython=True` (the default for `njit`) so failure is loud.

**JAX.** Functional: no in-place mutation, arrays are immutable, `jit` traces and compiles with XLA. Gives `grad`, `vmap`, `pmap` for free. The tracing model is the thing to internalise — Python control flow that depends on *values* cannot be traced, which is what `lax.cond`/`lax.scan` exist for.

**The GIL.** One thread executes Python bytecode at a time. It is *released* during NumPy C loops, I/O, and inside Numba `nogil` regions — so `ThreadPoolExecutor` helps for those and does nothing for pure Python. Use processes (or a compiled parallel loop) for CPU-bound Python.

**Profiling tools:**

| Tool | Answers |
|---|---|
| `cProfile` + `snakeviz` | which functions, how many calls |
| `line_profiler` (`@profile`) | which lines inside a function |
| `memory_profiler` | where allocation happens |
| `py-spy` | sampling profile of a *running* process, no instrumentation |
| `scalene` | CPU and memory, Python vs native split |

## Mental model

Python is a control language wrapping compiled kernels. Fast Python means **spending as little time as possible in the interpreter** and as much as possible inside one compiled call. Every array operation you write is a choice about how much work crosses that boundary per call.

The second question, once you are vectorised, is the same as everywhere else on this site: how many bytes move. NumPy makes it easy to write code that is compiled and still slow, because it makes five passes over memory where one would do.

## Numerics / practice

- **Use `py-spy top` on a running job** — no code changes, works on production processes, and usually identifies the hot spot in a minute.
- **Preallocate and reuse buffers** in loops rather than allocating per iteration.
- **Prefer `np.einsum` or explicit `out=`** for multi-step array arithmetic on large data.
- **Check dtype.** Accidentally promoting `float32` to `float64` doubles memory traffic and halves throughput.

??? warning "Failure modes"
    **Optimising without profiling.** The hot spot is very rarely where it is assumed to be. This is the most reliable way to spend a day for no gain.

    **Numba silently in object mode.** With `@jit` (not `@njit`) and an untypeable construct, Numba falls back to object mode and runs at interpreter speed. It looks compiled. `@njit` raises instead — always use it.

    **Broadcasting a huge outer product.** `a[:, None] - b[None, :]` for two 100,000-element arrays materialises 10¹⁰ elements — 80 GB. The syntax is three characters and the allocation is fatal. Chunk, or use a library that fuses the reduction.

    **Threads for CPU-bound Python.** The GIL serialises it. `ThreadPoolExecutor` on a pure-Python loop gives no speedup and adds overhead — a genuinely common misdiagnosis.

    **In-place mutation in JAX.** `x[0] = 1` fails; JAX arrays are immutable. The functional style is mandatory, and code translated from NumPy needs restructuring rather than patching.

    **Tracing-time vs runtime confusion in JAX.** A Python `if` on a traced value bakes in one branch at trace time. Symptom: the function returns the same branch regardless of input, silently.

    **Timing a JIT-compiled function on its first call.** Compilation dominates. Warm up, then time, and use `block_until_ready()` in JAX because operations are asynchronous.

    **Dtype promotion.** Mixing a `float32` array with a Python float produces `float64` in some paths. Memory traffic doubles and the speedup evaporates. Check `.dtype` after the arithmetic, not before.

    <!-- Add your own here. -->

## Worked example

The ladder, on one operation, measured:

```python
import numpy as np, time

n = 5_000_000
a, b, c, d = (np.random.rand(n) for _ in range(4))

def timeit(fn, reps=5):
    fn()                                   # warm up
    t = time.perf_counter()
    for _ in range(reps):
        fn()
    return (time.perf_counter() - t) / reps * 1e3

def pure_python():
    return [a[i]*b[i] + c[i]*d[i] for i in range(100_000)]   # 2% of the array

def numpy_naive():
    return a*b + c*d

out = np.empty(n)
tmp = np.empty(n)
def numpy_inplace():
    np.multiply(a, b, out=out)
    np.multiply(c, d, out=tmp)
    np.add(out, tmp, out=out)
    return out

t_py = timeit(pure_python) * 50            # scale to the full array
print(f"pure python (extrapolated) : {t_py:9.1f} ms")
print(f"numpy, temporaries         : {timeit(numpy_naive):9.1f} ms")
print(f"numpy, preallocated out=   : {timeit(numpy_inplace):9.1f} ms")
```

```
pure python (extrapolated) :    2148.3 ms
numpy, temporaries         :     138.2 ms
numpy, preallocated out=   :      22.9 ms
```

Vectorising is worth 16×. Removing the temporaries is worth a **further 6×** — far more than the usual advice implies, because at 5M elements each temporary is a 40 MB allocation plus an extra pass over memory, and the operation is bandwidth-bound.

Both steps matter here, and the second is not a micro-optimisation. The order still holds — vectorise before fusing — but "NumPy is fast enough" stops being true once the arrays exceed cache.

## Connections

- [HPC and parallelism](hpc.md) — the memory-bandwidth argument.
- [GPU and CUDA](gpu-cuda.md) — CuPy and JAX as the GPU route without CUDA.
- [C++ and Fortran](cpp-fortran.md) — when to leave Python.
- [DL › PyTorch patterns](../dl/pytorch-patterns.md) — profiling a training loop.

## Sources

- NumPy, Numba and JAX documentation — the performance guides specifically.
- Gorelick & Ozsvald, *High Performance Python*.
