---
title: Atmospheric boundary layer
status: working
tags: [pillar-1, meteorology, boundary-layer, turbulence]
updated: 2026-09-26
---

# Atmospheric boundary layer

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - The ABL is where the atmosphere feels the surface, over a timescale of about an hour. Everything above responds much more slowly.
    - **Monin–Obukhov similarity** is the organising theory of the surface layer: scale by \(u_*\), \(L\) and \(z\), and profiles collapse onto universal functions.
    - The **Obukhov length \(L\)** is the height at which buoyant and shear production of turbulence are comparable. Its sign is the stability.
    - The **diurnal cycle is the dominant signal**: a deep convective layer by day, a shallow stable layer with a residual layer above by night.
    - **MOST breaks in both limits** — very stable and free-convective — which are exactly the conditions that matter for pollutant dispersal and for nocturnal jets.

## Key results

**Surface-layer scaling.** With kinematic momentum flux \(\overline{u'w'}\) and heat flux \(\overline{w'\theta'}\):

<div class="result" markdown>

\[
u_* = \left(-\overline{u'w'}\right)^{1/2},
\qquad
\theta_* = -\frac{\overline{w'\theta'}}{u_*},
\qquad
L = -\frac{u_*^3\,\overline{\theta_v}}{\kappa g\,\overline{w'\theta_v'}}
\]

</div>

\(\kappa \approx 0.40\). Sign convention: \(L<0\) unstable (daytime, upward heat flux), \(L>0\) stable (nocturnal), \(|L|\to\infty\) neutral.

**Log wind profile** with stability correction:

\[
u(z) = \frac{u_*}{\kappa}\left[\ln\frac{z-d}{z_0} - \psi_m\!\left(\frac{z-d}{L}\right)\right]
\]

\(z_0\) is the roughness length, \(d\) the displacement height (about \(0.7h_c\) for a canopy of height \(h_c\); \(z_0 \approx 0.1h_c\)).

| Surface | \(z_0\) (m) |
|---|---|
| Open water | \(10^{-4}\)–\(10^{-3}\) |
| Grass | 0.01–0.05 |
| Cropland | 0.1–0.25 |
| Forest | 0.5–2 |
| Urban | 1–3 |

**Stability functions** (Businger–Dyer), \(\zeta = z/L\):

\[
\phi_m = (1-16\zeta)^{-1/4}\ (\zeta<0),
\qquad
\phi_m = 1 + 5\zeta\ (\zeta>0)
\]

**Bulk flux formulae**, how models actually compute surface exchange:

\[
\tau = \rho C_D U^2,
\qquad
H = \rho c_p C_H U(\theta_s - \theta_a),
\qquad
E = \rho C_E U(q_s - q_a)
\]

**Diurnal structure:**

| Time | Structure | Depth |
|---|---|---|
| Midday | convective ML, well mixed in \(\theta\) | 1–3 km |
| Late afternoon | ML decays | — |
| Night | shallow stable BL + residual layer | 50–300 m |
| Morning | ML grows into residual layer | rapid |

The **entrainment zone** at the ML top mixes warm dry free-tropospheric air downwards; entrainment flux is typically about \(-0.2\times\) the surface flux, and it controls ML growth.

**Nocturnal low-level jet.** When the stable layer decouples the surface from the flow above, the residual-layer air is released from friction and accelerates supergeostrophically, oscillating inertially. Peaks near 100–500 m, often after midnight — important for pollutant transport, wind energy and overnight fire behaviour.

## Mental model

Think of the ABL as the atmosphere's interface layer: momentum, heat and moisture all pass through it, and turbulence is the transport mechanism. During the day, buoyancy produces turbulence and the layer mixes deeply and quickly. At night, buoyancy destroys turbulence, mixing collapses, and the surface decouples from the air above.

MOST is dimensional analysis. In the surface layer the only relevant parameters are height, friction velocity, buoyancy flux and von Kármán's constant. Form the dimensionless groups and everything must be a universal function of \(z/L\) — which is a strong statement, and it works remarkably well in the middle of the stability range.

## Numerics / practice

- **Measure or estimate \(z_0\) and \(d\) properly** for vegetated surfaces. Using \(z_0\) without \(d\) over a forest gives wildly wrong near-canopy winds.
- **Iterate the flux calculation**: \(u_*\) and \(L\) depend on each other, so bulk schemes need a fixed-point iteration, which can fail to converge in very stable conditions.
- **Check \(z/L\)** before trusting a similarity-derived flux.
- For LES of the ABL, see [fluids › LES](../fluids/turbulence/les.md); the near-wall resolution arguments there apply, with the added complication of surface heterogeneity.

