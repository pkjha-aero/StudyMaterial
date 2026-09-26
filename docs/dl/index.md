---
title: Deep Learning
status: working
tags: [pillar-9, deep-learning]
---

# Deep Learning

<span class="status status-working">working</span>
<span class="pillar">pillar 9</span>

Architectures, the implementation patterns that recur, and generative modelling.
An **active growth area**.

## Pages

| Page | Covers |
|---|---|
| [Architectures](architectures.md) | MLP, CNN, RNN, Transformer, U-Net, GNN — and the prior each encodes |
| [PyTorch patterns](pytorch-patterns.md) | Training loops, data pipelines, distributed training, mixed precision |
| [Generative models](generative.md) | VAEs, GANs, diffusion, and what each sacrifices |
| [LLMs and generative AI](llm-genai.md) | Autoregressive generation, RAG, fine-tuning, agents |

## The theme

An architecture is **an assumption about structure, made cheap**. Convolution assumes
locality and translation equivariance. Attention assumes anything may be relevant and
learns which. Graph networks assume permutation invariance. U-Net assumes multiscale
structure with detail worth preserving.

Choosing well means matching the assumption to a symmetry the data actually has. Where it
holds, the prior buys data efficiency for free; where it does not, you are paying for a
constraint that only limits you — and where you have no idea, attention's
learn-the-relation approach is the expensive general answer.

## A note on volatility

[LLMs and generative AI](llm-genai.md) deliberately omits model names, prices and context
limits. Those change on a timescale of weeks, and a recap page that carried them would be
confidently wrong within a month. Mechanisms and failure modes are what belongs in a
durable note; specifics belong in the provider's live documentation.

## Connections

- [Machine Learning](../ml/index.md) — classical methods and the evaluation discipline.
- [Computer Vision](../cv/index.md) — where most of these architectures are applied.
- [Scientific ML](../sciml/index.md) — the same tools with physics as structure.
