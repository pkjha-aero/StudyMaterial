---
title: Aircraft and turbine icing
status: working
tags: [pillar-1, aerospace, boundary-layer, validation]
updated: 2026-10-24
---

# Aircraft and turbine icing

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Icing is a **three-part problem**: how much supercooled water hits the surface, how much of it freezes where it lands, and what shape the resulting ice takes.
    - The **freezing fraction** decides everything downstream. All of it freezes on impact → **rime**, a conformal and relatively benign shape. Only part freezes → **glaze**, with runback and horns, and the horns are what cost you.
    - Performance loss is dominated by shape, not mass: a horn a few millimetres high can cut \(C_{L,\max}\) by 30% and raise drag by far more than its frontal area suggests.
    - **Collection efficiency** is a Stokes-number problem. Small droplets follow streamlines and miss; large ones impact. This is why **SLD** conditions are a separate and harder certification case.
    - On a rotor or propeller the same physics acts on a blade whose relative velocity and incidence vary with radius and azimuth, so the accretion is non-uniform and the imbalance matters as much as the aerodynamics.

## Key results

### The three steps

<div class="result" markdown>

**flow field** → **droplet trajectories and collection efficiency \(\beta\)** →
**surface energy balance and freezing fraction \(n\)** → **ice shape** → *(repeat: the shape changes the flow)*

</div>

Icing codes march this loop in time with small accretion steps, because a developed shape alters the flow field that produced it. Single-shot accretion is only valid for short exposures.

### Collection efficiency

Whether a droplet hits is a competition between its inertia and the flow's ability to turn it, measured by an inertia (Stokes) parameter

\[
K = \frac{\rho_d d^2 V}{18 \mu c}
\]

Small \(K\) means the droplet follows streamlines around the body and misses. Large \(K\) means it flies straight and impacts. Consequences worth holding onto:

- **Small leading-edge radius collects more.** A thin, sharp airfoil or a slender blade catches a higher fraction of the water than a blunt one at the same conditions — the opposite of the intuition that a bigger nose catches more.
- **Collection peaks at the stagnation point** and falls to zero at the impingement limits, which set how far back the ice can reach.
- **SLD** — supercooled large droplets, above about 50 μm — have high \(K\), impinge far aft of the normal limits, and can run back behind the protected region before freezing. This is the regime behind appendix-O certification and a different problem from ordinary icing.

### The freezing fraction

A surface energy balance on the water film — the **Messinger** model — determines what fraction \(n\) of the arriving water freezes locally. Heat must be removed to freeze it; the available sinks are convection and evaporation, and the sources are the latent heat of fusion itself, the kinetic energy of the impacting droplets and the ram temperature rise.

| | \(n = 1\) | \(0 < n < 1\) |
|---|---|---|
| Name | **Rime** | **Glaze** |
| Conditions | Cold, low liquid water content | Near freezing, high LWC |
| Appearance | Opaque, white, air trapped in | Clear, dense |
| Shape | Conformal, follows the surface | **Horns**, runback, irregular |
| Severity | Usually mild | The dangerous case |

Glaze is worse for a specific reason: water that does not freeze on impact runs back along the surface and freezes further aft, building protruding horns astride the stagnation region. Those horns separate the flow immediately.

### What the ice costs

- \(C_{L,\max}\) reductions of 20–40% for horn ice of a few millimetres.
- Stall angle reduced, often sharply, and **stall behaviour changed** — frequently to an abrupt one with little buffet warning.
- Drag increases that greatly exceed the ice's frontal area, because the penalty is separation, not blockage.
- **Pitching-moment and hinge-moment changes**, which is the mechanism behind ice-contaminated tailplane stall: the tail stalls first, its download is lost, and the aircraft pitches nose-down with flap extension as the trigger.
- Asymmetric shedding on rotors and propellers produces **imbalance and vibration**, and shed ice becomes an impact hazard to the airframe behind it.

### Protection

| System | Principle | Cost |
|---|---|---|
| **Thermal anti-ice** (bleed or electric) | Keep the surface above freezing — *evaporative*, or *running-wet* with controlled runback | Large power or bleed penalty |
| **Electro-thermal de-ice** | Cyclic heating to shed accreted ice | Less power; accepts some accretion |
| **Pneumatic boot** | Inflate to crack the ice off | Light, cheap; residual ice, not for SLD |
| **Electro-mechanical / expulsive** | Rapid deformation sheds ice | Low power; mechanically demanding |
| **Ice-phobic coatings** | Reduce adhesion | Supplementary only; durability is the issue |

A running-wet anti-ice system removes ice from the protected area and relocates the problem: the water runs back and refreezes aft of the heated region as a **runback ridge**, which can be worse than the ice it prevented.

### Wind turbines

Same physics, different economics and a longer exposure. The blade's relative velocity rises with radius, so collection and kinetic heating both vary strongly along the span, and the outer third of the blade accretes most. Consequences: power loss of 10–20% in icing climates over a season, **mass imbalance** driving loads and vibration, ice throw as a safety constraint, and the fact that a turbine runs for days in conditions an aircraft passes through in minutes. Detection and curtailment are often more economic than heating a 60 m blade.

