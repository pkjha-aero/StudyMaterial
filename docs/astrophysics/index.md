---
title: Astrophysics
status: solid
tags: [pillar-1, astrophysics]
---

# Astrophysics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1</span>

Astrophysical fluid and plasma dynamics, and the numerical methods peculiar to them.

## Pages

| Page | Covers |
|---|---|
| [Radiative transfer](radiative-transfer.md) | Transfer equation, optical depth, LTE, diffusion and its limits, mean opacities |
| [Magnetohydrodynamics](mhd.md) | Ideal MHD, flux freezing, plasma beta, the \(\nabla\cdot\mathbf{B}=0\) constraint |
| [N-body and gravitational dynamics](n-body-gravity.md) | Tree and mesh methods, softening, symplectic integration, SPH |
| [Plasma physics](plasma.md) | Debye length, kinetic vs fluid, PIC and its numerical pathologies |

Code usage for FLASH, Athena, Gadget and ZEUS-MP lives in
[toolchains › astro codes](../toolchains/index.md); these pages cover the physics and the
numerics.

## What makes astrophysical numerics distinctive

Three constraints that rarely bind in engineering CFD and always bind here:

- **Enormous dynamic range.** Densities and timescales spanning many orders of magnitude
  in one domain, which is why AMR and individual timesteps are standard rather than exotic.
- **Constraints that must hold exactly.** \(\nabla\cdot\mathbf{B}=0\) is not a
  convergence target; violating it produces forces that do not exist.
- **Unreachable parameter regimes.** Astrophysical \(\mathrm{Rm}\sim10^{10}\) and
  \(\mathrm{Re}\sim10^{12}\) mean the simulation is never in the physical regime. Numerical
  resistivity and viscosity always dominate, and the honest question is whether the result
  depends on them.

## Connections

- [Fluids › Compressible flow](../fluids/compressible.md) — the Riemann machinery MHD extends.
- [Foundations › Numerical methods](../foundations/numerical-methods.md) — stability and order.
- [Aerospace › Space environment](../aerospace/space-environment.md) — the near-Earth end of the same physics.
- [Toolchains › Astro codes](../toolchains/astro-codes.md) — running these simulations.

## Sources

Per page. See the [course archive](../resources/course-archive.md) for the Astro folders.
