---
title: Aircraft design
status: working
tags: [pillar-1, aerospace, optimization, scaling]
updated: 2026-09-28
---

# Aircraft design

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Conceptual design is a **convergence problem, not an analysis problem**: weight depends on fuel, fuel depends on weight, and you iterate until it closes.
    - The **constraint diagram** turns every requirement — takeoff, climb, cruise, turn, landing — into a curve in \(T/W\) versus \(W/S\), and the design point is a corner of the feasible region.
    - **Weight growth compounds.** Added mass needs more lift, more structure, more fuel, more engine — the snowball factor is typically 3–8× the original addition.
    - Sizing uses **historical regression**, which is why it works and also where it fails: outside the database it extrapolates silently.
    - Optimising one discipline in isolation reliably produces a worse aircraft than a coordinated compromise.

## Key results

**The sizing loop** — the structure of conceptual design:

<div class="result" markdown>

requirements → guess \(W_0\) → empty-weight fraction from regression → fuel fraction from
the mission → new \(W_0\) → **repeat until converged** → constraint diagram gives \(T/W\)
and \(W/S\) → geometry → refined analysis → back to the top

</div>

**Takeoff weight buildup:**

\[
W_0 = W_{\text{payload}} + W_{\text{crew}} + W_f + W_e,
\qquad
W_0 = \frac{W_{\text{payload}} + W_{\text{crew}}}{1 - \dfrac{W_f}{W_0} - \dfrac{W_e}{W_0}}
\]

with \(W_e/W_0 = A W_0^{C}\) from historical data by aircraft class. The denominator is the point: as the two fractions approach 1, \(W_0\) diverges. A design that will not close is one where payload plus fuel plus structure cannot fit inside the weight they require.

**Mission fuel fraction** from segment ratios, with the cruise segment from [Breguet](flight-mechanics.md):

\[
\frac{W_f}{W_0} = 1.06\left(1 - \prod_i \frac{W_{i+1}}{W_i}\right)
\]

The 6% allows for reserves and trapped fuel.

**Constraint analysis.** Each requirement becomes a curve in the \((W/S,\ T/W)\) plane:

| Requirement | Constraint |
|---|---|
| Takeoff distance | \(T/W \propto (W/S)/(\sigma C_{L,TO} s_{TO})\) |
| Rate of climb | \(T/W \ge \frac{\mathrm{RoC}}{V} + \frac{q C_{D_0}}{W/S} + \frac{k}{q}(W/S)\) |
| Cruise speed | \(T/W \ge \frac{q C_{D_0}}{W/S} + \frac{k}{q}(W/S)\) |
| Sustained turn at \(n\) | as cruise, with \(k n^2\) |
| Landing distance | \(W/S \le \frac{\sigma C_{L,\max} s_L}{\text{const}}\) — a vertical line |

The feasible region lies above every thrust curve and left of the landing line. The design point is usually its lowest-leftmost corner: minimum thrust and maximum wing loading that still satisfies everything.

**Weight growth factor.** Adding \(\Delta W\) of equipment forces structure, fuel and engine to grow:

\[
\text{growth factor} = \frac{\partial W_0}{\partial W_{\text{fixed}}}
= \frac{1}{1 - \dfrac{\partial (W_e + W_f)}{\partial W_0}}
\]

For a transport this is typically 3–8. One kilogram of avionics costs several kilograms of aeroplane, and that is why weight control is a programme-level discipline rather than an engineering detail.

**Regression limits.** Empty-weight fractions are fits to aircraft that were built. A blended wing body, an electric aircraft, or a hydrogen tank configuration is outside the database, and the correlation will still return a number.

## Mental model

Conceptual design is a fixed-point iteration on weight, wrapped in a feasibility check on thrust and wing loading. Nothing in it is deep individually — the difficulty is that every quantity depends on every other, so no piece can be settled alone.

That coupling is also why discipline-local optimisation misleads. The lightest wing is not the wing of the lightest aircraft: a thinner wing weighs less and holds less fuel, needing a bigger wing. The constraint diagram and the sizing loop exist to make those couplings explicit rather than discovering them late.

## Numerics / practice

- **Draw the constraint diagram before choosing anything.** It shows which requirement is actually binding, and that is usually not the one people assume.
- **Converge the sizing loop and report the residual.** An unconverged \(W_0\) invalidates everything downstream.
- **Carry weight margin explicitly** and track it. Margin consumed silently is the normal failure mode of a programme.
- **Sanity-check regressions** against two or three known aircraft of the class before trusting a new point.

