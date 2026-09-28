---
title: Notebooks
status: working
tags: [pillar-3, foundations, discretization, validation]
---

# Notebooks

<span class="status status-working">working</span>
<span class="pillar">pillar 3 &middot; Discretization and numerical analysis</span>

Worked examples too long for a code block on a topic page. Each one runs end to end and
is committed with its outputs, so the figures and numbers on the site are the ones the
code actually produced.

## Pages

| Notebook | Shows |
|---|---|
| [Sod shock tube](sod-shock-tube.ipynb) | Exact Riemann solution, then three finite-volume schemes against it — isolating reconstruction order from Riemann-solver fidelity, and measuring the observed order on a discontinuous problem |
| [Modified wavenumber](modified-wavenumber.ipynb) | What a difference scheme does to a wave: dispersion, dissipation, and points-per-wavelength as the number that actually sizes a grid |

## Why these two

Both exist to make a claim from a topic page **measurable** rather than asserted.

[Compressible flow](../fluids/compressible.md) says second-order schemes buy sharpness but
not convergence rate on discontinuous problems. The Sod notebook measures it: observed
order ~0.85 for MUSCL against ~0.6 for first order, neither near the nominal 2, while the
error constant differs by a factor of four.

[Numerical methods](../foundations/numerical-methods.md) says formal order is asymptotic
and tells you little about the mesh you can afford. The wavenumber notebook turns that
into a table: 26 points per wavelength for a second-order scheme against 6 for
sixth-order, at the same 1% phase error.

## Running them

Committed pre-executed, and CI renders the stored outputs (`execute: false`) so the build
needs no kernel. To re-run:

```bash
pip install numpy matplotlib jupyter
jupyter nbconvert --to notebook --execute --inplace docs/notebooks/*.ipynb
```

## Connections

- [Compressible flow](../fluids/compressible.md) · [Finite volume](../fluids/cfd/finite-volume.md) · [Time integration](../fluids/cfd/time-integration.md)
- [Numerical methods](../foundations/numerical-methods.md) · [Verification and validation](../foundations/verification-validation.md)
