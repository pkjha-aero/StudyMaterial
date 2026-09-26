---
title: Scientific and remote-sensing imagery
status: working
tags: [pillar-9, computer-vision, remote-sensing, wildfire, validation]
updated: 2026-09-26
---

# Scientific and remote-sensing imagery

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - Scientific images are **measurements**, not pictures. Pixel values carry physical units, and the usual CV preprocessing destroys them.
    - **Never 8-bit-normalise radiometric data** before analysis. It discards the calibration that makes the measurement meaningful.
    - Multispectral data has **more than three channels**, and pretrained RGB backbones cannot use the rest without adaptation.
    - **Spatial autocorrelation makes random train/test splits leak.** Neighbouring pixels are not independent samples.
    - Georeferencing, projection and resolution mismatches between products are the dominant practical difficulty.

## Key results

**Radiometric chain.** What a sensor gives you, in order:

<div class="result" markdown>

digital number → **radiance** (calibration) → **reflectance** or **brightness temperature** (solar geometry / Planck inversion) → **surface** reflectance (atmospheric correction) → index or retrieval

</div>

Each step is a physical transformation with its own uncertainty. Skipping straight from digital number to a neural network works for detection tasks and destroys any possibility of physical interpretation.

**Spectral indices.** Normalised band ratios, designed to be robust to illumination:

\[
\mathrm{NDVI} = \frac{\rho_{NIR}-\rho_{RED}}{\rho_{NIR}+\rho_{RED}},
\qquad
\mathrm{NBR} = \frac{\rho_{NIR}-\rho_{SWIR}}{\rho_{NIR}+\rho_{SWIR}}
\]

NBR is the standard burn-severity index; dNBR (pre minus post fire) is how burn scars are mapped operationally.

**Resolution is four separate things**, and confusing them causes real errors:

| Resolution | Means | Typical trade |
|---|---|---|
| Spatial | ground sample distance | finer costs swath and revisit |
| Spectral | number and width of bands | more bands, less SNR per band |
| Temporal | revisit interval | geostationary is frequent, coarse, fixed view |
| Radiometric | bits per pixel | more bits, more data volume |

**Fire and smoke detection.** Active fire detection exploits the Planck shift: a hot subpixel source radiates strongly in the mid-infrared (~4 µm) relative to the longwave window (~11 µm), so a MIR/LWIR contrast test detects fires far smaller than a pixel. Smoke is detected in visible and near-IR by its scattering signature, and is much harder — it is confused with cloud, haze and bright surfaces.

**Georeferencing.** A raster is pixels plus an affine transform plus a coordinate reference system. Combining products requires agreeing all three. Reprojection resamples, and **resampling a classification raster with bilinear interpolation invents classes** — the same failure as in [image fundamentals](image-fundamentals.md), with worse consequences because the output looks like a map.

**Spatial cross-validation.** Neighbouring pixels are strongly correlated, so a random pixel split puts near-duplicates in train and test. Block or buffered spatial CV — holding out contiguous regions — is the honest version, and scores typically drop substantially when you switch.

## Mental model

Treat every pixel as an instrument reading with units, a calibration history and an uncertainty. That single habit prevents most of the errors on this page: you do not normalise away a calibration, you do not average across a band boundary, and you do not interpolate a categorical field.

The second habit is to ask what the sensor could physically have seen. A 375 m pixel cannot resolve a 10 m flame front — but it *can* detect it, because the radiometric signal is integrated over the pixel. Detection limits and resolution limits are different questions, and conflating them produces both false expectations and missed capability.

## Numerics / practice

- **Keep native dtype and units** as far into the pipeline as possible; convert for display only.
- **Use `rasterio`/`xarray` with explicit CRS handling**; GDAL underneath. Check the transform and CRS of every product before combining.
- **Nearest-neighbour for categorical rasters**, always, at every resampling step.
- **Use spatial block CV** and report it alongside any random-split number, so the gap is visible.
- **Handle no-data explicitly.** Fill values are often valid-looking numbers (\(-9999\), \(0\), \(65535\)) that silently enter statistics.

