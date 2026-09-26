---
title: Turbulence
status: solid
tags: [pillar-1, fluids, turbulence, scales, cascade]
updated: 2026-09-26
---

# Turbulence

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Turbulence is a **multiscale** problem: energy enters at the integral scale \(L\), cascades without loss, and dissipates at the Kolmogorov scale \(\eta\).
    - \(L/\eta \sim \mathrm{Re}^{3/4}\), so resolving everything costs \(\mathrm{Re}^{9/4}\) points in 3D and \(\mathrm{Re}^{3}\) in work. This single scaling explains why RANS and LES exist.
    - Averaging the equations creates **more unknowns than equations** — the closure problem. Every model is a guess at the missing term.
    - The \(k^{-5/3}\) inertial range is the one universal result, and it holds only at high \(\mathrm{Re}\), away from walls, over a limited band.
    - Choose the method by what you need: **RANS** for mean loads, **LES** for unsteady structure, **DNS** for physics at modest \(\mathrm{Re}\).

## Key results

**Scale separation.** With dissipation rate \(\varepsilon \sim u'^3/L\):

<div class="result" markdown>

\[
\eta = \left(\frac{\nu^3}{\varepsilon}\right)^{1/4},
\qquad
\frac{L}{\eta} \sim \mathrm{Re}_L^{3/4},
\qquad
N_{\text{3D}} \sim \mathrm{Re}_L^{9/4},
\qquad
\text{work} \sim \mathrm{Re}_L^{3}
\]

</div>

The Taylor microscale \(\lambda = \sqrt{15\nu u'^2/\varepsilon}\) sits between them — useful as a correlation length, but *not* a dissipation scale, a common misreading.

**Kolmogorov spectrum** in the inertial range \(1/L \ll k \ll 1/\eta\):

\[
E(k) = C_K\,\varepsilon^{2/3} k^{-5/3}, \qquad C_K \approx 1.5
\]

**Reynolds decomposition** \(u_i = \overline{u}_i + u_i'\) gives the RANS equations:

\[
\overline{u}_j\frac{\partial \overline{u}_i}{\partial x_j}
= -\frac{1}{\rho}\frac{\partial \overline{p}}{\partial x_i}
+ \nu\nabla^2\overline{u}_i
- \frac{\partial \overline{u_i'u_j'}}{\partial x_j}
\]

The last term, the **Reynolds stress** \(-\rho\overline{u_i'u_j'}\), is six new unknowns with no equation. Deriving one introduces triple correlations, and so on — the closure problem does not terminate.

**Turbulent kinetic energy budget:**

\[
\frac{Dk}{Dt} = \underbrace{-\overline{u_i'u_j'}\frac{\partial \overline{u}_i}{\partial x_j}}_{\text{production }P}
- \underbrace{\varepsilon}_{\text{dissipation}}
+ \underbrace{\text{transport}}_{\text{redistribution}}
\]

Near equilibrium \(P \approx \varepsilon\). How badly a model violates that is a good first diagnostic.

**Cost comparison**, wall-bounded flow:

| Method | Resolves | Cost scaling | Use when |
|---|---|---|---|
| RANS | mean only | \(\mathrm{Re}^{0}\) (grid set by geometry) | mean forces, design sweeps |
| Wall-modelled LES | energetic eddies | \(\sim\mathrm{Re}^{1.0\text{–}1.3}\) | unsteady loads, mixing, acoustics |
| Wall-resolved LES | to near-wall streaks | \(\sim\mathrm{Re}^{1.8}\) | transition, separation detail |
| DNS | everything | \(\sim\mathrm{Re}^{3}\) | model development, canonical physics |

## Mental model

Energy is injected by the mean shear at the scale of the geometry, handed down through a cascade of vortex stretching — each generation smaller and faster — until the strain rate is large enough for viscosity to convert it to heat. The cascade itself is inviscid; viscosity only sets *where* it stops, not *how much* is dissipated. \(\varepsilon\) is fixed by the large scales.

That is why the \(\mathrm{Re}\)-dependence is so brutal. Raising \(\mathrm{Re}\) does not change the energy flux; it just adds more generations before viscosity can act, and each generation needs its own grid points.

## Numerics / practice

- **Check \(P/\varepsilon\)** in a converged RANS solution. Far from 1 in an equilibrium boundary layer means the model is being used outside its calibration.
- **Compute the local \(\eta\)** before claiming DNS, and the local integral scale before claiming LES resolves the energetic eddies.
- **Average long enough.** Statistics need \(O(100)\) integral timescales \(L/u'\). Shorter records give confident-looking but unconverged means.
- **Spectra need care**: window the signal, and remember that the highest resolved wavenumbers are contaminated by the scheme's own dissipation long before the grid cutoff.

??? warning "Failure modes"
    **Assuming isotropy where there is none.** The \(k^{-5/3}\) law and most model constants are calibrated on homogeneous isotropic turbulence. Near walls, in strong curvature, under rotation or stratification, the anisotropy is the physics — and the model has averaged it away.

    **Too-short averaging.** Means and especially second moments converge slowly. Symptom: statistics that shift noticeably when you extend the window, or that differ between the upper and lower half of a symmetric geometry. Always report the averaging interval in integral timescales.

    **Reading the numerical cutoff as physics.** The tail of a computed spectrum rolls off because of the scheme's dissipation, not Kolmogorov's. Fitting \(\eta\) from that roll-off gives a number that depends on your grid.

    **Taylor microscale used as a dissipation scale.** It is a correlation length that happens to appear in the dissipation formula. Sizing a grid on \(\lambda\) rather than \(\eta\) under-resolves by roughly \(\mathrm{Re}^{1/4}\).

    **"DNS" that is not.** Resolving to \(\Delta x \approx \eta\) is necessary but not sufficient — the timestep, domain size (must contain several integral scales) and run length all bind. An under-sized periodic box artificially constrains the largest eddies and biases every statistic.

    <!-- Add your own here. -->

## Worked example

The cost scaling is worth feeling numerically rather than remembering as an exponent:

```python
Re = [1e4, 1e6, 1e8]
for r in Re:
    n_per_dim = r**0.75
    print(f"Re={r:.0e}   L/eta={n_per_dim:.2e}   "
          f"3D points={n_per_dim**3:.2e}   work~{r**3:.1e}")
```

```
Re=1e+04   L/eta=1.00e+03   3D points=1.00e+09   work~1.0e+12
Re=1e+06   L/eta=3.16e+04   3D points=3.16e+13   work~1.0e+18
Re=1e+08   L/eta=1.00e+06   3D points=1.00e+18   work~1.0e+24
```

A full-scale aircraft at \(\mathrm{Re}=10^8\) would need \(10^{18}\) points. Modelling is not a convenience.

## Pages in this section

- [RANS](rans.md) — closures, eddy viscosity, wall treatment.
- [LES](les.md) — filtering, subgrid models, resolution requirements.

## Connections

- [Governing equations](../governing-equations.md) — what averaging is applied to.
- [Incompressible flow](../incompressible.md) — where most turbulence modelling lives.
- [Meshing](../cfd/meshing.md) — \(y^+\) and boundary-layer resolution.

## Sources

- Pope, *Turbulent Flows* — the standard graduate reference.
- Tennekes & Lumley, *A First Course in Turbulence* — scales and the cascade, concisely.
- Archive: `Others/Turbulence_JCM`, `Others/UMD_Turb` — turbulence notes.
- Archive: see the [course archive](../../resources/course-archive.md).
