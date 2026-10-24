---
title: Aircraft design
status: working
tags: [pillar-1, aerospace, optimization, scaling]
updated: 2026-10-24
---

# Aircraft design

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Conceptual design is a **convergence problem, not an analysis problem**: weight depends on fuel, fuel depends on weight, and you iterate until it closes.
    - Almost everything reduces to four numbers: \((C_L)_{\max}\), \(L/D\), \(W/S\) and \(T/W\). The **drag polar** \(C_D = C_{D_0} + KC_L^2\) supplies the second and shapes the others.
    - The **constraint diagram** turns every requirement — takeoff, climb, cruise, turn, landing — into a curve in \(T/W\) versus \(W/S\), and the design point is a corner of the feasible region.
    - **Which aerodynamic ratio you maximise depends on the mission**, and it changes what you should spend money on: span for a propeller loiterer, cleanliness for a jet on range.
    - **Weight growth compounds.** Added mass needs more lift, more structure, more fuel, more engine — the snowball factor is typically 3–8× the original addition.
    - Design is **evolutionary**. Sizing uses historical regression, which is why it works and also where it fails: outside the database it extrapolates silently.

## Key results

### The three phases, and which one this page is about

| Phase | What is decided | What the product looks like |
|---|---|---|
| **Conceptual** | Overall shape, size, weight, performance | A layout with *fuzzy* lines — still movable |
| **Preliminary** | Configuration frozen and lofted; wind tunnel and CFD; structures and controls | Precise external geometry; the commit-to-manufacture decision |
| **Detail** | Every rib, spar, fastener; tooling and jigs | Rivet sizes and locations |

Essentially all of design *teaching* — and all of this page — is the conceptual phase. The preliminary phase ends at the point Anderson calls the "bet your company" decision, which is why the conceptual phase is asked to be more right than its crude tools deserve.

### The seven pivot points

Anderson's framing of conceptual design: not a recipe but seven anchors that any route through the problem has to touch.

<div class="result" markdown>

1. **Requirements** → 2. **Weight — first estimate** → 3. **Critical performance parameters**
\(\;(C_L)_{\max},\; L/D,\; W/S,\; T/W\) → 4. **Configuration layout** → 5. **Better weight estimate**
→ 6. **Performance analysis** — does it meet the requirements? *If no, return to 3* →
7. **Optimization** — is it the *best* design?

</div>

Two things in that loop are worth noticing. The iteration returns to **step 3**, not to step 1: the configuration is re-drawn against readjusted performance parameters. And step 7 is a separate question from step 6 — a design that meets the requirements is not thereby the best one, and most of the engineering value is in the gap between them.

The constraint diagram is not itself a pivot point; it is the tool that makes steps 6 and 7 tractable.

### The drag polar

Everything downstream is algebra once you have

\[
C_D = C_{D_0} + K C_L^2, \qquad K = \frac{1}{\pi e\,\mathrm{AR}}
\]

Two numbers. \(C_{D_0}\) is what you buy with cleanliness — wetted area, surface finish, excrescences, interference. \(K\) is what you buy with span. The design question is almost never "how do I reduce drag" but **which of those two coefficients to spend on**, and the mission answers it.

### Which ratio the mission maximises

The useful aerodynamic figure of merit is not always \(L/D\):

| | **Range** | **Endurance** |
|---|---|---|
| **Propeller** | \(\max\, C_L/C_D\) | \(\max\, C_L^{3/2}/C_D\) |
| **Jet** | \(\max\, C_L^{1/2}/C_D\) | \(\max\, C_L/C_D\) |

Each optimum is a fixed split between the two halves of the polar:

| Maximise | Condition | Value at the optimum | Speed |
|---|---|---|---|
| \(C_L/C_D\) | \(C_{D_0} = KC_L^2\) | \(\dfrac{1}{\sqrt{4C_{D_0}K}}\) | \(V_{(L/D)_{\max}}\) |
| \(C_L^{3/2}/C_D\) | \(C_{D_0} = \tfrac{1}{3}KC_L^2\) | \(\dfrac{1}{4}\left(\dfrac{3}{KC_{D_0}^{1/3}}\right)^{3/4}\) | \(0.76\,V_{(L/D)_{\max}}\) |
| \(C_L^{1/2}/C_D\) | \(C_{D_0} = 3KC_L^2\) | \(\dfrac{3}{4}\left(\dfrac{1}{3KC_{D_0}^{3}}\right)^{1/4}\) | \(1.32\,V_{(L/D)_{\max}}\) |

