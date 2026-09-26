---
title: Graph networks on meshes
status: working
tags: [pillar-9, sciml, neural-networks, mesh, extrapolation]
updated: 2026-09-26
---

# Graph networks on meshes

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - A mesh **is** a graph, so message passing is the natural learned analogue of a stencil operation on unstructured grids.
    - **Message passing is local**: \(k\) rounds propagate information \(k\) hops. Elliptic problems, which couple globally, need a multiscale scheme.
    - **Relative coordinates on edges, not absolute positions on nodes** — that is what buys translation invariance and generalisation to new geometries.
    - Rollout stability, not single-step accuracy, is the binding constraint for time-dependent problems.
    - Generalising to a mesh with different resolution or topology is the real test, and it is frequently not reported.

## Key results

**Encode–process–decode**, the standard architecture for mesh simulation:

<div class="result" markdown>

1. **Encode** — node features (state, node type) and edge features (relative displacement \(\mathbf{d}_{ij}\), \(|\mathbf{d}_{ij}|\)) into latent vectors.
2. **Process** — \(M\) rounds of message passing on the mesh graph.
3. **Decode** — latent node state to the predicted quantity, usually a time *derivative* or increment.

</div>

One message-passing round:

\[
\mathbf{e}'_{ij} = \phi_e\left(\mathbf{e}_{ij}, \mathbf{v}_i, \mathbf{v}_j\right),
\qquad
\mathbf{v}'_i = \phi_v\left(\mathbf{v}_i, \sum_{j\in\mathcal{N}(i)}\mathbf{e}'_{ij}\right)
\]

with residual connections around both.

**Why relative coordinates.** Putting absolute position on nodes lets the network memorise the training geometry. Putting *relative displacement* on edges makes the network translation-invariant by construction, so it generalises to a domain translated, extended, or re-meshed. This is the single most important design choice in mesh GNNs and the most common thing to get wrong.

**Receptive field.** \(M\) rounds reach \(M\) hops. For a mesh with \(N\) nodes across a characteristic length, a purely local GNN cannot represent a global coupling without \(O(N)\) rounds — which is unaffordable and would over-smooth anyway (see [architectures](../dl/architectures.md)). Options:

| Approach | Idea |
|---|---|
| Multiscale / hierarchical graphs | coarsened graph levels, like multigrid |
| World edges | extra long-range edges beyond mesh connectivity |
| Attention over a coarse set | global tokens the whole mesh reads |

The multigrid parallel is exact: local relaxation cannot propagate a global constraint, so you need a coarse level. The same argument that motivates [multigrid](../foundations/linear-solvers.md) motivates hierarchical GNNs.

**Aggregation choice** matters semantically. Sum preserves extensive quantities and scales with neighbour count; mean is invariant to neighbour count but loses magnitude; max is robust to irregular valence. On meshes with varying node degree, sum and mean give genuinely different inductive biases.

**Training for rollout.** Predicting a single step accurately is easy; predicting a thousand is not, because the model's own output becomes its input and drifts off-distribution. The standard mitigation is **training noise**: perturb inputs during training so the model learns to correct small errors rather than only to map clean states.

## Mental model

A finite-volume update reads the neighbouring cells and applies a hand-derived stencil. A mesh GNN reads the neighbouring nodes and applies a learned one. The information flow is identical; what changes is where the update rule comes from.

That equivalence is why the failure modes rhyme with numerical ones. Locality limits propagation speed, just as a CFL condition does. Coarse-graining loses small scales, just as under-resolution does. Rollout instability is the learned version of a scheme whose amplification factor exceeds one — with the difference that there is no von Neumann analysis to warn you in advance.

## Numerics / practice

- **Normalise node and edge features**, and predict normalised increments rather than absolute states.
- **Include node type as a feature** (interior, wall, inflow, outflow) so boundary behaviour can differ.
- **Add training noise** matched roughly to the error scale you expect after a few steps.
- **Report rollout error against horizon**, and test on a mesh the model never saw — different resolution and different topology.

