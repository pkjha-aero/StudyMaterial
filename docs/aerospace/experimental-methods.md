---
title: Experimental methods
status: working
tags: [pillar-10, aerospace, validation, uncertainty]
updated: 2026-09-28
---

# Experimental methods

<span class="status status-working">working</span>
<span class="pillar">pillar 10 &middot; V&V, research craft and communication</span>

!!! abstract "In one minute"
    - Every measurement is an **inference through a chain** — transducer, conditioning, digitiser, reduction — and each link has its own error and bandwidth.
    - **Bias and precision are different problems.** Averaging kills precision error and does nothing at all to bias.
    - **A result without an uncertainty is not a measurement.** It is a number, and it cannot validate anything.
    - Wind tunnels measure a *constrained* flow: blockage, wall interference and support effects are corrections, not optional refinements.
    - **Reynolds number is usually the thing you cannot match**, and knowing which results are Reynolds-sensitive is the whole skill.

## Key results

**Uncertainty, the two kinds:**

<div class="result" markdown>

\[
u_{\text{total}} = \sqrt{b^2 + (t\,s_{\bar{x}})^2},
\qquad
s_{\bar x} = \frac{s}{\sqrt{N}}
\]

**Bias** \(b\) is systematic — calibration offset, installation, a wrong reference. Repeating does not reduce it. **Precision** \(s_{\bar x}\) is random and falls as \(1/\sqrt{N}\).

</div>

**Propagation** through a data reduction \(y = f(x_1,\dots,x_n)\):

\[
u_y^2 = \sum_i \left(\frac{\partial f}{\partial x_i}\right)^2 u_{x_i}^2
\]

The sensitivity coefficients matter more than the individual uncertainties: a quantity entering squared contributes twice its relative uncertainty, and one entering as a small difference of two large numbers can dominate everything.

**Instruments and what limits them:**

| Instrument | Measures | Limited by |
|---|---|---|
| Pressure tap / Scanivalve | static pressure | tap geometry, tubing response |
| Pitot-static | total and static | misalignment, compressibility |
| Hot wire | velocity, high bandwidth | calibration drift, fragility, temperature |
| PIV | 2D/3D velocity field | seeding, peak locking, out-of-plane loss |
| LDV | point velocity, no calibration | seeding, access |
| Load cell / balance | forces and moments | interactions, temperature, calibration matrix |
| Thermocouple | temperature | radiation error, conduction along leads |
| Microphone | acoustic pressure | free-field vs pressure response |
| Laser diagnostics (LIF, Raman) | species, temperature | signal strength, quenching, collection optics |

**Sampling.** The Nyquist limit \(f_s > 2f_{\max}\) is necessary, not sufficient — you must **anti-alias filter in hardware before digitising**, because once folded, a high frequency is indistinguishable from a real low one. Exactly the effect demonstrated in the [image fundamentals](../cv/image-fundamentals.md) aliasing example, in the time domain.

**Wind tunnel corrections**, all of which are real and all of which are sometimes skipped:

- **Solid blockage** — the model displaces flow, raising local velocity.
- **Wake blockage** — the wake does the same, and grows with drag.
- **Streamline curvature** — walls constrain the flow, changing effective camber and incidence.
- **Support interference** — stings and struts alter the flow they hold.
- **Buoyancy** — streamwise pressure gradient from tunnel boundary-layer growth.

**Reynolds and Mach matching.** A sub-scale model at atmospheric conditions cannot match both. Pressurised, cryogenic or heavy-gas tunnels exist to buy Reynolds number. What matters is knowing which quantities are Reynolds-sensitive — maximum lift, separation, transition location — and which are not.

**Flight test** adds its own chain: air data calibration against a trailing cone or tower flyby, position error correction, and atmospheric variability that no one controls. The data are authoritative for the real vehicle and noisier than any tunnel.

## Mental model

An experiment is an instrument chain answering a question the physics poses, and each link degrades the answer in a characterisable way. The discipline is to know the degradation rather than hope it is small.

The habit worth carrying: before believing a number, ask what would have to be true for it to be wrong. A pressure that seems too low — is the tap burred? Is the tubing resonating? Is the reference wrong? A drag count that will not repeat — is it the balance temperature, or the transition location moving with tunnel turbulence?

## Numerics / practice