Read the middle column as a drag budget: best \(L/D\) is a 50/50 split between parasite and induced drag, best propeller endurance runs at three times as much induced as parasite, and best jet range at one third. **The induced-to-parasite ratio is a diagnostic** — if a cruise point does not show the split its mission implies, it is not at the optimum it claims.

Note also that each maximum depends *only* on the drag polar, not on weight or altitude. Weight and altitude move the *speed* at which the optimum occurs, not its value.

### The sizing loop

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

### Constraint analysis

Each requirement becomes a curve in the \((W/S,\ T/W)\) plane:

| Requirement | Constraint |
|---|---|
| Takeoff distance | \(T/W \propto (W/S)/(\sigma C_{L,TO} s_{TO})\) — a rising line |
| Rate of climb | \(T/W \ge \frac{\mathrm{RoC}}{V} + \frac{q C_{D_0}}{W/S} + \frac{K}{q}(W/S)\) |
| Cruise speed | \(T/W \ge \frac{q C_{D_0}}{W/S} + \frac{K}{q}(W/S)\) |
| Sustained turn at \(n\) | as cruise, with \(K n^2\) |
| Landing distance | \(W/S \le \frac{\sigma C_{L,\max} s_L}{\text{const}}\) — a vertical line |

The feasible region lies above every thrust curve and left of the landing line. The design point is usually its lowest-leftmost corner: minimum thrust and maximum wing loading that still satisfies everything.

Note what \((C_L)_{\max}\) does here. It appears in both the takeoff and the landing constraint, and it is the only one of the four critical parameters bought with a *mechanism* — flaps, slats — rather than with overall proportions. High-lift devices are how a design escapes the landing line without giving up wing loading, and they are the usual reason a wing is more complicated than it looks.

### Weight growth factor

Adding \(\Delta W\) of equipment forces structure, fuel and engine to grow:

\[
\text{growth factor} = \frac{\partial W_0}{\partial W_{\text{fixed}}}
= \frac{1}{1 - \dfrac{\partial (W_e + W_f)}{\partial W_0}}
\]

For a transport this is typically 3–8. One kilogram of avionics costs several kilograms of aeroplane, and that is why weight control is a programme-level discipline rather than an engineering detail.

**Regression limits.** Empty-weight fractions are fits to aircraft that were built. A blended wing body, an electric aircraft, or a hydrogen tank configuration is outside the database, and the correlation will still return a number.

## Mental model

Conceptual design is a fixed-point iteration on weight, wrapped in a feasibility check on thrust and wing loading. Nothing in it is deep individually — the difficulty is that every quantity depends on every other, so no piece can be settled alone.

That coupling is also why discipline-local optimisation misleads. The lightest wing is not the wing of the lightest aircraft: a thinner wing weighs less and holds less fuel, needing a bigger wing. The constraint diagram and the sizing loop exist to make those couplings explicit rather than discovering them late.

**Design is evolutionary, and that is a technical fact rather than a sentimental one.** The regressions that close the sizing loop are fits to aircraft that were actually built; the configuration you start drawing is a perturbation of one that worked. This is why knowing the lineage of a configuration is part of being able to size it — and why a genuinely novel configuration is hard not because the physics is harder but because the database is empty.

The nineteenth century makes the point by negation. Before the Wrights, the dominant approach was to fit a powerful enough engine to lift the machine off the ground, which runs straight into a circular argument: a more powerful engine is heavier, a heavier machine needs more lift, more lift needs more speed, more speed needs a more powerful engine. That is the sizing loop failing to converge, a century before anyone wrote it down as a loop. It was broken not by better aerodynamics but by engines with a higher power-to-weight ratio — which is exactly why \(T/W\) ended up as one of the four parameters that govern everything.

## Numerics / practice

- **Draw the constraint diagram before choosing anything.** It shows which requirement is actually binding, and that is usually not the one people assume.
- **Know which ratio your mission maximises** before optimising the polar. The 2×2 table above decides whether aspect ratio or cleanliness is the better place to spend weight and cost.
- **Check the induced-to-parasite split** at your cruise point. It should be 1:1, 3:1 or 1:3 depending on the mission; anything else means you are not where you think you are.
- **Converge the sizing loop and report the residual.** An unconverged \(W_0\) invalidates everything downstream.
- **Carry weight margin explicitly** and track it. Margin consumed silently is the normal failure mode of a programme.
- **Sanity-check regressions** against two or three known aircraft of the class before trusting a new point.

