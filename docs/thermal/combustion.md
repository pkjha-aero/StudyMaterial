---
title: Combustion
status: working
tags: [pillar-1, thermal, turbulence, numerical-stability, scaling]
updated: 2026-09-28
---

# Combustion

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Combustion is **chemistry coupled to transport**, and almost every difficulty comes from the two having wildly different timescales.
    - **Equivalence ratio \(\phi\) is the first number to establish.** Rich, lean and stoichiometric behave differently in flame speed, temperature and pollutants.
    - **Premixed and non-premixed flames are different physics.** One propagates at a speed the chemistry sets; the other sits where the mixing puts it.
    - **Chemical kinetics is stiff** — timescales spanning \(10^{-9}\) to \(10^{0}\) s in one mechanism. This dominates the numerics.
    - Equilibrium gives the ceiling; kinetics decides whether you get there. Pollutants live entirely in the gap.

## Key results

**Stoichiometry.** For \(\mathrm{C}_x\mathrm{H}_y\) in air:

<div class="result" markdown>

\[
\mathrm{C}_x\mathrm{H}_y + \left(x + \tfrac{y}{4}\right)(\mathrm{O}_2 + 3.76\,\mathrm{N}_2)
\rightarrow x\,\mathrm{CO}_2 + \tfrac{y}{2}\mathrm{H_2O} + 3.76\left(x+\tfrac{y}{4}\right)\mathrm{N}_2
\]

\[
\phi = \frac{(F/A)_{\text{actual}}}{(F/A)_{\text{stoich}}}
\qquad
\phi<1 \text{ lean} \quad \phi=1 \text{ stoichiometric} \quad \phi>1 \text{ rich}
\]

</div>

Peak flame temperature sits slightly **rich** of stoichiometric (around \(\phi \approx 1.05\)) because dissociation absorbs energy and the richer mixture shifts the product mix — a detail that surprises people expecting the peak exactly at \(\phi = 1\).

**Adiabatic flame temperature** from \(h_{\text{reactants}}(T_i) = h_{\text{products}}(T_{ad})\) with formation enthalpies. Constant-pressure values for stoichiometric air: methane ≈ 2226 K, propane ≈ 2267 K, hydrogen ≈ 2483 K. Equilibrium with dissociation gives values several hundred kelvin below the no-dissociation calculation.

**Kinetics.** Arrhenius rate with activation energy \(E_a\):

\[
k = A T^b \exp\left(-\frac{E_a}{R_u T}\right)
\]

The exponential is why combustion is stiff: a 100 K temperature change alters a rate by an order of magnitude. Mechanism sizes run from one global step to GRI-Mech 3.0 (53 species, 325 reactions) to detailed n-heptane mechanisms with thousands of species.

**Premixed flames.** Laminar flame speed \(S_L\) is a property of the mixture:

\[
S_L \sim \sqrt{\alpha \,\omega},
\qquad
\delta_L \sim \frac{\alpha}{S_L}
\]

Methane–air at stoichiometric: \(S_L \approx 0.38\) m/s, \(\delta_L \approx 0.5\) mm. Hydrogen is an order of magnitude faster. The flame structure is a preheat zone followed by a thin reaction zone.

**Non-premixed (diffusion) flames.** No propagation speed — the flame sits at the stoichiometric surface. Conserved-scalar formulation uses mixture fraction \(Z\):

\[
Z = \frac{\phi Y_F/Y_{F,0} - Y_O/Y_{O,0} + 1}{\phi + 1},
\qquad
Z_{st} = \frac{1}{1+\phi_s}
\]

Burke–Schumann is the infinitely-fast-chemistry limit; the flamelet model relaxes it using scalar dissipation rate \(\chi\), with extinction above a critical \(\chi_q\).

**Turbulent combustion regimes.** The Borghi diagram organises them by Damköhler and Karlovitz numbers:

\[
\mathrm{Da} = \frac{\tau_{\text{turb}}}{\tau_{\text{chem}}},
\qquad
\mathrm{Ka} = \frac{\tau_{\text{chem}}}{\tau_{\eta}}
\]

