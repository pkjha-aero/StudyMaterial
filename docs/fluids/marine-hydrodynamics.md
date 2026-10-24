---
title: Marine hydrodynamics
status: working
tags: [pillar-1, fluids, scaling, validation]
updated: 2026-10-24
---

# Marine hydrodynamics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - A surface ship carries a **free surface**, so gravity waves matter and **Froude number** joins Reynolds number as a governing parameter.
    - You cannot match both in a model test. Froude scaling fixes the speed, Reynolds then falls by \(\lambda^{3/2}\), and the whole discipline is built around correcting for that.
    - **Froude's hypothesis** splits resistance into a friction part that scales with Reynolds and a residuary part that scales with Froude. It is an assumption, and it is how every towing-tank result reaches full scale.
    - **Cavitation** adds a third parameter and a hard constraint: vapour pressure is a floor the pressure field cannot go below without consequences.
    - **Seakeeping** is a linear-systems problem — the ship is a filter driven by a wave spectrum — until it isn't.

## Key results

### The parameters

| Number | Ratio | Governs |
|---|---|---|
| **Froude** \(Fr = V/\sqrt{gL}\) | inertia / gravity | Wave-making, the wave pattern, hull speed |
| **Reynolds** \(Re = VL/\nu\) | inertia / viscosity | Boundary layer, friction, separation |
| **Cavitation** \(\sigma = (p-p_v)/\tfrac12\rho V^2\) | margin above vapour pressure | Cavitation inception on propellers and appendages |
| **Keulegan–Carpenter** | orbital excursion / diameter | Whether a cylinder sheds vortices in waves |

### Resistance, and Froude's hypothesis

Total resistance is conventionally split

<div class="result" markdown>

\[
C_T = \underbrace{(1+k)\,C_F(Re)}_{\text{viscous, scales with } Re} \;+\; \underbrace{C_W(Fr)}_{\text{wave-making, scales with } Fr}
\]

</div>

with \(C_F\) from the **ITTC-57 correlation line** \(C_F = 0.075/(\log_{10}Re - 2)^2\) and \(k\) a form factor for the hull's three-dimensionality. Froude's hypothesis is the assumption that the second term depends only on \(Fr\), so it transfers from model to ship unchanged.

That assumption is doing enormous work, and the worked example quantifies how much.

**Wave-making** itself is the distinctive physics. A moving hull generates the Kelvin wave system — transverse and divergent waves inside a wedge of half-angle \(19.47°\), independent of speed. Resistance rises in humps and hollows as the bow and stern wave systems reinforce or cancel, with the prominent hump near \(Fr \approx 0.4\) where the wavelength matches the hull length. "Hull speed" is this effect, not a physical barrier.

### Cavitation

When local pressure falls to vapour pressure the liquid boils. On a propeller this is routine at the blade tips and the question is how much, and what kind:

| Type | Where | Consequence |
|---|---|---|
| **Sheet** | Suction side, attached | Thrust breakdown if extensive |
| **Tip vortex** | Core of the tip vortex | Usually the first to appear; **noise** |
| **Bubble** | Mid-chord, low-pressure region | Erosion |
| **Cloud / collapse** | Shedding sheet cavity | **Erosion and vibration** — the damaging one |

Collapse near a surface is violent: a microjet directed at the wall, locally enormous pressures, and material removal from metal. Design responses are skew, chord and section changes to spread loading, and accepting lower efficiency to stay inside the cavitation bucket.

### Seakeeping and manoeuvring

**Seakeeping** treats the ship as a linear system driven by a random sea. The transfer function from wave amplitude to motion is the **response amplitude operator**; combined with a wave spectrum (Pierson–Moskowitz, JONSWAP) it gives motion statistics directly. Resonance in roll is the dangerous case because roll damping is small and largely viscous — so a linear potential-flow calculation under-predicts damping and over-predicts roll, and empirical damping is added.

**Manoeuvring** uses the [6-DOF rigid-body equations](fsi-6dof.md) with hydrodynamic forces as a polynomial model in the velocities and rates, fitted from captive-model tests or CFD. The **added-mass tensor** is central and strongly off-diagonal for a slender body: sway couples to yaw and heave to pitch, and those cross terms are what produce the turn.

For a submerged body the free surface disappears, Froude scaling relaxes, and the problem becomes closer to aerodynamics — with added mass, control-surface effectiveness and crossflow separation on the hull dominating.

## Mental model

Everything awkward about surface-ship hydrodynamics comes from the free surface. It introduces a second governing parameter that cannot be matched simultaneously with the first, so every experiment is an extrapolation; it introduces waves, which carry energy away and so appear as resistance; and it introduces a boundary whose position is part of the solution.