??? warning "Failure modes"
    **Point design optimised, off-design ignored.** A configuration tuned exactly at cruise can be unacceptable at takeoff, at alternate payload, or at hot-and-high conditions. The constraint diagram exists to prevent this and is often drawn after the configuration is already chosen.

    **Historical regression extrapolated.** Empty-weight fits are valid inside the class and era they were built from. Applied to a novel configuration they extrapolate with no warning, and the resulting \(W_0\) can be wrong by tens of percent — which then propagates through the entire sizing.

    **Sizing loop not converged.** Treating the first iteration as the answer. The loop can take several passes, and a design near non-closure converges slowly — which is itself the signal that the requirements may be infeasible.

    **Weight growth underestimated.** Quoting the mass of an added system rather than its installed, snowballed cost. A 50 kg addition on a transport is a 150–400 kg aircraft, and it is the second number that matters.

    **Single-discipline optimisation.** Minimum structural weight, minimum drag and minimum fuel burn give three different aircraft. Coupled optimisation, or at least coordinated trades, is the only way to avoid a locally optimal and globally poor design.

    **Requirements taken as fixed when one is unaffordable.** If a single requirement drives the design point far into an expensive corner, the right engineering answer is often to question it. Constraint diagrams make the cost of each requirement visible, which is their most underused function.

    **Technology factors used to close a design.** Applying an optimistic structural-weight factor to make an infeasible design close, rather than reporting that it does not.

    <!-- Add your own here. -->

## Worked example

Weight growth, and why a small addition is never small:

```python
# Empty-weight fraction We/W0 and fuel fraction Wf/W0 for a mid-size transport
we, wf = 0.52, 0.28
fixed = 20_000.0                          # payload + crew, kg

W0 = fixed / (1 - we - wf)
growth = 1.0 / (1 - (we + wf))
print(f"empty fraction {we}, fuel fraction {wf}")
print(f"takeoff weight            : {W0:,.0f} kg")
print(f"weight growth factor      : {growth:.1f}x\n")

for add in (50, 200, 500):
    print(f"  add {add:4d} kg of equipment -> aircraft grows {add*growth:,.0f} kg")

print(f"\n{'empty fraction':>16}{'growth factor':>16}{'W0 (kg)':>12}")
for we_i in (0.48, 0.52, 0.56, 0.62, 0.68):
    denom = 1 - we_i - wf
    if denom <= 0:
        print(f"{we_i:16.2f}{'does not close':>16}{'-':>12}")
    else:
        print(f"{we_i:16.2f}{1/denom:16.1f}{fixed/denom:12,.0f}")
```

```
empty fraction 0.52, fuel fraction 0.28
takeoff weight            : 100,000 kg
weight growth factor      : 5.0x

  add   50 kg of equipment -> aircraft grows 250 kg
  add  200 kg of equipment -> aircraft grows 1,000 kg
  add  500 kg of equipment -> aircraft grows 2,500 kg

  empty fraction   growth factor     W0 (kg)
            0.48             4.2      83,333
            0.52             5.0     100,000
            0.56             6.3     125,000
            0.62            10.0     200,000
            0.68            25.0     500,000
```

Fifty kilograms of equipment costs 250 kg of aeroplane. And the lower table is the more important one: as the empty-weight fraction rises the growth factor explodes hyperbolically, and past \(w_e + w_f = 1\) the design simply does not close. Designs near that boundary are fragile — a small adverse surprise in structural weight produces a very large increase in aircraft size, or no aircraft at all.

## Connections

- [Flight mechanics](flight-mechanics.md) — the performance equations the constraints come from.
- [Aerodynamics](aerodynamics.md) — the drag polar every constraint curve uses.
- [Structures and aeroelasticity](structures.md) — where the empty weight comes from.
- [Propulsion](propulsion.md) — the \(T/W\) axis.
- [Foundations › Optimization and adjoints](../foundations/optimization-adjoints.md) — coupled design optimisation.

## Sources

- Raymer, *Aircraft Design: A Conceptual Approach*.
- Torenbeek, *Synthesis of Subsonic Airplane Design*.
- Mattingly, Heiser & Pratt, *Aircraft Engine Design* — constraint analysis done carefully.
- Archive: `Aerospace/AERSP401`; see the [course archive](../resources/course-archive.md).
