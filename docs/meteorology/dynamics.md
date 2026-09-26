---
title: Atmospheric dynamics
status: working
tags: [pillar-1, meteorology, scaling]
updated: 2026-09-26
---

# Atmospheric dynamics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - **Rossby number decides the regime.** \(\mathrm{Ro}\ll1\) is rotation-dominated and balanced; \(\mathrm{Ro}\sim1\) is not, and balance arguments stop applying.
    - **Geostrophic balance** — pressure gradient against Coriolis — explains why synoptic winds blow along isobars rather than across them.
    - **Thermal wind** links vertical wind shear to horizontal temperature gradient. It is why the jet stream sits above the strongest baroclinic zone.
    - **Potential vorticity is the master variable**: conserved following the flow in adiabatic, frictionless conditions, and it determines the balanced flow via inversion.
    - Rossby waves exist because of \(\beta\), and they propagate **westward relative to the mean flow** — which is why weather systems can appear to move slowly eastward.

## Key results

**Scale analysis:**

<div class="result" markdown>

\[
\mathrm{Ro} = \frac{U}{fL},
\qquad
f = 2\Omega\sin\phi \approx 10^{-4}\ \mathrm{s^{-1}}\ \text{(midlatitudes)}
\]

</div>

| System | \(L\) | \(U\) | \(\mathrm{Ro}\) | Balanced? |
|---|---|---|---|---|
| Synoptic cyclone | 1000 km | 10 m/s | 0.1 | yes |
| Hurricane core | 50 km | 50 m/s | 10 | no |
| Thunderstorm | 10 km | 30 m/s | 30 | no |
| Ocean gyre | 1000 km | 0.1 m/s | 0.001 | strongly |

**Geostrophic and gradient wind:**

\[
f\,\mathbf{k}\times\mathbf{u}_g = -\frac{1}{\rho}\nabla_h p,
\qquad
\frac{V^2}{R} + fV = \frac{1}{\rho}\left|\nabla_h p\right|
\]

The curvature term makes gradient wind **subgeostrophic in troughs** and **supergeostrophic in ridges** — a 10–20% effect that matters for trajectory work.

**Thermal wind:**

\[
\frac{\partial \mathbf{u}_g}{\partial \ln p} = -\frac{R_d}{f}\,\mathbf{k}\times\nabla_p T
\]

Cold air to the north gives westerly shear increasing with height: the midlatitude jet.

**Vorticity and potential vorticity:**

\[
\zeta = \mathbf{k}\cdot(\nabla\times\mathbf{u}),
\qquad
\frac{D}{Dt}\left(\frac{\zeta + f}{H}\right) = 0 \quad\text{(shallow water)}
\]

\[
q = \frac{1}{\rho}(\zeta_a\cdot\nabla\theta) \quad\text{(Ertel PV, conserved adiabatically)}
\]

The **PV perspective**: given the PV distribution plus boundary \(\theta\), the balanced wind and mass fields follow by inversion. A single conserved scalar contains the balanced dynamics, which is why PV maps are how dynamicists read the atmosphere.

**Quasi-geostrophic omega equation** — where vertical motion comes from:

\[
\left(\nabla^2 + \frac{f_0^2}{\sigma}\frac{\partial^2}{\partial p^2}\right)\omega
= \frac{f_0}{\sigma}\frac{\partial}{\partial p}\left[\mathbf{u}_g\cdot\nabla(\zeta_g+f)\right]
+ \frac{R}{\sigma p}\nabla^2\left[\mathbf{u}_g\cdot\nabla T\right]
\]

Two forcings: differential vorticity advection, and thermal advection. Ascent (\(\omega<0\)) where positive vorticity advection increases with height, or where warm advection occurs.

**Rossby waves.** With \(\beta = df/dy\):

\[
c = \bar{u} - \frac{\beta}{k^2 + l^2}
\]

Always westward *relative to the mean flow*, and longer waves propagate westward faster — so long waves can be quasi-stationary or retrograde while short waves move east with the flow.

## Mental model

Rotation is the organising fact. On a rotating planet, a pressure gradient does not produce flow down the gradient — it produces flow *along* it, with low pressure to the left in the southern hemisphere and to the right... which is exactly the kind of sign convention worth deriving rather than recalling. (Northern hemisphere: low pressure to the left of the wind.)