Remove it — a submarine deep enough that the surface does not matter — and the problem collapses into something an aerodynamicist recognises immediately: a body in an unbounded fluid, with added mass and viscous separation, and only one governing parameter to match.

## Numerics / practice

- **Report \(Fr\) and \(Re\) together**, and the scale factor. A towing-tank result without them cannot be extrapolated or compared.
- **Say which friction line and which form factor** were used. ITTC-57 is a correlation line, not a friction law, and results depend on the choice.
- **For free-surface CFD, resolve the wave.** Roughly 20 cells per wavelength and 10 across the wave height, with the interface scheme (VOF or level set) compressive enough not to smear it.
- **Watch the air-side time step.** In a VOF simulation the light phase can set the CFL limit and dominate the cost for no physical benefit.
- **Check wave reflection from the boundaries.** Numerical beaches or damping zones are necessary, and a reflected wave returning to the hull quietly corrupts the resistance.
- **Treat roll damping as empirical.** Potential flow will not give it.

??? warning "Failure modes"
    **Expecting to match Froude and Reynolds together.** They scale oppositely with model size and cannot both be satisfied. Every towing-tank result is a Froude-scaled measurement with a Reynolds correction applied, and the correction is not small.

    **Froude's hypothesis taken as a law.** The split into friction and residuary resistance is an assumption, and the form factor is fitted. For unconventional hulls it is less reliable than the tidy decomposition suggests, which is why full-scale trials still surprise people.

    **Model-scale transition unaccounted for.** A model at \(Re \sim 10^7\) may be partly laminar where the ship is fully turbulent. Turbulence stimulators — studs, trip wires, sand strips — exist for this, and their own drag then needs subtracting.

    **Cavitation number not matched in a propeller test.** Froude and cavitation scaling conflict too. A depressurised tunnel exists specifically to set \(\sigma\) independently, and a result from an atmospheric tunnel says nothing about inception.

    **Potential-flow roll prediction believed.** Roll damping is dominated by viscous and bilge-keel effects that a potential code does not contain. Predicted roll at resonance can be several times reality — in the unsafe direction, since the prediction is larger.

    **Linear seakeeping applied in a severe sea.** RAOs assume small motions and linear superposition. Slamming, green water and parametric roll are all nonlinear and all occur in exactly the conditions the analysis is wanted for.

    **Free-surface grid too coarse for the wave.** Numerical damping removes the wave system, wave resistance vanishes, and the computed total resistance looks plausible because the friction part is still roughly right.

    **Shallow water and blockage ignored.** Both resistance and squat change sharply near the bottom or in a channel, and towing-tank blockage corrections are not optional at larger scales.

    <!-- Add your own here. -->

## Worked example

The scaling conflict, and how much of a towing-tank result survives the extrapolation:

```python
import numpy as np

# A ship model in a towing tank cannot match Froude and Reynolds at the same time.
# Froude scaling (waves) fixes the speed:  V_m = V_s / sqrt(lam).
# Reynolds then follows:  Re_m/Re_s = (L_m V_m)/(L_s V_s) = lam^(-3/2).
L_s, V_s, nu = 150.0, 10.0, 1.19e-6          # ship length m, speed m/s, kinematic visc
print(f"full scale: L = {L_s:.0f} m, V = {V_s:.1f} m/s, "
      f"Fr = {V_s/np.sqrt(9.81*L_s):.3f}, Re = {L_s*V_s/nu:.3e}")
print(f"\n{'scale lam':>10}{'L_m, m':>9}{'V_m, m/s':>10}{'Re_m':>11}{'Re_m/Re_s':>12}")
for lam in (10, 25, 50, 100):
    Lm, Vm = L_s/lam, V_s/np.sqrt(lam)
    print(f"{lam:10d}{Lm:9.2f}{Vm:10.2f}{Lm*Vm/nu:11.2e}{lam**-1.5:12.5f}")

# ITTC-57 model-ship correlation line: Cf = 0.075 / (log10(Re) - 2)^2
Cf = lambda Re: 0.075/(np.log10(Re) - 2)**2
print(f"\nfriction coefficient from ITTC-57, and the size of the correction:")
print(f"{'scale lam':>10}{'Cf model':>11}{'Cf ship':>10}{'Cf_m/Cf_s':>12}")
for lam in (10, 25, 50, 100):
    Lm, Vm = L_s/lam, V_s/np.sqrt(lam)
    print(f"{lam:10d}{Cf(Lm*Vm/nu):11.5f}{Cf(L_s*V_s/nu):10.5f}"
          f"{Cf(Lm*Vm/nu)/Cf(L_s*V_s/nu):12.3f}")

# Froude's hypothesis: Ct = Cf(Re) + Cr(Fr). Only Cr is assumed scale-independent.
lam = 25
Lm, Vm = L_s/lam, V_s/np.sqrt(lam)
Ct_m = 0.0065                                  # measured total in the tank (illustrative)
Cr   = Ct_m - Cf(Lm*Vm/nu)                     # residuary, carried across unchanged
Ct_s = Cf(L_s*V_s/nu) + Cr
print(f"\nextrapolating a measured model Ct = {Ct_m:.5f} at lam = {lam}:")
print(f"   model friction Cf_m   = {Cf(Lm*Vm/nu):.5f}   ({100*Cf(Lm*Vm/nu)/Ct_m:.0f}% of measured)")
print(f"   residuary  Cr         = {Cr:.5f}   (assumed scale-independent -- the hypothesis)")
print(f"   ship friction Cf_s    = {Cf(L_s*V_s/nu):.5f}")
print(f"   predicted ship Ct_s   = {Ct_s:.5f}")
print(f"\nmost of what was MEASURED is subtracted off and replaced by a correlation line:")
print(f"   {100*Cf(Lm*Vm/nu)/Ct_m:.0f}% of the model result is removed, "
      f"{100*Cf(L_s*V_s/nu)/Ct_s:.0f}% of the ship prediction is put back from a formula.")
```

