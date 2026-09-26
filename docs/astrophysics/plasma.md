---
title: Plasma physics
status: solid
tags: [pillar-1, astrophysics, plasma, kinetic, pic]
updated: 2026-09-26
---

# Plasma physics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - A plasma is quasi-neutral over scales larger than the **Debye length** and collective over times longer than the inverse **plasma frequency**. Those two numbers define the whole subject.
    - **Collisionality decides the model**: collisional plasmas can be treated as fluids (MHD); collisionless ones need a kinetic description.
    - The **Vlasov equation** lives in 6D phase space, which is why particle-in-cell exists.
    - **PIC numerically heats** if the Debye length is unresolved — a purely numerical instability that looks like physics.
    - Astrophysical and space plasmas are usually **magnetised and collisionless**, the hardest combination.

## Key results

**The defining scales:**

<div class="result" markdown>

\[
\lambda_D = \sqrt{\frac{\varepsilon_0 k_B T_e}{n_e e^2}},
\qquad
\omega_{pe} = \sqrt{\frac{n_e e^2}{\varepsilon_0 m_e}},
\qquad
\Lambda = n_e \lambda_D^3 \gg 1
\]

</div>

\(\Lambda\), the number of particles in a Debye sphere, is the plasma parameter. \(\Lambda\gg1\) means collective behaviour dominates over binary collisions — the definition of a plasma.

**Gyromotion:**

\[
\omega_c = \frac{qB}{m},
\qquad
r_L = \frac{m v_\perp}{qB}
\]

When \(r_L\) is small compared to gradient scales, guiding-centre theory applies and the magnetic moment \(\mu = mv_\perp^2/2B\) is an adiabatic invariant — the basis of magnetic mirrors and of radiation-belt trapping.

**Model hierarchy**, most to least detailed:

| Model | Dimensions | Valid when |
|---|---|---|
| Klimontovich / exact | 6N | never used |
| Vlasov / Fokker–Planck | 6D + t | collisionless / weakly collisional |
| Multi-fluid | 3D + t per species | scales above the ion inertial length |
| Hall MHD | 3D + t | ion and electron motions decouple |
| Ideal MHD | 3D + t | collisional, large-scale, single-fluid |

**Vlasov equation:**

\[
\frac{\partial f_s}{\partial t} + \mathbf{v}\cdot\nabla f_s + \frac{q_s}{m_s}\left(\mathbf{E} + \mathbf{v}\times\mathbf{B}\right)\cdot\nabla_{\mathbf{v}} f_s = 0
\]

Coupled to Maxwell's equations through the charge and current moments of \(f_s\).

**Particle-in-cell.** Sample \(f\) with macroparticles, deposit charge and current onto a grid, solve the fields there, interpolate back, push particles. Stability requires resolving the fastest scales:

\[
\Delta x \lesssim \lambda_D,
\qquad
\omega_{pe}\Delta t \lesssim 2,
\qquad
\text{and } c\Delta t < \Delta x \text{ for explicit EM}
\]

**Landau damping** is collisionless damping of a wave by particles moving near the phase velocity — energy transfers to the particle distribution with no collisions at all. It is the canonical result that a fluid model cannot reproduce, and the clearest reason kinetic theory is needed.

**Reconnection.** In collisionless plasma, reconnection proceeds far faster than resistive MHD predicts. The Hall term and electron pressure anisotropy set the rate in the diffusion region. This is the gap between ideal MHD and observed solar-flare and magnetospheric timescales.

## Mental model

Two pictures, and the skill is knowing which applies. The **fluid** picture treats the plasma as a conducting continuum — valid when collisions (or wave-particle scattering) keep the distribution close to Maxwellian. The **kinetic** picture tracks the distribution in velocity space — necessary when the distribution develops structure that matters: beams, temperature anisotropy, resonant particles.

The test is whether anything depends on particles at a specific velocity. Landau damping, reconnection rates and instability thresholds all do; bulk momentum balance usually does not.

## Numerics / practice