??? warning "Failure modes"
    **Absolute coordinates as node features.** The network memorises positions and fails on any translated or re-meshed domain. Symptom: excellent test error on held-out timesteps of the *same* geometry, collapse on a new one. Because the usual split is by time rather than by geometry, this passes validation.

    **Rollout divergence.** Single-step error of \(10^{-4}\) compounds; after hundreds of steps the state is unphysical, often blowing up in a boundary region first. Single-step validation is not evidence of rollout stability — always plot error against rollout horizon.

    **Too few message-passing steps for the physics.** An incompressible problem has an elliptic pressure coupling that is instantaneous and global. A 10-round local GNN physically cannot represent it. Symptom: local dynamics look right, global constraints (divergence-free, total mass) are violated.

    **Over-smoothing with too many rounds.** The opposite failure: past roughly 10–15 rounds, node representations converge and discriminative power is lost. The window between "enough hops" and "over-smoothed" is narrow, which is why hierarchical graphs rather than deeper flat ones are the answer.

    **Aggregation mismatched to the quantity.** Using mean aggregation for an extensive quantity (a flux sum) makes the result depend on mesh valence in a way the physics does not. Sum is usually right for fluxes, mean for intensive states.

    **No conservation.** Learned updates do not conserve mass or momentum unless the architecture enforces it. Over a long rollout the drift is visible and unphysical. Conservative formulations exist — predict fluxes on edges antisymmetrically — and are worth the constraint.

    **Evaluated only on the training mesh.** Generalisation to new topology and resolution is the whole reason to use a graph representation, and it is often not tested. If the paper or the model card does not show it, assume it does not hold.

    <!-- Add your own here. -->

## Worked example

Message-passing rounds versus the domain, which decides whether the architecture can represent the physics at all:

```python
import numpy as np

print(f"{'mesh (NxN)':>12} {'nodes':>9} {'hops to cross':>15} {'rounds for global':>19}")
for N in (16, 32, 64, 128, 256):
    nodes = N * N
    # structured quad mesh: crossing the domain takes N hops
    print(f"{N:6d}x{N:<5d} {nodes:9d} {N:15d} {N:19d}")

print()
print("hierarchical alternative (coarsen by 2 each level):")
for N in (16, 32, 64, 128, 256):
    levels = int(np.ceil(np.log2(N)))
    print(f"   {N:3d}x{N:<3d}  levels={levels:2d}  "
          f"rounds needed ~ {3*levels:3d}  (vs {N} flat)")
```

```
  mesh (NxN)     nodes   hops to cross   rounds for global
    16x16          256              16                  16
    32x32         1024              32                  32
    64x64         4096              64                  64
   128x128       16384             128                 128
   256x256       65536             256                 256

hierarchical alternative (coarsen by 2 each level):
    16x16   levels= 4  rounds needed ~  12  (vs 16 flat)
    32x32   levels= 5  rounds needed ~  15  (vs 32 flat)
    64x64   levels= 6  rounds needed ~  18  (vs 64 flat)
   128x128  levels= 7  rounds needed ~  21  (vs 128 flat)
   256x256  levels= 8  rounds needed ~  24  (vs 256 flat)
```

A flat GNN needs rounds proportional to the mesh width — 256 rounds on a 256² mesh, far past the over-smoothing limit. A hierarchical scheme needs \(O(\log N)\): 24 rounds for the same mesh. This is the multigrid argument, arrived at from a completely different direction.

## Connections

- [DL › Architectures](../dl/architectures.md) — message passing and over-smoothing.
- [Neural operators](neural-operators.md) — the grid-based alternative.
- [Hybrid coupling](hybrid-coupling.md) — GNN corrections inside a solver.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — multigrid, the same locality argument.
- [Fluids › Meshing](../fluids/cfd/meshing.md) — the meshes being learned on.

## Sources

- Pfaff et al. (2021), *Learning Mesh-Based Simulation with Graph Networks*.
- Sanchez-Gonzalez et al. (2020), *Learning to Simulate Complex Physics with Graph Networks*.
- Battaglia et al. (2018), *Relational inductive biases, deep learning, and graph networks*.
