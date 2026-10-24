---
title: SciML in aerospace
status: working
tags: [pillar-9, sciml, surrogates, validation, extrapolation]
updated: 2026-10-24
---

# SciML in aerospace

<span class="status status-working">working</span>
<span class="pillar">pillar 9</span>

!!! abstract "In one minute"
    - The aerospace use case is **design-loop amortisation**: one expensive training campaign, then thousands of near-free evaluations inside an optimiser, a UQ study or a flight-envelope sweep.
    - Current industrial models work from **raw geometry** — STL or point cloud — rather than a fixed grid. That is what makes them usable in a design loop where the shape is the variable.
    - **DoMINO** and **GeoTransolver**, both in [NVIDIA PhysicsNeMo](https://github.com/NVIDIA/physicsnemo), are the current reference architectures for external aerodynamics, and **SHIFT-Wing** is the first large open transonic-wing instance of the pattern.
    - Rotorcraft and wind turbines are the **hardest and most valuable** cases: rotating, unsteady, and so expensive to simulate that surrogate payback is immediate.
    - The reported accuracy metric is almost never the one your design decision needs. The worked example quantifies the gap.

## Where SciML actually pays in aerospace

| Workload | Why a surrogate wins | Typical method |
|---|---|---|
| Shape optimisation | Hundreds to thousands of geometry evaluations | Geometry-aware operator |
| Aerodynamic databases | Full envelope in Mach, \(\alpha\), \(\beta\), control deflection | Operator or [ROM](surrogates-rom.md) |
| Loads and aeroelastic sweeps | Many conditions × many mass cases | Operator, [mesh GNN](gnn-meshes.md) |
| Turbulence closure | A gap the physics leaves open | [Hybrid coupling](hybrid-coupling.md) |
| Sparse-data inference | Infer a field from limited measurements | [PINN](pinns.md) |
| Real-time control | Microsecond inference required | Any trained surrogate |
| One analysis of one shape | **Nothing — use the solver** | — |

## Airfoils and sections

The best-posed problem in the subject, and consequently the most solved. A 2D section has few shape parameters, cheap ground truth, and an enormous number of required evaluations — exactly the amortisation case.

Two threads matter beyond simple regression. **Operator surrogates for shape optimisation** predict the whole pressure distribution rather than integrated coefficients, which means the optimiser sees the shock, the suction peak and the pressure recovery rather than one number. And **airfoil tables for rotorcraft** are the oldest production use in aerospace: comprehensive rotor codes need \(C_l, C_d, C_m\) over wide ranges of \(\alpha\), Mach and Reynolds, tables have historically been built by hand from sparse CFD and test data, and a surrogate generates them for a novel section in seconds.

This is also where **data-driven turbulence closure** was first shown to work on something recognisably engineering. Singh, Medida & Duraisamy (2017) applied field inversion and machine learning to turbulent separated flow over airfoils and recovered surface pressure and integrated coefficients that the baseline RANS model got wrong — the demonstration that convinced the aerodynamics community the approach was more than curve fitting.

## Wings and whole aircraft

The step from 2D to 3D is where the geometry problem becomes the whole problem, and where the Era 5 architectures earn their place.

**SHIFT-Wing** is the clearest public instance. Built on parametric variants of the NASA Common Research Model wing-body, it consists of high-fidelity RANS solutions — roughly 1,130 cases at \(M = 0.70\) and 1,132 at \(M = 0.85\), drawn from about 2,330 generated — varying wing geometry alongside flight condition, so the surrogate learns the response to *shape* and not only to \(\alpha\) and Mach. It was produced with PhysicsNeMo using the DoMINO architecture.

Two things about it are worth noting for anyone reading the aerodynamics side of this site. It is split by Mach number rather than spanning it, which tells you the authors did not expect one model to interpolate across [drag divergence](../aerospace/transonic.md) — reasonable, since the physics changes character there. And transonic wing design chases differences of one or two drag counts, which is a far finer resolution than the headline accuracy of any current surrogate; see the worked example.

Related public datasets fill out the picture: **BlendedNet** for blended-wing-body configurations, **HiLiftAeroML** for high-lift aircraft aerodynamics, and **DrivAerML** / **SHIFT-SUV** / **CarBench** on the automotive side, which is where most architecture benchmarking actually happens because the geometries are plentiful and unclassified.

## Rotorcraft

The most demanding case on this page. A rotor is unsteady by construction, the blade passes through its own wake, and [dynamic stall](../aerospace/rotorcraft.md) on the retreating side is exactly the regime where both RANS and static airfoil tables are least reliable. A comprehensive analysis needs the answer thousands of times across a flight envelope.

Three places SciML is being used:

- **Section tables**, as above — the production use, and the least glamorous.
- **Dynamic stall modelling.** Semi-empirical models such as Leishman–Beddoes have many coefficients fitted per airfoil. Learned models trained on unsteady CFD or oscillating-aerofoil data are a natural replacement, and the hysteresis loop is a sequence-modelling problem that modern architectures handle well.
- **Unsteady blade loads.** Periodic neural mappings predict blade pressure and aeroelastic loads around the azimuth, amortising over operating condition rather than recomputing each one.

The caution specific to rotorcraft is that **a rollout is not a prediction**. A learned unsteady model fed its own output drifts, and a rotor is a periodic system in which small per-revolution errors accumulate into the wrong loads — the [rollout stability](gnn-meshes.md) problem in its least forgiving form.

## Wind turbines

Structurally the same problem as rotorcraft with different economics: wake interaction dominates, the array is large, and the optimisation target — layout and yaw scheduling across a farm — needs enormous numbers of evaluations.

The pattern that has emerged is **multi-fidelity**: pre-train on a cheap engineering wake model such as FLORIS, then fine-tune on a small number of LES or high-fidelity RANS cases. Reported results reproduce engineering-model wake fields to high accuracy while running two orders of magnitude faster, which turns a wind-farm yaw optimisation from hours into seconds. Graph networks are a natural fit here, because a wind farm *is* a graph of interacting turbines, and the learned message passing represents wake superposition directly.

The honest caveat is that a model distilled from FLORIS inherits FLORIS's physics. Speed against the low-fidelity model is not accuracy against reality, and the multi-fidelity step exists precisely to address that — so the question to ask of any such result is how many high-fidelity cases were in the fine-tuning set.

## The current architectures

**DoMINO** — *Decomposable Multi-scale Iterative Neural Operator*. Takes STL geometry as a point cloud, enriched with a signed distance field and positional encodings. It learns a **global** geometry representation by a multi-scale iterative pass over the point cloud, then for each query point builds a **local** encoding from a sub-region sampled around it — a learned computational stencil. It predicts surface pressure and wall shear stress, and volume velocity and pressure, with the surface and volume models currently trained separately. Reported DrivAerML results are \(R^2 \approx 0.983\) for drag and \(0.971\) for lift, with training on eight H100 GPUs taking around four hours.

**GeoTransolver** — builds on the Transolver backbone and adds **geometry-aware latent embeddings**: physics attention over learned state slices, plus cross-attention to a shared multi-scale geometry and global context at *every* block. The point is persistence — in a plain transformer, geometric information injected at the input degrades with depth, and re-presenting it at each layer is what buys robustness to geometry and regime shift. Benchmarked on DrivAerML, SHIFT-SUV, SHIFT-Wing and two crash-dynamics datasets against DoMINO, Transolver and AB-UPT.

**PhysicsNeMo** is the framework all of this ships in — NVIDIA's open-source stack for physics AI, formerly Modulus. What it supplies that matters in practice is not the architectures but the **engineering around them**: distributed and domain-parallel training, sharded tensors for meshes larger than one GPU's memory, curation pipelines that turn thousands of raw CFD runs into a training set, and reference recipes for external aerodynamics. The models above are research results; PhysicsNeMo is the reason a team can reproduce them without rebuilding the infrastructure.

## Mental model

Everything on this page is the same trade: convert a large, one-off, embarrassingly parallel CFD campaign into a model that answers the design loop's questions instantly. The campaign is the cost; the loop is the payoff; and the model is only as good as the campaign's coverage of the space the loop will explore.

That last clause is the whole risk. An optimiser is an adversary — it goes looking for the best point, which in practice means it goes looking for wherever the surrogate is optimistic. A surrogate inside an optimisation loop is being probed exactly where it is least trustworthy, and it will return a confident answer there.

## Numerics / practice

- **Record the training distribution as a deliverable**, in the same place as the model weights: geometry parameter ranges, Mach, Reynolds, angle of attack, mesh family, turbulence model. Without it nobody downstream can tell in-distribution from out.
- **Validate in the units of the decision.** Drag counts, not \(R^2\); pitching moment, not field \(L_2\). A model with excellent field error can have useless integrated loads, because integration cancels most of the field error and keeps the systematic part.
- **Keep a solver in the loop.** Verify the optimiser's final candidates with CFD. The surrogate chooses where to look; the solver decides.
- **Split train and test by geometry, not by sample.** Random splits across a parametric sweep leak, because neighbouring samples of the same shape are nearly the same case, and the reported error is then interpolation within a shape rather than generalisation across shapes.
- **Expect to retrain at the regime boundary.** SHIFT-Wing's separate Mach 0.70 and 0.85 models are the pattern, not a shortcut.

??? warning "Failure modes"
    **\(R^2\) read as design accuracy.** Reported \(R^2\) is normalised by the spread of the test population. Aerodynamic design chases differences far smaller than that spread, so a model at \(R^2 = 0.983\) may be unable to rank the candidates you care about. Quantified below.

    **Surrogate used as the optimiser's objective without a solver check.** Optimisation seeks extrema, and the extrema of a learned model include its artefacts. The result is a design that exploits the surrogate's error, looks excellent, and does not reproduce in CFD.

    **Random train/test split on a parametric sweep.** Neighbouring samples are nearly identical, so a random split measures interpolation and reports it as generalisation. Split by geometry, by family, or by held-out design.

    **Automotive benchmark accuracy assumed to transfer to aircraft.** Most architecture comparison happens on DrivAerML and similar, where the flow is massively separated and bluff-body dominated. Transonic wing aerodynamics is shock-dominated and far more sensitive to small geometry changes, and nothing guarantees the ranking carries over.

    **A rotor surrogate rolled out over many revolutions.** Per-revolution error accumulates, and a periodic system has no mechanism to forget it. Validate over the number of revolutions you actually intend to run, not over one.

    **Wind-farm model distilled from an engineering wake model and reported as physics.** Speed-up against FLORIS with 99% agreement means you have a fast FLORIS. The physics content is whatever the high-fidelity fine-tuning set contributed, and that number belongs in the headline.

    **Training-set geometry parameterisation mistaken for the design space.** A model trained on variants of one parametric CAD model has learned that parameterisation. A genuinely novel configuration — a different planform topology, a strut-braced wing, a BWB — is outside it, and the model will not say so.

    **Surface and volume models assumed consistent.** Where these are trained separately, as in current DoMINO practice, the surface pressure field and the volume pressure field are two predictions, not one. Integrated forces from each need not agree, and the discrepancy is a free diagnostic worth checking.

    <!-- Add your own here. -->

## Worked example

What a published \(R^2\) means for a wing design decision:

```python
import numpy as np

# A surrogate's reported R^2 is measured against the SPREAD OF THE TEST POPULATION.
# Residual scatter: sigma_res = sigma_pop * sqrt(1 - R^2).
def sigma_res(R2, sigma_pop): return sigma_pop*np.sqrt(1 - R2)

SIG = 40.0      # counts: spread of drag across the design space being explored
print(f"design-space drag spread sigma_pop = {SIG:.0f} counts")
print(f"{'reported R^2':>13}{'residual, counts':>19}{'resolvable delta (3 sigma)':>29}")
for R2 in (0.95, 0.971, 0.983, 0.995, 0.999, 0.9999):
    s = sigma_res(R2, SIG)
    print(f"{R2:13.4f}{s:19.2f}{3*s:29.1f}")

print("\nR^2 needed to rank two designs that differ by delta, at 3 sigma:")
print(f"{'delta, counts':>14}{'R^2 required':>15}{'equivalent residual':>21}")
for d in (10.0, 5.0, 2.0, 1.0):
    R2 = 1 - (d/(3*SIG))**2
    print(f"{d:14.1f}{R2:15.5f}{sigma_res(R2,SIG):21.2f}")

# Errors on SIMILAR geometries are correlated, so a difference is better resolved
# than two independent absolute predictions would suggest.
print("\nthe same question, allowing error correlation rho between two similar designs:")
print(f"{'rho':>6}{'sigma of the difference':>26}{'delta resolvable at R^2=0.983':>32}")
for rho in (0.0, 0.5, 0.9, 0.98):
    sd = sigma_res(0.983, SIG)*np.sqrt(2*(1-rho))
    print(f"{rho:6.2f}{sd:26.2f}{3*sd:32.1f}")
```

```
design-space drag spread sigma_pop = 40 counts
 reported R^2   residual, counts   resolvable delta (3 sigma)
       0.9500               8.94                         26.8
       0.9710               6.81                         20.4
       0.9830               5.22                         15.6
       0.9950               2.83                          8.5
       0.9990               1.26                          3.8
       0.9999               0.40                          1.2

R^2 needed to rank two designs that differ by delta, at 3 sigma:
 delta, counts   R^2 required  equivalent residual
          10.0        0.99306                 3.33
           5.0        0.99826                 1.67
           2.0        0.99972                 0.67
           1.0        0.99993                 0.33

the same question, allowing error correlation rho between two similar designs:
   rho   sigma of the difference   delta resolvable at R^2=0.983
  0.00                      7.38                            22.1
  0.50                      5.22                            15.6
  0.90                      2.33                             7.0
  0.98                      1.04                             3.1
```

Take the first table against a transonic wing study where the design space spans about 40 drag counts. At \(R^2 = 0.983\) — DoMINO's reported drag accuracy on DrivAerML, and a genuinely strong result — the residual scatter is **5.2 counts**, so two designs must differ by roughly **16 counts** before the surrogate can separate them with confidence. Transonic wing design routinely chases one or two.

The second table inverts it. Ranking 2-count differences needs \(R^2 = 0.9997\); ranking 1-count differences needs \(0.99993\). Those are three to four orders of magnitude less residual variance than the current state of the art, and no amount of training on the present data scale closes that gap. **The surrogate is not a replacement for the final CFD evaluation, and nothing about its headline accuracy suggests otherwise once the number is converted into the units of the decision.**

The third table is the reprieve, and it is why these models are useful anyway. Errors on *similar* geometries are correlated — the model is wrong in the same direction for two neighbouring shapes — so the error on the **difference** is much smaller than the error on either absolute value. At a correlation of 0.98 the resolvable difference falls to about 3 counts. This is the real mode of use: a surrogate is a good **ranking** instrument over small perturbations and a poor **absolute** one, which is exactly what a gradient-based or trust-region optimiser needs.

Two caveats on the numbers. The 40-count spread is a stand-in for a design study's range and should be replaced by yours — the conclusion scales with it directly. And the error correlation \(\rho\) is the quantity nobody reports; it is measurable on a held-out set of near-neighbour geometries, it is the single most useful number for deciding whether a surrogate can drive your optimiser, and asking for it is a reasonable thing to do of any vendor or paper.

## Connections

- [How the field evolved](evolution.md) — the chronology these architectures sit at the end of.
- [Neural operators](neural-operators.md) — DoMINO and GeoTransolver in method terms.
- [Mesh GNNs](gnn-meshes.md) — the other route to irregular geometry, and rollout stability.
- [Hybrid coupling](hybrid-coupling.md) — data-driven turbulence closure, the other aerospace thread.
- [Aerospace › Transonic](../aerospace/transonic.md) — why a wing surrogate is split by Mach number.
- [Aerospace › Rotorcraft](../aerospace/rotorcraft.md) · [Wind energy](../aerospace/wind-energy.md) · [Aircraft design](../aerospace/aircraft-design.md) — the problems being surrogated.

## Sources

- Brunton et al., "Data-driven aerospace engineering: reframing the industry with machine learning", *AIAA Journal* **59**(8) (2021) — the industry-side survey, written with Boeing.
- Singh, Medida & Duraisamy, "Machine-learning-augmented predictive modeling of turbulent separated flows over airfoils", *AIAA Journal* **55**(7) (2017).
- Adams, Ranade, Cherukuri & Choudhry, "GeoTransolver", arXiv:2512.20399 (2025).
- Wu et al., "Transolver", ICML (2024); and the AB-UPT anchored-branched physics transformer work (2025).
- [NVIDIA PhysicsNeMo documentation](https://docs.nvidia.com/physicsnemo/) — DoMINO architecture and the external-aerodynamics recipes.
- Luminary Cloud / Otto Aviation / NVIDIA, SHIFT-Wing dataset and model, built on the NASA Common Research Model.
- DrivAerML, SHIFT-SUV, CarBench, BlendedNet and HiLiftAeroML — the open benchmark datasets referenced above.
