---
title: Magnetohydrodynamics
status: solid
tags: [pillar-1, astrophysics, mhd, divergence-constraint]
updated: 2026-09-26
---

# Magnetohydrodynamics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Ideal MHD is fluid dynamics plus a magnetic field that is **frozen into the flow** — field lines move with the plasma.
    - \(\nabla\cdot\mathbf{B}=0\) is a **constraint, not an equation**. Discretizations that violate it produce unphysical forces along field lines.
    - Magnetic pressure and tension act like an anisotropic elastic medium; **plasma beta** \(\beta = p_{\text{gas}}/p_{\text{mag}}\) says which dominates.
    - The system has **seven waves** (fast, slow, Alfvén, entropy), and degeneracies between them make MHD Riemann solvers harder than hydrodynamic ones.
    - **Numerical reconnection** happens whether you want it or not: ideal MHD forbids reconnection, but any discretization has an effective resistivity.

## Key results

**Ideal MHD equations** (Gaussian-like units with \(\mu_0\) absorbed):

<div class="result" markdown>

\[
\frac{\partial \rho}{\partial t} + \nabla\cdot(\rho\mathbf{v}) = 0
\]

\[
\frac{\partial(\rho\mathbf{v})}{\partial t} + \nabla\cdot\left[\rho\mathbf{v}\mathbf{v} + \left(p + \frac{B^2}{2}\right)\mathbf{I} - \mathbf{B}\mathbf{B}\right] = 0
\]

\[
\frac{\partial \mathbf{B}}{\partial t} = \nabla\times(\mathbf{v}\times\mathbf{B}),
\qquad
\nabla\cdot\mathbf{B} = 0
\]

</div>

The Maxwell stress splits into **magnetic pressure** \(B^2/2\), isotropic, and **tension** \(\mathbf{B}\mathbf{B}\), directed along field lines. Tension is what makes field lines behave like stretched elastic bands and what carries Alfvén waves.

**Key parameters:**

\[
v_A = \frac{B}{\sqrt{\mu_0\rho}},
\qquad
\beta = \frac{p_{\text{gas}}}{B^2/2\mu_0},
\qquad
\mathrm{Rm} = \frac{vL}{\eta}
\]

\(\mathrm{Rm}\gg1\) justifies ideal MHD (flux freezing); astrophysical \(\mathrm{Rm}\) is typically \(10^{10}\) or more, which is exactly why numerical resistivity dominates in simulations.

**Alfvén's theorem.** For \(\eta=0\), magnetic flux through any co-moving surface is conserved: field lines are advected with the fluid and cannot break or reconnect. Every interesting event in solar and space physics — flares, CMEs, substorms — requires violating this, which means resistivity must enter somewhere.

**Wave families.** Seven waves: two fast magnetosonic, two slow, two Alfvén, one entropy. Unlike hydrodynamics, the wave speeds can coincide (degeneracies when \(\mathbf{B}\) is parallel or perpendicular to the propagation direction), which breaks the eigenvector basis that Roe-type solvers need. This is why MHD Riemann solvers require careful renormalisation.

**Maintaining \(\nabla\cdot\mathbf{B}=0\):**

| Scheme | Idea | Trade |
|---|---|---|
| Constrained transport | store \(\mathbf{B}\) on faces, EMF on edges | \(\nabla\cdot\mathbf{B}=0\) to machine precision; harder on AMR/unstructured |
| Divergence cleaning (GLM) | add a scalar field that advects and damps divergence | simple, general; divergence is small but not zero |
| Projection | solve a Poisson equation each step | exact; expensive |
| Powell 8-wave | add source terms proportional to \(\nabla\cdot\mathbf{B}\) | non-conservative; can give wrong jump conditions |

## Mental model

Add elasticity to a fluid. Magnetic pressure resists compression across field lines, tension resists bending along them — so the medium is stiff in some directions and not others, and that anisotropy is the whole subject.

Flux freezing is the other essential picture: the field is painted onto the fluid. Stretch the fluid and you stretch the field, amplifying it — this is the dynamo. Twist it and you store energy in the field. That stored energy can only be released by reconnection, which ideal MHD forbids, which is why the interesting astrophysics happens precisely where ideal MHD stops being valid.

## Numerics / practice

