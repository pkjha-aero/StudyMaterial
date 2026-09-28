---
title: Thermal Sciences
status: working
tags: [pillar-1, thermal, conservation, radiation]
---

# Thermal Sciences

<span class="status status-working">working</span>
<span class="pillar">pillar 1</span>

Thermodynamics, heat transfer and combustion — energy accounting, energy transport, and
energy release.

## Pages

| Page | Covers |
|---|---|
| [Thermodynamics](thermodynamics.md) | Laws, entropy generation and exergy, cycles, real-gas behaviour, the statistical connection |
| [Heat transfer](heat-transfer.md) | Conduction, convection and radiation; Biot, Nusselt and the groups that pick the model |
| [Combustion](combustion.md) | Stoichiometry, flame temperature, kinetics, premixed and diffusion flames, turbulent regimes, pollutants |

## Why this section exists

It was added late, and for a specific reason: the [course archive](../resources/course-archive.md)
holds **twelve courses** across these three subjects — engineering and statistical
thermodynamics, heat transfer, radiative heat transfer, three separate combustion courses
and laser diagnostics for combustion — and the site had no page for any of them. Thermal
science was appearing only as a passing mention inside propulsion and governing equations.

That is the kind of gap a catalogue is for: it made visible a body of material the
navigation tree had no home for.

## The theme

**Two clocks, and their ratio.** Thermodynamics asks what is possible given infinite time —
equilibrium, Carnot, the flame temperature you would reach. Heat transfer and combustion
ask how fast, and the answer is always a competition between a transport rate and a
chemical or diffusive one.

Every practically important quantity lives in the gap between those two questions:

- **Exergy destruction** is the price of doing things at finite rate rather than reversibly.
- **The Biot number** compares conduction inside an object with convection off its surface.
- **The Damköhler number** compares turbulent mixing with chemical reaction.
- **Pollutants** exist only because kinetics does not reach equilibrium.

Equilibrium sets the ceiling; rates decide what you actually get.

## Connections

- [Fluids](../fluids/index.md) — the transport half of every problem here.
- [Aerospace › Propulsion](../aerospace/propulsion.md) — cycles and heat release in an engine.
- [Astrophysics › Radiative transfer](../astrophysics/radiative-transfer.md) — the same transfer equation, different opacities.
- [Foundations › Numerical methods](../foundations/numerical-methods.md) — stiffness, which combustion supplies in abundance.
