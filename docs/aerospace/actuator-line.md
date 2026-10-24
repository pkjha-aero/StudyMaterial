---
title: Actuator line and disk models
status: working
tags: [pillar-1, aerospace, discretization, turbulence]
updated: 2026-10-24
---

# Actuator line and disk models

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - A rotor blade is replaced by **body forces in the flow** rather than a resolved surface. The boundary layer is never meshed, so the grid is set by the wake rather than by \(y^+\).
    - The force is computed from **blade-element theory using the locally sampled velocity**, then **smeared onto the grid with a Gaussian of width \(\varepsilon\)**.
    - \(\varepsilon\) is the whole method. It must be **large enough to resolve on the grid** and **small enough to represent the blade**, and those two requirements usually conflict.
    - Sampling velocity at the actuator point samples the flow the actuator itself induced. Getting the **induced velocity** right is the central difficulty, not an implementation detail.
    - The hierarchy — **disk → line → curve/surface** — trades cost against how much of the blade's near-field is represented.

## Key results

### The hierarchy

| Model | Represents | Resolves | Typical use |
|---|---|---|---|
| **Actuator disk** | Rotor as a permeable disk, forces azimuthally averaged | No blades, no tip vortices | Wind-farm and mesoscale arrays |
| **Actuator line** | Each blade as a rotating line of force points | Discrete tip vortices, blade passage | Wake and loads studies |
| **Actuator surface / curve** | Chordwise force distribution, not a point | Near-field pressure structure | Loads where the near wake matters |
| **Blade-resolved** | The actual geometry | Boundary layer, stall | Sectional aerodynamics, validation |

The disk gives the right momentum deficit and no blade signature. The line adds the periodic structure — tip and root vortices, 3P loading — for roughly the cost of a finer grid in the rotor region. Everything above the disk is a way of putting back some of what smearing a line removed.

### The algorithm

<div class="result" markdown>

sample velocity at each actuator point → compute \(\alpha\) and \(W\) → look up \(C_l, C_d\)
→ form the sectional force → **project onto the grid with a Gaussian kernel** →
advance the flow → repeat

</div>

The projection uses

\[
f_\varepsilon(\mathbf{x}) = \sum_i \mathbf{F}_i\,\eta_\varepsilon(|\mathbf{x}-\mathbf{x}_i|),
\qquad
\eta_\varepsilon(d) = \frac{1}{\varepsilon^3 \pi^{3/2}}\exp\!\left[-\left(\frac{d}{\varepsilon}\right)^2\right]
\]

A delta function would be ideal and is unrepresentable; the Gaussian is what makes the force integrable on a finite grid, and \(\varepsilon\) is its width.

### The two constraints on \(\varepsilon\), and why they fight

**Numerical.** The kernel must be resolved by the mesh or the projected force depends on where the actuator point happens to sit within a cell. The standard guideline is \(\varepsilon/\Delta \gtrsim 2\), and the worked example derives it.

**Physical.** The smeared force produces an induced velocity that is too weak near the blade, because spreading a bound vortex over width \(\varepsilon\) weakens its own induction. Matching the induced velocity of a real lifting surface requires \(\varepsilon\) tied to the **chord**, with \(\varepsilon \approx 0.25c\) a widely used value from 2D vortex-sheet arguments.

These conflict. On a wind-turbine blade the tip chord may be a metre or two while a practical LES cell is several metres, so \(\varepsilon \ge 2\Delta\) forces \(\varepsilon\) far above \(0.25c\) exactly where the loading gradient is steepest. The consequence is systematic: **tip loads are over-predicted and the tip vortex is too weak and too diffuse**, which then feeds the wake.

Three families of response, and they are the live research area:

- **Tip/smearing corrections** — add back the missing induction analytically, by estimating what a vortex of width \(\varepsilon\) fails to induce compared with a concentrated one.
- **Variable \(\varepsilon\)** — let the width follow the chord along the span rather than holding it constant, at the cost of needing the grid to follow too.
- **Actuator curve embedding** — embed the near-field of the lifting line analytically and let the grid carry only the far-field, decoupling the physical width from the grid width.

### Velocity sampling

The velocity used to compute the force must be the one the blade *would* see — but the only velocity available is the one at the actuator point, which already contains the actuator's own induction. Sampling naively double-counts it.

Options in use: sample at the point and accept the error (most common, and \(\varepsilon\)-dependent); sample on a ring or upstream and correct; or compute the induction analytically and subtract it. This is the same self-induction problem that vortex methods solve with a desingularised kernel, and it is the reason two ALM codes with identical airfoil tables can disagree by several percent in power.