??? warning "Failure modes"
    **Point design optimised, off-design ignored.** A configuration tuned exactly at cruise can be unacceptable at takeoff, at alternate payload, or at hot-and-high conditions. The constraint diagram exists to prevent this and is often drawn after the configuration is already chosen.

    **The wrong aerodynamic ratio optimised.** \(L/D\) is the default figure of merit and it is the right one for only two of the four mission cases. Designing a propeller-driven loiterer for best \(L/D\), or a jet transport for best \(L/D\) rather than best \(C_L^{1/2}/C_D\), leaves about 12% on the table — and worse, points the aspect-ratio and cleanliness trades in the wrong direction from the start.

    **The drag polar treated as a constant.** \(C_{D_0}\) and \(K\) are not fixed: they move with Mach number (sharply, through drag divergence), with Reynolds number, with configuration changes, and with trim. A single cruise polar used across the whole flight envelope quietly overstates performance everywhere except the point it was built for.

    **Historical regression extrapolated.** Empty-weight fits are valid inside the class and era they were built from. Applied to a novel configuration they extrapolate with no warning, and the resulting \(W_0\) can be wrong by tens of percent — which then propagates through the entire sizing.

    **Sizing loop not converged.** Treating the first iteration as the answer. The loop can take several passes, and a design near non-closure converges slowly — which is itself the signal that the requirements may be infeasible.

    **Weight growth underestimated.** Quoting the mass of an added system rather than its installed, snowballed cost. A 50 kg addition on a transport is a 150–400 kg aircraft, and it is the second number that matters.

    **Single-discipline optimisation.** Minimum structural weight, minimum drag and minimum fuel burn give three different aircraft. Coupled optimisation, or at least coordinated trades, is the only way to avoid a locally optimal and globally poor design.

    **Requirements taken as fixed when one is unaffordable.** If a single requirement drives the design point far into an expensive corner, the right engineering answer is often to question it. Constraint diagrams make the cost of each requirement visible, which is their most underused function.

    **"Meets the requirements" mistaken for "finished".** Steps 6 and 7 of the pivot-point loop are different questions. A design that satisfies every specification on the first configuration that closes is almost certainly not the best one available, and stopping there is the most common way the optimisation step gets skipped.

    **Technology factors used to close a design.** Applying an optimistic structural-weight factor to make an infeasible design close, rather than reporting that it does not.

    <!-- Add your own here. -->

## Worked example

### What the polar is worth, and what to spend on

Using the Gulfstream IV cruise polar — \(C_{D_0} = 0.015\), \(K = 0.08\) — the three ratios are maximised at three different lift coefficients, and each responds differently to the two levers a designer actually has.

```python
import numpy as np

# Gulfstream IV at 30,000 ft -- the drag polar is the entire aerodynamic input
CD0, K = 0.015, 0.08
W, S, rho = 73_000.0, 950.0, 8.9068e-4          # lb, ft^2, slug/ft^3
CL = np.arange(1e-3, 3.0, 1e-4)

MISSIONS = {   # exponent n in C_L^n/C_D : (label, closed form, what it sizes)
    1.0: ("C_L/C_D = L/D", 1/np.sqrt(4*CD0*K),            "prop range, jet endurance"),
    1.5: ("C_L^3/2 / C_D", .25*(3/(K*CD0**(1/3)))**.75,   "prop endurance"),
    0.5: ("C_L^1/2 / C_D", .75*(1/(3*K*CD0**3))**.25,     "jet range"),
}

V_ref = np.sqrt(2*(W/S)/(rho*np.sqrt(CD0/K)))
print(f"{'ratio':<15}{'grid':>7}{'closed':>8}{'C_L*':>8}{'Di/D0':>7}{'V/V_LD':>8}   sizes")
for n, (name, closed, sizes) in MISSIONS.items():
    i = np.argmax(CL**n / (CD0 + K*CL**2))
    V = np.sqrt(2*(W/S)/(rho*CL[i]))
    print(f"{name:<15}{(CL**n/(CD0+K*CL**2))[i]:7.2f}{closed:8.2f}{CL[i]:8.4f}"
          f"{K*CL[i]**2/CD0:7.2f}{V/V_ref:8.2f}   {sizes}")

# Which half of the polar is worth buying? Exponents of the two design levers.
print("\nsensitivity of each optimum to the two things a designer can buy:")
print(f"{'ratio':<15}{'d ln / d ln AR':>16}{'d ln / d ln (1/CD0)':>22}")
for n, (name, _, _) in MISSIONS.items():
    e = []
    for var in ("K", "CD0"):
        f = lambda k, c: np.max(CL**n / (c + k*CL**2))
        hi = f(K*0.99, CD0) if var == "K" else f(K, CD0*0.99)
        lo = f(K*1.01, CD0) if var == "K" else f(K, CD0*1.01)
        e.append(np.log(hi/lo) / np.log(1.01/0.99))      # d ln(ratio) / d ln(1/var)
    print(f"{name:<15}{e[0]:16.2f}{e[1]:22.2f}")
print("  (AR enters only through K = 1/(pi e AR), so d ln/d ln AR = d ln/d ln(1/K))")
```

