---
title: Generative models
status: working
tags: [pillar-9, deep-learning, gan, vae, diffusion]
updated: 2026-09-26
---

# Generative models

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - All generative models approximate \(p(x)\); they differ in **whether the likelihood is tractable** and what they sacrifice for sample quality.
    - **VAEs** optimise a bound on the likelihood, train stably, and produce blurry samples. The blur is a consequence of the objective, not a bug.
    - **GANs** produce sharp samples through an adversarial game that has no convergence guarantee and can collapse.
    - **Diffusion models** learn to reverse a noising process. Stable training, excellent samples, slow sampling — and the current default.
    - **FID is a flawed metric** but the standard one; it measures distribution overlap in a feature space, not correctness.

## Key results

**The three families:**

<div class="result" markdown>

| | Likelihood | Training | Samples | Sampling cost |
|---|---|---|---|---|
| VAE | lower bound (ELBO) | stable | blurry | one pass |
| GAN | implicit, none | adversarial, fragile | sharp | one pass |
| Diffusion | bound / score matching | stable | excellent | many passes |
| Normalizing flow | exact | stable | good | one pass |

</div>

**VAE.** Maximise the evidence lower bound:

\[
\mathcal{L} = \underbrace{\mathbb{E}_{q(z|x)}\left[\log p(x|z)\right]}_{\text{reconstruction}}
- \underbrace{D_{KL}\left(q(z|x)\,\|\,p(z)\right)}_{\text{regularisation}}
\]

The reparameterisation trick \(z = \mu + \sigma\odot\epsilon\), \(\epsilon\sim\mathcal N(0,I)\), makes the sampling differentiable. Blurriness comes from the Gaussian likelihood: averaging over plausible reconstructions minimises squared error, and the average of sharp images is blurry.

**GAN.** A minimax game:

\[
\min_G \max_D\ \mathbb{E}_{x\sim p_{\text{data}}}[\log D(x)] + \mathbb{E}_{z\sim p_z}[\log(1-D(G(z)))]
\]

There is no loss whose decrease means progress — the two losses move against each other, so they are almost uninformative about sample quality. WGAN-GP replaces the objective with a Wasserstein distance plus gradient penalty, which correlates better with quality and trains more reliably.

**Diffusion.** Forward process adds noise over \(T\) steps:

\[
q(x_t | x_{t-1}) = \mathcal{N}\left(x_t;\ \sqrt{1-\beta_t}\,x_{t-1},\ \beta_t I\right),
\qquad
x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon
\]

The model learns to predict the noise, and the training objective reduces to something remarkably simple:

\[
\mathcal{L} = \mathbb{E}_{t,x_0,\epsilon}\left[\left\|\epsilon - \epsilon_\theta(x_t, t)\right\|^2\right]
\]

A plain regression loss — which is why diffusion training is so much more stable than adversarial training. Sampling reverses the chain, and the cost is the \(T\) (or, with DDIM and distillation, far fewer) forward passes required.

**Classifier-free guidance** trades diversity for fidelity by extrapolating between conditional and unconditional predictions:

\[
\tilde\epsilon = \epsilon_\theta(x_t, \varnothing) + w\left(\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing)\right)
\]

**Latent diffusion** runs the process in a compressed autoencoder latent space rather than pixel space, which is what made high-resolution generation affordable.

## Mental model

Generative modelling is the problem of learning a distribution from samples, and each family makes a different concession to make it tractable.

The VAE says: assume a simple latent distribution and a simple likelihood, and accept the blur that the likelihood imposes. The GAN says: forget the likelihood entirely, and instead train a critic that cannot tell real from fake — sharp, but with no objective measure of progress. Diffusion says: turn one hard problem into a thousand easy ones, each a small denoising step, and pay for it at sampling time.

That reframing explains the field's trajectory: diffusion won because stable training on a regression loss beats an unstable game, and sampling cost turned out to be the easier problem to optimise.

## Numerics / practice

