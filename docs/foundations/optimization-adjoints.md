---
title: Optimization and adjoints
status: solid
tags: [pillar-4, foundations, optimization, inverse-problems]
updated: 2026-09-26
---

# Optimization and adjoints

<span class="status status-solid">solid</span>
<span class="pillar">pillar 4 &middot; Solvers, time integration and adjoints</span>

!!! abstract "In one minute"
    - The adjoint method gives the gradient of **one output with respect to all inputs** for the cost of roughly one extra solve — independent of the number of design variables.
    - Finite-difference gradients cost \(N+1\) solves for \(N\) variables. At \(N \sim 10^3\) design parameters, that is the difference between feasible and not.
    - **Discrete adjoint** differentiates the code; **continuous adjoint** derives the adjoint PDE then discretizes. They disagree, and the discrete one matches your actual gradient.
    - Adjoints also give **error estimates** and **data assimilation**, not just design optimization.
    - Adjoints of **chaotic** systems diverge exponentially backwards in time. This is a real limit, not a bug to fix.

## Key results

**The problem.** Minimise \(J(\mathbf{u}, \boldsymbol{\alpha})\) subject to a state equation \(\mathbf{R}(\mathbf{u}, \boldsymbol{\alpha}) = 0\), where \(\boldsymbol{\alpha}\) are design variables and \(\mathbf{u}\) the flow state.

Direct differentiation gives

\[
\frac{dJ}{d\boldsymbol{\alpha}} = \frac{\partial J}{\partial \boldsymbol{\alpha}} + \frac{\partial J}{\partial \mathbf{u}}\frac{d\mathbf{u}}{d\boldsymbol{\alpha}},
\qquad
\frac{\partial \mathbf{R}}{\partial \mathbf{u}}\frac{d\mathbf{u}}{d\boldsymbol{\alpha}} = -\frac{\partial \mathbf{R}}{\partial \boldsymbol{\alpha}}
\]

One linear solve **per design variable** — the sensitivity \(d\mathbf{u}/d\boldsymbol{\alpha}\) is a different vector for each \(\alpha_i\).

**The adjoint trick.** Introduce \(\boldsymbol{\psi}\) and solve instead:

<div class="result" markdown>

\[
\left(\frac{\partial \mathbf{R}}{\partial \mathbf{u}}\right)^{\!\mathsf T}\boldsymbol{\psi}
= \left(\frac{\partial J}{\partial \mathbf{u}}\right)^{\!\mathsf T}
\qquad\Longrightarrow\qquad
\frac{dJ}{d\boldsymbol{\alpha}} = \frac{\partial J}{\partial \boldsymbol{\alpha}} - \boldsymbol{\psi}^{\mathsf T}\frac{\partial \mathbf{R}}{\partial \boldsymbol{\alpha}}
\]

</div>

**One** adjoint solve, then the full gradient by cheap inner products. The cost is independent of \(N\).

**Cost comparison** for \(N\) design variables, \(M\) objectives:

| Approach | Solves | Best when |
|---|---|---|
| Finite difference | \(N+1\) | \(N\) tiny, code is a black box |
| Complex step | \(N\) | as above, but machine-precision gradients |
| Forward/tangent | \(N\) | \(N \ll M\) |
| **Adjoint** | \(M\) | \(N \gg M\) — the usual aerodynamic case |

**Discrete versus continuous adjoint:**

- **Discrete** — transpose the linearised discrete operator, usually via algorithmic differentiation. Gradient is exact for the discretised problem, so optimizers converge cleanly. Implementation effort is high and memory-hungry.
- **Continuous** — derive the adjoint PDE by hand, discretize it independently. Cheaper and more intuitive, but the gradient is only consistent in the limit \(h\to0\), so line searches can stall on the mismatch.

**Complex-step differentiation** — exact to machine precision, no subtractive cancellation, for real-analytic code:

\[
f'(x) \approx \frac{\mathrm{Im}\,f(x + ih)}{h},\qquad h \sim 10^{-20}
\]

**Other uses of the adjoint.** Goal-oriented error estimation weights the local residual by adjoint sensitivity to say which cells matter for *your* output — the basis of output-based mesh adaptation. 4D-Var data assimilation is an adjoint optimization over initial conditions.

## Mental model

The forward sensitivity asks: *if I nudge this input, how does everything respond?* You must ask it once per input.

