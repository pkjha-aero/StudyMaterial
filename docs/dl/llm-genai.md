---
title: LLMs and generative AI
status: working
tags: [pillar-9, deep-learning, neural-networks]
updated: 2026-09-26
---

# LLMs and generative AI

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! warning "This page deliberately omits model names, prices and context limits"
    Those change on a timescale of weeks — model IDs, per-token prices, context windows,
    and even API parameter shapes have all churned repeatedly. A recap page that listed
    them would be wrong within a month and, worse, would *look* authoritative.

    What is below is the part that has stayed stable: mechanisms, architecture patterns,
    and failure modes. For anything current, go to the provider's own documentation —
    and for the Anthropic API specifically, this repository's Claude Code environment
    ships a `claude-api` skill whose whole purpose is to hold those volatile facts.

!!! abstract "In one minute"
    - An LLM is a next-token predictor. **Everything else — chat, tools, agents — is scaffolding** around that one operation.
    - **Retrieval beats fine-tuning for knowledge**; fine-tuning is for form, format and behaviour, not for facts.
    - **Context is a budget, not a container.** Filling it degrades attention to the middle and costs money linearly.
    - **Evaluation is the hard part.** Without a task-specific eval set, prompt "improvements" are indistinguishable from noise.
    - Agents are a loop, not a model feature — and the loop is where most of the engineering risk lives.

## Key results

**Autoregressive generation:**

<div class="result" markdown>

\[
p(x_{1:n}) = \prod_{i=1}^{n} p(x_i \mid x_{<i})
\]

</div>

Training maximises the log-likelihood of the next token. Every capability that emerges — reasoning, translation, code — is a consequence of doing that well over a large corpus, not a separately trained function.

**Decoding controls:**

| Parameter | Effect |
|---|---|
| Temperature | scales logits before softmax; \(\to0\) is greedy, \(>1\) flattens |
| Top-\(k\) | sample from the \(k\) most likely tokens |
| Top-\(p\) (nucleus) | sample from the smallest set with cumulative probability \(p\) |
| Repetition / frequency penalty | discourages loops |

Note that some current models no longer accept sampling parameters at all — another reason to check the provider docs rather than assume.

**Adaptation, from cheapest to most expensive:**

| Approach | Changes | Cost | Right for |
|---|---|---|---|
| Prompting | nothing | ~0 | most tasks; always try first |
| Few-shot | nothing | tokens | format and style demonstration |
| RAG | nothing | retrieval infra | knowledge that is large, private, or changing |
| LoRA / PEFT | small adapter | hours on one GPU | consistent format, tone, domain behaviour |
| Full fine-tune | all weights | large | rarely justified |
| Pretraining | all weights | very large | essentially never, outside labs |

**The rule that matters: retrieval for knowledge, fine-tuning for behaviour.** Fine-tuning a model on facts teaches it the *shape* of those facts more reliably than their content, and it cannot be updated without retraining. Retrieval puts the fact in the context where the model can read it, and updating means updating a document.

**RAG pipeline**, and where each stage fails:

1. **Chunk** — too small loses context, too large dilutes the embedding. Overlap helps.
2. **Embed and index** — a vector store, usually with approximate nearest neighbour search.
3. **Retrieve** — vector similarity alone is weak on exact terms; hybrid (vector + BM25) is materially better.
4. **Rerank** — a cross-encoder over the top \(k\) retrieved, which is often the single largest quality gain.
5. **Generate** — with the retrieved context, and an instruction to cite or abstain.

**LoRA.** Freeze \(W\), learn a low-rank update:

\[
W' = W + BA,
\qquad B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k},\ r \ll d
\]

At \(r=8\) this is a fraction of a percent of the parameters, trains on one GPU, and the adapter is a small file that can be swapped per task.

**Agents.** A loop: the model emits a tool call, the harness executes it, the result is appended, repeat until a stop condition. The model does not "run" anything — the harness does. Nearly all agent engineering is about the harness: what tools exist, what they return, how errors surface, when to stop, and what the model is allowed to do without approval.

## Mental model

