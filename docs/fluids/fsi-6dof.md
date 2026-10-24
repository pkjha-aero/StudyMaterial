---
title: Fluid–structure and 6-DOF coupling
status: working
tags: [pillar-1, fluids, numerical-stability, conservation]
updated: 2026-10-24
---

# Fluid–structure and 6-DOF coupling

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Coupling a flow solver to a moving body is **a stability problem before it is an accuracy problem**, and the instability has nothing to do with the time step.
    - **Added mass** is the culprit: accelerating a body accelerates fluid with it, so the fluid reaction is proportional to the body's own acceleration. Lag that term and the scheme can diverge.
    - **Partitioned** coupling reuses two mature solvers and can be unstable; **monolithic** coupling is stable and means writing one solver. Most production work is partitioned with sub-iteration.
    - For a **rigid body** the coupling is six ordinary differential equations, and the difficulty moves to mesh motion and to quaternions.
    - The mesh is the other half of the problem: **deform, overset, or immersed**, each with a different failure mode.

## Key results

### The coupling hierarchy

| Scheme | Exchange per step | Stability | Cost |
|---|---|---|---|
| **One-way** | Fluid → structure only | Always stable | Cheapest; valid only when motion barely changes the flow |
| **Loose / explicit partitioned** | One exchange, lagged | **Conditionally unstable** — see below | One fluid solve per step |
| **Strong / implicit partitioned** | Sub-iterate to convergence within the step | Stable with relaxation | 3–10 fluid solves per step |
| **Monolithic** | One coupled system | Unconditionally stable | One large ill-conditioned solve |

### The added-mass instability

Accelerate a body through a fluid and you accelerate some fluid with it. For an incompressible fluid this reaction is instantaneous and proportional to the body's acceleration:

<div class="result" markdown>

\[
F_{\text{fluid}} = -m_a\,\ddot{x} + (\text{other terms}),
\qquad m_a \sim \rho_f \mathcal{V}
\]

</div>

In a partitioned explicit scheme the fluid is solved using the structure's acceleration from the **previous** step, so this term is lagged. The resulting iteration amplifies by roughly \(m_a/m_s\) per step, giving the central result:

**Loose partitioned coupling is unstable when the added mass exceeds the structural mass, and reducing the time step does not help.** This is a property of the operator splitting, not a CFL condition. It is why water couples badly and air couples easily, and why the instability so often appears first on the lightest component.

| Regime | \(m_a/m_s\) | Behaviour |
|---|---|---|
| Aeroelastic wing in air | small | Loose coupling fine |
| Wind turbine blade | moderate | Loose coupling usually fine; watch the tip |
| Submarine, ship, valve in water | large | Loose coupling diverges; sub-iteration required |
| Flexible pipe, heart valve, parachute | very large | Strong coupling or monolithic only |

The fixes, in increasing order of robustness: **under-relaxation** of the exchanged interface quantity; **Aitken dynamic relaxation**, which adapts the factor from successive residuals; **interface quasi-Newton** (IQN-ILS), which builds an approximate Jacobian from past iterates and is the current standard; and **monolithic**, which removes the question.

### Rigid-body 6-DOF

For an unflexing body the structure is six ODEs — translation in an inertial frame, rotation in the body frame:

\[
m\dot{\mathbf{v}} = \mathbf{F}, \qquad
\mathbf{I}\dot{\boldsymbol{\omega}} + \boldsymbol{\omega}\times(\mathbf{I}\boldsymbol{\omega}) = \mathbf{M}
\]

Three practical points dominate implementations:

- **Use quaternions, not Euler angles.** Euler angles gimbal-lock, and a manoeuvring vehicle will find it. Renormalise the quaternion every step.
- **Added mass is a \(6\times6\) tensor**, not a scalar, and its off-diagonal terms couple heave to pitch and sway to yaw. For a slender submerged body those cross terms are what make the manoeuvre, and omitting them produces a vehicle that turns wrongly rather than one that is merely inaccurate.
- **The hydrodynamic coefficients are the model.** Classical manoeuvring practice fits a polynomial force model in the velocities and rates; CFD-in-the-loop replaces the polynomial with a solve, at a cost that makes the coupling scheme matter.

### Mesh motion

| Approach | Idea | Fails when |
|---|---|---|
| **Deforming mesh** | Move boundary nodes, diffuse into the interior | Rotation or large displacement destroys cells |
| **Overset / Chimera** | Separate body-fitted grids that overlap and interpolate | Interpolation is not conservative; hole-cutting is fiddly |
| **Immersed boundary** | Fixed grid, body imposed through forcing | Wall resolution is poor; boundary layers expensive |
| **Sliding interface** | Rotation only, matched interface | Only for pure rotation |