```
ratio             grid  closed    C_L*  Di/D0  V/V_LD   sizes
C_L/C_D = L/D    14.43   14.43  0.4330   1.00    1.00   prop range, jet endurance
C_L^3/2 / C_D    10.83   10.83  0.7500   3.00    0.76   prop endurance
C_L^1/2 / C_D    25.00   25.00  0.2500   0.33    1.32   jet range

sensitivity of each optimum to the two things a designer can buy:
ratio            d ln / d ln AR   d ln / d ln (1/CD0)
C_L/C_D = L/D              0.50                  0.50
C_L^3/2 / C_D              0.75                  0.25
C_L^1/2 / C_D              0.25                  0.75
  (AR enters only through K = 1/(pi e AR), so d ln/d ln AR = d ln/d ln(1/K))
```

The grid search and the closed forms agree to the digits shown, and the drag splits come out at exactly 1, 3 and 1/3 — the conditions in the table above, recovered numerically rather than assumed.

The second block is the design content. The exponents are not equal, and they are mirror images:

- A **propeller endurance** aircraft gains as \(\mathrm{AR}^{3/4}\) but only \(C_{D_0}^{-1/4}\). Span is worth three times as much as cleanliness.
- A **jet on range** gains as \(C_{D_0}^{-3/4}\) but only \(\mathrm{AR}^{1/4}\). Cleanliness is worth three times as much as span.
- **Best \(L/D\)** splits the difference evenly, which is why it is a reasonable default and a poor optimum.

This is visible on the ramp. Sailplanes, the U-2 and high-altitude long-endurance UAVs — all loitering on \(C_L^{3/2}/C_D\) — carry aspect ratios of 20 to 40 and accept the wing-structure weight that comes with them. Jet transports, optimising \(C_L^{1/2}/C_D\), settle around 9 or 10 and spend their effort on wetted area, surface finish and interference instead. The configurations differ that much because an exponent of 3/4 and an exponent of 1/4 are being traded against the same structural-weight penalty.

### Weight growth, and why a small addition is never small

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

Fifty kilograms of equipment costs 250 kg of aeroplane. And the lower table is the more important one: as the empty-weight fraction rises the growth factor explodes hyperbolically, and past \(w_e + w_f = 1\) the design simply does not close. Designs near that boundary are fragile — a small adverse surprise in structural weight produces a very large increase in aircraft size, or no aircraft at all. This is the modern, quantified form of the nineteenth-century circular argument: the aeroplane that cannot lift the engine that would lift it.

## Connections

- [Flight mechanics](flight-mechanics.md) — the performance equations the constraints come from, and the range/endurance speeds in flight rather than in sizing.
- [Aerodynamics](aerodynamics.md) — where the drag polar comes from.
- [Structures and aeroelasticity](structures.md) — where the empty weight comes from, and the penalty that caps aspect ratio.
- [Propulsion](propulsion.md) — the \(T/W\) axis.
- [Foundations › Optimization and adjoints](../foundations/optimization-adjoints.md) — coupled design optimisation, which is pivot point 7 done properly.

## Sources

- Anderson, *Aircraft Performance and Design* — performance and design as one subject; the seven pivot points, the drag polar as the organising object, and the aerodynamic ratios in §5.4.
- Raymer, *Aircraft Design: A Conceptual Approach*.
- Torenbeek, *Synthesis of Subsonic Airplane Design*.
- Mattingly, Heiser & Pratt, *Aircraft Engine Design* — constraint analysis done carefully.
- Archive: `Aerospace/AERSP401`; see the [course archive](../resources/course-archive.md).
