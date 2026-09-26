---
title: Image fundamentals
status: working
tags: [pillar-9, computer-vision, filtering, geometry, color]
updated: 2026-09-26
---

# Image fundamentals

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - An image is a **sampled 2D signal**, so every sampling result applies: aliasing, Nyquist, and the need to low-pass before downsampling.
    - **Convolution is the basic operation**, and the kernel is the prior — smoothing, differentiating, or matching.
    - **Gamma is not linear light.** Most image files are gamma-encoded, and arithmetic on them is arithmetic on the wrong quantity.
    - A pinhole camera maps 3D to 2D by a **projective transform**, which destroys depth and preserves straight lines.
    - Interpolation choice matters more than people expect — nearest for labels, bilinear or bicubic for intensities, never the reverse.

## Key results

**Convolution and the common kernels:**

<div class="result" markdown>

\[
(I * k)(x,y) = \sum_{u}\sum_{v} I(x-u, y-v)\,k(u,v)
\]

| Kernel | Effect |
|---|---|
| Box / Gaussian | smoothing; Gaussian is separable, \(O(2n)\) not \(O(n^2)\) |
| Sobel / Scharr | first derivative — edges |
| Laplacian | second derivative — zero crossings at edges |
| Laplacian of Gaussian | smooth then differentiate; blob response |
| Unsharp mask | \(I + \alpha(I - G*I)\), sharpening |

</div>

**Sampling.** Downsampling without a low-pass filter aliases: high frequencies fold back as false low-frequency structure. `cv2.resize` with `INTER_AREA` does the filtering; naive slicing (`img[::2, ::2]`) does not — the most common aliasing bug in vision code.

**Gamma.** Displays and file formats encode with roughly \(V_{\text{out}} = V_{\text{in}}^{1/2.2}\). Consequences:

- Averaging, blurring or resizing gamma-encoded pixels averages the wrong quantity, darkening the result.
- Physically meaningful operations (photometry, HDR merging, physically based rendering) need linearisation first.
- For neural networks it usually does not matter — the network learns whatever encoding it is fed — provided training and inference agree.

**Colour spaces:**

| Space | Property | Use |
|---|---|---|
| RGB | device-native | default, display |
| HSV / HSL | separates hue from intensity | colour thresholding under varying light |
| Lab | perceptually uniform | colour difference, gamut work |
| YCbCr | luma/chroma separation | compression |

**Pinhole camera model:**

\[
s\begin{bmatrix}u\\v\\1\end{bmatrix}
= \underbrace{\begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1\end{bmatrix}}_{K,\ \text{intrinsics}}
\begin{bmatrix} R & t \end{bmatrix}
\begin{bmatrix}X\\Y\\Z\\1\end{bmatrix}
\]

Radial and tangential distortion are corrected separately with the Brown–Conrady coefficients \(k_1,k_2,p_1,p_2,k_3\).

**Homography.** A \(3\times3\) projective transform relating two views of a **plane**, or two views from a camera rotating about its centre. Eight degrees of freedom, so four point correspondences determine it. It does not describe general 3D scenes under translation — that requires the fundamental matrix.

**Interpolation:**

| Method | Use | Never use for |
|---|---|---|
| Nearest | label masks, class indices | intensities (blocky) |
| Bilinear | intensities, general resizing | **label masks** — creates non-existent classes |
| Bicubic | upsampling intensities | anything where overshoot matters |
| Lanczos | high-quality downsampling | speed-critical paths |

## Mental model

Treat the image as a signal first and a picture second. Most classical operations are a filter, and most artefacts are a sampling problem. Blur is a low-pass; edges are a high-pass; noise lives at high frequency, which is why smoothing reduces noise and blurs edges at the same time — they occupy the same band, and every denoiser is a way of separating them using some additional assumption.

The geometric side is the other half: a camera is a projection that throws away one dimension. Everything in multi-view geometry is about recovering what the projection discarded, using more than one projection.

## Numerics / practice