## Mental model

Think of a water budget on the surface. Water arrives at a rate set by the droplet field and the geometry; it leaves by freezing, by evaporating or by running downstream. The freezing fraction is just the share taken by the first route, and the ice shape is the spatial record of where the budget balanced.

That framing explains why glaze is the dangerous case. At \(n = 1\) the water freezes where it lands, so the ice is a map of the collection efficiency — smooth, conformal, no surprises. At \(n < 1\) the surplus water moves before it freezes, and the deposit no longer matches the impingement pattern. Horns appear where the flow slows and the film stalls, which is exactly where they do most aerodynamic harm.

## Numerics / practice

- **March the accretion in steps** and re-solve the flow between them. A single-shot shape for a 45-minute hold is not a shape.
- **Report the envelope point**, not just "icing": LWC, droplet MVD, total temperature, exposure time, and which appendix.
- **Check the impingement limits** against the protected area. A system sized for appendix C does not cover SLD impingement.
- **Use total temperature, not static.** Ram rise is tens of degrees at speed and shifts the whole problem.
- **Validate the shape before the penalty.** Predicted \(\Delta C_D\) from a wrong shape is meaningless; the shape is the thing to compare against tunnel data.
- **Grid the horn.** Separation from a horn is the aerodynamic effect, and it needs resolution in a region the clean-airfoil mesh never had.

??? warning "Failure modes"
    **Rime methods used in glaze conditions.** A rime model assumes everything freezes on impact and has no runback, so it produces a conformal shape and misses the horns entirely. The predicted performance loss is then far too small, in the conditions that matter most.

    **Static temperature used instead of total.** Kinetic heating raises surface temperature substantially at flight speed, and using static temperature predicts icing where none occurs — or the reverse near the boundary.

    **Clean-airfoil tables used with ice on.** An iced section has a different \(C_{L,\max}\), a different stall angle and a different stall character. Performance codes, [actuator-line](actuator-line.md) models and rotor comprehensive analyses all read from tables, and none of them know.

    **SLD treated as ordinary icing scaled up.** Large droplets splash, re-impinge and run back far aft of normal limits. Appendix-C-based tools and protection extents do not transfer.

    **Anti-ice runback not modelled.** A running-wet system does not remove the water, it moves it. The refrozen ridge aft of the heated area can be aerodynamically worse than the ice that was prevented.

    **Performance penalty estimated from ice mass or frontal area.** The penalty comes from separation triggered by shape. A small, badly placed horn beats a large, smooth accretion.

    **Tailplane ignored.** The tail has a smaller leading-edge radius, so it collects more efficiently than the wing and is usually unmonitored. Ice-contaminated tailplane stall is triggered by flap extension and is nose-down and rapid.

    **Tunnel ice shapes scaled without a scaling law.** Icing similitude needs collection efficiency, freezing fraction and accretion parameter matched together, not just geometry and speed.

    <!-- Add your own here. -->

## Worked example

Where the rime–glaze boundary actually sits, from a simplified Messinger energy balance:

```python
import numpy as np

# Messinger-style surface energy balance, simplified. Water arrives at the surface,
# some fraction n freezes there (freezing fraction). n = 1 is rime, 0 < n < 1 is glaze.
L_f, c_w, c_p = 3.34e5, 4218.0, 1005.0        # J/kg, J/kg/K, J/kg/K
h, beta = 500.0, 0.6                          # convective coeff W/m2/K, collection efficiency

def freezing_fraction(T_inf, LWC, V):
    """T_inf in degC (negative), LWC in kg/m3, V in m/s."""
    mdot = beta*LWC*V                                  # kg/m2/s of water caught
    dT   = -T_inf                                      # degrees below freezing
    conv = h*dT                                        # convective cooling, W/m2
    sens = mdot*c_w*dT                                 # warming the incoming cold droplets
    kin  = mdot*V**2/2                                 # kinetic heating of the droplets
    n = (conv + sens - kin)/(mdot*L_f)
    return min(max(n, 0.0), 1.0)

print("freezing fraction n:   n = 1 rime (all freezes on impact),  n < 1 glaze (runback)")
LWCs = [0.1e-3, 0.3e-3, 0.6e-3, 1.0e-3, 2.0e-3]
print(f"{'T, degC':>8}" + "".join(f"{'LWC='+str(int(l*1e3*10)/10):>12}" for l in LWCs))
for T in (-30, -20, -15, -10, -5, -2):
    row = "".join(f"{freezing_fraction(T, l, 80.0):12.3f}" for l in LWCs)
    print(f"{T:8d}{row}")

print("\nrime/glaze boundary at V = 80 m/s -- the warmest temperature still giving rime:")
for l in LWCs:
    rime = [T for T in np.arange(-40, -0.05, 0.05) if freezing_fraction(T, l, 80.0) >= 0.999]
    print(f"   LWC = {l*1e3:.1f} g/m3 : rime below T = {max(rime):6.1f} degC, glaze above it")

print("\nram (kinetic) heating raises surface temperature; above a speed, ice cannot form:")
for V in (50, 100, 150, 200, 250):
    print(f"   V = {V:3d} m/s -> ram rise {V**2/(2*c_p):5.1f} K"
          f"  -> no icing warmer than about {-V**2/(2*c_p):6.1f} degC ambient")
```