```
full scale: L = 150 m, V = 10.0 m/s, Fr = 0.261, Re = 1.261e+09

 scale lam   L_m, m  V_m, m/s       Re_m   Re_m/Re_s
        10    15.00      3.16   3.99e+07     0.03162
        25     6.00      2.00   1.01e+07     0.00800
        50     3.00      1.41   3.57e+06     0.00283
       100     1.50      1.00   1.26e+06     0.00100

friction coefficient from ITTC-57, and the size of the correction:
 scale lam   Cf model   Cf ship   Cf_m/Cf_s
        10    0.00239   0.00149       1.607
        25    0.00300   0.00149       2.014
        50    0.00362   0.00149       2.433
       100    0.00446   0.00149       2.998

extrapolating a measured model Ct = 0.00650 at lam = 25:
   model friction Cf_m   = 0.00300   (46% of measured)
   residuary  Cr         = 0.00350   (assumed scale-independent -- the hypothesis)
   ship friction Cf_s    = 0.00149
   predicted ship Ct_s   = 0.00499

most of what was MEASURED is subtracted off and replaced by a correlation line:
   46% of the model result is removed, 30% of the ship prediction is put back from a formula.
```

The first table is the conflict. Fixing Froude number — which you must, or the wave pattern is wrong — forces \(V_m = V_s/\sqrt{\lambda}\), and Reynolds number then falls as \(\lambda^{-3/2}\). At a routine scale factor of 25 the model runs at **0.8% of the ship's Reynolds number**, two orders of magnitude down. There is no model size that fixes this: making the model bigger helps as \(\lambda^{-3/2}\) and towing tanks are finite.

The second table shows what that costs. The model's friction coefficient is **twice** the ship's at \(\lambda = 25\) and three times at \(\lambda = 100\), purely because it is at a lower Reynolds number.

The third block is the honest summary of the method. Of the total resistance measured in the tank, **46% is friction that does not scale** and must be subtracted using a correlation line. What remains — the residuary coefficient — is carried to full scale unchanged on Froude's hypothesis, and a *different* friction coefficient is added back, supplying **30% of the predicted ship resistance**. Nearly a third of the final answer comes from a formula rather than from the measurement.

That is not a criticism of the method, which has been calibrated against full-scale trials for a century and works. It is the reason the ITTC correlation line, the form factor and the correlation allowance are argued about so carefully: they are not corrections at the margin, they are a large fraction of the answer.

## Connections

- [Fluid–structure and 6-DOF coupling](fsi-6dof.md) — added mass, manoeuvring, and why water couples so badly.
- [Incompressible flow](incompressible.md) — the solver underneath.
- [Turbulence › RANS](turbulence/rans.md) — what resolves the hull boundary layer.
- [Aerospace › Propellers](../aerospace/propellers.md) — the same blade-element machinery, plus a vapour-pressure floor.
- [Aerospace › Experimental methods](../aerospace/experimental-methods.md) — scaling, tunnel corrections and the general similitude argument.
- [Foundations › V&V](../foundations/verification-validation.md) — validating against trials when the experiment is itself an extrapolation.

## Sources

- Newman, *Marine Hydrodynamics* — the standard reference.
- Faltinsen, *Sea Loads on Ships and Offshore Structures* — seakeeping and wave loads.
- Fossen, *Handbook of Marine Craft Hydrodynamics and Motion Control* — manoeuvring and 6-DOF models.
- Carlton, *Marine Propellers and Propulsion* — cavitation types, inception and erosion.
- ITTC Recommended Procedures, in particular the 1957 model–ship correlation line and the resistance extrapolation procedure.
