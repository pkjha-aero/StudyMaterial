---
title: Verification and validation
status: solid
tags: [pillar-10, foundations, verification, validation, mms]
updated: 2026-09-26
---

# Verification and validation

<span class="status status-solid">solid</span>
<span class="pillar">pillar 10 &middot; V&V, research craft and communication</span>

!!! abstract "In one minute"
    - **Verification**: are you solving the equations right? **Validation**: are they the right equations? Different activities, different evidence, routinely conflated.
    - Verification is a **mathematics** exercise and needs no experiment. Validation needs data, and the data has its own uncertainty.
    - The **method of manufactured solutions** is the strongest code-verification tool available and is under-used because it feels like cheating.
    - Order-of-accuracy testing beats any other check: a bug that does not change the formal order is rare.
    - A result from a single grid is not a result. Three grids in the asymptotic range give an error estimate.

## Key results

**The distinction**, which everything else follows from:

<div class="result" markdown>

| | Verification | Validation |
|---|---|---|
| Question | solving the equations right? | right equations? |
| Compares against | exact/manufactured solutions, refinement | experiment, higher-fidelity data |
| Error source | discretization, iteration, coding | model form, physics assumptions |
| Needs experiments | no | yes |
| Can be automated | yes | rarely |

</div>

**Code verification by MMS.** Pick any smooth \(\phi_{\text{MS}}\) you like, substitute into the governing operator \(\mathcal{L}\), and define the residual as a source term:

\[
S = \mathcal{L}(\phi_{\text{MS}})
\qquad\Longrightarrow\qquad
\mathcal{L}(\phi) = S \ \text{ has exact solution } \phi_{\text{MS}}
\]

Now you have an exact solution to a problem your code can solve, on any geometry, exercising every term. Run a refinement study and confirm the **observed order matches the formal order**. It need not be physical — \(\phi_{\text{MS}} = \sin(x)\cos(y)e^{z}\) is fine and often better, because it makes every term non-zero.

**Observed order of accuracy.** From three systematically refined grids with spacing ratio \(r\):

\[
p = \frac{\ln\!\big((\phi_3-\phi_2)/(\phi_2-\phi_1)\big)}{\ln r}
\]

**Richardson extrapolation** estimates the exact value:

\[
\phi_{\text{exact}} \approx \phi_1 + \frac{\phi_1 - \phi_2}{r^p - 1}
\]

**Grid Convergence Index** turns that into a reportable uncertainty band:

\[
\mathrm{GCI}_{12} = \frac{F_s\,|\phi_1-\phi_2|}{|\phi_1|\,(r^p-1)},
\qquad F_s = 1.25 \ \text{(three grids)},\ 3.0 \ \text{(two)}
\]

Use \(r \ge 1.3\); closer grids make the differences comparable to iterative error and the estimate meaningless.

**Iterative convergence** is a separate error source, and must be driven several orders below the discretization error before a grid study means anything. Otherwise you are measuring solver tolerance.

**Validation metric.** Compare simulation \(S\) with experiment \(D\) accounting for both uncertainties:

\[
E = S - D,
\qquad
u_{\text{val}} = \sqrt{u_{\text{num}}^2 + u_{\text{input}}^2 + u_D^2}
\]

Agreement means \(|E| \lesssim u_{\text{val}}\). Agreement within an uncertainty band that is wide because the experiment was poor is weak evidence, and should be stated as such.

## Mental model

Verification asks whether the code is a faithful implementation of a mathematical model. You can answer it completely, in principle, without any reference to reality — it is a closed question with a right answer.

Validation asks whether that mathematical model resembles the world. It is never finished; it is established over a domain of applicability, and a model validated for attached flow says nothing about separated flow.

Getting these backwards produces the most common failure in computational engineering: tuning a model until it matches an experiment, then presenting the match as validation. That is calibration, and calibrated agreement carries almost no predictive weight.

## Numerics / practice

- **Automate MMS** as a regression test. A manufactured-solution order test in CI catches a large fraction of refactoring bugs, and catches them immediately.
- **Report all three**: iterative convergence level, grid convergence/GCI, and the validation comparison. Omitting any one makes the others unreadable.
- **Check the observed order first.** If \(p\) is far from nominal, stop — nothing downstream is meaningful until that is explained.
- **Validate on held-out conditions**, not on the case used for calibration.

??? warning "Failure modes"
    **Calling calibration validation.** Adjusting a coefficient until the simulation matches the experiment, then reporting the match. The model now interpolates one dataset and has no demonstrated predictive ability. Symptom: excellent agreement on the tuning case and unexplained disagreement elsewhere.

    **Observed order far from nominal, reported anyway.** \(p=1.2\) from a nominally second-order scheme means the grids are not in the asymptotic range, or there is a bug, or a limiter is active. Computing a GCI from it produces an uncertainty number with no basis. This is the most common misuse of the GCI formula.

    **Iterative error contaminating the grid study.** If the solver is converged to \(10^{-4}\) and grid differences are \(10^{-4}\), the refinement study measures the solver. Converge several orders deeper than the effect you are resolving.

    **MMS passing while the physics is wrong.** MMS verifies that the code solves the equations *as implemented*. If the implemented equation has the wrong sign on a physical term, MMS will happily confirm second-order convergence to the wrong model. Verification cannot catch model-form error — that is validation's job.

    **Single-grid results.** Extremely common, and uninterpretable: there is no way to distinguish physics from discretization error. If only one grid is affordable, say so and state that no numerical uncertainty estimate exists.

    **Non-systematic refinement.** Remeshing with a different algorithm rather than uniformly refining changes mesh topology and quality, so the differences are not purely discretization. The observed-order formula assumes systematic refinement.

    **Validating against data with unreported uncertainty.** Agreement to within 2% is meaningless if the experiment has 10% uncertainty — and also if it has 0.1%, because then 2% is a real discrepancy. Without \(u_D\) the comparison cannot be interpreted either way.

    <!-- Add your own here. -->

## Worked example

An order test, and what it looks like when the grids are not asymptotic:

```python
import numpy as np

def order(phi_fine, phi_med, phi_coarse, r=2.0):
    return np.log((phi_coarse - phi_med) / (phi_med - phi_fine)) / np.log(r)

# clean 2nd-order sequence: error ~ h^2 about an exact value of 1.0
good = [1.0 + 0.04 / 4**k for k in (2, 1, 0)]          # fine, medium, coarse
print("asymptotic   :", [f"{v:.6f}" for v in good], f"-> p = {order(*good):.3f}")

# the same data, plus a non-vanishing iterative error
bad = [good[0] + 5e-3, good[1] + 2e-3, good[2] + 2e-3]
print("contaminated :", [f"{v:.6f}" for v in bad], f"-> p = {order(*bad):.3f}")
```

```
asymptotic   : ['1.002500', '1.010000', '1.040000'] -> p = 2.000
contaminated : ['1.007500', '1.012000', '1.042000'] -> p = 2.737
```

The same physics, with a small non-converging error added, reports an order of 2.7 for a second-order scheme. An observed order *above* nominal is as much a warning as one below.

## Connections

- [Numerical methods](numerical-methods.md) — formal order and where it comes from.
- [Uncertainty quantification](uncertainty-quantification.md) — what comes after verification.
- [Fluids › Meshing](../fluids/cfd/meshing.md) — GCI applied to a real grid study.
- [Research craft](research-craft.md) — reporting all of this honestly.

## Sources

- Roache, *Verification and Validation in Computational Science and Engineering*.
- Oberkampf & Roy, *Verification and Validation in Scientific Computing*.
- Salari & Knupp (2000), *Code verification by the method of manufactured solutions*.
