---
title: Fire weather
status: working
tags: [pillar-1, meteorology, wildfire, coupled-modelling, fire-indices]
updated: 2026-09-26
---

# Fire weather

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Fire behaviour is set by the **fire behaviour triangle**: fuel, weather, topography. Weather is the fastest-varying leg and the one meteorology owns.
    - **Fuel moisture is the dominant weather-driven control**, and it responds to humidity and temperature with a lag that depends on fuel size.
    - Fires split into **wind-driven** and **plume-dominated** regimes, and they behave completely differently — including how they respond to a wind shift.
    - **Fire-atmosphere coupling is two-way**: the fire generates its own winds, and one-way coupled models systematically miss that.
    - Fire weather **indices are regionally calibrated**. Moving one outside its calibration region quietly invalidates the thresholds.

## Key results

**Fuel moisture timelag classes**, the standard organising scheme:

<div class="result" markdown>

| Class | Diameter | Response time | Drives |
|---|---|---|---|
| 1-hour | \(<6\) mm | ~1 h | ignition, rate of spread |
| 10-hour | 6–25 mm | ~10 h | spread, spotting |
| 100-hour | 25–75 mm | ~4 days | sustained burning |
| 1000-hour | 75–200 mm | ~6 weeks | drought signal, resistance to control |

</div>

Response time is the e-folding time towards the equilibrium moisture content set by temperature and relative humidity. Fine fuels track the diurnal RH cycle; heavy fuels integrate weeks of drought.

**Rothermel rate of spread**, the basis of most operational fire models:

\[
R = \frac{I_R \xi (1 + \phi_w + \phi_s)}{\rho_b \epsilon Q_{ig}}
\]

with \(I_R\) reaction intensity, \(\xi\) propagating flux ratio, \(\phi_w\) and \(\phi_s\) wind and slope factors. Note \(R\) rises steeply with wind and slope — the wind factor is a power law, so a doubling of wind speed can more than triple spread rate.

**Byram's fireline intensity** and flame length:

\[
I = H\,w\,R,
\qquad
L \approx 0.0775\,I^{0.46}
\]

with \(H\) the heat yield (~18,600 kJ/kg), \(w\) fuel consumed per unit area, \(R\) rate of spread. Intensity above roughly 4,000 kW/m is generally beyond direct attack.

**Fire weather indices:**

| Index | Uses | Calibrated for |
|---|---|---|
| Haines Index | lower-atmosphere stability and dryness | US; known regional bias |
| Fosberg FWI | wind, temperature, RH | fine-fuel-driven spread |
| Canadian FWI system | full moisture-code chain | Canadian boreal; adapted elsewhere |
| Hot-Dry-Windy (HDW) | max product of VPD and wind in the mixed layer | designed to be more transferable |

HDW deserves note as a deliberate response to Haines's limitations: it uses physically motivated quantities (vapour pressure deficit and wind through the boundary layer) rather than regionally tuned thresholds.

**Plume-dominated versus wind-driven.** The distinction is between a fire whose spread is governed by ambient wind and one whose own convective column dominates. Plume-dominated fires are associated with weak winds and an unstable, dry mid-troposphere; they produce erratic, multi-directional spread, strong indrafts, and can generate **pyrocumulonimbus** with its own downdrafts and lightning.

**Coupled fire-atmosphere models** — WRF-Fire, WRF-SFIRE, CAWFE, FIRETEC, QUIC-Fire — run a spread model on a fine grid two-way coupled to the atmospheric model, so fire heat and moisture fluxes modify the wind field which in turn drives the fire.

## Mental model

Ambient weather sets the stage; the fire then rewrites the local weather. A large fire is a heat source of gigawatts, which produces its own convergent inflow — frequently stronger than the synoptic wind. That is why one-way coupling fails: it predicts spread using a wind field that the fire would have changed.

The two regimes come out of the same picture. When the ambient wind is strong, the plume is tilted and carried downstream, the fire runs with the wind, and its behaviour is predictable from the wind forecast. When the ambient wind is weak and the atmosphere unstable, the plume goes vertical, the indraft becomes symmetric, and the fire's spread direction becomes much harder to anticipate.