??? warning "Failure modes"
    **MOST in the very stable limit.** Under strong stability turbulence becomes intermittent and patchy, and the similarity functions lose their footing. \(z/L > 1\) is where predictions and observations diverge badly. This is also where models most need to be right — nocturnal inversions trap pollutants and set minimum temperatures.

    **MOST in free convection.** With \(u_*\to0\) and strong heating, \(L\to0\) and the scaling degenerates. Bulk schemes handle this with a convective velocity scale \(w_*\) and a gustiness parameterisation; without it, the surface flux collapses to zero on a calm sunny afternoon, which is exactly backwards.

    **Displacement height omitted over canopies.** Over a 20 m forest, \(d \approx 14\) m. Measuring at 25 m and using \(\ln(z/z_0)\) rather than \(\ln((z-d)/z_0)\) misstates the profile badly.

    **Neutral profile assumed at night.** The log law without \(\psi_m\) overestimates wind shear in stable conditions. Wind-energy resource assessment that extrapolates a 10 m measurement to hub height with a neutral profile is systematically wrong overnight — and overnight is when the low-level jet makes the resource largest.

    **Similarity theory over heterogeneous terrain.** MOST assumes horizontal homogeneity and stationarity. Over patchy terrain, coastlines or complex topography, an internal boundary layer forms and the measured flux represents an upwind footprint that changes with wind direction.

    **Flux-iteration non-convergence.** In strong stability the bulk-flux fixed point can oscillate or converge to a spurious solution. Many models cap \(z/L\) or add a minimum wind speed — a numerical patch that changes the physics, and one worth knowing about in your model.

    <!-- Add your own here. -->

## Worked example

Why the stability correction cannot be skipped for hub-height extrapolation:

```python
import numpy as np

kappa, z0, u_ref, z_ref, z_hub = 0.40, 0.03, 6.0, 10.0, 100.0

def psi_m(zeta):
    if zeta < 0:                                   # unstable
        x = (1 - 16*zeta)**0.25
        return 2*np.log((1+x)/2) + np.log((1+x*x)/2) - 2*np.arctan(x) + np.pi/2
    return -5*zeta                                 # stable

for name, L in (("neutral", 1e9), ("unstable (day)", -50.0), ("stable (night)", 200.0)):
    ustar = kappa * u_ref / (np.log(z_ref/z0) - psi_m(z_ref/L))
    u_hub = ustar/kappa * (np.log(z_hub/z0) - psi_m(z_hub/L))
    print(f"{name:16s} u*={ustar:.3f} m/s   u(100 m)={u_hub:5.2f} m/s   "
          f"P ratio={u_hub**3/ (u_ref**3):.2f}")
```

```
neutral          u*=0.413 m/s   u(100 m)= 8.38 m/s   P ratio=2.72
unstable (day)   u*=0.449 m/s   u(100 m)= 7.42 m/s   P ratio=1.89
stable (night)   u*=0.396 m/s   u(100 m)=10.51 m/s   P ratio=5.37
```

The same 10 m wind gives 7.4 m/s at hub height by day and 10.5 m/s at night. Because power goes as \(V^3\), that is a factor of 2.8 in available power between the two, and a neutral profile sits between them — wrong in both conditions.

    Note the stable case uses \(L=200\) m, putting \(z/L = 0.5\) at hub height. Pushing it to \(L=50\) m gives \(z/L=2\) and a shear exponent of 0.43, which is not credible — the linear \(\psi_m\) is being extrapolated well past its validity. That is the first failure mode above, reproduced by accident.

## Connections

- [Thermodynamics](thermodynamics.md) — static stability, and the parcels the ABL supplies to convection.
- [Dynamics](dynamics.md) — Ekman balance, friction on the large-scale flow.
- [NWP](nwp.md) — boundary-layer schemes in operational models.
- [Aerospace › Wind energy](../aerospace/wind-energy.md) — this is the turbine inflow.
- [Fire weather](fire-weather.md) — nocturnal decoupling and fire behaviour.

## Sources

- Stull, *An Introduction to Boundary Layer Meteorology*.
- Garratt, *The Atmospheric Boundary Layer*.
- Archive: `METEO 421` material; see the [course archive](../resources/course-archive.md).
