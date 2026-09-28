---
title: Heat transfer
status: working
tags: [pillar-1, thermal, radiation, boundary-layer, scaling]
updated: 2026-09-28
---

# Heat transfer

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Three mechanisms, three different mathematical characters: conduction is **parabolic and local**, convection is **advective and boundary-layer controlled**, radiation is **integral and non-local**.
    - **Dimensionless groups decide everything.** Biot says whether an object has an internal gradient; Nusselt is the answer a convection correlation gives you; Fourier is dimensionless time.
    - **Biot > 0.1 kills the lumped assumption**, and this is the single most common modelling error in transient heat transfer.
    - Radiation scales as \(T^4\), so it is negligible at room temperature and dominant above roughly 700 K — the crossover is abrupt.
    - Correlations are fits with a stated range. Outside it they return a number and no warning.

## Key results

**The three mechanisms:**

<div class="result" markdown>

\[
\text{conduction:}\quad \mathbf{q} = -k\nabla T,
\qquad
\rho c_p \frac{\partial T}{\partial t} = \nabla\cdot(k\nabla T) + \dot{q}
\]

\[
\text{convection:}\quad q'' = h(T_s - T_\infty),
\qquad
\mathrm{Nu} = \frac{hL}{k} = f(\mathrm{Re}, \mathrm{Pr})
\]

\[
\text{radiation:}\quad q'' = \varepsilon\sigma\left(T_s^4 - T_{sur}^4\right),
\qquad \sigma = 5.670\times10^{-8}\ \mathrm{W/m^2K^4}
\]

</div>

**The groups that decide the model:**

| Group | Definition | Says |
|---|---|---|
| Biot | \(hL_c/k_s\) | internal vs surface resistance — **lumped valid if \(<0.1\)** |
| Fourier | \(\alpha t/L_c^2\) | dimensionless time for diffusion |
| Nusselt | \(hL/k_f\) | convective enhancement over pure conduction |
| Prandtl | \(\nu/\alpha\) | relative thickness of momentum and thermal layers |
| Rayleigh | \(g\beta\Delta T L^3/(\nu\alpha)\) | natural convection strength; transition near \(10^9\) |
| Péclet | \(\mathrm{Re}\,\mathrm{Pr}\) | advection vs diffusion |

Note Biot uses the **solid** conductivity and Nusselt the **fluid** conductivity — the same \(hL/k\) shape with different \(k\), which is a standard source of confusion.

**Boundary-layer relation.** For \(\mathrm{Pr} > 1\) the thermal layer sits inside the momentum layer:

\[
\frac{\delta}{\delta_t} \approx \mathrm{Pr}^{1/3}
\]

which is why oils (\(\mathrm{Pr}\sim10^3\)) have very thin thermal layers and liquid metals (\(\mathrm{Pr}\sim10^{-2}\)) the reverse.

**Correlations worth remembering, with their ranges:**

| Situation | Correlation | Range |
|---|---|---|
| Flat plate, laminar | \(\mathrm{Nu}_x = 0.332\,\mathrm{Re}_x^{1/2}\mathrm{Pr}^{1/3}\) | \(\mathrm{Pr}\gtrsim0.6\) |
| Flat plate, turbulent | \(\mathrm{Nu}_x = 0.0296\,\mathrm{Re}_x^{4/5}\mathrm{Pr}^{1/3}\) | \(\mathrm{Re}<10^7\) |
| Pipe, turbulent (Dittus–Boelter) | \(\mathrm{Nu} = 0.023\,\mathrm{Re}^{4/5}\mathrm{Pr}^{n}\) | \(\mathrm{Re}>10^4\), \(L/D>10\) |
| Cylinder in crossflow | Churchill–Bernstein | wide |

\(n = 0.4\) heating, \(0.3\) cooling. Dittus–Boelter is quoted everywhere and is accurate to only about ±25% — a fact usually omitted.

**Transient conduction.** With \(\mathrm{Bi}<0.1\), lumped capacitance:

\[
\frac{T - T_\infty}{T_i - T_\infty} = \exp\left(-\frac{hA}{\rho V c_p}t\right) = \exp\left(-\mathrm{Bi}\cdot\mathrm{Fo}\right)
\]

Above that, the internal gradient matters and you need the series solution, a chart, or a numerical solve.

**Radiation between surfaces** needs view factors, with \(\sum_j F_{ij} = 1\) and reciprocity \(A_iF_{ij} = A_jF_{ji}\). For participating media — combustion gases, furnaces — the [radiative transfer equation](../astrophysics/radiative-transfer.md) applies, with the same optical-depth regimes.