## Numerics / practice

- **Resolution matters more than physics here.** Terrain-driven winds — channelling, lee slopes, downslope windstorms — need sub-kilometre grids and are often what actually drives a run.
- **Fuel moisture models need spin-up**, weeks of it for the 1000-hour class. A cold-started fuel-moisture field is meaningless for heavy fuels.
- **Verify the wind field independently** before attributing spread error to the fire model.
- **Use ensembles.** Fire spread is highly sensitive to wind direction, so a deterministic forecast conveys false precision.

??? warning "Failure modes"
    **One-way coupling.** Driving a spread model with an uncoupled weather forecast misses fire-induced winds entirely. For large fires these can exceed the ambient wind, so the error is not a correction — it changes the predicted spread direction. This is the single most important modelling choice on this page.

    **Indices applied outside their calibration region.** The Haines Index has known regional biases and its category thresholds were set for the continental US. Applied elsewhere, "high" may be climatologically routine — the index still returns a number, and the number means something different.

    **Fine-fuel moisture from station RH alone.** Fuel moisture depends on the microclimate under the canopy, on shading and on recent precipitation. Open-station RH overestimates drying under closed canopy and underestimates it on exposed slopes.

    **Grid too coarse for terrain-driven wind.** At 3 km, a canyon is not resolved. Downslope windstorms, channelling and lee-side rotors — all major drivers of extreme fire behaviour — require hundreds of metres or finer. Symptom: a forecast that misses the acceleration entirely, with no indication anything is wrong.

    **Plume-dominated behaviour forecast with wind-driven logic.** Under weak winds and an unstable dry mid-troposphere, spread direction becomes erratic and downdraft outflows can push fire in any direction. Applying a wind-driven mental model here is actively dangerous.

    **Rate of spread extrapolated beyond the fuel model.** Rothermel is a fit to laboratory and field data for defined fuel models. Extreme winds, crown fire and mass spotting are outside it; operational systems bolt on separate crown-fire and spotting models for exactly this reason.

    **Ignoring the nocturnal decoupling.** Fires usually lie down at night as the boundary layer stabilises and RH recovers — unless a [low-level jet](boundary-layer.md) couples down to the surface, or the fire is above the inversion on a slope. Both exceptions produce dangerous overnight runs.

    <!-- Add your own here — this is your applied area, and these notes are generic. -->

## Worked example

Vapour pressure deficit is the fire-relevant moisture variable, not relative humidity:

```python
import numpy as np

def es(Tc):                                       # Tetens, Pa
    return 611.2 * np.exp(17.67 * Tc / (Tc + 243.5))

print(f"{'T (C)':>6} {'RH (%)':>7} {'VPD (kPa)':>10}")
for Tc, rh in ((20.0, 30.0), (35.0, 30.0), (35.0, 15.0), (40.0, 10.0)):
    vpd = es(Tc) * (1 - rh/100.0) / 1000.0
    print(f"{Tc:6.1f} {rh:7.1f} {vpd:10.2f}")
```

```
 T (C)  RH (%)  VPD (kPa)
  20.0    30.0       1.64
  35.0    30.0       3.94
  35.0    15.0       4.79
  40.0    10.0       6.66
```

The first two rows have identical relative humidity and a 2.4× difference in drying power. RH alone cannot rank fire danger across temperatures, which is why VPD-based indices such as HDW transfer between regions better than RH-threshold ones.

## Connections

- [Thermodynamics](thermodynamics.md) — VPD, stability, plume buoyancy.
- [Boundary layer](boundary-layer.md) — nocturnal decoupling, low-level jets, terrain winds.
- [NWP](nwp.md) — resolution requirements and the grey zone.
- [CV › Scientific imagery](../cv/index.md) — smoke and fire detection from satellite.
- [SciML](../sciml/index.md) — ML surrogates for spread prediction.

## Sources

- Rothermel (1972), *A mathematical model for predicting fire spread in wildland fuels*.
- Potter (2012), *Atmospheric interactions with wildland fire behaviour* (two-part review).
- Srock et al. (2018), *The Hot-Dry-Windy Index*.
- Coen et al., *WRF-Fire* documentation.
