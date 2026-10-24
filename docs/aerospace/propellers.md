---
title: Propellers
status: working
tags: [pillar-1, aerospace, scaling]
updated: 2026-10-24
---

# Propellers

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - A propeller is a **rotating wing**, and its entire operating point is set by one number: the advance ratio \(J = V/(nD)\).
    - The blade sees the vector sum of forward and rotational velocity. **Pitch is geometry; angle of attack is what makes thrust**, and the difference between them is why blades are twisted.
    - Efficiency is a property of the *operating point*, not of the propeller. A fixed-pitch blade is efficient over a narrow band of \(J\) and a compromise everywhere else — which is the whole reason constant-speed units exist.
    - The limit is **helical tip Mach number**, not RPM. It ties efficiency, noise and blade count together into a single constraint.
    - A propeller is not only a thrust source. Torque reaction, slipstream swirl, P-factor and gyroscopic moments all feed into handling, and they are the reason a twin has a critical engine.

## Key results

### Geometry, and why blades are twisted

At radius \(r\), the blade section sees forward speed \(V\) and rotational speed \(\Omega r\). The angle between the resultant and the plane of rotation is the **helix angle**:

\[
\phi(r) = \arctan\frac{V}{\Omega r},
\qquad
\alpha(r) = \beta(r) - \phi(r)
\]

where \(\beta\) is the **blade angle** — the geometric setting — and \(\alpha\) is the angle of attack that actually produces lift. Because \(\phi\) falls as \(r\) grows, a blade at uniform \(\beta\) would run at wildly different \(\alpha\) along its span. **Twist exists to cancel \(\phi(r)\)**, not for any subtler reason. The classical choice is constant geometric pitch, \(p = 2\pi r\tan\beta(r) = \text{const}\).

A vocabulary worth keeping straight, because the terms are old and overloaded:

| Term | Meaning |
|---|---|
| **Geometric pitch** | Advance per revolution if the blade section followed its own angle, \(2\pi r\tan\beta\) |
| **Effective pitch** | The distance the aircraft actually advances per revolution, \(V/n\) |
| **Slip** | The difference between them — and the reason there is any \(\alpha\) at all |
| **Experimental pitch** | Advance per revolution at which the propeller produces zero thrust |

Slip is often described as a loss. It is not: zero slip means zero angle of attack and zero thrust.

### Advance ratio

\[
J = \frac{V}{nD}
\]

with \(n\) in revolutions per second. \(J\) fixes the helix angle everywhere on the blade — at the conventional reference station,

\[
\tan\phi_{0.75R} = \frac{J}{0.75\pi}
\]

so two propellers at the same \(J\) are aerodynamically similar regardless of size or RPM. This is why propeller data is always plotted against \(J\) and never against airspeed.

### Coefficients, and a trap

\[
C_T = \frac{T}{\rho n^2 D^4},
\qquad
C_P = \frac{P}{\rho n^3 D^5},
\qquad
\eta = \frac{TV}{P} = J\,\frac{C_T}{C_P}
\]

**These are not the rotorcraft coefficients.** [Rotorcraft](rotorcraft.md) normalises on disk area and tip speed, \(C_T = T/\rho A(\Omega R)^2\); the propeller convention normalises on \(n\) and \(D\). The two differ by a factor involving \(\pi^3/8\), and mixing them is one of the most common ways to get a wrong answer that looks plausible. Check which convention a data set uses before using it.

The momentum-theory ceiling on efficiency, from the same argument as [propulsive efficiency](propulsion.md):

\[
\eta_i = \frac{2}{1 + \sqrt{1 + C_{T_{\text{disk}}}}},
\qquad C_{T_{\text{disk}}} = \frac{T}{\tfrac{1}{2}\rho V^2 A}
\]

Lightly loaded is efficient. That is the same statement as low disk loading in hover and high bypass ratio in a turbofan.

### Why constant-speed units exist

A fixed blade angle is correct at one \(J\). Below it the blade stalls, above it the blade reaches zero and then negative \(\alpha\). A **constant-speed unit** governs RPM by varying \(\beta\), which keeps the blade near its best angle of attack across the speed range — the propeller then rides the upper envelope of the whole fixed-pitch family. The worked example below quantifies the gain.

The full range of blade angle is wider than cruise control:

| Mode | Blade angle | What is happening |
|---|---|---|
| **Fine / takeoff** | Low \(\beta\) | High RPM, high thrust, low \(J\) |
| **Coarse / cruise** | High \(\beta\) | Low RPM, best \(\eta\) at high \(J\) |
| **Windmilling** | Low \(\beta\), no power | Airflow drives the propeller; **large drag** |
| **Feathered** | \(\beta \approx 90°\) | Blade edge-on, minimum drag after an engine failure |
| **Reverse** | \(\beta < 0\) | Negative thrust for braking on the ground |

The windmilling case is the one that matters for safety. A failed engine with an unfeathered propeller can produce more drag than the whole rest of the airframe, which is why feathering is automatic on most multi-engine aircraft and why engine-out performance is quoted feathered.

### The tip speed constraint

The tip sees the vector sum of rotation and flight speed:

\[
M_{\text{helical}} = \frac{\sqrt{V^2 + (\Omega R)^2}}{a}
\]

Keeping this below roughly 0.85–0.9 caps the usable product of RPM and diameter. Everything else about propeller configuration follows from that cap: you cannot absorb more power by spinning faster, and you cannot grow the diameter indefinitely (ground clearance, and \(\Omega R\) again), so **more power means more blades or wider blades** — which is why high-power turboprops carry five and six blades and why propfans use many highly swept ones. The same constraint sets the noise, since tip Mach drives [thickness and high-speed impulsive noise](aeroacoustics.md) directly.

**Activity factor** quantifies how much power a blade can absorb for its diameter, weighting chord by \(r^3\); blade **solidity** and activity factor are the two knobs once diameter is capped.

### Installed effects

A propeller does more to an aircraft than push it. All four of these are asymmetric, and all four appear in handling:

- **Torque reaction** — the airframe rolls against the direction of rotation.
- **Slipstream swirl** — the helical wake strikes the fin at an angle, producing a yawing moment that varies with power and speed. The usual reason an aircraft needs rudder in a climb.
- **P-factor** — at positive fuselage incidence the descending blade meets a higher \(\alpha\) than the ascending one, moving the thrust centroid sideways and yawing the aircraft.
- **Gyroscopic moment** — the rotating mass precesses, converting a pitch rate into a yaw rate and vice versa.

On a twin with both propellers turning the same way these combine to make one engine the **critical engine**: losing it leaves the shorter moment arm for the remaining thrust and the higher \(V_{MC}\). **Counter-rotating** propellers (one engine handed) remove the asymmetry; **contra-rotating** coaxial pairs on a single shaft recover the swirl energy as well, at a large cost in mechanical complexity and noise.

## Mental model

A propeller is a wing travelling on a helix, and the helix angle changes along the span and with flight speed. Every distinctive feature follows from that one fact: twist exists because \(\phi\) varies with radius, constant-speed units exist because \(\phi\) varies with speed, and the tip Mach limit exists because the helix is longest at the tip.

The second idea is that a propeller is a *low disk loading* device. It accelerates a large mass of air slightly, which is exactly what [propulsive efficiency](propulsion.md) rewards, and it is why propellers beat jets below about \(M = 0.6\) and lose above it — not because the blades stop working, but because the tips reach the compressibility limit first.

## Numerics / practice

- **Use the induced-velocity form of BEMT, not the induction-factor form.** Writing momentum as \(dT = 4\pi r\rho(V+v)v\,F\,dr\) stays well posed down to \(V = 0\); the \(a\)-form has \(V^2\) in the denominator and degenerates at low \(J\), returning efficiencies above 1 if you do not notice.
- **Always include Prandtl tip loss.** Without it thrust is overpredicted by several percent, as in [rotorcraft](rotorcraft.md) and [wind energy](wind-energy.md).
- **Plot against \(J\), never against airspeed.** A \(\eta(V)\) curve is specific to one RPM and one diameter and transfers nowhere.
- **Correct the outboard sections for compressibility** once helical tip Mach exceeds about 0.7; the outer 20% of the blade does most of the work and reaches the limit first.
- **Check Reynolds number before trusting model-scale data.** Model propellers run an order of magnitude lower in \(Re\), and the section \(C_{d_0}\) that sets efficiency is exactly what \(Re\) changes.