Mesh quality is a stability issue in its own right: a deforming mesh degrades gradually, and the simulation usually diverges some way after the mesh actually became unusable.

## Mental model

Two solvers that are each stable can be unstable when coupled, and the reason is that the splitting throws away a term that is not small. The added mass is physically part of the structure's inertia; lagging it is equivalent to solving the structure with the wrong mass, and if the error exceeds the real mass the sign of the effective inertia flips.

Read that way, the whole subject is about how much of the coupling to treat implicitly. One-way keeps none, loose keeps none but exchanges, strong iterates until it is effectively implicit, monolithic is implicit by construction. The cost ordering and the stability ordering are the same list read in opposite directions.

## Numerics / practice

- **Estimate \(m_a/m_s\) before choosing a scheme.** A potential-flow added-mass estimate takes minutes and tells you whether loose coupling can possibly work.
- **Sub-iterate to a residual, not a fixed count.** A fixed three iterations is a scheme with no convergence statement.
- **Check interface conservation.** Force transferred to the structure should equal force on the fluid surface; overset interpolation in particular does not guarantee it.
- **Monitor mesh quality as a solution variable** and stop on a threshold rather than on divergence.
- **Verify the rigid-body integrator separately**, with the fluid off: a free body under known force should conserve energy and momentum to the integrator's order.
- **Test added mass directly**: impulsively accelerate the body in still fluid and compare the measured reaction with potential theory.

??? warning "Failure modes"
    **Time step reduced to cure an added-mass instability.** The threshold does not depend on \(\Delta t\), and refining usually makes the divergence *faster* in wall-clock terms because more amplifying steps are taken per unit of physical time. This is the single most common wasted week in FSI work.

    **One-way coupling used where motion changes the flow.** Fine for a stiff wing in cruise; wrong for flutter, for a manoeuvring hull, or for anything near a stability boundary — and one-way coupling cannot by construction predict an instability, so it returns a reassuring answer.

    **Added mass treated as a scalar on a non-slender body.** It is a tensor with off-diagonal coupling. A 6-DOF model using a single added-mass number gets the coupled modes — pitch-heave, yaw-sway — qualitatively wrong.

    **Euler angles in a manoeuvring simulation.** The singularity is at 90° pitch, which is exactly where an interesting manoeuvre goes.

    **Fixed number of coupling sub-iterations.** Convergence varies through a run, typically worsening as the motion grows. A fixed count silently becomes loose coupling at the worst moment.

    **Mesh deformation quality unmonitored.** By the time the solver diverges the mesh has been invalid for some time, and the last plausible-looking output is already wrong.

    **Interface interpolation assumed conservative.** Overset and non-matching interfaces interpolate; interpolation does not conserve. Over a long run the imbalance integrates into a drift that looks like physics.

    <!-- Add your own here. -->

## Worked example

The added-mass instability, in the simplest system that shows it: a spring-mounted piston pushing an incompressible fluid column, coupled explicitly.

```python
import numpy as np

# Piston of mass m_s on a spring, pushing an INCOMPRESSIBLE column of fluid (area A,
# length L). The fluid exerts a reaction -m_a * xddot with added mass m_a = rho_f*A*L.
# Partitioned explicit coupling: the fluid is solved with the structure acceleration from
# the PREVIOUS step, so the added-mass term is lagged.
def loose(mr, dt, n=60, relax=1.0):
    """mr = m_a/m_s. Returns peak |x| over n steps; growth means instability."""
    k, x, v, a_prev = 1.0, 1.0, 0.0, 0.0
    peak = 1.0
    for _ in range(n):
        a = -k*x - mr*a_prev          # structure sees LAGGED fluid reaction
        a = relax*a + (1-relax)*a_prev
        v += a*dt; x += v*dt
        a_prev = a
        peak = max(peak, abs(x))
    return peak

print("partitioned explicit FSI: peak displacement after 60 steps (started at x=1)")
print(f"{'m_a/m_s':>9}" + "".join(f"{'dt='+str(d):>14}" for d in (0.1, 0.05, 0.025, 0.0125)))
for mr in (0.2, 0.5, 0.9, 1.0, 1.1, 2.0, 5.0):
    row = "".join(f"{loose(mr, d, int(6/d)):14.3e}" for d in (0.1, 0.05, 0.025, 0.0125))
    print(f"{mr:9.1f}{row}")

print("\nThe instability threshold is m_a/m_s = 1, and it does NOT move with dt.")
print("Refining the time step is the usual reflex and it does not help:")
for d in (0.1, 0.01, 0.001):
    print(f"   dt = {d:<7} m_a/m_s = 2.0 -> peak {loose(2.0, d, int(6/d)):.2e}")

print("\nAitken-style under-relaxation on the coupling buys back stability:")
print(f"{'relax':>7}{'m_a/m_s = 2':>16}{'m_a/m_s = 5':>16}")
for r in (1.0, 0.5, 0.3, 0.2, 0.1):
    print(f"{r:7.2f}{loose(2.0, 0.01, 600, r):16.3e}{loose(5.0, 0.01, 600, r):16.3e}")
```