PV thinking is the most powerful single idea here. Instead of tracking winds and temperatures separately, track one conserved scalar. An upper-level PV anomaly "induces" a circulation beneath it, and the whole life cycle of a midlatitude cyclone becomes the interaction of an upper PV anomaly with a surface temperature anomaly.

## Numerics / practice

- **Check \(\mathrm{Ro}\)** before applying any balance argument. Balanced diagnostics on a convective scale are meaningless.
- **Use gradient rather than geostrophic wind** in strongly curved flow; the error is systematic, not random.
- **PV on isentropic surfaces** is the natural frame — that is where the conservation statement is clean.
- **Diabatic heating destroys PV conservation**, and that is often the point: latent heating generates low-level PV, which is central to cyclone development.

??? warning "Failure modes"
    **Geostrophy applied near the equator.** \(f\to0\) at the equator, so the geostrophic wind diverges. Equatorial dynamics is a different regime — Kelvin and mixed Rossby-gravity waves, not balanced flow. Roughly, geostrophic reasoning is unsafe within about 10° of the equator.

    **Geostrophic wind used in strongly curved flow.** In a sharp trough the gradient wind is significantly subgeostrophic. Using \(u_g\) to advect a parcel through a trough overestimates its speed, and errors accumulate along a trajectory.

    **PV conservation assumed through diabatic processes.** Latent heating, radiation and friction all generate or destroy PV. In a developing cyclone, diabatic PV generation in the warm conveyor belt is a first-order effect, not a correction.

    **QG applied outside its scaling.** QG assumes \(\mathrm{Ro}\ll1\), small Rossby number *and* small relative depth changes. It fails for fronts (where along-front scales collapse), for hurricanes and for anything convective. Semigeostrophic or full primitive equations are needed.

    **Sign errors in hemisphere-dependent relations.** \(f<0\) in the southern hemisphere flips the sense of geostrophic flow, Ekman turning and vorticity conventions. Code written and tested only on northern-hemisphere cases fails silently south of the equator.

    **Vorticity computed on a coarse grid.** \(\zeta\) is a derivative, so it amplifies noise and is strongly resolution-dependent. Comparing vorticity fields between models at different resolutions compares smoothing as much as dynamics.

    <!-- Add your own here. -->

## Worked example

Rossby number as the regime test, computed rather than recalled:

```python
import numpy as np

Omega = 7.292e-5
for name, lat, L_km, U in (("synoptic cyclone", 45.0, 1000.0, 10.0),
                           ("hurricane core",   20.0,   50.0, 50.0),
                           ("thunderstorm",     40.0,   10.0, 30.0),
                           ("sea breeze",       35.0,   30.0,  5.0)):
    f  = 2 * Omega * np.sin(np.deg2rad(lat))
    Ro = U / (f * L_km * 1e3)
    verdict = "balanced" if Ro < 0.3 else ("marginal" if Ro < 3 else "NOT balanced")
    print(f"{name:18s} f={f:.2e}  Ro={Ro:8.3f}   {verdict}")
```

```
synoptic cyclone   f=1.03e-04  Ro=   0.097   balanced
hurricane core     f=4.99e-05  Ro=  20.048   NOT balanced
thunderstorm       f=9.37e-05  Ro=  32.002   NOT balanced
sea breeze         f=8.37e-05  Ro=   1.992   marginal
```

The sea breeze is the interesting case: marginal, so rotation matters but does not dominate — which is why sea-breeze fronts turn with time over a day rather than propagating straight inland.

## Connections

- [Thermodynamics](thermodynamics.md) — static stability enters the QG equations as \(\sigma\).
- [NWP](nwp.md) — which of these balances a dynamical core respects.
- [Boundary layer](boundary-layer.md) — Ekman balance and friction.
- [Fluids › Governing equations](../fluids/governing-equations.md) — the parent equations.

## Sources

- Holton & Hakim, *An Introduction to Dynamic Meteorology*.
- Vallis, *Atmospheric and Oceanic Fluid Dynamics*.
- Hoskins, McIntyre & Robertson (1985) — the PV perspective paper.
- Archive: see the [course archive](../resources/course-archive.md).