## Mental model

Ask which resistance dominates, then model that one carefully and the rest crudely. A thermal circuit in series — conduction through a wall, convection off it, radiation from it — is limited by the largest resistance, and refining the small ones changes nothing.

That framing also explains the Biot number: it is the ratio of internal conduction resistance to surface convection resistance. Small Biot means the surface is the bottleneck, so the interior is nearly isothermal and one temperature describes the object.

## Numerics / practice

- **Evaluate properties at the film temperature** \((T_s+T_\infty)/2\) for external flow, bulk mean for internal. Correlations are fitted that way, and ignoring it is a several-percent error.
- **Check the correlation's stated range** every time. `Re`, `Pr`, `L/D` and orientation all have limits.
- **Linearise radiation only when \(\Delta T\) is small**: \(h_r = 4\varepsilon\sigma T_m^3\) is fine over tens of kelvin and badly wrong over hundreds.
- **Include contact resistance** at any real interface; it often exceeds the conduction resistance of the parts it joins.

??? warning "Failure modes"
    **Lumped capacitance above Bi = 0.1.** The object is treated as isothermal when it has a real internal gradient, so the surface temperature is underpredicted and the centre overpredicted. Symptom: a transient model that matches early time and diverges later. Checking Biot costs one line and is skipped constantly.

    **Correlation used outside its range.** Dittus–Boelter at \(L/D = 3\), or a flat-plate correlation on a curved surface. The formula returns a number; nothing indicates it is extrapolating. Always state the range alongside the result.

    **Biot and Nusselt confused.** Both are \(hL/k\); Biot uses the solid's \(k\), Nusselt the fluid's. Mixing them can be off by two orders of magnitude for a metal in air, and the number still looks plausible.

    **Radiation neglected at high temperature.** At 300 K radiation is a small correction; at 1000 K it dominates. Because \(T^4\) grows so fast, a model calibrated at moderate temperature fails abruptly rather than gradually.

    **Contact resistance ignored.** Two bolted plates do not conduct like one. Interface resistance is often the dominant term in an electronics or engine thermal path, and it depends on pressure and surface finish, not just materials.

    **Constant properties across a large \(\Delta T\).** Viscosity and conductivity vary strongly; correlations with a property-ratio correction exist for exactly this and are usually dropped.

    **Natural and forced convection treated as exclusive.** When \(\mathrm{Gr}/\mathrm{Re}^2 \sim 1\) both matter and the combined case can be *lower* than either alone in opposing flow. Check the ratio rather than assuming.

    <!-- Add your own here. -->

## Worked example

Where the lumped assumption stops being allowed:

```python
import numpy as np

h = 50.0                      # W/m^2K, moderate forced convection in air
cases = [("copper",   401.0), ("steel", 45.0), ("glass", 1.4), ("plastic", 0.2)]
print(f"{'material':10s}{'k (W/mK)':>10}{'Bi @ L=10mm':>14}{'lumped ok?':>12}{'max L for Bi=0.1':>19}")
for name, k in cases:
    L = 0.010
    Bi = h * L / k
    L_max = 0.1 * k / h
    print(f"{name:10s}{k:10.1f}{Bi:14.4f}{'yes' if Bi < 0.1 else 'NO':>12}{1000*L_max:16.1f} mm")
```

```
material    k (W/mK)   Bi @ L=10mm  lumped ok?   max L for Bi=0.1
copper         401.0        0.0012         yes           802.0 mm
steel           45.0        0.0111         yes            90.0 mm
glass            1.4        0.3571          NO             2.8 mm
plastic          0.2        2.5000          NO             0.4 mm
```

A 10 mm copper block is lumped-valid up to 800 mm; a 10 mm plastic block is not lumped-valid past 0.4 mm. The same geometry and the same convection give answers three orders of magnitude apart — which is why the check is on the material, not the size.

## Connections

- [Thermodynamics](thermodynamics.md) — the energy accounting this serves.
- [Combustion](combustion.md) — heat release and flame–wall interaction.
- [Astrophysics › Radiative transfer](../astrophysics/radiative-transfer.md) — the same transfer equation, participating media.
- [Fluids › Turbulence](../fluids/turbulence/index.md) — the analogy between momentum and heat transport.

## Sources

- Incropera & DeWitt, *Fundamentals of Heat and Mass Transfer*.
- Modest, *Radiative Heat Transfer* — the reference for participating media.
- Archive: `Mechanical/ME410`, `Mechanical/ME514`, `Mechanical/ME523`; see the [course archive](../resources/course-archive.md).