- **Calibrate in place, end to end**, against a known input, not component by component from data sheets.
- **Filter before digitising.** A digital filter after the fact cannot undo aliasing.
- **Quote uncertainty with a confidence level and its basis**, separating bias from precision.
- **Repeat points within and between runs.** Scatter between nominally identical runs is the honest estimate of repeatability, and it is usually larger than the within-run scatter.

??? warning "Failure modes"
    **Uncertainty reported as scatter only.** Averaging 10,000 samples makes the precision term small and leaves the bias untouched. A result quoted as ±0.1% because the mean is stable, when the transducer calibration is ±1%, is wrong by an order of magnitude — and confidently so.

    **Aliasing from digitising without an analogue filter.** A 5 kHz component sampled at 2 kHz appears at 1 kHz, indistinguishable from real content. No post-processing recovers it. This is the single most common data-acquisition error.

    **Thermocouple radiation error.** A bare bead in a hot gas stream radiates to cooler walls and reads low — by tens of kelvin in a combustor, sometimes hundreds. Needs shielding, aspiration, or a two-thermocouple correction.

    **Blockage correction skipped.** At a few percent blockage the correction is percent-level on velocity and therefore several percent on the coefficients, which is often larger than the effect being studied. "Small model, ignore it" is a judgement that should be quantified, not assumed.

    **PIV peak locking.** Displacement biasing toward integer pixel values when particle images are under-resolved. Symptom: a histogram of sub-pixel displacement with spikes at whole pixels. Fixed at acquisition — particle image diameter of 2–3 pixels — not in post-processing.

    **Hot wire drifting uncalibrated.** Sensitive to ambient temperature and contamination. Without a pre- and post-run calibration you cannot tell drift from signal, and the drift is smooth and plausible.

    **Reynolds mismatch not declared.** Tunnel data at \(\mathrm{Re}=10^6\) used to validate a computation at flight \(\mathrm{Re}=10^7\). Maximum lift and separation will differ genuinely, and the disagreement gets blamed on the turbulence model.

    **Comparing a tripped experiment with an untripped computation.** The single most common apples-to-oranges validation error — see [stability and transition](../fluids/transition.md).

    <!-- Add your own here — this is the section where lab experience is irreplaceable. -->

## Worked example

Why averaging cannot rescue a biased measurement:

```python
import numpy as np

bias = 1.0          # % of reading, systematic (calibration)
noise = 3.0         # % of reading, random (turbulence, electrical)

print(f"{'samples N':>10}{'precision term':>17}{'bias term':>12}{'total':>9}{'dominated by':>16}")
for N in (1, 10, 100, 10_000, 1_000_000):
    prec = noise / np.sqrt(N)
    total = np.hypot(bias, prec)
    who = "precision" if prec > bias else "BIAS"
    print(f"{N:10d}{prec:17.4f}{bias:12.2f}{total:9.3f}{who:>16}")
```

```
 samples N   precision term   bias term    total    dominated by
         1           3.0000        1.00    3.162       precision
        10           0.9487        1.00    1.378            BIAS
       100           0.3000        1.00    1.044            BIAS
     10000           0.0300        1.00    1.000            BIAS
   1000000           0.0030        1.00    1.000            BIAS
```

Past about ten samples the bias dominates, and beyond a hundred the total uncertainty is *exactly* the bias — further averaging buys nothing at all. A million samples and ten samples give the same answer to three figures.

The practical consequence: once you are bias-limited, more data is wasted effort and better calibration is the only path. Knowing which side of that line you are on takes one calculation.

## Connections

- [Foundations › V&V](../foundations/verification-validation.md) — this is where validation data comes from, and why it has error bars.
- [Foundations › Probability and statistics](../foundations/probability-statistics.md) — effective sample size, which applies to turbulent time series here too.
- [Fluids › Stability and transition](../fluids/transition.md) — tripping, and tunnel turbulence.
- [Thermal › Combustion](../thermal/combustion.md) — laser diagnostics for species and temperature.
- [Aerodynamics](aerodynamics.md) — what the tunnel is measuring.

## Sources

- Coleman & Steele, *Experimentation, Validation, and Uncertainty Analysis for Engineers*.
- Barlow, Rae & Pope, *Low-Speed Wind Tunnel Testing*.
- Tropea, Yarin & Foss, *Springer Handbook of Experimental Fluid Mechanics*.
- Archive: `Aerospace/AERSP305`, `Aerospace/AERSP597A_Exp_Methods`, `Aerospace/AERSP420`, `Mechanical/ME537_Shashank`; see the [course archive](../resources/course-archive.md).
