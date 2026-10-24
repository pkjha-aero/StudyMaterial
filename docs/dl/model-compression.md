---
title: Model compression and edge deployment
status: working
tags: [pillar-5, deep-learning, performance, neural-networks]
updated: 2026-10-24
---

# Model compression and edge deployment

<span class="status status-working">working</span>
<span class="pillar">pillar 5 &middot; Programming and software engineering</span>

!!! abstract "In one minute"
    - Edge inference is bound by **memory bandwidth and energy**, not by arithmetic. Compression is mostly about moving fewer bytes.
    - **Quantisation** is the highest-return technique by a wide margin: INT8 gives roughly 4× the memory and bandwidth of FP32 for typically under 1% accuracy loss — *if the granularity is right*.
    - **Per-tensor versus per-channel** quantisation is not a detail. With realistic channel scale spread, per-tensor INT8 can destroy whole channels.
    - **Structured pruning** gives real speed-up; unstructured pruning gives compression that most hardware cannot exploit.
    - The deployed artefact is not the trained model. Export, graph optimisation and kernel selection all change numerics, so **validate the thing you ship**.

## Key results

### What actually costs you at the edge

| Resource | Why it binds | What helps |
|---|---|---|
| **Memory bandwidth** | Weights must be read every inference | Quantisation, smaller models |
| **Energy per inference** | DRAM access costs ~100–1000× a MAC | Keep weights in on-chip SRAM |
| **Peak memory** | Activations at the widest layer | Tiling, operator fusion, lower precision |
| **Latency tail** | p99 is the product requirement, not p50 | Fixed shapes, no dynamic allocation |
| Raw FLOPs | Rarely the limit | Rarely the right target |

Optimising FLOPs is the standard instinct and usually the wrong one. A depthwise-separable convolution cuts FLOPs dramatically and often runs no faster, because it is bandwidth-bound and poorly served by the available kernels.

### Quantisation

Map a float tensor to integers with a scale (and optionally a zero point):

<div class="result" markdown>

\[
q = \mathrm{round}\!\left(\frac{w}{s}\right),\qquad s = \frac{\max|w|}{2^{b-1}-1}
\]

</div>

The choices that matter:

- **Granularity.** One scale per tensor, or one per output channel. Per-channel costs a vector of scales and is almost always worth it — the worked example shows why.
- **Symmetric vs asymmetric.** Symmetric (zero point 0) is cheaper; asymmetric fits skewed activation distributions, which matters after ReLU.
- **Static vs dynamic.** Static calibrates activation ranges offline from a representative set; dynamic computes them per batch, which costs time but handles distribution shift.
- **PTQ vs QAT.** Post-training quantisation needs a few hundred calibration samples and an afternoon. Quantisation-aware training simulates the rounding in the forward pass with a straight-through estimator on the backward pass, costs a retrain, and recovers most of what PTQ loses below 8 bits.

Rules of thumb worth knowing and worth re-measuring: INT8 PTQ is usually within 1% top-1; INT4 generally needs QAT; and the first and last layers are routinely kept at higher precision because they are small and sensitive.

### Pruning

| Kind | Removes | Speed-up on normal hardware |
|---|---|---|
| **Unstructured** | Individual weights | **None** without sparse kernels — a sparse matrix stored densely is the same size |
| **Structured** | Whole channels, filters, heads, blocks | Real, because the tensor genuinely shrinks |
| **Semi-structured (2:4)** | 2 of every 4 weights | Real on hardware with sparse tensor cores |

The honest summary: unstructured pruning produces impressive sparsity percentages and usually no wall-clock gain. Structured pruning produces smaller numbers and actual speed-up. Report latency, not sparsity.

### Distillation

Train a small student against a large teacher's **soft outputs** rather than hard labels. The soft distribution carries relative class similarity — the "dark knowledge" — which is more informative per sample than a one-hot target. Usually combined with a ground-truth loss, and often with intermediate feature matching. It is the technique that most reliably shrinks a model by a large factor when quantisation and pruning have run out, and it costs a full training run.

### The deployment path