??? warning "Failure modes"
    **The two coefficient conventions mixed.** Propeller \(C_T = T/\rho n^2D^4\) and rotor \(C_T = T/\rho A(\Omega R)^2\) are different numbers for the same thrust. Reading a value from one source into a formula written for the other produces a plausible-looking answer that is wrong by a constant factor, and nothing in the units flags it.

    **Induction-factor BEMT used near static thrust.** The axial momentum relation carries \(V^2\), so as \(J \to 0\) the induction factor must diverge. Solvers clip or stall and quietly return nonsense — efficiencies above 1 are the usual symptom, but the thrust is wrong long before that becomes visible.

    **Efficiency treated as a property of the propeller.** \(\eta\) is a property of the operating point. A propeller quoted at "88% efficient" is being quoted at its best \(J\), which may be nowhere near the one it will fly at.

    **Windmilling drag ignored in engine-out analysis.** An unfeathered stopped-engine propeller is a large bluff disk, not a neutral object. Single-engine climb performance computed without it is optimistic to the point of being dangerous.

    **Slip treated as a loss to be minimised.** Zero slip is zero angle of attack and therefore zero thrust. The useful quantity is efficiency, not slip.

    **Tip Mach ignored when adding power.** Raising RPM to absorb more power runs into compressibility on the advancing tip, where it costs efficiency and noise simultaneously. Past the limit, more RPM buys less thrust.

    **Slipstream treated as purely axial.** The wake rotates, and the swirl is what strikes the fin and tailplane. Trim, fin sizing and the power-dependent yaw all come from the component that an axial model discards.

    **Model-scale propeller data scaled on \(J\) alone.** \(J\) matching gives kinematic similarity but not Reynolds similarity, and section drag — which is what efficiency is made of — does not transfer.

    <!-- Add your own here. -->

## Worked example

Why a fixed-pitch propeller is always a compromise. Blade-element momentum theory in induced-velocity form, with Prandtl tip loss, run across advance ratio for a family of blade angles:

```python
import numpy as np

B, R, c, rho = 3, 1.25, 0.10, 1.225          # blades, radius m, chord m, air density
cd0, a0, Clmax, n = 0.010, 2*np.pi, 1.4, 40.0      # airfoil, and rev/s (held fixed)
r  = np.linspace(0.20*R, 0.98*R, 80)
dr = r[1] - r[0]

def solve(J, beta75):
    """BEMT in induced-velocity form (well posed down to J=0), Prandtl tip loss."""
    Om, V = 2*np.pi*n, J*n*2*R
    beta  = np.arctan(np.tan(beta75) * 0.75*R / r)       # constant geometric pitch
    v, w  = np.full_like(r, 1.0), np.zeros_like(r)
    for _ in range(500):
        Va, Vt = V + v, Om*r - w
        phi = np.arctan2(Va, Vt)
        W2  = Va**2 + Vt**2
        F   = (2/np.pi)*np.arccos(np.clip(
                  np.exp(-B*(R-r)/(2*r*np.sin(phi))), 0, 1))
        Cl  = np.clip(a0*(beta - phi), -Clmax, Clmax)
        Cd  = cd0 + 0.02*Cl**2
        Cn  = Cl*np.cos(phi) - Cd*np.sin(phi)
        Ct  = Cl*np.sin(phi) + Cd*np.cos(phi)
        Z   = W2*B*c*Cn/(8*np.pi*r*F)
        v_n = (-V + np.sqrt(np.maximum(V**2 + 4*Z, 0)))/2     # v^2 + Vv - Z = 0
        w_n = W2*B*c*Ct/(8*np.pi*r*(V + v_n)*F)
        v, w = v + 0.2*(v_n - v), w + 0.2*(np.clip(w_n, 0, Om*r*0.5) - w)
    T = np.sum(0.5*rho*W2*B*c*Cn)*dr
    P = np.sum(0.5*rho*W2*B*c*Ct*r)*dr*Om
    return T, P, (T*V/P if P > 0 else 0.0)

betas = np.radians([15, 20, 25, 30, 35, 40])
print("propulsive efficiency: fixed-pitch blade angles vs the constant-speed envelope")
print(f"{'J':>5}" + "".join(f"{d:>7.0f}" for d in np.degrees(betas)) + f"{'CSU':>8}")
for J in np.arange(0.2, 1.81, 0.2):
    row = [solve(J, b)[2] for b in betas]
    print(f"{J:5.1f}" + "".join("      -" if e <= 0 else f"{e:7.2f}" for e in row)
          + f"{max(row):8.2f}")
print()
Js = np.arange(0.05, 2.61, 0.02)
for b in betas:
    es = np.array([solve(J, b)[2] for J in Js])
    i  = int(np.argmax(es))
    band = Js[es > 0.80]
    span = (f"eta > 0.80 over J = {band.min():.2f}-{band.max():.2f}"
            if band.size else "never reaches 0.80")
    print(f"beta75 = {np.degrees(b):2.0f} deg : peak {es[i]:.2f} at J = {Js[i]:.2f};  {span}")

env = np.array([max(solve(J, b)[2] for b in betas) for J in Js])
band = Js[env > 0.80]
print(f"\nconstant-speed envelope: eta > 0.80 over J = {band.min():.2f}-{band.max():.2f}"
      f"  (a span of {band.max()-band.min():.2f} in J)")
```