The adjoint asks the reverse: *what would have to change to move this one output?* The answer is a field over the whole domain — the adjoint solution is literally a map of influence, showing where a perturbation would most affect your objective. One question, one solve, all inputs answered.

This is the same duality as reverse-mode automatic differentiation, and backpropagation in neural networks is exactly this argument: one backward pass gives the gradient with respect to all weights.

## Numerics / practice

- **Always verify the gradient.** Compare against complex-step (or a careful finite difference) on a small case. An unverified adjoint that is subtly wrong wastes far more time than the check.
- **Checkpointing** for unsteady adjoints: the backward sweep needs the forward state at each step. Storing everything is impossible; binomial checkpointing trades recomputation for memory at a known optimum.
- **Freeze limiters and turbulence models** or differentiate them properly. Treating them as constants ("frozen turbulence") gives a cheap but inconsistent gradient — often good enough to descend, never good enough to converge tightly.
- **Regularize shape optimization.** Unconstrained, the optimizer produces oscillatory, unmanufacturable geometries that exploit discretization error. Smooth the gradient or parameterize with a limited basis.

??? warning "Failure modes"
    **Non-differentiable operators in the forward code.** Slope limiters, `min`/`max`, upwind switches and if-branches are not differentiable. The adjoint of such a code is wrong at exactly the points where the switch activates — near shocks and extrema, which is usually where the objective is sensitive. Symptom: gradient verification failing only on certain configurations.

    **Chaotic sensitivity.** For turbulent or otherwise chaotic systems, the adjoint grows exponentially backwards in time: \(\|\psi\| \sim e^{\lambda T}\). Long-time LES or DNS adjoints blow up and the computed gradient of a time-averaged objective is meaningless — it does not converge as the averaging window grows. This is a property of the physics. Workarounds (least-squares shadowing, ensemble adjoints) are expensive and still research-grade.

    **Discrete/continuous mismatch.** A continuous adjoint gradient differs from the true gradient of the discrete objective by \(O(h^p)\). Symptom: the line search stalls, or the optimizer converges to a point where the reported gradient is not zero. Not a bug — an inconsistency.

    **Unverified adjoint.** The single most expensive mistake here. A sign error or a missing term produces a gradient that points *somewhere*, and the optimizer will dutifully follow it downhill-ish for many iterations before it becomes obvious.

    **Finite-difference step tuning.** Too large gives truncation error, too small gives cancellation, and the sweet spot moves with the function. If you are verifying an adjoint, use complex step instead and remove the variable entirely.

    **Checkpointing memory blowup.** Naively storing the full unsteady trajectory. A 10⁷-cell mesh over 10⁴ steps is petabytes. Budget this before starting.

    <!-- Add your own here. -->

## Worked example

Complex step against finite difference — the reason to stop tuning step sizes:

```python
import numpy as np

f  = lambda x: np.exp(x) / np.sqrt(np.sin(x)**3 + np.cos(x)**3)
x  = 1.5
exact = 4.05342789389862               # analytic derivative at x=1.5

for h in (1e-4, 1e-8, 1e-12):
    fd = (f(x + h) - f(x)) / h
    print(f"FD   h={h:.0e}   error={abs(fd-exact):.3e}")
cs = np.imag(f(complex(x, 1e-20))) / 1e-20
print(f"CS   h=1e-20   error={abs(cs-exact):.3e}")
```

```
FD   h=1e-04   error=4.732e-04
FD   h=1e-08   error=9.936e-08
FD   h=1e-12   error=1.107e-03
CS   h=1e-20   error=8.882e-16
```

Finite difference has an optimum near \(10^{-8}\) and degrades either side; complex step has no step-size trade-off at all, which is what makes it the right tool for verifying an adjoint.

## Connections

- [Numerical methods](numerical-methods.md) — the roundoff floor that motivates complex step.
- [Linear solvers](linear-solvers.md) — the adjoint system is a transposed linear solve.
- [Uncertainty quantification](uncertainty-quantification.md) — adjoint-based sensitivity.
- [Fluids › CFD](../fluids/cfd/index.md) — where shape optimization is applied.

## Sources

- Giles & Pierce (2000), *An introduction to the adjoint approach to design*.
- Jameson (1988), *Aerodynamic design via control theory* — the founding paper.
- Archive: `Others/Jameson` — CFD and aerodynamic shape optimization.
- Martins & Ning, *Engineering Design Optimization*.
