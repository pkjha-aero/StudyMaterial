---
title: Atmospheric thermodynamics
status: working
tags: [pillar-1, meteorology, moist-thermodynamics, cape, skew-t]
updated: 2026-09-26
---

# Atmospheric thermodynamics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - **Potential temperature \(\theta\)** removes the pressure dependence, so vertical motion becomes visible as a departure from constant \(\theta\). It is the working vertical coordinate of the field.
    - \(\theta_e\) conserves **moist** processes too: it survives condensation, which \(\theta\) does not.
    - **Clausius–Clapeyron gives ~7% more saturation vapour per kelvin.** That one number underlies most thinking about a warming atmosphere.
    - **CAPE is an area on a sounding**, and which parcel you lift changes it by a factor of two or more. Always say which.
    - The **virtual temperature correction** is not optional — it typically adds 10% to CAPE and is routinely dropped.

## Key results

**Hydrostatic balance and scale height:**

<div class="result" markdown>

\[
\frac{\partial p}{\partial z} = -\rho g,
\qquad
p(z) = p_0 e^{-z/H},
\qquad
H = \frac{R_d T}{g} \approx 8\ \text{km}
\]

</div>

**Potential temperature**, with \(\kappa = R_d/c_p \approx 0.286\):

\[
\theta = T\left(\frac{p_0}{p}\right)^{\kappa},
\qquad p_0 = 1000\ \mathrm{hPa}
\]

Conserved for dry adiabatic motion. \(\partial\theta/\partial z > 0\) is statically stable, \(< 0\) unstable, \(= 0\) neutral (a well-mixed layer).

**Equivalent potential temperature** — conserved through condensation, so it labels an air mass through its whole moist history:

\[
\theta_e \approx \theta \exp\left(\frac{L_v q_s}{c_p T}\right)
\]

**Moisture variables**, all easy to confuse:

| Symbol | Name | Definition |
|---|---|---|
| \(e\) | vapour pressure | partial pressure of water vapour |
| \(w\) | mixing ratio | \(m_v/m_d\), conserved under pressure change |
| \(q\) | specific humidity | \(m_v/m_{\text{total}} \approx w\) |
| RH | relative humidity | \(e/e_s(T)\) — depends on \(T\), so it changes with no moisture change |
| \(T_d\) | dewpoint | \(T\) at which \(e = e_s\) |

**Clausius–Clapeyron:**

\[
\frac{de_s}{dT} = \frac{L_v e_s}{R_v T^2}
\qquad\Longrightarrow\qquad
\frac{1}{e_s}\frac{de_s}{dT} \approx 7\%\ \mathrm{K^{-1}}
\]

**Lapse rates:**

\[
\Gamma_d = \frac{g}{c_p} = 9.8\ \mathrm{K\,km^{-1}},
\qquad
\Gamma_m \approx 4\text{–}7\ \mathrm{K\,km^{-1}}
\]

\(\Gamma_m\) is smaller because latent heat release partly offsets adiabatic cooling, and it varies strongly with temperature — near 4 K/km in warm tropical air, approaching \(\Gamma_d\) in cold air where there is little vapour.

**CAPE and CIN**, with \(T_v\) virtual temperature:

\[
\mathrm{CAPE} = g\int_{\mathrm{LFC}}^{\mathrm{EL}} \frac{T_{v,\text{parcel}} - T_{v,\text{env}}}{T_{v,\text{env}}}\,dz,
\qquad
w_{\max} = \sqrt{2\,\mathrm{CAPE}}
\]

\(w_{\max}\) is an upper bound that real updrafts reach maybe half of, because of entrainment and water loading.

| Parcel choice | Meaning |
|---|---|
| SB (surface-based) | lifted from the surface |
| ML (mixed-layer) | averaged over lowest 100 hPa — usually most representative |
| MU (most-unstable) | the parcel giving maximum CAPE; matters for elevated convection |

## Mental model

A sounding is a plot of the environment; a parcel is a thought experiment lifted through it. Everything in convective forecasting is the comparison between the two — where the parcel is cooler (CIN, a barrier) and where it is warmer (CAPE, the fuel).

