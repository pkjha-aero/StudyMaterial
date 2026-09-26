---
title: MLOps and deployment
status: working
tags: [pillar-5, computing, docker, kubernetes, cicd, cloud]
updated: 2026-09-26
---

# MLOps and deployment

<span class="status status-working">working</span>
<span class="pillar">pillar 5 &middot; Programming and software engineering</span>

!!! abstract "In one minute"
    - A container image is a **reproducibility artifact**. `latest` tags and unpinned installs destroy that property.
    - **Singularity/Apptainer, not Docker, on HPC** — it runs unprivileged and respects the scheduler.
    - Kubernetes solves orchestration you may not have. For a single long-running job, a scheduler or a VM is simpler and cheaper.
    - **The model is the easy part.** Data pipelines, monitoring and rollback are where deployed ML actually fails.
    - **Training/serving skew** — different preprocessing in the two paths — is the classic production ML bug.

## Key results

**Containers:**

<div class="result" markdown>

| | Docker | Singularity / Apptainer |
|---|---|---|
| Privilege | daemon runs as root | runs as the user |
| HPC suitability | usually disallowed | the standard |
| Filesystem | isolated by default | binds `$HOME`, `$PWD` by default |
| Image | layered, registry | single `.sif` file |
| MPI | awkward | works with host MPI via bind |

</div>

On a shared cluster, an unprivileged runtime is not a preference — it is the only thing the site will allow. Apptainer can build directly from a Docker image, so the usual workflow is to author a Dockerfile and convert.

**Dockerfile practices that matter:**

- **Pin everything** — base image by digest, packages by version, a lockfile for Python. `FROM ubuntu:latest` makes the image unreproducible by construction.
- **Order layers by volatility** — dependencies before source, so a code change does not reinstall the world.
- **Multi-stage builds** to keep compilers out of the runtime image.
- **Non-root user** in the final stage.
- **`.dockerignore`** — otherwise the build context includes your data directory.

**Kubernetes concepts**, in the order they become relevant: Pod (one or more containers, scheduled together) → Deployment (replicas, rolling updates) → Service (stable virtual IP, load balancing) → Ingress (HTTP routing from outside) → ConfigMap/Secret (configuration) → PersistentVolumeClaim (storage) → NetworkPolicy (pod-level firewall).

Worth the honesty: this is a lot of machinery. It pays off for many services with independent lifecycles. For one training job on one machine, it is pure overhead.

**Networking, the parts that recur:** ClusterIP (internal only), NodePort (a port on every node), LoadBalancer (cloud LB), and the distinction between a Pod IP (ephemeral) and a Service IP (stable). L4 load balancing routes by connection, L7 by HTTP request — ingress controllers are L7.

**CI/CD for scientific and ML code.** The useful pipeline is: lint → unit tests → a **fast physics or numerical regression test** (an MMS order check, a known-solution comparison) → build the image → push. The numerical regression test is the part generic CI advice omits and the part that catches real breakage — see [V&V](../foundations/verification-validation.md).

**Model serving.** Batch (offline scoring), online (request/response), and streaming. Monitor: latency percentiles (p50/p95/p99, not the mean), throughput, error rate, **input distribution drift**, and prediction distribution drift. Drift monitoring is what tells you the model has silently stopped being right.

## Mental model

Deployment is about making the environment part of the artifact. A result that depends on "the libraries that happened to be on that machine" is not reproducible, and a service that depends on it is not reliable. Containers, lockfiles and pinned digests are all the same move: turn an implicit dependency into an explicit one.

For ML specifically, there is a second environment to pin — the *data* path. The model is a pure function; everything around it is where the variance lives.

## Numerics / practice

- **Pin by digest**, not tag. Tags are mutable, including `latest` and including version tags on many registries.
- **Build once, promote the same image** through environments. Rebuilding per environment defeats the purpose.
- **Share preprocessing code** between training and serving — literally the same module, not a reimplementation.
- **Log p99, not the mean.** A mean latency of 50 ms with a p99 of 4 s is a broken service.

??? warning "Failure modes"
    **Training/serving skew.** Preprocessing implemented twice — once in the training notebook, once in the serving path — and they drift apart. Symptom: offline metrics excellent, production performance poor, with no error anywhere. The only robust fix is a single shared implementation.

    **`latest` tags.** The image that worked last month pulls a different base today. The failure arrives at the worst time and is hard to attribute because nothing in your repository changed.

    **Docker attempted on HPC.** The daemon needs root; shared clusters do not grant it. Use Apptainer, and expect to bind-mount the host MPI rather than shipping one in the image — a mismatched MPI inside the container is a classic silent hang.

    **Kubernetes for a single job.** Weeks of YAML to run something `sbatch` would have started in a minute. Choose the orchestration your problem actually needs.

    **No rollback path.** A deployment strategy without a tested rollback is a one-way door. This includes the model artifact, not just the code.

    **Monitoring only aggregate accuracy.** Overall accuracy can hold steady while a subgroup or a recent time window degrades badly. Monitor input drift and per-segment metrics.

    **Secrets in the image.** Layers persist even if a later layer deletes the file — anyone who can pull the image can recover it. Use runtime secrets.

    **Resource limits unset.** A pod without limits can starve its neighbours; one with limits set too low is OOM-killed mid-run, often reported as an unexplained crash.

    <!-- Add your own here. -->

## Worked example

Why the mean latency is the wrong number to alert on:

```python
import numpy as np
rng = np.random.default_rng(0)

n = 100_000
# 97% fast requests, 3% hitting a slow path
fast = rng.lognormal(np.log(0.030), 0.3, int(n * 0.97))
slow = rng.lognormal(np.log(2.5),   0.5, int(n * 0.03))
lat = np.concatenate([fast, slow])

print(f"mean  : {lat.mean()*1000:8.1f} ms")
for q in (50, 90, 95, 99, 99.9):
    print(f"p{q:<5}: {np.percentile(lat, q)*1000:8.1f} ms")
print(f"\nrequests over 1 s: {100*(lat > 1.0).mean():.2f}%")
```

```
mean  :    116.5 ms
p50   :     30.3 ms
p90   :     46.4 ms
p95   :     55.2 ms
p99   :   3132.0 ms
p99.9 :   6660.8 ms

requests over 1 s: 2.91%
```

The mean says 117 ms, which sounds acceptable and describes no actual request — the typical request is 30 ms, and the unlucky 2.9% are measured in seconds. An alert on the mean would never fire; an alert on p99 fires immediately.

## Connections

- [HPC and parallelism](hpc.md) — the other deployment target.
- [Data and I/O](data-io.md) — versioning the inputs.
- [Foundations › Research craft](../foundations/research-craft.md) — reproducibility as a property of the record.
- [ML › Evaluation](../ml/evaluation.md) — what to monitor after deployment.

## Sources

- Sculley et al. (2015), *Hidden Technical Debt in Machine Learning Systems*.
- Apptainer and Kubernetes documentation.
