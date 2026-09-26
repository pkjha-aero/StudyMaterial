---
title: PyTorch patterns
status: working
tags: [pillar-5, pillar-9, deep-learning, pytorch, distributed]
updated: 2026-09-26
---

# PyTorch patterns

<span class="status status-working">working</span>
<span class="pillar">pillars 5, 9 &middot; Software engineering, scientific ML</span>

!!! abstract "In one minute"
    - **`model.eval()` and `torch.no_grad()` are different things** and you need both at inference. Forgetting either is the most common bug in the language.
    - **`zero_grad()` before backward**, every step. PyTorch accumulates gradients by design.
    - The input pipeline is usually the bottleneck, not the GPU. Profile before optimising the model.
    - **bf16 over fp16** on modern hardware: same speed, far wider dynamic range, no loss scaling.
    - Loss `.item()` inside a training loop forces a device sync — cheap once, expensive every step.

## Key results

**The canonical training step**, with every mandatory piece:

<div class="result" markdown>

```python
model.train()
for x, y in loader:
    x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
    optimizer.zero_grad(set_to_none=True)        # 1. clear accumulated grads
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss = criterion(model(x), y)            # 2. forward under autocast
    loss.backward()                              # 3. backward OUTSIDE autocast
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    scheduler.step()                             # 4. per-step schedulers
```

</div>

**Evaluation** — both guards, and they do different jobs:

```python
model.eval()                     # BatchNorm uses running stats; Dropout off
with torch.no_grad():            # no autograd graph built; saves memory
    for x, y in val_loader:
        ...
```

`model.eval()` changes *layer behaviour*; `torch.no_grad()` changes *graph construction*. Neither implies the other.

**Dataset and DataLoader.** Implement `__len__` and `__getitem__`; keep per-item work light and do heavy transforms on the GPU where possible.

| Argument | Guidance |
|---|---|
| `num_workers` | ~4× GPUs to start; measure |
| `pin_memory=True` | with CUDA, pairs with `non_blocking=True` |
| `persistent_workers=True` | avoids re-spawning each epoch |
| `prefetch_factor` | raise if workers starve the GPU |
| `drop_last=True` | for BatchNorm stability and fixed shapes |

**Distributed training:**

| Strategy | When |
|---|---|
| `DistributedDataParallel` (DDP) | multi-GPU, model fits in memory — the default |
| `DataParallel` | **deprecated**, single-process, imbalanced; do not use |
| FSDP / ZeRO | model does not fit; shards parameters, gradients, optimizer state |
| Gradient accumulation | emulate a large batch on one GPU |
| Gradient checkpointing | trade recompute for activation memory |

DDP needs `DistributedSampler`, and `sampler.set_epoch(epoch)` each epoch — otherwise every epoch sees the same shuffle.

**Checkpointing.** Save `model.state_dict()`, `optimizer.state_dict()`, `scheduler.state_dict()`, the epoch, and the RNG states. Saving only the model makes a run un-resumable in a way that is only discovered when you need to resume.

## Mental model

PyTorch is eager and mutable: tensors carry an autograd graph built during the forward pass, consumed by `backward()`, and discarded. Most confusing bugs come from that graph being built when you did not want it (memory growth at eval), not being built when you did (a detached tensor), or being reused when it no longer exists (calling `backward()` twice).

The second recurring theme is device and dtype placement. A tensor on the wrong device raises loudly; a tensor in the wrong dtype quietly changes numerics.

## Numerics / practice

- **Profile with `torch.profiler`** before optimising. If GPU utilisation is below ~80%, the problem is data loading.
- **`set_to_none=True`** in `zero_grad` — cheaper than writing zeros, now the default.
- **Compile with `torch.compile`** for a typically large speedup on modern versions; check numerics afterwards.
- **Accumulate loss as a tensor** and `.item()` once per epoch, not per step.

??? warning "Failure modes"
    **Forgetting `model.eval()`.** Dropout stays active and BatchNorm keeps updating its running statistics from evaluation data. Validation loss is then noisy and biased, and — subtly — the model has been contaminated by the validation set through the BatchNorm buffers.

    **Forgetting `torch.no_grad()` at eval.** The autograd graph is built and never freed, so memory grows steadily through the validation loop and OOMs on a long one. The model's *outputs* are correct, which is why this is diagnosed as a memory problem rather than a code problem.

    **Missing `zero_grad()`.** Gradients accumulate across steps, so the effective gradient is a running sum. Symptom: loss decreases briefly then diverges. PyTorch accumulates deliberately — to support gradient accumulation — so this is documented behaviour, not a trap, but it catches everyone once.

    **Accumulating a tensor instead of a float.** `total_loss += loss` keeps the whole graph alive for every step of the epoch. Memory grows linearly and OOMs. Use `total_loss += loss.detach()` or `.item()`.

    **`DistributedSampler` without `set_epoch`.** Every epoch draws the identical shuffle order. Training still works, and generalisation is quietly worse. Nothing in the logs indicates it.

    **`.item()` or `.cpu()` every step.** Each call synchronises the device, serialising the pipeline. On a fast model this can halve throughput. Log every \(N\) steps instead.

    **fp16 without a gradient scaler.** fp16 has a narrow dynamic range and small gradients flush to zero. Symptom: loss stops decreasing, or goes NaN. Either use `GradScaler` or — better on Ampere and later — use bf16, which needs no scaling.

    **Checkpoint missing optimizer state.** Resuming from a model-only checkpoint restarts Adam's moment estimates from zero, producing a visible loss spike and a different trajectory. Save the whole training state.

    <!-- Add your own here. -->

## Worked example

Gradient accumulation without loss scaling silently multiplies your learning rate:

```python
import torch

torch.manual_seed(0)
w = torch.zeros(1, requires_grad=True)
x = torch.ones(8, 1)
target = torch.full((8, 1), 2.0)

def grad_after(accum_steps, scale):
    w.grad = None
    micro = x.shape[0] // accum_steps
    for i in range(accum_steps):
        xb = x[i*micro:(i+1)*micro]
        yb = target[i*micro:(i+1)*micro]
        loss = ((xb * w - yb)**2).mean()
        (loss / scale).backward()
    return w.grad.item()

print(f"single batch of 8          : {grad_after(1, 1):.4f}")
print(f"4 accum steps, unscaled    : {grad_after(4, 1):.4f}")
print(f"4 accum steps, loss/4      : {grad_after(4, 4):.4f}")
```

```
single batch of 8          : -4.0000
4 accum steps, unscaled    : -16.0000
4 accum steps, loss/4      : -4.0000
```

Accumulating four micro-batches without dividing the loss produces a gradient four times too large — exactly as if the learning rate had been quadrupled. The run may still train, badly, which is what makes it hard to spot.

## Connections

- [Architectures](architectures.md) — what you are implementing.
- [ML › Training craft](../ml/training-craft.md) — optimizers and schedules.
- [Computing › GPU and CUDA](../computing/index.md) — what the hardware is doing.
- [Foundations › Research craft](../foundations/research-craft.md) — checkpoints as provenance.

## Sources

- PyTorch documentation — performance tuning guide and DDP notes.
- Karpathy, *A Recipe for Training Neural Networks*.
