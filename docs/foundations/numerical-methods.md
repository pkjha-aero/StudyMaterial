---
title: Numerical methods
status: solid
tags: [pillar-3, foundations, discretization, numerical-stability, spectral-methods]
updated: 2026-09-26
---

# Numerical methods

<span class="status status-solid">solid</span>
<span class="pillar">pillar 3 &middot; Discretization and numerical analysis</span>

!!! abstract "In one minute"
    - **Lax equivalence**: for a well-posed linear problem, consistency + stability \(\Leftrightarrow\) convergence. You verify the first two; the third follows.
    - **von Neumann analysis** gives the stability condition by asking what the scheme does to a single Fourier mode.
    - The **modified equation** tells you what your scheme actually solves — usually the target PDE plus a diffusion or dispersion term you did not ask for.
    - Even-order truncation errors produce **dissipation**; odd-order produce **dispersion** (wiggles trailing sharp features).
    - Formal order is an asymptotic statement about smooth solutions. It tells you nothing about the error at the mesh you can afford.

## Key results

**Truncation error from Taylor expansion.** For the first derivative:

<div class="result" markdown>

\[
\frac{\phi_{i+1}-\phi_i}{\Delta x} = \phi' + \frac{\Delta x}{2}\phi'' + O(\Delta x^2)
\quad\text{(1st order)}
\]

\[
\frac{\phi_{i+1}-\phi_{i-1}}{2\Delta x} = \phi' + \frac{\Delta x^2}{6}\phi''' + O(\Delta x^4)
\quad\text{(2nd order)}
\]

</div>

**Lax equivalence theorem.** For a consistent finite-difference approximation to a well-posed linear initial-value problem, stability is necessary and sufficient for convergence. Note the conditions: *linear*, *well-posed*. Nonlinear problems get no such guarantee, which is why nonlinear stability (TVD, entropy) is a separate theory.

**von Neumann analysis.** Substitute \(\phi_j^n = G^n e^{ikj\Delta x}\) and require \(|G| \le 1\). For explicit upwind advection with \(c = u\Delta t/\Delta x\):

\[
G = 1 - c\left(1 - e^{-ik\Delta x}\right),
\qquad
|G|^2 = 1 - 2c(1-c)(1-\cos k\Delta x)
\]

\(|G|\le1\) for \(0 \le c \le 1\) — the CFL condition, derived rather than asserted.

**Modified equation.** First-order upwind actually solves

\[
\phi_t + u\phi_x = \underbrace{\frac{u\Delta x}{2}(1-c)\,\phi_{xx}}_{\text{numerical diffusion}} + O(\Delta x^2)
\]

and second-order central solves

\[
\phi_t + u\phi_x = -\underbrace{\frac{u\Delta x^2}{6}\,\phi_{xxx}}_{\text{numerical dispersion}} + O(\Delta x^4)
\]

This is the single most useful diagnostic tool on this page: it converts "the scheme is too diffusive" into a number you can compare against the physical diffusivity.

**Dissipation and dispersion**, read from the modified equation:

| Leading error term | Effect | Visible as |
|---|---|---|
| even derivative (\(\phi_{xx}\), \(\phi_{xxxx}\)) | dissipation | amplitude decay, smearing |
| odd derivative (\(\phi_{xxx}\)) | dispersion | phase error, wiggles behind sharp fronts |

**Observed order of accuracy.** With errors \(e_1, e_2\) on grids refined by ratio \(r\):

\[
p = \frac{\ln(e_2/e_1)}{\ln r}
\]

If \(p\) differs materially from the nominal order, either you are not in the asymptotic range, or something is wrong — a boundary closure, a limiter, or a bug.

**Roundoff versus truncation.** For a first-order difference, total error \(\approx C\Delta x + \varepsilon_{\text{machine}}/\Delta x\), minimised near \(\Delta x \sim \sqrt{\varepsilon_{\text{machine}}} \approx 10^{-8}\). Below that, refining makes things *worse*.