\(\theta\) is the right way to see this because it converts "would this air rise?" into "is \(\theta\) increasing upward?" The pressure dependence that obscures the question in \(T\) is divided out.

## Numerics / practice

- **State the parcel** with every CAPE value. SB and ML CAPE can differ by a factor of two on the same sounding.
- **Use virtual temperature.** The correction \(T_v = T(1 + 0.61w)\) is small pointwise and integrates to roughly +10% on CAPE.
- **Know which saturation formulation** your code uses — over water or over ice below freezing. They differ by several percent, and mixed-phase handling varies between libraries.
- **MetPy** implements the standard calculations consistently; hand-rolling parcel ascent is a reliable source of subtle error.

??? warning "Failure modes"
    **CAPE quoted without the parcel.** The single most common ambiguity in convective discussion. Surface-based CAPE on a sounding with a shallow moist layer can be triple the mixed-layer value, which is the one that actually corresponds to a realistic updraft.

    **Virtual temperature correction omitted.** Adds roughly 10% to CAPE, and more in very moist environments. Consistently biases estimates low, and it is silent.

    **\(\theta\) used where \(\theta_e\) is needed.** \(\theta\) is *not* conserved once condensation begins. Tracking an air mass through a cloud with \(\theta\) shows spurious heating — which is real latent heat, but it means \(\theta\) is no longer a tracer.

    **Relative humidity read as moisture content.** RH depends on temperature through \(e_s\). Air can cool overnight to 100% RH with no moisture added at all. For moisture budgets use mixing ratio or specific humidity; RH is a diagnostic, not a conserved variable.

    **Pseudoadiabatic and reversible ascent conflated.** Pseudoadiabatic assumes condensate falls out immediately; reversible carries it along, and the water loading reduces buoyancy. Real ascent is between the two, and the CAPE difference can be 10–20%.

    **Ice processes ignored.** Freezing above the melting level releases additional latent heat and raises CAPE. Warm-rain-only parcel calculations understate deep convection.

    <!-- Add your own here. -->

## Worked example

Clausius–Clapeyron, and why 7% per kelvin is the number to remember:

```python
import numpy as np

Lv, Rv = 2.5e6, 461.5

def es(T):                                   # Tetens, over water, T in K
    Tc = T - 273.15
    return 611.2 * np.exp(17.67 * Tc / (Tc + 243.5))

for Tc in (0.0, 15.0, 30.0):
    T = Tc + 273.15
    rate_cc = Lv / (Rv * T**2)               # fractional change per K
    rate_fd = (es(T + 0.5) - es(T - 0.5)) / es(T)
    print(f"T={Tc:5.1f} C   es={es(T):8.1f} Pa   "
          f"CC rate={100*rate_cc:.2f} %/K   finite diff={100*rate_fd:.2f} %/K")
```

```
T=  0.0 C   es=   611.2 Pa   CC rate=7.26 %/K   finite diff=7.26 %/K
T= 15.0 C   es=  1704.0 Pa   CC rate=6.52 %/K   finite diff=6.44 %/K
T= 30.0 C   es=  4245.6 Pa   CC rate=5.89 %/K   finite diff=5.75 %/K
```

The "7% per kelvin" figure is the cold-end value; it falls towards 6% in warm air. Saturation vapour pressure itself rises sevenfold from 0 °C to 30 °C, which is why warm air holds so much more water.

## Connections

- [Dynamics](dynamics.md) — stability and static structure feed the large-scale flow.
- [Radiation and clouds](radiation-clouds.md) — what happens once the parcel saturates.
- [Boundary layer](boundary-layer.md) — where the lifted parcel comes from.
- [Fire weather](fire-weather.md) — Haines index and plume buoyancy rest on these quantities.

## Sources

- Wallace & Hobbs, *Atmospheric Science: An Introductory Survey*.
- Emanuel, *Atmospheric Convection* — parcel theory done carefully.
- Archive: see the [course archive](../resources/course-archive.md) for the METEO folders.