### Grid and time step

- The rotor region needs \(\Delta\) fine enough that \(\varepsilon \ge 2\Delta\) with \(\varepsilon\) small enough to be physical — in practice this sets the cell size, not the wake.
- The time step should keep the blade tip from crossing more than about one cell per step: \(\Omega R\,\Delta t \lesssim \Delta\). This is usually more restrictive than the flow CFL.
- The wake region can coarsen, which is what makes [AMR](../computing/amr.md) natural for these problems.

## Mental model

The actuator line is a deliberate trade: give up the blade boundary layer, which costs orders of magnitude in grid, and buy the wake, which is what you actually wanted. The sectional aerodynamics is imported from tables — so the method knows nothing about stall it was not told — and the CFD supplies only the three-dimensional, unsteady, turbulent velocity field the blade flies through.

That split explains the error structure. Anything the airfoil tables get wrong, the ALM gets wrong, including [dynamic stall](rotorcraft.md). Anything the grid cannot resolve, the wake gets wrong, including the tip vortex. The method is accurate in the middle — integrated loads and far-wake structure — and least reliable at exactly the two ends.

## Numerics / practice

- **Report \(\varepsilon\), \(\varepsilon/\Delta\) and \(\varepsilon/c\)** with every result. Without all three the result cannot be compared with anyone else's, and most published discrepancies between ALM codes come down to this.
- **Check the projected force sums to the applied force.** It is one line of diagnostics and it catches both a too-narrow kernel and a truncated projection stencil.
- **Use a tip correction, and say which one.** Without one, tip loading and therefore power are over-predicted; with one, the result depends on the choice.
- **Resolve the chord-scale time step**, not just the CFL.
- **Validate on blade loads before wake statistics.** A wake can look plausible while the loads that generated it are wrong.

??? warning "Failure modes"
    **\(\varepsilon\) chosen from the grid alone.** Setting \(\varepsilon = 2\Delta\) and refining the mesh changes the *physics* of the model, not just its accuracy, because \(\varepsilon\) is a physical width. Grid convergence with \(\varepsilon\) tied to \(\Delta\) converges to the wrong answer — a convergence study that looks textbook and is meaningless.

    **\(\varepsilon\) chosen from the chord alone.** If the resulting \(\varepsilon/\Delta\) is below about 2, the projected force depends on sub-cell blade position, which oscillates at blade-passing frequency and pollutes exactly the unsteady loads the method was run to obtain.

    **Self-induced velocity double-counted.** Sampling the velocity at the actuator point includes the actuator's own induction. The effective angle of attack is then too low, and the error scales with \(\varepsilon\) — so it changes when the grid changes, which is easily mistaken for grid sensitivity.

    **Tip correction omitted or applied twice.** Some airfoil tables and some ALM implementations already include a tip treatment. Applying Prandtl's correction on top of a corrected table double-counts and under-predicts tip loading.

    **Blade-element tables used outside their range.** The method has no mechanism to detect that a section is at 30° incidence at a Reynolds number the table never covered. It will interpolate, return a number, and the simulation will proceed.

    **Disk model used where blade structure matters.** An actuator disk cannot produce tip vortices, blade-passing unsteadiness or the wake meandering that depends on them. Using it for fatigue loads or for near-wake structure is a category error, however good the momentum deficit looks.

    **Grid refined only in the wake.** The expensive region is the rotor, because \(\varepsilon\) couples to \(\Delta\) there. Refining the wake while leaving the rotor coarse improves the picture and not the physics.

    <!-- Add your own here. -->

## Worked example

Where the \(\varepsilon/\Delta \gtrsim 2\) guideline comes from. The Gaussian is exact as an integral; the grid evaluates it as a **sum** over cell centres, and the actuator point moves continuously through the mesh as the blade rotates:

```python
import numpy as np

# Actuator line: a blade-element force is a point in the flow. It is spread onto the grid
# with a 3D Gaussian of width epsilon.  eta(d) = exp(-(d/eps)^2) / (eps^3 pi^(3/2))
# The grid only "sees" the kernel at cell centres, so the projected force is a SUM,
# and whether that sum recovers the force depends on eps/dx -- and on where in the cell
# the actuator point happens to sit.
def projected(eps_dx, offset):
    """Total force recovered after projecting a unit point force onto the grid."""
    half = max(12, int(np.ceil(6*eps_dx)))      # stencil wide enough to not truncate
    i = np.arange(-half, half + 1)
    X, Y, Z = np.meshgrid(i - offset[0], i - offset[1], i - offset[2], indexing="ij")
    d2 = (X**2 + Y**2 + Z**2) / eps_dx**2            # distances in units of dx
    return np.sum(np.exp(-d2)) / (eps_dx**3 * np.pi**1.5)

# worst case over sub-cell placement: the actuator line sweeps, it is never cell-aligned
offsets = [(0,0,0), (0.5,0,0), (0.5,0.5,0), (0.5,0.5,0.5), (0.25,0.1,0.4)]
print("recovered fraction of the applied force (1.000 = exact)")
print(f"{'eps/dx':>8}{'best':>10}{'worst':>10}{'spread':>11}")
for e in (0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
    v = [projected(e, o) for o in offsets]
    print(f"{e:8.2f}{max(v):10.4f}{min(v):10.4f}{max(v)-min(v):11.2e}")

print("\nsub-cell placement sensitivity -- the reason the guideline exists:")
for e in (1.0, 2.0, 3.0):
    v = [projected(e, o) for o in offsets]
    print(f"   eps/dx = {e:.0f}:  force varies by {100*(max(v)-min(v)):.4f}% "
          f"depending only on where in the cell the actuator point lies")
```

```
recovered fraction of the applied force (1.000 = exact)
  eps/dx      best     worst     spread
    0.50    1.6004    0.5728   1.03e+00
    0.75    1.0235    0.9769   4.66e-02
    1.00    1.0003    0.9997   6.21e-04
    1.50    1.0000    1.0000   2.72e-09
    2.00    1.0000    1.0000   3.33e-16
    2.50    1.0000    1.0000   0.00e+00
    3.00    1.0000    1.0000   0.00e+00
    4.00    1.0000    1.0000   1.11e-16

sub-cell placement sensitivity -- the reason the guideline exists:
   eps/dx = 1:  force varies by 0.0621% depending only on where in the cell the actuator point lies
   eps/dx = 2:  force varies by 0.0000% depending only on where in the cell the actuator point lies
   eps/dx = 3:  force varies by 0.0000% depending only on where in the cell the actuator point lies
```

At \(\varepsilon/\Delta = 0.5\) the projected force is between 57% and 160% of what was applied, depending only on where in the cell the actuator point currently sits. Nothing physical changes between those two cases — the blade is at the same radius with the same loading — so this is pure quadrature error, and because the blade sweeps through the mesh it appears as a spurious oscillation at blade-passing frequency.

By \(\varepsilon/\Delta = 1\) the spread is 0.06%, and by \(\varepsilon/\Delta = 2\) it is at machine precision. That is the guideline: **two cells per kernel width makes the projection grid-independent**, and the convergence is fast enough that there is no reason to sit near the edge of it.

What the example cannot show is the other half of the problem. This calculation says only that the force lands on the grid correctly; it says nothing about whether \(\varepsilon\) is the right *physical* width. A blade with a 2 m tip chord wants \(\varepsilon \approx 0.5\) m, and a 4 m LES cell demands \(\varepsilon \ge 8\) m — a factor of sixteen apart, with no setting satisfying both. Everything in the literature about tip corrections, variable kernels and curve embedding exists in that gap.

## Connections

- [Wind energy](wind-energy.md) — actuator disk, the Betz limit, and BEM.
- [Rotorcraft](rotorcraft.md) — the same method applied to a rotor in forward flight.
- [Propellers](propellers.md) — blade-element machinery shared with both.
- [Fluids › LES](../fluids/turbulence/les.md) — the solver these forces are injected into.
- [Meteorology › Multiscale coupling](../meteorology/multiscale-coupling.md) — where the inflow turbulence comes from.
- [Computing › Adaptive mesh refinement](../computing/amr.md) — resolving the rotor without resolving the domain.

## Sources

- Sørensen & Shen, "Numerical modeling of wind turbine wakes", *J. Fluids Engineering* **124** (2002) — the original actuator line.
- Jha, Churchfield, Moriarty & Schmitz, "Guidelines for volume force distributions within actuator line modeling of wind turbines on large-eddy simulation-type grids", *J. Solar Energy Engineering* **136** (2014).
- Jha & Schmitz, "Actuator curve embedding — an advanced actuator line model", *J. Fluid Mechanics* **834**, R2 (2018).
- Troldborg, *Actuator line modeling of wind turbine wakes*, PhD thesis, DTU (2008).
- Martínez-Tossas, Churchfield & Meneveau, "Optimal smoothing length scale for actuator line models of wind turbine blades", *Wind Energy* **20** (2017).
- Schmitz & Jha, "Modeling the wakes of wind turbines and rotorcraft using the actuator-line method in an OpenFOAM-LES solver", 69th AHS Annual Forum (2013).
