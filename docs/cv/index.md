---
title: Computer Vision
status: working
tags: [pillar-9, computer-vision]
---

# Computer Vision

<span class="status status-working">working</span>
<span class="pillar">pillar 9</span>

Image fundamentals through modern detection, with an eye to scientific imagery.
An **active growth area**.

## Pages

| Page | Covers |
|---|---|
| [Image fundamentals](image-fundamentals.md) | Sampling and aliasing, filtering, gamma, colour, the pinhole model, interpolation |
| [Classical computer vision](classical-cv.md) | Features, RANSAC, epipolar geometry, stereo depth error, optical flow, calibration |
| [Detection and segmentation](detection-segmentation.md) | The four tasks and their metrics, NMS, focal loss, anchor and set-prediction families |
| [Vision-language models](vlms.md) | Contrastive alignment, generative VLM structure, what they cannot do |
| [Scientific and remote-sensing imagery](scientific-imagery.md) | Radiometry, spectral indices, georeferencing, spatial CV, fire detection |

## The theme

**Deep learning replaced the matching, not the geometry.** Which pixel corresponds to
which is now learned, and learned well. Triangulation, calibration, the epipolar
constraint and the \(Z^2\) depth-error law are unchanged, because they are statements
about projection rather than about appearance.

Most production systems are therefore hybrids: learn the correspondences, solve the
geometry classically. Knowing which half of a pipeline is which is what lets you diagnose
it — a depth error that scales as \(Z^2\) is geometry, and no amount of retraining will
move it.

## A note for the scientific case

[Scientific imagery](scientific-imagery.md) is the page that departs most from standard CV
practice, because the pixels are **measurements with units**. Normalising to 8-bit,
bilinear-resampling a class map, or splitting spatially-correlated pixels at random are all
routine in vision work and all destroy something in a radiometric product.

## Connections

- [Deep Learning](../dl/index.md) — the backbones and architectures.
- [Meteorology › Fire weather](../meteorology/fire-weather.md) — what the detections feed.
- [Scientific ML](../sciml/index.md) — imagery as one modality among several.
