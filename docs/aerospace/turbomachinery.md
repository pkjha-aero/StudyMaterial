---
title: Turbomachinery
status: working
tags: [pillar-1, aerospace, boundary-layer, scaling]
updated: 2026-09-28
---

# Turbomachinery

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - **Euler's turbomachinery equation is the whole subject in one line**: work is the change in \(rV_\theta\). Everything else is how you achieve it without the flow separating.
    - **Velocity triangles** are the working notation. Absolute frame for the stator, relative frame for the rotor, and the difference is the blade speed.
    - Compressors fight an **adverse pressure gradient** and turbines a favourable one — which is why a turbine stage does several times the work of a compressor stage, and why compressors need many more.
    - **Surge and rotating stall are different failures.** Surge is a system-level axial oscillation; rotating stall is a cell propagating around the annulus.
    - **Corrected speed and flow** collapse a machine's whole map onto one curve set — and only if you use the right reference conditions.

## Key results

**Euler turbomachinery equation** — from angular momentum, with no loss assumptions:

<div class="result" markdown>

\[
w = U_2 V_{\theta 2} - U_1 V_{\theta 1}
\]

For an axial stage with \(U_1 = U_2 = U\): \(w = U\,\Delta V_\theta\). Work is set by blade speed and the *turning* the blades impose, nothing else.

</div>

**Stage design parameters:**

\[
\phi = \frac{V_x}{U} \ \text{(flow coefficient)},
\qquad
\psi = \frac{\Delta h_0}{U^2} \ \text{(stage loading)},
\qquad
R = \frac{\Delta h_{\text{rotor}}}{\Delta h_{\text{stage}}} \ \text{(reaction)}
\]

\(R = 0.5\) splits the static enthalpy rise evenly between rotor and stator and gives symmetric velocity triangles — the usual axial-compressor choice. \(R = 0\) is an impulse stage, all the turning in the rotor at constant static pressure.

The **Smith chart** plots stage efficiency contours against \(\phi\) and \(\psi\); peak efficiency sits near \(\phi \approx 0.5\text{–}0.7\), \(\psi \approx 0.3\text{–}0.4\). Pushing loading higher buys fewer stages at the cost of efficiency and stall margin.

**Why compressors need more stages.** A compressor blade row diffuses — the flow decelerates against rising pressure, so the boundary layer is always close to separating. **de Haller** limits the relative velocity ratio to \(W_2/W_1 \gtrsim 0.72\), and **diffusion factor** \(DF \lesssim 0.6\). A turbine accelerates the flow, the boundary layer is favourable, and turning of 90°+ is routine. The practical consequence: one turbine stage can drive several compressor stages.

**Compressor instabilities**, distinct and often confused:

| | Rotating stall | Surge |
|---|---|---|
| Nature | local, cells rotating around the annulus | global, axial oscillation of the whole system |
| Frequency | ~20–70% of rotor speed | Helmholtz frequency of the ducting |
| Mass flow | steady in the mean | oscillates, can reverse |
| Damage | blade high-cycle fatigue | violent, can destroy the machine |

Rotating stall often precedes surge, and the surge line on a map is the operating boundary the control system must protect.

**Corrected (referred) parameters** collapse the operating map:

\[
\dot m_{c} = \frac{\dot m \sqrt{\theta}}{\delta},
\qquad
N_{c} = \frac{N}{\sqrt{\theta}},
\qquad
\theta = \frac{T_{0}}{T_{ref}},\ \ \delta = \frac{p_{0}}{p_{ref}}
\]

These follow from dimensional analysis on \(\dot m\sqrt{RT_0}/(D^2 p_0)\) and \(ND/\sqrt{RT_0}\), with \(R\), \(\gamma\) and \(D\) dropped as constant for one machine and one gas. That last clause is exactly where the method breaks.

**Tip clearance** costs roughly 1–2% stage efficiency per 1% of span, and drives a leakage vortex that interacts with the passage flow. It is one of the largest single loss sources and one of the hardest to model.

## Mental model

A blade row is a cascade of aerofoils doing one job: turn the flow. Work follows from the turning via Euler; loss follows from how hard you asked for it.

Compressor and turbine are the same machinery run against and with the pressure gradient, and nearly every asymmetry between them — stage count, turning limits, stall behaviour, cooling — traces to that one difference. It is the [boundary-layer](../fluids/transition.md) story on a rotating blade.

## Numerics / practice

- **Draw the velocity triangles first.** Most stage-design errors are frame errors, and a triangle makes them visible.
- **Check de Haller and diffusion factor** before believing a compressor stage design; they are cheap screens against an unachievable loading.
- **State the reference conditions** with any corrected quantity. Sea-level standard is conventional but not universal.
- **Radial equilibrium** governs spanwise distribution in an axial machine; a purely two-dimensional mean-line design will not close in three dimensions.