ONNX export → graph optimisation (constant folding, operator fusion, layout transforms) → a runtime that selects kernels for the target (TensorRT, ONNX Runtime, TFLite, CoreML, OpenVINO).

Each stage can change numerics. Fused convolution-batchnorm-ReLU is not bitwise identical to the three operations run separately; a different kernel may accumulate in a different order; TF32 or reduced-precision accumulation may be enabled by default. None of this is a bug, and all of it means **the exported artefact needs its own accuracy check**.

## Mental model

Compression trades a known, measurable accuracy loss for a known, measurable resource gain, and the whole discipline is about keeping both sides measured. The failure mode is treating it as free — applying INT8 because it is standard, never checking per-channel behaviour, and discovering the regression in the field.

The second idea is that **the hardware decides which techniques are real**. Sparsity is a speed-up only if there are sparse kernels; INT8 is a speed-up only if there are INT8 kernels; a clever architecture is fast only if someone wrote a kernel for it. The question is never "is this smaller" but "is this faster on the chip I am shipping to."

## Numerics / practice

- **Profile before compressing.** Find whether you are bandwidth- or compute-bound; the answer changes which technique helps.
- **Use per-channel weight quantisation by default**, and per-tensor only after measuring that it is adequate.
- **Calibrate on in-distribution data**, several hundred samples, covering the operating range. Calibration on a convenient subset produces ranges that clip in deployment.
- **Measure p95 and p99 latency**, with fixed input shapes and no allocation in the inference path.
- **Compare the exported model against the trained model** on a held-out set, numerically, as a gate in CI.
- **Watch the first and last layers**, and any layer feeding a softmax or a regression head with a wide dynamic range.

??? warning "Failure modes"
    **Per-tensor quantisation on weights with wide channel-scale spread.** A single scale is set by the largest channel, so small channels receive a handful of quantisation levels and the smallest may round entirely to zero. The average error looks acceptable and specific channels are destroyed — see the worked example.

    **Accuracy checked on the training framework, not the exported artefact.** Export, fusion and kernel selection all change numerics. The number that matters comes from the runtime you ship.

    **Calibration set unrepresentative.** Activation ranges derived from clean daytime images clip at night, in rain, or on a different camera. The failure is silent and condition-dependent, which makes it hard to reproduce from a bug report.

    **Unstructured sparsity reported as speed-up.** 90% sparsity in a dense tensor is 0% speed-up without sparse kernel support. The metric to report is latency.

    **FLOPs optimised instead of latency.** FLOP reduction and wall-clock reduction are only loosely related on memory-bound workloads, and some low-FLOP operators have no efficient kernel at all.

    **Batch-norm folded without re-checking ranges.** Folding changes the effective weight distribution, often widening the per-channel scale spread, which is exactly what breaks per-tensor quantisation. Quantise after folding, not before.

    **Mean latency used as the requirement.** Real-time systems fail on the tail. A model with good mean latency and a long p99 drops frames exactly when the scene is busy, which is when it mattered.

    **One accuracy number for the whole model.** Compression damage is uneven — by class, by object size, by condition. Aggregate accuracy can hold while the rare-but-critical class collapses.

    <!-- Add your own here. -->

## Worked example

Why quantisation granularity is not a detail:

```python
import numpy as np
rng = np.random.default_rng(0)

# A linear layer whose output channels have very different weight scales -- the normal
# situation in a trained network, especially after BatchNorm folding.
C_out, C_in = 64, 256
scales = np.exp(rng.normal(0, 1.4, C_out))          # channel scales span orders of magnitude
W = rng.normal(0, 1, (C_out, C_in)) * scales[:, None]

def quantise(W, per_channel, bits=8):
    qmax = 2**(bits-1) - 1
    s = (np.abs(W).max(axis=1, keepdims=True) if per_channel else np.abs(W).max()) / qmax
    return np.round(W/s).clip(-qmax-1, qmax) * s

print(f"weight tensor {W.shape}, channel scale spread "
      f"{scales.max()/scales.min():.0f}x (max/min)")
print(f"{'scheme':<14}{'bits':>6}{'overall rel err':>18}{'worst channel':>16}")
for bits in (8, 6, 4):
    for pc in (False, True):
        Q = quantise(W, pc, bits)
        err = np.linalg.norm(Q-W)/np.linalg.norm(W)
        per = np.linalg.norm(Q-W, axis=1)/np.linalg.norm(W, axis=1)
        print(f"{'per-channel' if pc else 'per-tensor':<14}{bits:6d}"
              f"{err:18.5f}{per.max():16.5f}")

print("\nwhy per-tensor fails: the scale is set by the LARGEST channel,")
print("so small channels get almost no quantisation levels.")
q8 = 127
s_t = np.abs(W).max()/q8
for pct, name in ((100, "largest"), (50, "median"), (5, "5th percentile")):
    ch = np.argsort(np.abs(W).max(axis=1))[int((pct/100)*(C_out-1))]
    used = int(np.abs(W[ch]).max()/s_t)
    print(f"   {name:16s} channel uses {used:4d} of {q8} available levels"
          f"  ({100*used/q8:5.1f}%)")
```

```
weight tensor (64, 256), channel scale spread 403x (max/min)
scheme          bits   overall rel err   worst channel
per-tensor         8           0.02515         1.00000
per-channel        8           0.00673         0.00933
per-tensor         6           0.09500         1.00000
per-channel        6           0.02777         0.03652
per-tensor         4           0.31347         1.00000
per-channel        4           0.12235         0.17604

why per-tensor fails: the scale is set by the LARGEST channel,
so small channels get almost no quantisation levels.
   largest          channel uses  126 of 127 available levels  ( 99.2%)
   median           channel uses    9 of 127 available levels  (  7.1%)
   5th percentile   channel uses    1 of 127 available levels  (  0.8%)
```

The overall error column makes per-tensor INT8 look tolerable: 2.5% relative error against 0.7% for per-channel. The next column is the problem. **The worst channel has a relative error of exactly 1.0** — that channel has been quantised entirely to zero and contributes nothing at all. The model has silently lost a feature, and an aggregate metric averaged over 64 channels will barely register it.

The breakdown underneath explains the mechanism without any appeal to subtlety. The per-tensor scale is set by the largest-magnitude channel, which then uses 126 of the 127 available levels. The median channel gets **9**. The 5th-percentile channel gets **1** — it is a binary feature now.

This is the normal situation rather than a constructed one: trained networks routinely show one to two orders of magnitude of spread in per-channel weight scale, and folding batch normalisation into the preceding convolution widens it further. Per-channel scales cost one float per output channel, a rounding error in model size, and they remove the failure entirely — the worst-channel error drops from 1.0 to 0.009.

The same argument explains why INT4 needs quantisation-aware training. At 4 bits the per-channel scheme is already at 12% worst-channel error, so there are no longer enough levels to absorb the rounding passively and the network has to be retrained to tolerate it.

## Connections

- [PyTorch patterns](pytorch-patterns.md) — the training side, and where QAT hooks in.
- [Architectures](architectures.md) — what is being compressed.
- [Computing › MLOps and deployment](../computing/mlops.md) — serving, containers and monitoring.
- [Computing › GPU and CUDA](../computing/gpu-cuda.md) — why bandwidth rather than FLOPs binds.
- [CV › Detection and segmentation](../cv/detection-segmentation.md) — the models most often deployed at the edge.
- [ML › Evaluation](../ml/evaluation.md) — measuring the damage honestly, per class.

## Sources

- Jacob et al., "Quantization and training of neural networks for efficient integer-arithmetic-only inference", CVPR (2018).
- Krishnamoorthi, "Quantizing deep convolutional networks for efficient inference: a whitepaper", arXiv (2018) — the per-channel argument.
- Nagel et al., "A white paper on neural network quantization", Qualcomm AI Research (2021).
- Hinton, Vinyals & Dean, "Distilling the knowledge in a neural network", NIPS workshop (2015).
- Blalock et al., "What is the state of neural network pruning?", MLSys (2020) — on how rarely pruning results are comparable.
- NVIDIA TensorRT and ONNX Runtime documentation for the export and kernel-selection path.