```
partitioned explicit FSI: peak displacement after 60 steps (started at x=1)
  m_a/m_s        dt=0.1       dt=0.05      dt=0.025     dt=0.0125
      0.2     1.000e+00     1.000e+00     1.000e+00     1.000e+00
      0.5     1.000e+00     1.000e+00     1.000e+00     1.000e+00
      0.9     1.000e+00     1.000e+00     1.000e+00     1.000e+00
      1.0     1.000e+00     1.000e+00     1.000e+00     1.000e+00
      1.1     1.062e+00     3.216e+01     7.288e+05     1.537e+15
      2.0     1.955e+15     5.264e+32     1.692e+68    7.348e+139
      5.0     1.091e+39     2.269e+80    4.180e+163           inf

The instability threshold is m_a/m_s = 1, and it does NOT move with dt.
Refining the time step is the usual reflex and it does not help:
   dt = 0.1     m_a/m_s = 2.0 -> peak 1.95e+15
   dt = 0.01    m_a/m_s = 2.0 -> peak 6.23e+175
   dt = 0.001   m_a/m_s = 2.0 -> peak inf

Aitken-style under-relaxation on the coupling buys back stability:
  relax     m_a/m_s = 2     m_a/m_s = 5
   1.00      6.230e+175             inf
   0.50       1.000e+00      3.094e+175
   0.30       1.001e+00       1.000e+00
   0.20       1.006e+00       1.000e+00
   0.10       1.021e+00       1.000e+00
```

The first table is the result that matters. Below \(m_a/m_s = 1\) the scheme is stable at every time step tried; above it, the scheme diverges at every time step tried. **The threshold is a mass ratio, and the time step does not appear in it.**

The second block makes the point that the reflex fails. Going from \(\Delta t = 0.1\) to \(0.001\) at \(m_a/m_s = 2\) takes the peak displacement from \(10^{15}\) to overflow — refining the step makes it *worse*, because the amplification is per coupling exchange and a smaller step means more exchanges over the same physical time. Anyone who has tried to stabilise a water-coupled FSI run by halving \(\Delta t\) has watched this happen.

The third block is the practical fix. Under-relaxing the exchanged interface quantity restores stability, and the relaxation needed scales with the mass ratio — 0.5 is enough at \(m_a/m_s = 2\), 0.3 at 5. Aitken's method automates the choice by estimating it from successive residuals, which is why it is the default in most coupling libraries.

One caveat on the numbers: the clean threshold at exactly 1 belongs to this lumped two-mass model. For a real geometry the condition involves the largest eigenvalue of the added-mass operator against the structural mass distribution, so the threshold moves — but the structure of the result, including its independence from \(\Delta t\), does not.

## Connections

- [Aerospace › Structures and aeroelasticity](../aerospace/structures.md) — divergence and flutter, the aeroelastic end of this.
- [Aerospace › Actuator line](../aerospace/actuator-line.md) — turbine blades coupled to a structural solver.
- [Aerospace › Rotorcraft](../aerospace/rotorcraft.md) — rotor blade dynamics, where the same coupling appears per revolution.
- [CFD › Meshing](cfd/meshing.md) — deforming, overset and immersed grids.
- [CFD › Time integration](cfd/time-integration.md) — the stability framework this sits inside.
- [Foundations › Estimation and filtering](../foundations/estimation-filtering.md) — state estimation for the same rigid-body models.

## Sources

- Causin, Gerbeau & Nobile, "Added-mass effect in the design of partitioned algorithms for fluid–structure problems", *CMAME* **194** (2005) — the stability analysis behind the worked example.
- Degroote, "Partitioned simulation of fluid–structure interaction", *Arch. Comput. Methods Eng.* **20** (2013) — IQN-ILS and the quasi-Newton family.
- Fossen, *Handbook of Marine Craft Hydrodynamics and Motion Control* — 6-DOF conventions, added-mass tensors, manoeuvring models.
- Motta-Mena, Jha, Campbell, Schmitz & Brasseur, "Wind turbine fluid–structure interaction using an actuator line solver and a finite element solver in a tightly-coupled implementation", AIAA SciTech (2014).
