---
title: Rotorcraft
status: solid
tags: [pillar-1, aerospace, scaling]
updated: 2026-09-26
---

# Rotorcraft

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Momentum theory gives the **ideal** hover power; figure of merit measures how close a real rotor gets, typically 0.7–0.8.
    - **Induced power dominates in hover, profile and parasite power in forward flight** — which is why the power curve has a minimum at moderate speed, not at zero.
    - Forward flight is fundamentally **asymmetric**: the advancing blade sees \(V_{tip}+V\), the retreating blade \(V_{tip}-V\). Everything hard about rotorcraft follows from this.
    - Speed is limited at both ends: **advancing-blade compressibility** above, **retreating-blade stall** below.
    - Momentum theory **fails in descent**. The vortex ring state is outside its assumptions, and it is a real flight hazard.

## Key results

**Momentum theory in hover**, disk area \(A\), thrust \(T\):

<div class="result" markdown>

\[
v_i = \sqrt{\frac{T}{2\rho A}},
\qquad
P_{\text{ideal}} = T v_i = \frac{T^{3/2}}{\sqrt{2\rho A}},
\qquad
\mathrm{FM} = \frac{P_{\text{ideal}}}{P_{\text{actual}}}
\]

</div>

Power scales as \(T^{3/2}/\sqrt{A}\): **disk loading is the dominant design parameter**. A helicopter (low disk loading) hovers far more efficiently than a jet in VTOL (very high disk loading).

**Blade element momentum theory.** Equate blade-element lift to momentum flux in each annulus, iterating on the inflow. For a rotor with solidity \(\sigma = Nc/(\pi R)\), the standard non-dimensional results:

\[
C_T = \frac{T}{\rho A (\Omega R)^2},
\qquad
\lambda_i = \sqrt{\frac{C_T}{2}} \quad\text{(uniform inflow, hover)},
\qquad
C_P = \frac{C_T^{3/2}}{\sqrt{2}} + \frac{\sigma C_{d_0}}{8}
\]

The two terms are induced and profile power — the split that organises all rotor performance.

**Forward flight.** Advance ratio \(\mu = V\cos\alpha/(\Omega R)\). At blade azimuth \(\psi\), the local velocity is

\[
U_T = \Omega r + V\sin\psi
\]

so the retreating side (\(\psi = 270°\)) has a **reverse flow region** of radius \(\mu R\) where the blade section sees flow from the trailing edge. Blades flap to equalise lift between the two sides; flapping is what makes forward flight possible at all.

**Power curve:**

\[
P = \underbrace{\kappa T v_i}_{\text{induced}} + \underbrace{\frac{\rho A (\Omega R)^3 \sigma C_{d_0}}{8}(1+4.6\mu^2)}_{\text{profile}} + \underbrace{\tfrac{1}{2}\rho V^3 f}_{\text{parasite}}
\]

Induced power falls with speed, parasite rises as \(V^3\). Minimum power — best endurance — sits at moderate speed; best range is at the tangent from the origin, faster still.

**Autorotation.** With power off, the rotor is driven by upward flow through the disk. An autorotative region near mid-span drives the blade, balancing the drag of the inboard and outboard regions. Stored rotor kinetic energy \(\tfrac{1}{2}I\Omega^2\) is the resource available for the flare.

## Mental model

A hovering rotor is an air pump, and the momentum theory result says that pumping a large mass of air slowly is cheaper than a small mass quickly — the same argument as bypass ratio in [propulsion](propulsion.md). Disk loading *is* the rotorcraft equivalent of bypass ratio.

In forward flight, picture the rotor as a wing whose two halves see wildly different airspeeds and whose blades must therefore change incidence once per revolution. Every rotorcraft complication — flapping hinges, lead-lag, cyclic control, 1/rev vibration — exists to manage that asymmetry.

## Numerics / practice

- **Use a tip-loss factor** (\(B \approx 0.97\), Prandtl correction) in BEMT; without it thrust is overpredicted by several percent.
- **Non-uniform inflow matters.** Uniform inflow is a starting point; real rotors need at least a linear inflow model in forward flight, and a free-wake model for descent or close formation.
- **Induced power factor** \(\kappa \approx 1.15\) accounts for non-uniform inflow, tip loss and swirl. Ideal momentum theory is optimistic without it.
- Compressibility on the advancing tip: keep \(M_{\text{tip,adv}} = (\Omega R + V)/a\) below about 0.9.

??? warning "Failure modes"
    **Momentum theory in descent.** The theory assumes a well-defined streamtube with flow in one direction. In moderate descent the rotor sits in its own wake, the streamtube concept collapses, and momentum theory gives complex or nonsensical inflow. Physically this is the **vortex ring state**: high descent rate, severe vibration, loss of thrust, and worse with more collective. A real and fatal hazard, not merely a modelling gap. The recovery is lateral or forward speed, not power.

    **Uniform inflow in forward flight.** Real inflow is strongly fore-aft asymmetric. Uniform inflow misses the resulting 1/rev flapping and blade loads, and predicts vibration levels far below reality.

    **Reverse flow region ignored.** At \(\mu = 0.4\), the reverse-flow circle covers 40% of the retreating blade radius. Blade-element codes that assume attached forward flow over the whole disk get retreating-side loads badly wrong.

    **Hover figure of merit quoted for a forward-flight design.** FM is a hover metric only. Comparing rotors on FM tells you nothing about cruise efficiency.

    **Tip loss omitted.** Overpredicts thrust by 3–6% — enough to make a marginal design look adequate.

    **Ground resonance treated as an aerodynamic problem.** It is a mechanical instability coupling blade lead-lag with the airframe on its landing gear, and it can destroy an aircraft in seconds on the ground. It depends on damper condition, not on airflow.

    <!-- Add your own here. -->

## Worked example

Why disk loading dominates hover efficiency:

```python
import numpy as np

rho, T = 1.225, 50_000.0                # 5-tonne aircraft
for name, R in (("helicopter", 8.0), ("tiltrotor", 4.0), ("lift fan", 1.5)):
    A  = np.pi * R**2
    DL = T / A
    vi = np.sqrt(T / (2 * rho * A))
    P  = T * vi / 1e3
    print(f"{name:12s} R={R:4.1f} m  disk loading={DL:7.0f} N/m^2  "
          f"vi={vi:5.1f} m/s  ideal power={P:6.0f} kW")
```

```
helicopter   R= 8.0 m  disk loading=    249 N/m^2  vi= 10.1 m/s  ideal power=   504 kW
tiltrotor    R= 4.0 m  disk loading=    995 N/m^2  vi= 20.1 m/s  ideal power=  1007 kW
lift fan     R= 1.5 m  disk loading=   7074 N/m^2  vi= 53.7 m/s  ideal power=  2687 kW
```

The same aircraft weight needs five times the hover power on a small-diameter lift fan. Halving rotor radius doubles ideal power — the \(1/\sqrt{A}\) scaling, and the reason VTOL configurations live or die on disk loading.

## Connections

- [Aerodynamics](aerodynamics.md) — blade section behaviour.
- [Aeroacoustics](aeroacoustics.md) — BVI and why descent is the noisiest condition.
- [Propulsion](propulsion.md) — the same mass-flow argument as bypass ratio.
- [Structures](structures.md) — blade dynamics, ground resonance.
- [Wind energy](wind-energy.md) — BEM again, with the flow going the other way.

## Sources

- Leishman, *Principles of Helicopter Aerodynamics*.
- Johnson, *Rotorcraft Aeromechanics*.
- Archive: `Others/2015RotaryWing`, `Others/LN_Shankar` — rotorcraft aerodynamics.