??? warning "Failure modes"
    **Normalising radiometric data to 8-bit before analysis.** Standard CV preprocessing (`img / 255`, percentile stretch) destroys the calibration. The detector may still work; the retrieval is meaningless. This is the single most common mistake when a CV practitioner meets remote-sensing data.

    **Random pixel splits on spatially autocorrelated data.** Adjacent pixels are near-duplicates, so a random split trains and tests on effectively the same samples. Reported accuracy can be 20+ points above the spatially-blocked value. Symptom: excellent validation, poor performance on a new scene.

    **Bilinear resampling of a classification raster.** Interpolating between class codes 2 and 6 produces 4. The resulting map looks smooth and professional and contains classes that were never predicted.

    **No-data values entering statistics.** \(-9999\) fill in a mean is not subtle in the result, but \(0\) in a reflectance product is — it looks like a dark surface. Always mask explicitly rather than trusting the array to be clean.

    **RGB-pretrained backbone on multispectral input.** The pretrained weights cover three bands. Common fixes — dropping to three bands, or averaging pretrained weights across new channels — discard information or mismatch the statistics. Neither is wrong, but the choice should be deliberate and stated.

    **Cloud and shadow not masked.** Clouds are bright and shadows dark, so any index or time series is contaminated. Cloud masks are themselves imperfect, and their errors correlate with terrain and season.

    **Detection limit confused with spatial resolution.** A subpixel hot source is detectable well below the pixel size because the signal is radiometric, not geometric. Conversely, a large but low-contrast feature can be invisible at high resolution. Reasoning about "can the sensor see it" needs the radiometry, not just the GSD.

    **Time series across a sensor change.** Instrument replacement, orbital drift and calibration updates produce step changes that look like trends. The same problem as [observing-system changes](../meteorology/observations.md) in reanalysis.

    <!-- Add your own here — this is your applied area. -->

## Worked example

Why mid-infrared detects fires far smaller than a pixel — Planck, not geometry:

```python
import numpy as np

h, c, kB = 6.62607015e-34, 2.99792458e8, 1.380649e-23

def planck(wavelength_um, T):
    lam = wavelength_um * 1e-6
    return (2*h*c**2 / lam**5) / (np.exp(h*c/(lam*kB*T)) - 1)

T_bg, T_fire = 300.0, 800.0
for lam in (4.0, 11.0):
    ratio = planck(lam, T_fire) / planck(lam, T_bg)
    # pixel signal if a fraction f of the pixel is at fire temperature
    f = 0.0001                                   # 0.01% of the pixel
    mix = (1 - f) * planck(lam, T_bg) + f * planck(lam, T_fire)
    uplift = mix / planck(lam, T_bg)
    print(f"{lam:5.1f} um   fire/background radiance = {ratio:10.1f}x   "
          f"pixel uplift at f=0.01% = {100*(uplift-1):6.2f}%")
```

```
  4.0 um   fire/background radiance =     1816.8x   pixel uplift at f=0.01% =  18.16%
 11.0 um   fire/background radiance =       18.7x   pixel uplift at f=0.01% =   0.18%
```

A fire filling one ten-thousandth of a pixel raises the 4 µm radiance by 18% and the 11 µm radiance by 0.18% — a hundredfold difference in detectability, from a source occupying 0.01% of the ground area. That contrast is the entire basis of satellite active-fire detection, and it is why a 375 m pixel reliably flags a fire front a few metres across.

## Connections

- [Image fundamentals](image-fundamentals.md) — sampling, interpolation, why nearest for labels.
- [Detection and segmentation](detection-segmentation.md) — the models applied here.
- [Meteorology › Fire weather](../meteorology/fire-weather.md) — what the detections feed.
- [Meteorology › Observations](../meteorology/observations.md) — satellite retrievals and their caveats.
- [Astrophysics › Radiative transfer](../astrophysics/radiative-transfer.md) — the same Planck function.

## Sources

- Giglio et al. (2016), *The Collection 6 MODIS active fire detection algorithm*.
- Roberts & Wooster — geostationary fire radiative power retrieval.
- Ploton et al. (2020), *Spatial validation reveals poor predictive performance of large-scale ecological mapping models*.
