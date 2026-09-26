---
title: Foundations
status: solid
tags: [pillar-2, pillar-3, pillar-4, pillar-8, pillar-10, foundations, discretization, statistics]
---

# Foundations

<span class="status status-solid">solid</span>
<span class="pillar">pillars 2, 3, 4, 8, 10</span>

The methods that do not care which physics you point them at: mathematical machinery,
discretization and its error theory, solvers, statistics and uncertainty, and the
discipline of establishing that any of it is right.

Every other section on this site links back here.

## Pages

| Page | Pillar | Covers |
|---|---|---|
| [Mathematical methods](math-methods.md) | 2 | PDE classification, well-posedness, conditioning, SVD, asymptotics |
| [Numerical methods](numerical-methods.md) | 3 | Truncation error, Lax equivalence, von Neumann, modified equations |
| [Linear solvers](linear-solvers.md) | 4 | Direct vs Krylov, preconditioning, multigrid, residual vs error |
| [Optimization and adjoints](optimization-adjoints.md) | 4 | Adjoint gradients, discrete vs continuous, complex step, chaotic limits |
| [Probability and statistics](probability-statistics.md) | 8 | Estimators, effective sample size, regression, model selection |
| [Uncertainty quantification](uncertainty-quantification.md) | 8 | Aleatory vs epistemic, Monte Carlo, PCE, Sobol indices, emulators |
| [Verification and validation](verification-validation.md) | 10 | MMS, observed order, Richardson, GCI, the V-vs-V distinction |
| [Research craft](research-craft.md) | 10 | Reproducibility, figures, claims, audience |

## Reading order

There is a chain running through this section, and it is worth following once:

**[Mathematical methods](math-methods.md)** establishes PDE type and conditioning →
**[numerical methods](numerical-methods.md)** turns the PDE into a discrete system and
says what error that introduces → **[linear solvers](linear-solvers.md)** solves it, at a
cost set by the conditioning from the first page →
**[verification and validation](verification-validation.md)** establishes the answer is
right → **[UQ](uncertainty-quantification.md)** says how much to trust it →
**[research craft](research-craft.md)** reports it honestly.

[Optimization and adjoints](optimization-adjoints.md) and
[probability and statistics](probability-statistics.md) are entered as needed.

## The theme running through all of it

Three failures recur across these pages, and they are the same mistake in different
clothing — **confusing a measure of effort with a measure of correctness**:

- A small **residual** read as a small error. The gap is the condition number.
- A converged **iteration** read as a converged solution. Iterative and discretization
  error are independent.
- A **calibrated** model read as a validated one. Fitting is not prediction.

Each is recorded in the failure-modes block of the relevant page.

## Connections

- [Fluids](../fluids/index.md) · [Aerospace](../aerospace/index.md) · [Astrophysics](../astrophysics/index.md) — where these methods are applied.
- [Computing](../computing/index.md) — making them run fast.
- [Scientific ML](../sciml/index.md) — and why verification is harder there.

## Sources

Per page. See the [course archive](../resources/course-archive.md) for the Maths and CSE
folders.