Think of the context window as the model's entire world for one call. It has no memory between calls, no access to anything you did not put in front of it, and no way to verify what it was given. Every technique in this area is a way of deciding what goes in that window: prompting writes it by hand, few-shot adds examples, RAG fetches it, agents let the model request it.

That framing makes the fine-tuning decision easy. Fine-tuning changes how the model behaves given a context; it does not give it a bigger world. If the problem is "it does not know X", the answer is retrieval. If the problem is "it knows X but responds in the wrong shape", that is fine-tuning.

## Numerics / practice

- **Build an eval set before optimising anything.** Twenty to fifty real cases with known-good outputs is enough to stop guessing, and without it every change is a vibe.
- **Measure retrieval separately from generation.** If recall@k is 0.6, no prompt engineering will fix the answers.
- **Add a reranker before adding a bigger model.** It is usually cheaper and more effective.
- **Log the full prompt and the full response**, including tool calls. Debugging without the actual bytes sent is guesswork.

??? warning "Failure modes"
    **Fine-tuning to add knowledge.** The model learns the style of the training documents and hallucinates content in that style — arguably worse than before, because the output now sounds more authoritative. Symptom: confident, well-formatted, wrong answers about the fine-tuning domain. Use retrieval.

    **RAG with retrieval that is not measured.** Teams debug the generation prompt for weeks when recall@k is the bottleneck. Always evaluate the retriever on its own: if the right chunk is not in the context, the generator cannot recover it.

    **Chunking that splits the answer.** A fact spanning a chunk boundary is retrievable only as two halves, each individually unconvincing. Overlap, and prefer semantic or structural boundaries over fixed token counts.

    **Lost in the middle.** Models attend less reliably to content in the middle of a long context than at either end. Stuffing fifty retrieved chunks in is worse than five good ones — and costs ten times more.

    **Evaluating with the model that generated the output.** LLM-as-judge is useful and biased: models prefer their own outputs and longer responses. Use it with a rubric, calibrate against human labels on a subset, and never as the only measure.

    **Prompt "improvements" without an eval.** Changes are evaluated by trying two examples and preferring the nicer one. Variance across runs exceeds the effect being measured. This is the single most common waste of effort in the area.

    **Agent loops with no budget or stop condition.** Retry logic plus tool errors produce loops that burn tokens indefinitely. Cap iterations, cap spend, and make tool errors legible to the model so it can change course rather than repeat.

    **Treating output as validated.** The model produces plausible text, including plausible citations, plausible numbers and plausible code. Anything consequential needs a checking step outside the model — execution, a schema, a lookup.

    <!-- Add your own here — and note which model and date, since behaviour changes. -->

## Worked example

Why context is a budget: cost and the attention profile both scale against you.

```python
chunk_tokens   = 500
overhead       = 1200          # system prompt, instructions, question
answer_tokens  = 600

print(f"{'chunks':>7} {'input tok':>10} {'total tok':>10}  {'relative cost':>13}")
base = None
for k in (3, 5, 10, 25, 50):
    inp   = overhead + k * chunk_tokens
    total = inp + answer_tokens
    base  = base or total
    print(f"{k:7d} {inp:10d} {total:10d}  {total/base:12.1f}x")
```

```
 chunks  input tok  total tok  relative cost
      3       2700       3300           1.0x
      5       3700       4300           1.3x
     10       6200       6800           2.1x
     25      13700      14300           4.3x
     50      26200      26800           8.1x
```

Going from 5 chunks to 50 costs 6× more per call — and because of the lost-in-the-middle effect, typically produces *worse* answers. Retrieval quality is what buys accuracy here; context volume mostly buys latency and spend.

## Connections

- [Architectures](architectures.md) — the transformer underneath.
- [Generative models](generative.md) — the non-autoregressive families.
- [ML › Evaluation](../ml/evaluation.md) — the eval discipline this area badly needs.
- [Computing › MLOps](../computing/index.md) — serving and deployment.

## Sources

- Vaswani et al. (2017), *Attention Is All You Need*.
- Lewis et al. (2020), *Retrieval-Augmented Generation*.
- Hu et al. (2021), *LoRA: Low-Rank Adaptation of Large Language Models*.
- Liu et al. (2023), *Lost in the Middle*.
- Provider documentation for anything version-specific — see the warning at the top.
