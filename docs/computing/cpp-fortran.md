---
title: C++ and Fortran
status: working
tags: [pillar-5, computing, performance]
updated: 2026-09-26
---

# C++ and Fortran

<span class="status status-working">working</span>
<span class="pillar">pillar 5 &middot; Programming and software engineering</span>

!!! abstract "In one minute"
    - **Fortran is not legacy trivia.** Modern Fortran is a live language for array-heavy numerics, and a great deal of working scientific code is in it.
    - **Array ordering differs**: Fortran is column-major, C/C++ row-major. Every interop bug eventually traces back to this.
    - C++ gives abstraction at zero runtime cost when used carefully, and considerable cost when not.
    - **Aliasing is why Fortran often beats C** on the same loop: Fortran assumes arguments do not alias, C must assume they might.
    - Build systems are part of the code. CMake is the practical standard; treat it as source, not configuration debris.

## Key results

**Language comparison for numerics:**

<div class="result" markdown>

| | Modern Fortran | Modern C++ |
|---|---|---|
| Arrays | first class, slicing, `reshape` | `std::vector`, `mdspan` (C++23), or a library |
| Aliasing | assumed absent — better optimisation | assumed possible unless `restrict` |
| Generic code | limited | templates, very powerful |
| Ecosystem | numerical libraries, MPI | everything |
| Ordering | column-major | row-major |
| Learning curve | gentle for array code | steep |

</div>

**Memory layout.** For a 2D array, Fortran stores columns contiguously and C stores rows:

\[
\text{Fortran } A(i,j) \leftrightarrow \text{C } A[j][i]
\]

Loop nesting must match: in Fortran the **first** index varies fastest in the inner loop; in C the **last** does. Getting this backwards on a large array costs an order of magnitude through cache misses, and produces correct results, so nothing flags it.

**Aliasing.** Given `void f(double* a, double* b, int n)`, a C compiler must assume `a` and `b` may overlap, so it cannot reorder or vectorise freely. Fortran's standard forbids argument aliasing, so the compiler is free by default. In C/C++, `restrict` recovers it — and is under-used.

**Interoperability.** `iso_c_binding` is the standard route:

```fortran
subroutine compute(n, x, y) bind(C, name="compute")
  use iso_c_binding, only: c_int, c_double
  integer(c_int), value :: n
  real(c_double), intent(in)  :: x(n)
  real(c_double), intent(out) :: y(n)
  y = 2.0_c_double * x
end subroutine
```

Three rules: pass scalars by `value` when the C side passes by value, match the kind constants exactly, and remember that arrays arrive with the *other* language's ordering convention.

**Modern C++ that matters for numerics:** RAII for resource safety, `std::span`/`mdspan` for non-owning array views, `constexpr` for compile-time work, and the parallel algorithms (`std::execution::par`). Avoid deep template metaprogramming in numerical kernels unless the payoff is measured — compile times and error messages are real costs.

**Build systems.** CMake with targets (`target_link_libraries`, `target_include_directories`) rather than global variables. Pin the compiler and flags in the build, not in a shell history — otherwise the run is not reproducible, and `-O3 -ffast-math` versus `-O2` can change results.

## Mental model

Both languages exist in this space for the same reason: they compile to code where you can reason about what the machine does. The differences are about what the compiler is *allowed to assume*. Fortran assumes arrays do not overlap and that shapes are known, so it optimises aggressively with no annotations. C++ assumes very little and gives you the tools to assert more.

That explains the division of labour. Fortran wins where the code is array expressions over regular grids. C++ wins where the structure is irregular, or where genericity and composition matter more than the inner loop.

## Numerics / practice

- **Match loop order to memory order.** This is the highest-value, lowest-effort optimisation in either language.
- **Use `-Wall -Wextra`** and, in Fortran, `-fcheck=all -fimplicit-none` during development; the runtime checks catch out-of-bounds immediately.
- **Record compiler and flags** with every result. `-ffast-math` changes floating-point semantics.
- **Prefer `iso_c_binding`** to compiler-specific name-mangling assumptions for interop.

