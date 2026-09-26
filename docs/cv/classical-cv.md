---
title: Classical computer vision
status: working
tags: [pillar-9, computer-vision, features, calibration, stereo, optical-flow]
updated: 2026-09-26
---

# Classical computer vision

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - Classical CV is **not obsolete**: calibration, stereo geometry and optical flow remain the right tools when you need metric answers with error bars.
    - **RANSAC is the workhorse** for fitting a model when most of your correspondences are wrong.
    - **Stereo depth error grows as \(Z^2\)** — the single most important fact for anyone specifying a depth rig.
    - Optical flow relies on **brightness constancy**, which fails at exactly the interesting moments: occlusion, lighting change, specularity.
    - Calibration quality bounds everything downstream. A poorly calibrated rig cannot be rescued by better algorithms.

## Key results

**Feature detection and description:**

<div class="result" markdown>

| Detector | Invariance | Notes |
|---|---|---|
| Harris | rotation | corner response from the structure tensor |
| SIFT | scale, rotation, partial affine | the quality benchmark; now patent-free |
| ORB | scale, rotation | binary, very fast, FAST + BRIEF |
| AKAZE | scale, rotation | nonlinear scale space, good on texture |

</div>

Harris corner response from the structure tensor \(M\):

\[
R = \det(M) - k\,\mathrm{tr}(M)^2,
\qquad
M = \sum_w \begin{bmatrix} I_x^2 & I_xI_y \\ I_xI_y & I_y^2\end{bmatrix}
\]

Two large eigenvalues means a corner; one means an edge; none means flat.

**RANSAC.** Iterations needed for probability \(p\) of at least one clean sample, with inlier ratio \(w\) and sample size \(s\):

\[
N = \frac{\log(1-p)}{\log\left(1-w^{s}\right)}
\]

This grows brutally with \(s\). Estimating a homography (\(s=4\)) at 50% inliers needs ~72 iterations; a fundamental matrix (\(s=8\)) at the same inlier ratio needs ~1,177.

**Epipolar geometry.** For corresponding points \(x, x'\):

\[
x'^{\mathsf T} F x = 0,
\qquad
E = K'^{\mathsf T} F K,
\qquad
E = [t]_\times R
\]

The fundamental matrix \(F\) constrains a match to a line rather than a point, reducing the search from 2D to 1D. Rectification makes those lines horizontal, which is what allows fast scanline stereo matching.

**Stereo depth and its error:**

\[
Z = \frac{f B}{d},
\qquad
\left|\frac{\partial Z}{\partial d}\right| = \frac{fB}{d^2} = \frac{Z^2}{fB}
\]

with \(B\) baseline and \(d\) disparity. **Depth uncertainty is quadratic in range.** Doubling the distance quadruples the error for the same disparity precision — which is why stereo rigs have a usable range, and why increasing baseline (at the cost of overlap and occlusion) is the main lever.

**Optical flow.** Brightness constancy \(I(x,y,t) = I(x+\delta x, y+\delta y, t+\delta t)\) linearises to:

\[
I_x u + I_y v + I_t = 0
\]

One equation, two unknowns — the **aperture problem**. Lucas–Kanade resolves it by assuming constant flow in a window; Horn–Schunck by a global smoothness term. Both need a coarse-to-fine pyramid for motion larger than a few pixels.

**Camera calibration.** Zhang's method: images of a planar target at varied orientations give the intrinsics \(K\) and distortion coefficients. Practicalities that actually determine quality: 15–25 images, the target filling the frame including the corners, strong tilt variation, and a rigid, accurately printed target. Reprojection error below ~0.3 px is a reasonable bar.

## Mental model

Classical CV recovers geometry from a projection that discarded it, using constraints. Two views constrain a point to the intersection of two rays. Known camera motion constrains the search to a line. A planar assumption reduces the transform to eight parameters.

Deep learning replaced the *matching* — telling which pixel corresponds to which — far more than it replaced the geometry. The triangulation, the calibration, the epipolar constraint are still exactly as they were, because they are statements about projection rather than about appearance. Modern systems usually learn the correspondences and solve the geometry classically.

## Numerics / practice

- **Always report reprojection error** after calibration, and inspect its spatial distribution — error concentrated at the frame edge means insufficient distortion modelling.
- **Use RANSAC with a sensible threshold** in pixels, and report the inlier count. A homography from 6 inliers out of 500 is not a homography.
- **Undistort before anything geometric.**
- **Check stereo depth precision at your working range** before committing to a baseline. The \(Z^2\) law makes this a design decision, not a tuning one.

??? warning "Failure modes"
    **Calibration with a degenerate target set.** All images at the same orientation, or the target never near the frame edge. The intrinsics are then poorly constrained, particularly the distortion terms, and the reprojection error looks *fine* because it is evaluated on the same degenerate set. Symptom: good calibration numbers, bad measurements at the frame periphery.

    **Stereo range expectations set linearly.** A rig with 1 cm accuracy at 2 m has 4 cm accuracy at 4 m and 25 cm at 10 m. Specifications written as "±1 cm" without a range are meaningless.

    **Brightness constancy violated.** Optical flow fails where lighting changes, surfaces are specular, or objects occlude. These are usually the moments of interest. Symptom: large, confident, wrong flow vectors at object boundaries — and the algorithm does not flag them.

    **Aperture problem ignored.** Along a featureless edge, only the normal component of motion is observable. A flow field over a striped or textureless region is partly fabricated by the smoothness prior.

    **RANSAC threshold mis-set.** Too tight rejects genuine inliers and the model is fitted to a handful of points; too loose admits outliers and the estimate drifts. Always inspect the inlier fraction, not just the returned model.

    **Homography from four nearly collinear points.** Degenerate configuration — the system is rank-deficient and returns garbage that may still have low residual on those four points. Check the spread of the sample.

    **Feature matching without a ratio test.** Lowe's ratio test (best/second-best distance < 0.7–0.8) removes ambiguous matches. Without it, repetitive texture — brickwork, foliage, ocean — produces confident wrong correspondences.

    <!-- Add your own here. -->

## Worked example

Stereo depth error, which decides the rig before any algorithm does:

```python
f_px, baseline_m, disp_precision_px = 800.0, 0.12, 0.25

print(f"{'range (m)':>10} {'disparity (px)':>15} {'depth error (m)':>17}")
for Z in (1.0, 2.0, 5.0, 10.0, 20.0):
    d = f_px * baseline_m / Z
    dZ = Z**2 / (f_px * baseline_m) * disp_precision_px
    print(f"{Z:10.1f} {d:15.2f} {dZ:17.4f}")
```

```
 range (m)  disparity (px)   depth error (m)
       1.0           96.00            0.0026
       2.0           48.00            0.0104
       5.0           19.20            0.0651
      10.0            9.60            0.2604
      20.0            4.80            1.0417
```

Two-and-a-half millimetres at 1 m, and a full metre at 20 m — a 400-fold degradation over a 20-fold range increase. No matching algorithm changes this; only \(f\), \(B\), or sub-pixel disparity precision do.

## Connections

- [Image fundamentals](image-fundamentals.md) — the filtering and geometry this builds on.
- [Detection and segmentation](detection-segmentation.md) — what learning replaced, and what it did not.
- [Scientific imagery](scientific-imagery.md) — calibration for measurement rather than perception.

## Sources

- Hartley & Zisserman, *Multiple View Geometry in Computer Vision*.
- Szeliski, *Computer Vision: Algorithms and Applications*.
- Zhang (2000), *A flexible new technique for camera calibration*.
