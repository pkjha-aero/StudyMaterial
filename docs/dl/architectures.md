---
title: Architectures
status: working
tags: [pillar-9, deep-learning, cnn, transformer, unet, gnn]
updated: 2026-09-26
---

# Architectures

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - An architecture is an **encoded prior about structure**: convolution assumes locality and translation equivariance, attention assumes any token may matter, graphs assume permutation invariance.
    - **Residual connections are what made depth trainable.** Everything deep is residual.
    - Attention is \(O(n^2)\) in sequence length — the single fact that shapes transformer engineering.
    - **U-Net's skip connections carry spatial detail** that the bottleneck destroys; that is why it dominates dense prediction.
    - Positional information must be *added* to a transformer, because attention alone is permutation-invariant.

## Key results

**Convolution.** Parameters independent of input size, local receptive field, translation equivariance:

<div class="result" markdown>

\[
(f * k)(i,j) = \sum_{m}\sum_{n} f(i-m, j-n)\,k(m,n)
\]

Receptive field after \(L\) layers of kernel \(k\), stride 1: \(1 + L(k-1)\). Dilation \(d\) multiplies the growth without adding parameters.

</div>

**Residual block.** The gradient path that makes depth work:

\[
y = x + \mathcal{F}(x)
\qquad\Longrightarrow\qquad
\frac{\partial y}{\partial x} = I + \frac{\partial \mathcal{F}}{\partial x}
\]

The identity term guarantees gradient flow even when \(\partial\mathcal F/\partial x\) is small — which is why 100-layer networks train at all.

**Attention:**

\[
\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\!\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}}\right)V
\]

The \(\sqrt{d_k}\) scaling keeps the logits from growing with dimension and saturating the softmax. Multi-head attention runs \(h\) of these in parallel subspaces and concatenates.

Cost: \(O(n^2 d)\) time and \(O(n^2)\) memory for naive attention. FlashAttention removes the memory term by never materialising the matrix; sparse, linear, and sliding-window variants attack the time term with different approximations.

**Architecture families and their priors:**

| Family | Prior | Natural data |
|---|---|---|
| MLP | none beyond smoothness | fixed-size vectors |
| CNN | locality, translation equivariance | images, grids, fields |
| RNN / LSTM | sequential, Markov-ish state | streaming, short sequences |
| Transformer | any-to-any, learned relevance | language, long-range dependence |
| U-Net | multiscale + detail preservation | segmentation, dense prediction |
| GNN | permutation invariance, sparse relations | meshes, molecules, networks |

**U-Net.** Encoder downsamples to capture context, decoder upsamples to restore resolution, and **skip connections** concatenate matching encoder features into the decoder. Without the skips, fine spatial detail is irrecoverable after the bottleneck. This is why U-Net is the default for segmentation, and why it transfers so well to scientific fields on grids.

**Graph networks.** Message passing:

\[
h_v^{(k+1)} = \phi\left(h_v^{(k)},\ \bigoplus_{u\in\mathcal{N}(v)}\psi\left(h_v^{(k)}, h_u^{(k)}, e_{uv}\right)\right)
\]

with \(\bigoplus\) a permutation-invariant aggregator (sum, mean, max). \(k\) rounds propagate information \(k\) hops, which is why depth and receptive field are coupled the way they are on unstructured meshes.

**Positional encoding.** Attention is permutation-invariant, so order must be injected — sinusoidal (fixed), learned absolute, or rotary (RoPE, which encodes relative position in the attention product and extrapolates better).

## Mental model

Choose the architecture whose built-in assumption matches the data's actual symmetry. A CNN on images works because a cat is a cat wherever it appears — translation equivariance is true of the problem. Apply a CNN where that symmetry does not hold and you are paying for a constraint that buys nothing.

Transformers make the opposite bet: assume nothing about which positions relate, and learn it. That is more general and strictly more expensive, which is the trade. With enough data the learned relation beats the assumed one; without it, the built-in prior wins.