```
propulsive efficiency: fixed-pitch blade angles vs the constant-speed envelope
    J     15     20     25     30     35     40     CSU
  0.2   0.48   0.42   0.38   0.36   0.36   0.36    0.48
  0.4   0.73   0.67   0.61   0.57   0.56   0.56    0.73
  0.6   0.57   0.81   0.76   0.71   0.68   0.67    0.81
  0.8      -   0.75   0.85   0.80   0.76   0.74    0.85
  1.0      -      -   0.84   0.87   0.82   0.79    0.87
  1.2      -      -      -   0.88   0.87   0.84    0.88
  1.4      -      -      -      -   0.90   0.88    0.90
  1.6      -      -      -      -   0.74   0.90    0.90
  1.8      -      -      -      -      -   0.89    0.89

beta75 = 15 deg : peak 0.77 at J = 0.49;  never reaches 0.80
beta75 = 20 deg : peak 0.83 at J = 0.69;  eta > 0.80 over J = 0.59-0.75
beta75 = 25 deg : peak 0.86 at J = 0.91;  eta > 0.80 over J = 0.69-1.01
beta75 = 30 deg : peak 0.88 at J = 1.15;  eta > 0.80 over J = 0.81-1.29
beta75 = 35 deg : peak 0.90 at J = 1.39;  eta > 0.80 over J = 0.93-1.57
beta75 = 40 deg : peak 0.90 at J = 1.67;  eta > 0.80 over J = 1.07-1.89

constant-speed envelope: eta > 0.80 over J = 0.59-1.89  (a span of 1.30 in J)
```

Read the table down a column and the compromise is obvious. A 25° blade peaks at \(\eta = 0.86\) near \(J = 0.9\) and produces no useful thrust at all by \(J = 1.4\); a 40° blade is excellent in cruise and mediocre at the low speeds where takeoff happens. Each fixed setting holds \(\eta > 0.80\) over a span of roughly **0.16 to 0.48 in \(J\)**. The envelope — what a constant-speed unit delivers by rotating the blade as speed changes — holds it over **1.30**, three to eight times wider.

Two details worth noticing. The dashes are not failures of the solver: they are blade angles too coarse for that speed, where \(\alpha\) has gone negative and the propeller is windmilling rather than thrusting. And the peak efficiency itself climbs with blade angle, from 0.77 to 0.90, because a coarser blade at higher \(J\) runs at a better lift-to-drag ratio on its sections — the same reason a high-speed propeller is a different object from a climb propeller.

The model is deliberately simple: thin-airfoil lift, a quadratic drag polar, no compressibility and no hub or spinner. It gets the shape of the family and the width of the envelope right, which is the point here; absolute efficiencies from it should be treated as a few percent optimistic.

## Connections

- [Rotorcraft](rotorcraft.md) — the same BEMT machinery, with the disk loaded across its own axis.
- [Wind energy](wind-energy.md) — BEM again, with the energy flowing the other way.
- [Propulsion](propulsion.md) — where the shaft power comes from, and the propulsive efficiency argument in general form.
- [Aeroacoustics](aeroacoustics.md) — tip Mach, thickness and loading noise; the constraint that caps tip speed.
- [Aerodynamics](aerodynamics.md) — the blade sections themselves.
- [Aircraft design](aircraft-design.md) — propeller-driven sizing, and why span pays more than cleanliness for a loiterer.

## Sources

- Hitchens, *Propellor Aerodynamics* — history, terminology, constant-speed units and the installed handling effects.
- Leishman, *Principles of Helicopter Aerodynamics* — the BEMT machinery, tip loss, and the momentum theory this shares with rotors.
- McCormick, *Aerodynamics, Aeronautics and Flight Mechanics* — propeller charts and the classical coefficient conventions.
- Glauert, *The Elements of Aerofoil and Airscrew Theory* — the original treatment.