| Regime | Condition | Character |
|---|---|---|
| Wrinkled flamelet | \(u'/S_L < 1\) | laminar flame, gently corrugated |
| Corrugated flamelet | \(\mathrm{Ka}<1\) | flame front intact, strongly wrinkled |
| Thin reaction zone | \(1<\mathrm{Ka}<100\) | preheat zone broadened, reaction zone intact |
| Broken reaction zone | \(\mathrm{Ka}>100\) | turbulence penetrates the reaction zone |

Most gas-turbine and engine combustion sits in the corrugated-to-thin-reaction-zone band, which is why flamelet-based closures remain useful.

**Pollutants.** Thermal NO via the Zeldovich mechanism has an enormous activation energy, so formation is negligible below ~1800 K and severe above it — NOx is exponentially sensitive to peak temperature, which is the entire rationale for lean-premixed and staged combustion. Soot forms in rich, high-temperature regions and burns out if it reaches oxygen while hot enough.

## Mental model

Two clocks: how fast the chemistry wants to go, and how fast transport can supply reactants and remove heat. Their ratio, the Damköhler number, decides nearly everything.

Fast chemistry relative to mixing means the flame is a thin sheet and its position is set by where the mixture is stoichiometric — a mixing problem. Slow chemistry means reactants and products interpenetrate and the reaction is distributed — a kinetics problem. Extinction is what happens when the clocks cross.

## Numerics / practice

- **Use a reduced mechanism matched to the question.** Global one-step for heat release and gross flow; skeletal for ignition delay; detailed only for pollutants or where you will validate against speciation.
- **Integrate chemistry implicitly** or with a dedicated stiff solver (CVODE), usually operator-split from transport. Explicit integration of detailed kinetics is unaffordable.
- **Check the flame is resolved.** A premixed flame needs several cells across \(\delta_L \approx 0.5\) mm; at 1 mm grid spacing you are not resolving a methane flame, you are resolving your scheme.
- **Cantera** for zero- and one-dimensional problems — equilibrium, flame speed, ignition delay, flamelet libraries — before committing to a CFD run.

??? warning "Failure modes"
    **Equilibrium used where kinetics governs.** Equilibrium gives the final state given infinite time. Ignition delay, flame speed, extinction, CO burnout and every pollutant depend on rates, not equilibrium. A model that equilibrates instantly predicts zero CO and plausible-looking NO for the wrong reason.

    **Stiff chemistry integrated explicitly.** Timescales spanning nine orders of magnitude. Symptom: negative species mass fractions, or a timestep collapsing to \(10^{-12}\) s. Operator-split with an implicit stiff solver.

    **Unresolved flame front.** With \(\delta_L \approx 0.5\) mm and 1 mm cells, the computed flame speed is set by numerical diffusion rather than chemistry — and it will look like a converged, stable answer. Either resolve, or use a model (thickened flame, flame-surface density, progress-variable) that does not require resolution.

    **One-step mechanism outside its calibration.** A global step tuned to reproduce flame speed at \(\phi=1\) gets the rich and lean limits, extinction and ignition delay wrong. It is a heat-release model, not a chemistry model.

    **NOx predicted from a mean temperature.** Thermal NO is exponential in \(T\), so \(\overline{\exp(-E/RT)} \ne \exp(-E/R\overline{T})\) — by orders of magnitude. Mean-field NOx predictions without a PDF or subgrid model are systematically low.

    **Adiabatic flame temperature quoted without dissociation.** The no-dissociation value overstates peak temperature by several hundred kelvin, which then feeds an exponential NOx model. Two compounding errors in the same direction.

    **Lewis number assumed unity.** Fine for heavy hydrocarbons, wrong for hydrogen (\(\mathrm{Le}\approx0.3\)), where preferential diffusion drives thermodiffusive instability and cellular flames. Any hydrogen or hydrogen-blend calculation with unity Lewis number misses the mechanism that matters.

    <!-- Add your own here — this is close to your experimental work. -->

## Worked example

Why thermal NOx is a temperature problem and nothing else:

```python
import numpy as np

# Zeldovich initiation N2 + O -> NO + N dominates; Ea ~ 319 kJ/mol
Ea, Ru = 319e3, 8.314

def rel_rate(T, Tref=1800.0):
    return np.exp(-Ea/(Ru*T)) / np.exp(-Ea/(Ru*Tref))

print(f"{'T (K)':>7}{'rate relative to 1800 K':>26}")
for T in (1600, 1700, 1800, 1900, 2000, 2200):
    print(f"{T:7d}{rel_rate(T):26.2f}")

print()
Tm, dT = 1900.0, 150.0            # mean temperature with +/- fluctuation
mean_of_rate = 0.5*(rel_rate(Tm-dT) + rel_rate(Tm+dT))
rate_of_mean = rel_rate(Tm)
print(f"rate at the mean temperature      : {rate_of_mean:.2f}")
print(f"mean of the rate over +/-{dT:.0f} K    : {mean_of_rate:.2f}")
print(f"underprediction using mean T      : {mean_of_rate/rate_of_mean:.1f}x")
```

```
  T (K)   rate relative to 1800 K
   1600                      0.07
   1700                      0.29
   1800                      1.00
   1900                      3.07
   2000                      8.43
   2200                     48.21

rate at the mean temperature      : 3.07
mean of the rate over +/-150 K    : 7.00
underprediction using mean T      : 2.3x
```

A 400 K rise multiplies the rate by 48. And even a modest ±150 K fluctuation about a fixed mean produces 2.3× the NO of the mean-temperature calculation — because the exponential weights the hot excursions far more than the cold ones. That gap is the whole reason turbulent NOx needs a subgrid distribution rather than a mean.

## Connections

- [Thermodynamics](thermodynamics.md) — flame temperature and equilibrium.
- [Heat transfer](heat-transfer.md) — radiation from hot products, flame–wall quenching.
- [Fluids › Turbulence](../fluids/turbulence/index.md) — the transport half of the coupling.
- [Aerospace › Propulsion](../aerospace/propulsion.md) — where the heat release is used.
- [Foundations › Numerical methods](../foundations/numerical-methods.md) — stiffness and operator splitting.

## Sources

- Turns, *An Introduction to Combustion*.
- Poinsot & Veynante, *Theoretical and Numerical Combustion*.
- Peters, *Turbulent Combustion*.
- Archive: `Mechanical/ME430`, `Mechanical/ME532_Shashank`, `Mechanical/ME537_Shashank`; see the [course archive](../resources/course-archive.md).
