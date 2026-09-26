---
title: Vision-language models
status: working
tags: [pillar-9, computer-vision, neural-networks]
updated: 2026-09-26
---

# Vision-language models

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! warning "Model-specific details are omitted on purpose"
    Named models, benchmark scores and context limits in this area change monthly. What
    is below is the mechanism and the failure modes, which have been stable. For current
    capability, test on your own data — published benchmarks in this area saturate and
    leak faster than almost anywhere else in ML.

!!! abstract "In one minute"
    - **Contrastive pretraining** (CLIP-style) aligns image and text embeddings in a shared space, which is what makes zero-shot classification by text prompt possible.
    - A generative VLM is usually **a vision encoder bolted to a language model** through a projection layer — most of the capability comes from the language half.
    - Zero-shot performance tracks **how well your domain is represented in web-scale training data**. Natural images: excellent. Scientific imagery: often poor.
    - **They cannot count or localise reliably**, and they will answer confidently anyway.
    - Prompt phrasing changes results materially, which means prompts need evaluating like hyperparameters.

## Key results

**Contrastive alignment.** Train image encoder \(f\) and text encoder \(g\) so matched pairs are close and mismatched pairs far, using the InfoNCE loss over a batch of \(N\) pairs:

<div class="result" markdown>

\[
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N}\log
\frac{\exp\left(\langle f(I_i), g(T_i)\rangle/\tau\right)}
{\sum_{j=1}^{N}\exp\left(\langle f(I_i), g(T_j)\rangle/\tau\right)}
\]

</div>

Symmetrised over both directions. \(\tau\) is a learned temperature. **Large batches matter**, because every other item in the batch is a negative — this is why contrastive pretraining is compute-hungry in a way that is about batch size rather than parameters.

**Zero-shot classification.** Embed candidate class names as text ("a photo of a {class}"), embed the image, take the nearest. No training on the target classes at all — the alignment does the work.

**Generative VLM architecture:**

```
image ──► vision encoder ──► projection ──► ┐
                                            ├──► language model ──► text
text  ──────────── tokenizer ──────────────►┘
```

The projection maps visual features into the language model's token embedding space, so images become "tokens" the LM can attend over. Training usually proceeds in stages: align the projection with the rest frozen, then instruction-tune.

**What they are good and bad at:**

| Reliable | Unreliable |
|---|---|
| Scene description, general VQA | Counting beyond small numbers |
| OCR in natural images | Precise spatial relations and localisation |
| Coarse classification | Fine-grained domain distinctions |
| Common-sense reasoning about content | Measurement of any kind |

**Prompt sensitivity.** Zero-shot accuracy varies by several points with template wording, and prompt ensembling (averaging embeddings over several templates) is a standard, cheap improvement.

## Mental model

A contrastive model learns a shared space where "a photo of a dog" and a picture of a dog land near each other. That is all it learns — which is why it generalises so well to naming things and so poorly to questions the training captions never answered. Web captions say what is in a picture; they rarely say how many, how far apart, or how large.

A generative VLM inherits the language model's fluency along with its willingness to produce an answer regardless of whether the visual evidence supports one. The vision encoder supplies evidence; the language model supplies confidence. Those are decoupled, and that is the root of most failures here.

## Numerics / practice

- **Evaluate on your own labelled sample** before deploying. Published benchmarks in this area are saturated and partially contaminated.
- **Ensemble prompt templates** for zero-shot classification; it is free accuracy.
- **Use linear probing to measure representation quality**: freeze the encoder, fit a linear classifier. It separates "the features are good" from "the zero-shot prompt is good".
- **Ask for structured output** (JSON with a schema) when the result feeds a pipeline, and validate it — free-text parsing is fragile.

??? warning "Failure modes"
    **Zero-shot assumed to transfer to scientific imagery.** Contrastive models are trained on web images with web captions. Radar reflectivity, thermal imagery, microscopy and satellite bands are barely represented, and zero-shot performance there can be near chance while remaining confident. Always measure rather than assume.

    **Counting.** VLMs are unreliable beyond roughly four or five objects and produce a plausible number regardless. If a count matters, use a detector and count boxes.

    **Spatial relations and localisation.** "Left of", "above", "nearest to" are answered inconsistently. Some models emit bounding boxes; their coordinates are approximate and should not be used for measurement.

    **Benchmark contamination.** Web-scale pretraining corpora include many public benchmark images and, sometimes, their labels. High reported scores may partly reflect memorisation. This is one of the strongest arguments for a private evaluation set.

    **Prompt phrasing treated as incidental.** Accuracy can shift by several points on wording alone. Two prompts, one comparison, and a conclusion about a *model* is not supported.

    **Hallucinated detail.** Asked to describe an image, a VLM will produce fluent detail not present in it — objects, text, relationships. Increases with longer requested outputs. Anything consequential needs verification outside the model.

    **Resolution loss in the vision encoder.** Many encoders downsample to a fixed modest resolution, so fine detail — small text, thin structures, distant objects — is gone before the language model ever sees it. Tiling or a high-resolution variant is needed, and no amount of prompting recovers information the encoder discarded.

    <!-- Add your own here, with the model and date — behaviour changes between versions. -->

## Worked example

Why contrastive pretraining is batch-size hungry — the task gets harder, and more informative, as the batch grows:

```python
import numpy as np

print(f"{'batch':>8} {'negatives/sample':>18} {'chance acc':>12} {'bits/sample':>13}")
for N in (16, 256, 4096, 32768):
    chance = 1.0 / N
    bits = np.log2(N)
    print(f"{N:8d} {N-1:18d} {chance:12.2e} {bits:13.1f}")
```

```
   batch   negatives/sample   chance acc   bits/sample
      16                 15     6.25e-02           4.0
     256                255     3.91e-03           8.0
    4096               4095     2.44e-04          12.0
   32768              32767     3.05e-05          15.0
```

Each sample's task is to pick the right caption out of \(N\). At batch 16 that is a 1-in-16 guess worth 4 bits; at 32,768 it is 15 bits. Nearly four times the supervisory signal per image for the same data — which is why these models are trained with batch sizes that require hundreds of accelerators, and why small-batch reproductions underperform badly.

## Connections

- [Detection and segmentation](detection-segmentation.md) — when you need boxes rather than descriptions.
- [Scientific imagery](scientific-imagery.md) — the domain where zero-shot transfer is weakest.
- [DL › LLMs and generative AI](../dl/llm-genai.md) — the language half, and the same volatility caveat.
- [ML › Evaluation](../ml/evaluation.md) — why a private eval set matters here.

## Sources

- Radford et al. (2021), *Learning Transferable Visual Models From Natural Language Supervision* (CLIP).
- Alayrac et al. (2022), *Flamingo* — the frozen-LM + adapter pattern.
- Your own evaluation set, for anything current.