```
freezing fraction n:   n = 1 rime (all freezes on impact),  n < 1 glaze (runback)
 T, degC     LWC=0.1     LWC=0.3     LWC=0.6     LWC=1.0     LWC=2.0
     -30       1.000       1.000       1.000       1.000       0.837
     -20       1.000       1.000       1.000       0.867       0.555
     -15       1.000       1.000       0.960       0.648       0.414
     -10       1.000       1.000       0.637       0.429       0.273
      -5       1.000       0.573       0.313       0.210       0.132
      -2       0.639       0.224       0.120       0.078       0.047

rime/glaze boundary at V = 80 m/s -- the warmest temperature still giving rime:
   LWC = 0.1 g/m3 : rime below T =   -3.2 degC, glaze above it
   LWC = 0.3 g/m3 : rime below T =   -8.7 degC, glaze above it
   LWC = 0.6 g/m3 : rime below T =  -15.7 degC, glaze above it
   LWC = 1.0 g/m3 : rime below T =  -23.1 degC, glaze above it
   LWC = 2.0 g/m3 : rime below T =  -35.8 degC, glaze above it

ram (kinetic) heating raises surface temperature; above a speed, ice cannot form:
   V =  50 m/s -> ram rise   1.2 K  -> no icing warmer than about   -1.2 degC ambient
   V = 100 m/s -> ram rise   5.0 K  -> no icing warmer than about   -5.0 degC ambient
   V = 150 m/s -> ram rise  11.2 K  -> no icing warmer than about  -11.2 degC ambient
   V = 200 m/s -> ram rise  19.9 K  -> no icing warmer than about  -19.9 degC ambient
   V = 250 m/s -> ram rise  31.1 K  -> no icing warmer than about  -31.1 degC ambient
```

The table is the whole phenomenology in one grid. Cold and dry — top left — gives \(n = 1\): everything freezes on impact, rime, conformal, comparatively benign. Warm and wet — bottom right — gives \(n \approx 0.05\): **95% of the arriving water does not freeze where it lands**, runs back, and freezes somewhere else. That is the horn-building regime.

The boundary moves a long way with liquid water content, which is the non-obvious part. At 0.1 g/m³ the accretion is rime only below about \(-3°\mathrm{C}\); at 2.0 g/m³ you need \(-36°\mathrm{C}\) before everything freezes on contact. More water does not simply make more ice — it changes the *kind* of ice, because the same convective cooling now has far more latent heat to remove. A cloud that produces harmless rime at low LWC produces glaze at high LWC at the same temperature.

The last block is why high-speed aircraft worry less. Ram heating raises the surface total temperature by \(V^2/2c_p\): 5 K at 100 m/s, 31 K at 250 m/s. At transport cruise speeds the surface simply is not below freezing in most icing clouds, which is why the serious icing exposure is at hold and approach speeds — and why a wind turbine blade, whose outboard sections see 60–80 m/s and a ram rise under 3 K, has no such protection and accretes for hours.

Two caveats. This is a simplified balance: it omits evaporation and sublimation, assumes a surface at exactly 0°C in the glaze regime, and takes a fixed convective coefficient and collection efficiency, all of which vary over the surface. The boundary temperatures are therefore indicative rather than design values. What is robust is the *structure* — the strong LWC dependence, and the direction each term pushes.

## Connections

- [Aerodynamics](aerodynamics.md) — the clean sections this degrades, and why separation dominates the penalty.
- [Actuator line and disk models](actuator-line.md) — where iced airfoil tables would have to enter a rotor calculation.
- [Rotorcraft](rotorcraft.md) · [Wind energy](wind-energy.md) · [Propellers](propellers.md) — rotating applications, with span-varying accretion.
- [Flight mechanics](flight-mechanics.md) — stall margin, trim and tailplane effects.
- [Thermal › Heat transfer](../thermal/heat-transfer.md) — the convective and latent terms in the energy balance.
- [Meteorology › Radiation and clouds](../meteorology/radiation-clouds.md) — where supercooled liquid water comes from.

## Sources

- Messinger, "Equilibrium temperature of an unheated icing surface as a function of air speed", *J. Aeronautical Sciences* **20** (1953) — the energy balance.
- Gent, Dart & Cansdale, "Aircraft icing", *Phil. Trans. R. Soc. A* **358** (2000) — a good overview of the whole chain.
- Bragg, Broeren & Blumenthal, "Iced-airfoil aerodynamics", *Progress in Aerospace Sciences* **41** (2005) — the performance penalties.
- Jha, Brillembourg & Schmitz, "Wind turbines under atmospheric icing conditions: ice accretion modeling, aerodynamics, and control strategies for mitigating performance degradation", 50th AIAA Aerospace Sciences Meeting (2012).
- FAR/CS-25 Appendix C and Appendix O — the certification icing envelopes, including SLD.
- LEWICE and FENSAP-ICE documentation for the standard computational approaches.