- **Compute \(\lambda_D\), \(\omega_{pe}\), \(r_L\) and the mean free path** before choosing a model. These four numbers justify the choice.
- **Resolve \(\lambda_D\) in explicit PIC**, or use an implicit/energy-conserving formulation designed to avoid the constraint.
- **Use many particles per cell.** PIC noise scales as \(1/\sqrt{N_{ppc}}\); fewer than ~20 per cell gives noticeably noisy moments.
- **Reduced mass ratios** (\(m_i/m_e = 100\) rather than 1836) are common for cost and change the scale separation. State the value used.

??? warning "Failure modes"
    **Numerical heating in PIC.** If \(\Delta x \gg \lambda_D\), the finite-grid instability transfers energy from the grid to the particles and the plasma heats steadily for no physical reason. Symptom: total energy climbing monotonically. The standard mistake is reading this as physical heating; the diagnostic is that it scales with \(\Delta x/\lambda_D\), not with any physical parameter.

    **Fluid model on a collisionless problem.** MHD cannot produce Landau damping, temperature anisotropy, or fast reconnection. It will still produce an answer — smooth, stable and wrong in the specific ways that matter.

    **PIC noise mistaken for turbulence.** Finite particle number produces broadband fluctuations that look like a turbulent cascade in a spectrum. Diagnostic: increase particles per cell; physical turbulence is unchanged, noise falls as \(1/\sqrt{N_{ppc}}\).

    **Reduced mass ratio effects unreported.** \(m_i/m_e=100\) compresses the separation between ion and electron scales, which changes reconnection rates and instability growth. Legitimate for cost, but it must be stated and its effect assessed.

    **Guiding-centre theory where \(r_L\) is not small.** Near nulls and in thin current sheets the Larmor radius is comparable to the gradient scale, the adiabatic invariant is not conserved, and particles become chaotic. Guiding-centre codes give smooth, confidently wrong trajectories there.

    **Quasi-neutrality assumed below \(\lambda_D\).** Charge separation is real at Debye scales — in sheaths, double layers, and near boundaries. A quasi-neutral model cannot represent a sheath at all.

    <!-- Add your own here. -->

## Worked example

Which model is justified, from four numbers:

```python
import numpy as np

eps0, kB, e, me = 8.8541878128e-12, 1.380649e-23, 1.602176634e-19, 9.1093837015e-31

cases = [("solar wind at 1 AU", 5e6,  1e5,  5e-9),
         ("solar corona",       1e15, 2e6,  1e-2),
         ("tokamak core",       1e20, 1e8,  5.0)]

for name, n, T, B in cases:
    lam_D = np.sqrt(eps0 * kB * T / (n * e**2))
    w_pe  = np.sqrt(n * e**2 / (eps0 * me))
    Lam   = n * lam_D**3
    r_L   = np.sqrt(2 * me * kB * T) / (e * B)
    print(f"{name:20s} lam_D={lam_D:9.2e} m  w_pe={w_pe:9.2e} rad/s  "
          f"Lambda={Lam:9.2e}  r_Le={r_L:8.2e} m")
```

```
solar wind at 1 AU   lam_D= 9.76e+00 m  w_pe= 1.26e+05 rad/s  Lambda= 4.65e+09  r_Le=1.98e+03 m
solar corona         lam_D= 3.09e-03 m  w_pe= 1.78e+09 rad/s  Lambda= 2.94e+07  r_Le=4.43e-03 m
tokamak core         lam_D= 6.90e-05 m  w_pe= 5.64e+11 rad/s  Lambda= 3.29e+07  r_Le=6.26e-05 m
```

All three have \(\Lambda \gg 1\), so all are genuine plasmas. But \(\lambda_D\) spans five orders of magnitude — resolving it in the solar wind means 10 m cells across an astronomical unit, which is why kinetic simulation of the solar wind is always done in small boxes and never globally.

## Connections

- [MHD](mhd.md) — the fluid limit, and where it stops being valid.
- [Radiative transfer](radiative-transfer.md) — emission from plasmas.
- [Aerospace › Space environment](../aerospace/space-environment.md) — spacecraft charging and the radiation belts.

## Sources

- Chen, *Introduction to Plasma Physics and Controlled Fusion*.
- Birdsall & Langdon, *Plasma Physics via Computer Simulation* — PIC and its numerical pathologies.
- Archive: `Aerospace/AERSP597I_SpaceEnvInteraction`.