- **Monitor \(\nabla\cdot\mathbf{B}\)** in a dimensionless form such as \(|\nabla\cdot\mathbf{B}|\Delta x/|\mathbf{B}|\) throughout the run, not just at the end.
- **Use constrained transport where you can.** It removes an entire class of failure by construction.
- **Watch the effective resistivity.** Estimate the numerical magnetic Reynolds number from grid spacing; if reconnection rate scales with resolution, it is numerical.
- **Positivity is fragile at low \(\beta\).** When magnetic energy dominates, the thermal pressure recovered from total energy is a small difference of large numbers and can go negative. Use a dual-energy formulation or an entropy variable.

??? warning "Failure modes"
    **\(\nabla\cdot\mathbf{B}\ne0\) producing unphysical force.** A finite divergence yields a force component *along* the field, which cannot exist physically. Symptom: plasma mysteriously accelerated parallel to field lines, worst near strong gradients. This is the defining numerical pathology of MHD.

    **Numerical reconnection mistaken for physical.** Any grid has an effective resistivity of order \(v\Delta x\), so reconnection always occurs at a rate set by resolution. Diagnostic: refine the mesh — if the reconnection rate changes, it was numerical. Astrophysical \(\mathrm{Rm}\sim10^{10}\) is unreachable, so this is a permanent caveat rather than a fixable bug.

    **Negative pressure at low \(\beta\).** With \(\beta\sim10^{-3}\), thermal energy is a 0.1% residual after subtracting kinetic and magnetic energy from the total. Roundoff alone can make it negative. Fix: dual-energy formalism.

    **Roe-type solvers hitting MHD degeneracies.** When wave speeds coincide the eigenvectors become linearly dependent and the decomposition breaks down. Requires renormalised eigenvectors; otherwise expect NaNs at specific field orientations that appear at random times.

    **Powell source terms with strong shocks.** The 8-wave formulation is non-conservative, so shock jump conditions are not guaranteed — the same failure as non-conservative hydrodynamics, giving shocks at the wrong speed.

    **Ideal MHD where kinetic effects matter.** Collisionless reconnection, anisotropic conduction, and the Hall term all break the single-fluid ideal picture at small scales. Ideal MHD gives an answer regardless.

    <!-- Add your own here. -->

## Worked example

Plasma beta decides which physics dominates:

```python
import numpy as np

mu0, kB, mp = 4e-7*np.pi, 1.380649e-23, 1.67262192e-27

cases = [("solar corona",    1e15, 2e6,  1e-2),
         ("solar photosphere", 1e23, 6e3, 1e-1),
         ("ISM cold cloud",  1e8,  20.0, 5e-10)]

for name, n, T, B in cases:
    p_gas = n * kB * T
    p_mag = B**2 / (2 * mu0)
    rho   = n * mp
    vA    = B / np.sqrt(mu0 * rho)
    print(f"{name:20s} beta={p_gas/p_mag:9.3e}   v_A={vA/1e3:9.1f} km/s   "
          f"{'magnetically dominated' if p_gas < p_mag else 'gas dominated'}")
```

```
solar corona         beta=6.940e-04   v_A=   6897.6 km/s   magnetically dominated
solar photosphere    beta=2.082e+00   v_A=      6.9 km/s   gas dominated
ISM cold cloud       beta=2.776e-01   v_A=      1.1 km/s   magnetically dominated
```

Three orders of magnitude apart, and they behave completely differently. The corona at \(\beta\sim10^{-3}\) is magnetically dominated — the field dictates the structure, which is why coronal loops trace field lines and why flares are magnetic-energy releases. The photosphere just below it is gas dominated, so there the flow drags the field around instead. That reversal across a few thousand kilometres is the engine of solar activity, and it is also the numerically hardest thing about modelling it: the low-\(\beta\) corona is exactly where the positivity failure described above bites.

## Connections

- [Plasma](plasma.md) — when the single-fluid description breaks down.
- [Radiative transfer](radiative-transfer.md) — radiation-MHD coupling.
- [Fluids › Compressible flow](../fluids/compressible.md) — the hydrodynamic Riemann machinery MHD extends.
- [Aerospace › Space environment](../aerospace/space-environment.md) — magnetosphere and space weather.

## Sources

- Goedbloed & Poedts, *Principles of Magnetohydrodynamics*.
- Tóth (2000), *The \(\nabla\cdot B = 0\) constraint in shock-capturing MHD codes*.
- Archive: `Astro/ZEUS_MP` — astrophysical MHD code.