## Numerics / practice

- **Compute the receptive field** before believing a CNN can see the feature you care about. It is a common and easily checked mismatch.
- **Match the aggregator to the semantics** in a GNN: sum preserves count information, mean does not; max is robust to neighbourhood size.
- **Pre-norm over post-norm** for deep transformers — it trains stably without careful warmup tuning.
- **Use FlashAttention** or the fused SDPA path where available; the memory saving is what makes long contexts feasible.

??? warning "Failure modes"
    **Receptive field smaller than the feature.** A stack of 3×3 convolutions has a surprisingly small receptive field — ten layers reaches 21 pixels. If the object of interest spans 200 pixels, the network physically cannot see it whole. Symptom: performance that plateaus regardless of width, data, or training length. Fix: dilation, pooling, or attention.

    **Positional encoding omitted or wrong.** A transformer without positional information treats the input as a bag. Symptom: the model works but ignores order — plausible on some tasks, catastrophic on others. Related: absolute encodings that do not extrapolate beyond the trained sequence length.

    **Over-smoothing in deep GNNs.** After many message-passing rounds, all node representations converge to the same value and the network loses discriminative power. Most GNNs stop at 2–4 layers for this reason. Symptom: accuracy *decreasing* with depth, which is the opposite of the usual intuition.

    **Skip connections dropped from a U-Net variant.** Someone simplifies the architecture, keeps the encoder-decoder shape, and the output becomes blurry. The skips are not an optimisation detail — they are the mechanism.

    **Quadratic attention on long inputs.** Memory scales as \(n^2\). Doubling sequence length quadruples it, and OOM arrives abruptly. Budget it before designing the input format.

    **BatchNorm inside a residual block at inference.** Train/eval discrepancy compounds through depth. Symptom: large train/eval gap that is not overfitting — it closes if you keep BatchNorm in training mode at eval, which is the diagnostic.

    **Mismatched padding in an encoder-decoder.** Odd input dimensions produce shape mismatches at skip-connection concatenation, usually solved by cropping — which then silently misaligns features by a pixel or two. Prefer input sizes divisible by \(2^{\text{depth}}\).

    <!-- Add your own here. -->

## Worked example

Receptive field, which is easy to get wrong by an order of magnitude:

```python
def receptive_field(layers):
    """layers: list of (kernel, stride, dilation)"""
    rf, jump = 1, 1
    for k, s, d in layers:
        rf += (k - 1) * d * jump
        jump *= s
    return rf

plain    = [(3, 1, 1)] * 10
strided  = [(3, 2, 1) if i % 2 else (3, 1, 1) for i in range(10)]
dilated  = [(3, 1, 2**i) for i in range(6)]

print(f"10x conv3 stride1        : {receptive_field(plain):5d} px")
print(f"10x conv3, every 2nd s=2 : {receptive_field(strided):5d} px")
print(f"6x conv3 dilated 1..32   : {receptive_field(dilated):5d} px")
```

```
10x conv3 stride1        :    21 px
10x conv3, every 2nd s=2 :   125 px
6x conv3 dilated 1..32   :   127 px
```

Ten plain 3×3 layers see 21 pixels. Adding strides reaches 125 with the same kernel count; six dilated layers reach 127 with 40% fewer layers. If your target feature is 100 px across, the first network cannot represent it at all — and nothing in the loss curve will say so.

## Connections

- [PyTorch patterns](pytorch-patterns.md) — implementing these.
- [ML › Training craft](../ml/training-craft.md) — making them converge.
- [CV](../cv/index.md) — where CNNs and U-Nets are applied.
- [SciML › GNN on meshes](../sciml/index.md) — graph networks on unstructured grids.

## Sources

- Vaswani et al. (2017), *Attention Is All You Need*.
- He et al. (2016), *Deep Residual Learning for Image Recognition*.
- Ronneberger et al. (2015), *U-Net*.
- Battaglia et al. (2018), *Relational inductive biases, deep learning, and graph networks*.
