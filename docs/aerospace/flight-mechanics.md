---
title: Flight mechanics
status: solid
tags: [pillar-1, aerospace, scaling]
updated: 2026-09-26
---

# Flight mechanics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Performance follows from the drag polar plus thrust: **range, endurance, climb rate and turn** are all algebra once you have \(C_D(C_L)\).
    - **Static margin** — distance from CG to neutral point, in chords — is the single number governing longitudinal stability. Positive is stable, and it moves as fuel burns.
    - Linearised about trim, the longitudinal dynamics split into a fast **short period** and a slow **phugoid**; the lateral into **roll subsidence**, **Dutch roll** and **spiral**.
    - **Stability and controllability trade against each other.** More static margin costs trim drag and control authority.
    - Breguet range assumes constant \(L/D\) and \(\mathrm{SFC}\) — a cruise-climb idealisation, not a flight plan.

## Key results

**Steady level flight and the polar:**

<div class="result" markdown>

\[
L = W = \tfrac{1}{2}\rho V^2 S C_L,
\qquad
D = \tfrac{1}{2}\rho V^2 S\left(C_{D_0} + kC_L^2\right),
\qquad
k = \frac{1}{\pi e \mathrm{AR}}
\]

</div>

**Breguet range**, jet aircraft:

\[
R = \frac{V}{c_t}\,\frac{L}{D}\,\ln\frac{W_i}{W_f}
\qquad\text{(propeller: } R = \frac{\eta_p}{c_p}\frac{L}{D}\ln\frac{W_i}{W_f}\text{)}
\]

Maximum range for a jet occurs at \(\max(V\,L/D)\), i.e. \(\max(C_L^{1/2}/C_D)\) — *faster* than best \(L/D\). Maximum endurance is at \(\max(L/D)\).

**Climb and energy:**

\[
\text{RoC} = \frac{P_{\text{avail}} - P_{\text{req}}}{W},
\qquad
h_e = h + \frac{V^2}{2g}
\]

Specific excess power \(P_s = V(T-D)/W\) contours are the standard way to see what an aircraft can actually do across its envelope.

**Turning:**

\[
n = \frac{1}{\cos\phi},
\qquad
R_{\text{turn}} = \frac{V^2}{g\sqrt{n^2-1}},
\qquad
\dot{\psi} = \frac{g\sqrt{n^2-1}}{V}
\]

**Longitudinal static stability.** With \(h\) the CG position and \(h_n\) the neutral point, both in chords from the leading edge:

\[
\frac{dC_m}{dC_L} = h - h_n,
\qquad
\text{static margin} = h_n - h > 0 \ \text{for stability}
\]

**Dynamic modes:**

| Mode | Character | Typical | Driven by |
|---|---|---|---|
| Short period | fast, well damped | 1–5 s | pitch stiffness \(M_\alpha\), damping \(M_q\) |
| Phugoid | slow, lightly damped | 30–100 s | exchange of altitude and speed |
| Roll subsidence | fast, non-oscillatory | <1 s | roll damping \(L_p\) |
| Dutch roll | moderate, oscillatory | 3–10 s | yaw stiffness vs dihedral effect |
| Spiral | very slow, often divergent | 20–100+ s | balance of \(L_\beta\) and \(N_\beta\) |

A mildly divergent spiral is acceptable and common — it is slow enough for the pilot or autopilot to correct.

## Mental model

Performance is a bookkeeping exercise on energy: thrust adds it, drag removes it, and the difference is available for climbing or accelerating. Once that framing is in place, the specific-excess-power chart replaces a dozen separate formulae.

Stability is about restoring moments. Displace the aircraft in pitch, and a stable configuration generates a moment that reduces the displacement. The neutral point is where that restoring moment vanishes; putting the CG behind it makes the aircraft divergent. Everything about static margin follows from that one picture.

## Numerics / practice

- **Track CG travel across the whole loading envelope.** Fuel burn, payload and stores all move it. The binding case is usually aft CG at low fuel.
- **Linearised models are valid near trim only.** Large-amplitude manoeuvres, stall and spin need the full nonlinear equations.
- **Non-dimensionalise consistently.** Sign and reference-length conventions for stability derivatives differ between textbooks and between tools; mixing them is a classic source of sign errors.
- **Check mode characteristics against handling-qualities criteria** (e.g. Cooper–Harper, MIL-STD-1797 bands) rather than judging damping ratios in isolation.

??? warning "Failure modes"
    **Static margin sign and reference confusion.** Different sources define it from the leading edge, the quarter chord, or the CG, and some flip the sign. A sign error here inverts the stability conclusion entirely. Always state the reference and sanity-check against a known-stable configuration.

    **CG checked at one loading only.** An aircraft stable at takeoff can be unstable at aft-CG, low-fuel conditions. This is a loading-envelope question, not a single-point one.

    **Breguet applied to a real mission.** It assumes constant \(L/D\), constant \(\mathrm{SFC}\) and cruise-climb. Real missions have step climbs, reserves, and off-design cruise. Symptom: range overpredicted by 10–20% against a segment-by-segment integration.

    **Best range and best endurance confused.** For a jet, best endurance is at \(\max(L/D)\) and best range at \(\max(C_L^{1/2}/C_D)\) — a noticeably higher speed. Cruising at best \(L/D\) costs range.

    **Stability equated with good handling.** A very stable aircraft is sluggish and needs large control surfaces and more trim drag. Modern fighters are deliberately relaxed-stability or unstable, closed-loop stabilised. Stability is a design variable, not a virtue.

    **Linearised dynamics used past their range.** Small-perturbation derivatives evaluated at cruise say nothing about post-stall behaviour. Departure and spin are nonlinear phenomena.

    **Ignoring thrust-line offset.** A thrust line above or below the CG produces a pitching moment that varies with power setting, coupling throttle to trim. Easy to omit and very visible in flight.

    <!-- Add your own here. -->

## Worked example

Best-range and best-endurance speeds are not the same point:

```python
import numpy as np

CD0, e, AR = 0.022, 0.80, 9.0
k  = 1.0 / (np.pi * e * AR)

CL_endurance = np.sqrt(CD0 / k)             # max L/D
CL_range     = np.sqrt(CD0 / (3 * k))       # max CL^(1/2)/CD  (jet)

for name, CL in (("endurance (max L/D)", CL_endurance), ("range (jet)", CL_range)):
    CD = CD0 + k * CL**2
    print(f"{name:22s} CL={CL:.3f}  L/D={CL/CD:5.2f}  V/V_ref={1/np.sqrt(CL):.3f}")
```

```
endurance (max L/D)    CL=0.705  L/D=16.03  V/V_ref=1.191
range (jet)            CL=0.407  L/D=13.88  V/V_ref=1.567
```

Best range flies about 32% faster than best endurance, and accepts a 13% lower \(L/D\) to do it — the extra speed more than pays for the lost efficiency.

## Connections

- [Aircraft design](aircraft-design.md) — where these performance equations become constraints.
- [Aerodynamics](aerodynamics.md) — where the drag polar comes from.
- [Propulsion](propulsion.md) — thrust and specific fuel consumption.
- [Structures](structures.md) — load factor limits that bound the manoeuvre envelope.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — eigenanalysis of the linearised system.

## Sources

- Anderson, *Introduction to Flight* — performance fundamentals.
- Etkin & Reid, *Dynamics of Flight: Stability and Control*.
- Archive: `Aerospace/AERSP420` and related; see the [course archive](../resources/course-archive.md).
