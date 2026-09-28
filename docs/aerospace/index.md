---
title: Aerospace
status: solid
tags: [pillar-1, aerospace]
---

# Aerospace

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1</span>

Applied aerospace disciplines — the domain physics layered on top of
[fluids](../fluids/index.md) and [foundations](../foundations/index.md).

## Pages

| Page | Covers |
|---|---|
| [Aircraft design](aircraft-design.md) | The sizing loop, constraint diagrams, weight growth, the limits of regression |
| [Aerodynamics](aerodynamics.md) | Circulation, thin airfoil and lifting-line theory, drag decomposition, compressibility |
| [Flight mechanics](flight-mechanics.md) | Performance, Breguet range, static margin, the five dynamic modes |
| [Propulsion](propulsion.md) | Thrust, Brayton cycle, propulsive efficiency and bypass ratio, rockets |
| [Structures and aeroelasticity](structures.md) | Thin-walled sections, buckling, divergence, flutter, fatigue |
| [Turbomachinery](turbomachinery.md) | Euler equation, velocity triangles, stage loading limits, stall and surge |
| [Aeroacoustics](aeroacoustics.md) | Lighthill's analogy, FW-H, velocity scaling, rotor noise |
| [Rotorcraft](rotorcraft.md) | Momentum theory, BEMT, forward-flight asymmetry, autorotation |
| [Wind energy](wind-energy.md) | Betz limit, BEM with corrections, wakes, Weibull resource |
| [Space environment and orbits](space-environment.md) | Two-body motion, \(J_2\), delta-v, drag, the space hazard set |
| [Experimental methods](experimental-methods.md) | The measurement chain, bias vs precision, tunnel corrections, flight test |

## One idea that recurs

**Move a lot of mass slowly rather than a little mass quickly.** It appears as
[propulsive efficiency and bypass ratio](propulsion.md), as
[disk loading in hover](rotorcraft.md), and inverted as the
[Betz limit](wind-energy.md). Three subjects, one momentum argument — worth recognising,
because a result derived in one transfers directly to the others.

[Aeroacoustics](aeroacoustics.md) arrives at the same place from a fourth direction: jet
noise scales as \(U^8\), so the quiet engine and the efficient engine are the same
engine. When four independent lines of reasoning converge on one design choice, that is
usually the real constraint.

## One more, about measurement

[Experimental methods](experimental-methods.md) sits slightly apart — it is pillar 10
rather than pillar 1, and it is the only page here about how you would *know* any of this
is true. The rest of the site is theory and computation; validation data has to come from
somewhere, and it arrives with error bars that decide what a comparison can support.

## Connections

- [Fluids](../fluids/index.md) — the underlying flow physics.
- [Foundations](../foundations/index.md) — the numerics.
- [Meteorology › Boundary layer](../meteorology/boundary-layer.md) — turbine and low-altitude inflow.
- [Astrophysics › Plasma](../astrophysics/plasma.md) — the spacecraft charging environment.

## Sources

Per page. See the [course archive](../resources/course-archive.md) for the Aerospace and
Mechanical folders, which hold most of this material.