## Mental model

Every discretization is a lie about what happens between grid points, and the modified equation tells you which lie. That reframing is useful: instead of "my scheme is second order", ask "what extra physics did my scheme add?" A diffusion term of size \(u\Delta x/2\) is a concrete, comparable quantity; "second order" is not.

Stability analysis asks a different question: not how wrong one step is, but whether errors grow. A scheme can be highly accurate per step and useless because the error doubles every step.

## Numerics / practice

- **Always compute the observed order** in a refinement study. The nominal order is an assumption until measured.
- **Check the modified-equation coefficient against the physical one.** If numerical diffusion exceeds \(\nu\), the simulation is resolving your scheme, not the flow.
- **Watch boundary closures.** A second-order interior scheme with a first-order boundary treatment is often globally first order — and the loss shows up as a mysteriously low observed \(p\).
- **Do not chase \(\Delta x \to 0\)** in a finite-difference derivative check. Around \(10^{-8}\) roundoff takes over; complex-step differentiation avoids the problem entirely.

??? warning "Failure modes"
    **Order verified only on smooth solutions.** Every high-order scheme drops to first order at a discontinuity — that is Godunov's theorem, not a bug. Reporting the smooth-case order for a shocked problem overstates accuracy badly.

    **Refining a finite-difference gradient too far.** Error falls, bottoms out near \(\Delta x \approx 10^{-8}\), then rises as subtractive cancellation dominates. The classic symptom is a "V" in a log-log error plot, often misread as the scheme breaking down.

    **von Neumann applied outside its assumptions.** It assumes linear, constant coefficients, periodic boundaries. Real problems violate all three, so it gives a necessary condition, not a sufficient one. A scheme that passes can still go unstable through boundary treatment or nonlinearity.

    **Boundary closure silently reducing global order.** Interior fourth order, boundary second order, global order between two and three. Symptom: observed \(p\) that refuses to reach nominal no matter how fine the grid.

    **Aliasing in nonlinear terms.** Products of resolved modes generate wavenumbers above the grid cutoff, which fold back onto resolved scales as spurious energy. In spectral methods this is fatal without dealiasing (the 3/2 rule); in finite differences it appears as grid-scale noise that grows slowly.

    **Comparing errors between grids that are not nested.** The observed-order formula assumes systematic refinement. Comparing two unrelated meshes gives a number with no meaning.

    <!-- Add your own here. -->

## Worked example

The roundoff floor, which every derivative check eventually hits:

```python
import numpy as np

f, fp = np.sin, np.cos
x = 1.0
for h in (1e-1, 1e-4, 1e-8, 1e-12):
    fd = (f(x + h) - f(x)) / h
    print(f"h={h:.0e}   error={abs(fd - fp(x)):.3e}")
```

```
h=1e-01   error=4.294e-02
h=1e-04   error=4.207e-05
h=1e-08   error=2.970e-09
h=1e-12   error=4.324e-05
```

Error falls as \(O(h)\) to about \(10^{-8}\), then *rises* by four orders as cancellation takes over. Refining past the floor makes the answer worse.

## Connections

- **[Modified wavenumber notebook](../notebooks/modified-wavenumber.ipynb)** — dispersion, dissipation and points-per-wavelength, computed.
- [Mathematical methods](math-methods.md) — PDE type, which decides admissible schemes.
- [Linear solvers](linear-solvers.md) — solving the systems this produces.
- [Verification and validation](verification-validation.md) — measuring observed order properly.
- [Fluids › Finite volume](../fluids/cfd/finite-volume.md) — these ideas applied.

## Sources

- LeVeque, *Finite Difference Methods for Ordinary and Partial Differential Equations*.
- Hirsch, *Numerical Computation of Internal and External Flows* — modified equations, stability.
- Archive: see the [course archive](../resources/course-archive.md).
