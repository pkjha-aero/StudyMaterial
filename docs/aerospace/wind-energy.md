---
title: Wind energy
status: solid
tags: [pillar-1, aerospace, wind-energy, betz, wakes]
updated: 2026-09-26
---

# Wind energy

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - **Betz limit**: no turbine in open flow can extract more than \(16/27 \approx 59.3\%\) of the kinetic energy flux. Modern rotors reach \(C_P \approx 0.45\text{–}0.50\).
    - Power scales as \(V^3\), so the **wind speed distribution matters far more than the mean**. Sizing on mean speed badly underestimates energy yield.
    - BEM is the workhorse, and it **breaks above axial induction \(a \approx 0.4\)** — the turbulent wake state needs an empirical correction.
    - **Wake losses across an array** are typically 10–20% of gross energy, and are the main reason plant output falls short of the sum of its turbines.
    - Capacity factor, not rated power, is the meaningful output metric.

## Key results

**Actuator disk and the Betz limit.** With axial induction \(a = 1 - V_d/V_\infty\):

<div class="result" markdown>

\[
C_P = 4a(1-a)^2,
\qquad
C_T = 4a(1-a)
\]

\[
\frac{dC_P}{da}=0 \ \Rightarrow\ a = \tfrac{1}{3},
\qquad
C_{P,\max} = \frac{16}{27} = 0.593
\]

</div>

The limit exists because extracting all the kinetic energy would require the flow to stop, and stopped flow cannot leave the disk.

**Power:**

\[
P = \tfrac{1}{2}\rho A V^3 C_P(\lambda, \beta),
\qquad
\lambda = \frac{\Omega R}{V_\infty}
\]

Tip speed ratio \(\lambda\) and pitch \(\beta\) define the \(C_P\) surface. Modern three-bladed rotors peak near \(\lambda \approx 7\text{–}8\).

**Control regions:**

| Region | Wind speed | Strategy |
|---|---|---|
| Below cut-in | \(< 3\text{–}4\) m/s | idle |
| II (partial load) | cut-in to rated | hold optimal \(\lambda\), maximise \(C_P\) |
| III (full load) | rated to cut-out | pitch to shed power, hold rated |
| Above cut-out | \(> 25\) m/s | shut down |

**BEM with corrections.** Blade element and momentum balance in each annulus, iterating on \(a\) and \(a'\). Two corrections are mandatory:

- **Prandtl tip/hub loss** \(F\), for finite blade number.
- **Glauert correction** for \(a > a_c \approx 0.4\), where momentum theory fails and the empirical \(C_T\)–\(a\) relation takes over.

**Weibull resource and yield:**

\[
f(V) = \frac{k}{c}\left(\frac{V}{c}\right)^{k-1} e^{-(V/c)^k},
\qquad
\mathrm{AEP} = 8760 \int_0^\infty f(V)\,P(V)\,dV
\]

\(k \approx 2\) (Rayleigh) is typical. Because \(P \propto V^3\) and \(f\) is skewed, most annual energy comes from winds well above the mean.

\[
\mathrm{CF} = \frac{\mathrm{AEP}}{8760\,P_{\text{rated}}}
\]

Onshore 0.25–0.40; offshore 0.40–0.55.

## Mental model

A turbine is a rotor running the [rotorcraft](rotorcraft.md) argument in reverse: instead of adding momentum to the flow it removes it, and the same BEM machinery applies with signs changed. The Betz limit is the statement that you cannot take momentum from air without letting it keep enough to get out of the way.

At plant scale the problem changes character. Individual turbine aerodynamics is close to solved; the open questions are about **wakes** — how fast a wake recovers, how it meanders, and how deep-array turbines behave in permanently disturbed inflow. Plant output is a wake problem, not a rotor problem.

## Numerics / practice

- **Integrate over the distribution, never evaluate at the mean.** Jensen's inequality plus a cubic makes the error large and always in the same direction.
- **Use measured shear and turbulence intensity**; power curves are certified at reference conditions and real sites differ.
- **Wake models**: Jensen/Park for quick array layout, Gaussian deficit models for better accuracy, LES when wake dynamics genuinely matter. Each over-predicts recovery if calibrated on the wrong stability regime.
- **Atmospheric stability changes everything.** Stable nocturnal boundary layers produce long, slowly-recovering wakes; unstable daytime conditions mix them out quickly. A model tuned on neutral conditions will be wrong at night.

??? warning "Failure modes"
    **Evaluating power at the mean wind speed.** Because \(P\propto V^3\), \(\overline{V^3} > \overline{V}^3\) — always. For a Rayleigh distribution \(\overline{V^3} = 1.91\,\overline{V}^3\), so using the mean understates the resource by nearly half.

    **BEM above the critical induction.** Momentum theory predicts \(C_T\) falling for \(a > 0.5\), while reality rises towards \(C_T \approx 1.8\) in the turbulent wake state. Without the Glauert correction, high-thrust operating points are simply wrong, and the solver may not converge at all.

    **Tip loss omitted.** Overpredicts power by several percent, and the error is largest where the blade does most of its work.

    **Betz limit applied to ducted or array configurations.** The \(16/27\) bound is for an unconstrained actuator disk in free flow. Ducted rotors can exceed it relative to *rotor* area (not to total frontal area), and the statement "no turbine can exceed 59.3%" needs that qualification.

    **Wake recovery over-predicted.** Simple models calibrated on neutral conditions recover too fast in stable stratification. Symptom: predicted array losses of 5% against measured 15% — and the shortfall shows up as an unexplained revenue gap.

    **Power curve applied off-reference.** Certified curves assume a reference air density, shear and turbulence intensity. Site air density alone can shift output by 10% at altitude.

    <!-- Add your own here. -->

## Worked example

Why the mean wind speed is the wrong number to design on:

```python
import numpy as np
from math import gamma

rho, R = 1.225, 60.0
A, Cp  = np.pi * R**2, 0.45

for k, Vmean in ((2.0, 8.0),):
    c = Vmean / gamma(1 + 1/k)                    # Weibull scale
    V = np.linspace(0.1, 30, 3000)
    f = (k/c) * (V/c)**(k-1) * np.exp(-(V/c)**k)
    P = 0.5 * rho * A * V**3 * Cp
    P_dist = np.sum(f * P) * (V[1] - V[0]) / 1e6      # np.trapz is gone in NumPy 2
    P_mean = 0.5 * rho * A * Vmean**3 * Cp / 1e6
    print(f"mean wind {Vmean} m/s (Weibull k={k})")
    print(f"  power at mean speed      = {P_mean:.2f} MW")
    print(f"  power over distribution  = {P_dist:.2f} MW")
    print(f"  understated by           = {P_dist/P_mean:.2f}x")
```

```
mean wind 8.0 m/s (Weibull k=2.0)
  power at mean speed      = 1.60 MW
  power over distribution  = 3.05 MW
  understated by           = 1.91x
```

Exactly the factor 1.91 that the Rayleigh distribution predicts — evaluating at the mean loses nearly half the resource.

## Connections

- [Rotorcraft](rotorcraft.md) — the same BEM machinery, flow reversed.
- [Aerodynamics](aerodynamics.md) — blade section behaviour.
- [Meteorology › Boundary layer](../meteorology/index.md) — shear, stability, the inflow itself.
- [Fluids › LES](../fluids/turbulence/les.md) — wake simulation.

## Sources

- Burton et al., *Wind Energy Handbook*.
- Hansen, *Aerodynamics of Wind Turbines*.
- Archive: `Aerospace/AERSP880_WindTurbineSystems`, `Aerospace/AERSP886_WindPowerPlants`.