??? warning "Failure modes"
    **Loop order mismatched to array order.** A Fortran loop with the row index outermost, or a C loop with the column index innermost, strides through memory by the row length. Correct results, an order of magnitude slower, and no warning. First thing to check in any slow array kernel.

    **Off-by-one and base index in interop.** Fortran arrays default to base 1, C to base 0, and Fortran allows arbitrary lower bounds. Mixing them produces silent corruption at the edges rather than an error.

    **Implicit typing in legacy Fortran.** Without `implicit none`, an undeclared variable gets a type from its first letter — so a typo becomes a new variable rather than a compile error. `implicit none` in every unit, non-negotiable.

    **Assuming `-ffast-math` is free.** It permits reassociation and drops NaN/Inf handling, so reductions change, comparisons against NaN stop working, and results differ between optimisation levels. Fine for some codes, fatal for others — decide deliberately and record it.

    **Uninitialised memory that works in debug.** Debug builds often zero memory; release builds do not. A bug that only appears with optimisation on is frequently this. Run with a sanitiser (`-fsanitize=address,undefined`) rather than guessing.

    **C++ abstraction in the inner loop.** A virtual call, a `std::function`, or an unexpected copy inside a hot loop defeats inlining and vectorisation. Check the generated assembly or the vectorisation report (`-fopt-info-vec`) rather than assuming zero cost.

    **Array temporaries in Fortran.** A non-contiguous slice passed to a routine expecting a contiguous array makes the compiler create a temporary copy — silently, inside a loop. `-Warray-temporaries` reveals it.

    <!-- Add your own here. -->

## Worked example

Loop order against memory order, in the language where it is easiest to demonstrate:

```python
import numpy as np, time

n = 4000
A_c = np.ascontiguousarray(np.random.rand(n, n))       # row-major
A_f = np.asfortranarray(A_c)                            # column-major, same values

def bench(A, axis):
    A.sum(axis=axis)                                    # warm up
    t = time.perf_counter()
    for _ in range(5):
        A.sum(axis=axis)
    return (time.perf_counter() - t) / 5 * 1e3

print(f"row-major,    sum over axis 1 (along rows)    : {bench(A_c, 1):7.1f} ms")
print(f"row-major,    sum over axis 0 (across rows)   : {bench(A_c, 0):7.1f} ms")
print(f"column-major, sum over axis 0 (along columns) : {bench(A_f, 0):7.1f} ms")
print(f"column-major, sum over axis 1 (across columns): {bench(A_f, 1):7.1f} ms")
```

```
row-major,    sum over axis 1 (along rows)    :     7.1 ms
row-major,    sum over axis 0 (across rows)   :     8.5 ms
column-major, sum over axis 0 (along columns) :     7.5 ms
column-major, sum over axis 1 (across columns):     8.6 ms
```

Reducing along the contiguous axis is about 20% faster in both layouts — and note that the fast axis *swaps* between row-major and column-major, which is the ordering rule made visible.

Twenty percent, not the order of magnitude a naive hand-written loop would show, because NumPy's reduction iterates in memory order where it can. **That gap is the point**: a good library absorbs most of the layout penalty, and your own C or Fortran loop will not. What shows as 20% here shows as 10× in a kernel you write yourself.

## Connections

- [HPC and parallelism](hpc.md) — where these kernels run.
- [Python performance](python-performance.md) — when to drop down to a compiled language.
- [GPU and CUDA](gpu-cuda.md) — coalescing is the same ordering argument on a GPU.

## Sources

- Metcalf, Reid & Cohen, *Modern Fortran Explained*.
- Stroustrup, *The C++ Programming Language*; and the C++ Core Guidelines.
- Archive: the Fortran-heavy course folders in the [course archive](../resources/course-archive.md).