- **Use \(v\)-prediction or \(\epsilon\)-prediction** with a cosine noise schedule; the original linear schedule wastes steps at high noise.
- **EMA of the weights** is close to mandatory for diffusion sample quality — often a larger effect than architecture changes.
- **Report FID with the sample count**, since it is biased downward with more samples and is not comparable across counts.
- **Look at samples.** Every metric here is a proxy, and visual inspection catches failures that FID does not.

??? warning "Failure modes"
    **GAN mode collapse.** The generator finds a few outputs that fool the discriminator and stops covering the distribution. Samples look good individually and are nearly identical. Losses look *normal* throughout — this is the defining problem with adversarial training and the reason generator/discriminator loss curves are not a progress signal.

    **Posterior collapse in a VAE.** With a powerful decoder, the KL term drives \(q(z|x)\) to the prior and the latent carries no information — the decoder ignores \(z\) entirely. Symptom: KL term near zero and reconstructions that ignore the input. Fix: KL annealing, free bits, or a weaker decoder.

    **Reading FID as correctness.** FID measures the distance between Inception feature statistics of two sets. It is sensitive to resolution, sample count, and preprocessing, and it can be gamed. Two models with identical FID can differ obviously by eye.

    **Guidance scale too high.** Large classifier-free guidance produces saturated, over-sharpened, low-diversity samples that score well on fidelity metrics and are visibly wrong. There is a sweet spot and it is task-dependent.

    **No EMA on diffusion weights.** Raw weights produce noticeably worse samples than an exponential moving average of them. Easy to omit and easy to mistake for an architecture problem.

    **Training/sampling schedule mismatch.** Using a different noise schedule or timestep discretisation at sampling than at training degrades output subtly — often read as an undertrained model.

    **Generative model used for scientific extrapolation.** These models reproduce the training distribution. Samples outside it are not predictions; they are interpolation artefacts with no physical constraint. This matters directly for [SciML](../sciml/index.md) applications.

    <!-- Add your own here. -->

## Worked example

Why the diffusion objective is so much easier than the adversarial one — the noise schedule:

```python
import numpy as np

T = 1000
# linear schedule (original DDPM) vs cosine (improved)
beta_lin = np.linspace(1e-4, 0.02, T)
abar_lin = np.cumprod(1 - beta_lin)

s = 0.008
t = np.arange(T + 1) / T
f = np.cos((t + s) / (1 + s) * np.pi / 2) ** 2
abar_cos = (f / f[0])[1:]

print(" t/T    alphabar_linear   alphabar_cosine")
for frac in (0.1, 0.25, 0.5, 0.75, 0.9):
    i = int(frac * T) - 1
    print(f"{frac:4.2f}        {abar_lin[i]:.4f}            {abar_cos[i]:.4f}")
```

```
 t/T    alphabar_linear   alphabar_cosine
0.10        0.8970            0.9721
0.25        0.5241            0.8470
0.50        0.0786            0.4938
0.75        0.0034            0.1443
0.90        0.0003            0.0241
```

The linear schedule has destroyed almost all signal by \(t/T=0.5\) (\(\bar\alpha = 0.08\)) and effectively all of it by 0.75 (\(0.003\)), so the back half of the training steps see near-pure noise and teach the model very little. The cosine schedule still retains \(\bar\alpha = 0.49\) at the midpoint and \(0.14\) at three-quarters — most of why it improved sample quality.

## Connections

- [Architectures](architectures.md) — U-Nets are the standard diffusion backbone.
- [LLMs and generative AI](llm-genai.md) — autoregressive generation, the other family.
- [CV](../cv/index.md) — where image generation is applied.
- [SciML](../sciml/index.md) — generative surrogates, and their extrapolation limits.

## Sources

- Kingma & Welling (2014), *Auto-Encoding Variational Bayes*.
- Goodfellow et al. (2014), *Generative Adversarial Networks*.
- Ho et al. (2020), *Denoising Diffusion Probabilistic Models*.
- Rombach et al. (2022), *High-Resolution Image Synthesis with Latent Diffusion Models*.