??? warning "Failure modes"
    **Surge and rotating stall conflated.** They have different physics, different frequencies and different remedies — bleed and variable geometry for stall margin, volume and control for surge. Diagnosing one as the other sends the fix in the wrong direction.

    **Corrected parameters across different gas or size.** \(\theta\) and \(\delta\) collapse the map for *one* machine on *one* gas. Comparing a rig on air to an engine on combustion products, or scaling across diameter, needs \(\gamma\) and \(R\) carried explicitly. The numbers still plot; they just no longer collapse.

    **Mean-line design taken as three-dimensional.** Mean-line gives work and loading; it says nothing about spanwise distribution, secondary flow or tip leakage. A stage that closes at mid-span can be separated at the hub.

    **de Haller ignored.** Asking for high stage loading is arithmetically easy and aerodynamically impossible. A design that violates \(W_2/W_1 > 0.72\) will separate, and the mean-line calculation will not say so.

    **Tip clearance omitted from a CFD model.** Clearance flow is a first-order loss and changes the whole passage structure. A sealed-tip computation overpredicts efficiency by points and misses the leakage vortex entirely.

    **Off-design ignored.** Machines spend most of their life away from the design point. A stage optimised at one condition can have unacceptable stall margin at part speed, where the front stages stall and the rear stages choke.

    **Total and static conditions mixed.** Efficiency defined total-to-total, total-to-static and static-to-static differ materially, especially for the last turbine stage where exit kinetic energy is or is not counted. State which.

    <!-- Add your own here. -->

## Worked example

Why a turbine drives many compressor stages:

```python
import numpy as np

U = 350.0                      # blade speed, m/s
cp = 1005.0

# Compressor: turning limited by diffusion. Take a realistic dVtheta.
dV_comp = 90.0                 # m/s of turning a compressor stage can manage
dV_turb = 500.0                # a turbine stage accelerates, so far more turning

w_comp = U * dV_comp
w_turb = U * dV_turb
print(f"compressor stage work : {w_comp/1e3:7.1f} kJ/kg   (dT0 = {w_comp/cp:5.1f} K)")
print(f"turbine stage work    : {w_turb/1e3:7.1f} kJ/kg   (dT0 = {w_turb/cp:5.1f} K)")
print(f"stages driven per turbine stage: {w_turb/w_comp:.1f}")

print()
print(f"{'stage loading psi':>18}{'de Haller W2/W1':>18}{'feasible?':>12}")
for psi in (0.25, 0.35, 0.45, 0.60):
    # crude 50%-reaction estimate of the relative velocity ratio
    phi = 0.55
    W1 = np.hypot(phi, 0.5 + psi/2); W2 = np.hypot(phi, 0.5 - psi/2)
    print(f"{psi:18.2f}{W2/W1:18.3f}{'yes' if W2/W1 > 0.72 else 'NO':>12}")
```

```
compressor stage work :    31.5 kJ/kg   (dT0 =  31.3 K)
turbine stage work    :   175.0 kJ/kg   (dT0 = 174.1 K)
stages driven per turbine stage: 5.6

 stage loading psi   de Haller W2/W1   feasible?
              0.25             0.800         yes
              0.35             0.734         yes
              0.45             0.676          NO
              0.60             0.603          NO
```

One turbine stage drives roughly six compressor stages — which is why a high-pressure spool has one or two turbine stages and eight to ten compressor stages.

The de Haller column shows the ceiling. At this flow coefficient the limit falls between
\(\psi = 0.35\) and \(0.45\) — crossing \(W_2/W_1 = 0.72\) at about \(\psi = 0.37\).
Ask for more loading and the stage cannot be built, however attractive the reduced stage
count looks on paper.

That limit is **strongly dependent on flow coefficient**, which is the part worth carrying
away. Repeating the calculation across \(\phi\) gives a maximum loading of 0.30 at
\(\phi = 0.45\), 0.37 at 0.55, 0.46 at 0.65 and 0.57 at 0.75 — so loading and flow
coefficient cannot be chosen independently. That coupling is exactly why the Smith chart
is a two-dimensional map rather than a pair of limits, and why this screen is a screen
rather than a design rule.

## Connections

- [Propulsion](propulsion.md) — the cycle these components realise.
- [Aerodynamics](aerodynamics.md) — cascade aerofoils and loading limits.
- [Fluids › Stability and transition](../fluids/transition.md) — bypass transition is the norm on blades.
- [Thermal › Heat transfer](../thermal/heat-transfer.md) — turbine blade cooling.

## Sources

- Dixon & Hall, *Fluid Mechanics and Thermodynamics of Turbomachinery*.
- Cumpsty, *Compressor Aerodynamics*.
- Archive: `Mechanical/ME422`, `Mechanical/ME404`, `Aerospace/AERSP410`; see the [course archive](../resources/course-archive.md).