- **Use `INTER_AREA` when downsampling** and `INTER_LINEAR`/`INTER_CUBIC` when upsampling.
- **Watch the channel order** — OpenCV is BGR, almost everything else is RGB. Silently produces colour-swapped results that still look plausible.
- **Separable filters** where possible: a 2D Gaussian is two 1D passes, an enormous saving at large kernel sizes.
- **Keep masks in nearest-neighbour interpolation** through every resize in the pipeline, including augmentation.

??? warning "Failure modes"
    **Downsampling without antialiasing.** `img[::2, ::2]` or `INTER_NEAREST` on a detailed image folds high frequencies into false structure — moiré on textures, and in scientific imagery, plausible-looking features that are not there. Worst case: the artefact is stable across frames, so it looks like a real object.

    **Bilinear interpolation on a label mask.** Averaging class index 1 and class index 3 gives 2, a class that was not present at that location. Symptom: thin spurious regions of an unrelated class along every boundary. Always nearest for labels.

    **BGR/RGB confusion.** Loading with OpenCV and displaying or feeding a model expecting RGB. The image looks wrong but recognisable, and a model trained this way works — until inference uses a different loader.

    **Arithmetic on gamma-encoded pixels.** Averaging two sRGB values is not averaging two light intensities. Matters for photometric work and HDR; largely does not for learned models, provided the pipeline is consistent end to end.

    **Homography applied to a non-planar scene.** Valid only for planes or pure rotation. Applied to a general 3D scene with camera translation, it aligns one depth plane and misregisters everything else — often read as a stitching "quality" problem rather than a model error.

    **Distortion not corrected before geometric measurement.** Wide-angle lenses bend straight lines noticeably at the frame edge. Any measurement in pixels from an uncorrected image inherits that curvature.

    **uint8 overflow in intermediate arithmetic.** `img1 + img2` on `uint8` wraps around, producing dark speckle where it should saturate. Convert to float or use saturating operations.

    <!-- Add your own here. -->

## Worked example

Aliasing from naive downsampling, on a pattern whose true frequency is known:

```python
import numpy as np

n = 256
x = np.arange(n)
signal = np.sin(2 * np.pi * 100 * x / n)      # 100 cycles across 256 samples

naive = signal[::4]                            # decimate, no filtering
box   = signal.reshape(-1, 4).mean(axis=1)     # 4-tap box, then decimate

k = np.exp(-0.5 * (np.arange(-16, 17) / 4.0)**2); k /= k.sum()
padded = np.r_[signal[-16:], signal, signal[:16]]
gauss = np.convolve(padded, k, mode='valid')[::4]   # proper low-pass, then decimate

def dominant(v):
    return int(np.argmax(np.abs(np.fft.rfft(v))[1:]) + 1)

for name, v in (("naive /4", naive), ("box-4 /4", box), ("gaussian /4", gauss)):
    print(f"{name:14s} dominant={dominant(v):3d} cycles   amplitude={np.abs(v).max():.4f}")
```

```
naive /4       dominant= 28 cycles   amplitude=1.0000
box-4 /4       dominant= 28 cycles   amplitude=0.2576
gaussian /4    dominant= 28 cycles   amplitude=0.0000
```

All three report a 28-cycle pattern, and no such pattern exists — the real 100-cycle signal
folded past the new Nyquist. **Only the amplitude distinguishes them.** Naive decimation
passes the alias at full strength. A 4-tap box average — the intuitive "averaging fixes it"
move — only attenuates it to 0.26, because a short box is a poor low-pass filter. A proper
Gaussian prefilter removes it.

The lesson is not "filter before decimating" but *filter adequately*: averaging a few
neighbours feels like antialiasing and mostly is not.

## Connections

- [Classical CV](classical-cv.md) — features and geometry built on these operations.
- [Scientific imagery](scientific-imagery.md) — where aliasing produces false physical features.
- [DL › Architectures](../dl/architectures.md) — convolution as a learned filter bank.
- [Foundations › Numerical methods](../foundations/numerical-methods.md) — the same sampling theory.

## Sources

- Szeliski, *Computer Vision: Algorithms and Applications* — free online.
- Hartley & Zisserman, *Multiple View Geometry* — the projective geometry reference.
