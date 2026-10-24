---
title: Rotorcraft
status: solid
tags: [pillar-1, aerospace, scaling]
updated: 2026-10-24
---

# Rotorcraft

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Momentum theory gives the **ideal** hover power; figure of merit measures how close a real rotor gets, typically 0.7–0.8.
    - **Induced power dominates in hover, profile and parasite power in forward flight** — which is why the power curve has a minimum at moderate speed, not at zero.
    - Forward flight is fundamentally **asymmetric**: the advancing blade sees \(V_{tip}+V\), the retreating blade \(V_{tip}-V\). Everything hard about rotorcraft follows from this.
    - Speed is limited at both ends: **advancing-blade compressibility** above, **retreating-blade stall** below.
    - Momentum theory **fails in descent**. The vortex ring state is outside its assumptions, and it is a real flight hazard.
    - A single main rotor needs **anti-torque**, and the tail rotor is a whole second rotor design problem that consumes 3–5% of main rotor power in normal flight and up to 20% at the edges of the envelope.
    - The rotor does not lift the weight — it lifts the weight **plus its own download on the fuselage**, and near the ground it gets a large thrust bonus back.
    - Retreating-blade stall is **dynamic** stall: the blade pitches up rapidly, overshoots static \(C_{L,\max}\), sheds a leading-edge vortex, and pays for it with a violent nose-down pitching moment.

## Key results

### Hover

**Momentum theory in hover**, disk area \(A\), thrust \(T\):

<div class="result" markdown>

\[
v_i = \sqrt{\frac{T}{2\rho A}},
\qquad
P_{\text{ideal}} = T v_i = \frac{T^{3/2}}{\sqrt{2\rho A}},
\qquad
\mathrm{FM} = \frac{P_{\text{ideal}}}{P_{\text{actual}}}
\]

</div>

Power scales as \(T^{3/2}/\sqrt{A}\): **disk loading is the dominant design parameter**. A helicopter (low disk loading) hovers far more efficiently than a jet in VTOL (very high disk loading).

### The rotor is not the aircraft

Two corrections separate the rotor from the machine, and both are routinely left out of first estimates.

**Download.** The rotor slipstream strikes the fuselage, so the rotor must lift more than the weight:

\[
T = \frac{W}{1 - f_v/A}
\]

with \(f_v\) the fuselage equivalent vertical drag area. Typically \(f_v/A \lesssim 0.05\) for a conventional helicopter — but much larger for a tilt-rotor or compound, whose wing sits squarely in the downwash. It is a configuration penalty, not a detail.

**Ground effect.** Near the ground the slipstream cannot contract freely, and thrust rises for the same power. Cheeseman and Bennett's result, valid for \(z/R \gtrsim 0.5\):

\[
\left[\frac{T}{T_\infty}\right]_{P=\text{const}} = \frac{1}{1 - (R/4z)^2}
\]

which gives roughly +33% thrust at \(z/R = 0.5\), +7% at \(z/R = 1\), and under 2% by \(z/R = 2\). Hence the operational rule that a helicopter can hover in ground effect at a weight or density altitude it could not manage out of ground effect — and the test rule that a rotor must be at least \(2R\) off the ground before its measurements mean anything.

**Anti-torque.** A single main rotor applies a torque reaction to the fuselage that something must balance. The tail rotor thrust follows from the main rotor power and the tail moment arm \(x_{TR}\):

\[
T_{TR} = \frac{P_i + P_0 + P_p}{\Omega\, x_{TR}}
\]

It costs 3–5% of main rotor power in normal flight and up to 20% at the extremes, and it is a rotor design problem in its own right — operating in the main rotor wake, in sideways flow, and with its own vortex ring state. A **fan-in-fin** trades some hover efficiency for safety and noise; **NOTAR** replaces it with boom circulation control; **coaxial, tandem and synchropter** layouts dispose of the problem by cancelling torque between rotors instead, and pay for it in hub complexity or interference losses.

Loss of tail rotor effectiveness in crosswind or at high power is a recognised handling hazard, and tail rotor failure is one of the few rotorcraft emergencies with no good outcome in the hover.

### Blade element and forward flight

**Blade element momentum theory.** Equate blade-element lift to momentum flux in each annulus, iterating on the inflow. For a rotor with solidity \(\sigma = Nc/(\pi R)\), the standard non-dimensional results:

\[
C_T = \frac{T}{\rho A (\Omega R)^2},
\qquad
\lambda_i = \sqrt{\frac{C_T}{2}} \quad\text{(uniform inflow, hover)},
\qquad
C_P = \frac{C_T^{3/2}}{\sqrt{2}} + \frac{\sigma C_{d_0}}{8}
\]

The two terms are induced and profile power — the split that organises all rotor performance.

**Forward flight.** Advance ratio \(\mu = V\cos\alpha/(\Omega R)\). At blade azimuth \(\psi\), the local velocity is

\[
U_T = \Omega r + V\sin\psi
\]

so the retreating side (\(\psi = 270°\)) has a **reverse flow region** of radius \(\mu R\) where the blade section sees flow from the trailing edge. Blades flap to equalise lift between the two sides; flapping is what makes forward flight possible at all.

**Power curve:**

\[
P = \underbrace{\kappa T v_i}_{\text{induced}} + \underbrace{\frac{\rho A (\Omega R)^3 \sigma C_{d_0}}{8}(1+4.6\mu^2)}_{\text{profile}} + \underbrace{\tfrac{1}{2}\rho V^3 f}_{\text{parasite}}
\]

Induced power falls with speed, parasite rises as \(V^3\). Minimum power — best endurance — sits at moderate speed; best range is at the tangent from the origin, faster still.

### Dynamic stall

What limits the retreating side is not the static stall angle. A blade in forward flight pitches up rapidly as it retreats, and an airfoil pitching through stall does not behave like the same airfoil held there:

- Lift **overshoots** static \(C_{L,\max}\), sometimes by a large margin, because separation lags the motion.
- A **leading-edge vortex** forms, convects back over the chord, and while it does the section is still lifting.
- As it passes the trailing edge the centre of pressure moves sharply aft, producing a large **nose-down pitching moment** — the torsional load that sizes pitch links and control loads.
- Reattachment on the downstroke lags again, so the cycle encloses a **hysteresis loop**, and the net work done on the blade in torsion can be negative: **stall flutter**.

The practical consequences are that the useful thrust limit of a rotor is set by moment and vibration, not by lift; that the limit depends on the *rate* of pitching and so on advance ratio; and that semi-empirical models (Leishman–Beddoes and its relatives) rather than static airfoil tables are needed to predict it.

### Autorotation

**Autorotation.** With power off, the rotor is driven by upward flow through the disk. An autorotative region near mid-span drives the blade, balancing the drag of the inboard and outboard regions. Stored rotor kinetic energy \(\tfrac{1}{2}I\Omega^2\) is the resource available for the flare, and the **autorotation index** — that energy normalised by weight and disk loading — is how configurations are compared on it.

The **height–velocity diagram** maps where an engine failure is survivable. Two regions are not: low altitude with low airspeed, where there is neither height to trade for rotor speed nor speed to trade for height; and high altitude at very low speed, where the descent establishes before the flare can be set up. The avoid regions are a direct consequence of how much energy the rotor stores, which is why a heavy rotor with high inertia is a safety feature.

### Configurations

| Layout | Anti-torque | The trade |
|---|---|---|
| Single main + tail rotor | Tail rotor | Simple, but 3–5% of power thrown away and a vulnerable tail |
| Coaxial | Rotors cancel | Compact, no tail rotor loss; hub drag and interference |
| Tandem | Rotors cancel | Large CG range, good for cargo; rear rotor in front rotor's wake |
| Synchropter | Intermeshing rotors cancel | No tail rotor, no overlap loss; complex transmission |
| Tilt-rotor | Rotors cancel in cruise | Aeroplane cruise speed; heavy, large download in hover |
| Compound | Tail rotor or jet | Breaks the speed limit with a wing and auxiliary thrust; weight and complexity |
| Gyroplane | None needed — rotor is unpowered | Autorotates by design, cannot hover |

## Mental model

A hovering rotor is an air pump, and the momentum theory result says that pumping a large mass of air slowly is cheaper than a small mass quickly — the same argument as bypass ratio in [propulsion](propulsion.md). Disk loading *is* the rotorcraft equivalent of bypass ratio.

In forward flight, picture the rotor as a wing whose two halves see wildly different airspeeds and whose blades must therefore change incidence once per revolution. Every rotorcraft complication — flapping hinges, lead-lag, cyclic control, 1/rev vibration — exists to manage that asymmetry.

The three blade motions are worth separating because they are often confused. **Flapping** is out-of-plane and it is what equalises lift between the advancing and retreating sides. **Lead–lag** is in-plane, driven by the Coriolis effect as the flapping blade's radius of gyration changes, and it is what ground resonance couples into. **Feathering** is pitch change about the blade axis, commanded through the swashplate — collective for all blades equally, cyclic once per revolution. Three different hinges for three different jobs, and the order in which they are stacked on the hub changes the aircraft's response.

Because of this, "the rotor" has three distinct axes that only coincide in the hover: the **shaft axis**, the **tip-path axis** normal to the plane the blade tips sweep, and the **control axis** normal to the swashplate. Cyclic control works by tilting the tip-path plane, and the thrust vector follows it; the fuselage comes along afterwards. That is why a helicopter responds to cyclic in two stages, and why rotor and fuselage attitudes are not the same thing.

## Numerics / practice

- **Use a tip-loss factor** (\(B \approx 0.97\), Prandtl correction) in BEMT; without it thrust is overpredicted by several percent.
- **Non-uniform inflow matters.** Uniform inflow is a starting point; real rotors need at least a linear inflow model in forward flight, and a free-wake model for descent or close formation.
- **Induced power factor** \(\kappa \approx 1.15\) accounts for non-uniform inflow, tip loss and swirl. Ideal momentum theory is optimistic without it.
- Compressibility on the advancing tip: keep \(M_{\text{tip,adv}} = (\Omega R + V)/a\) below about 0.9.
- **Size the rotor against the tip speed constraint first.** \(\Omega R\) is squeezed from above by advancing-tip Mach and from below by retreating-blade stall and by the rotor energy needed for autorotation. Almost every other main rotor parameter is chosen inside that window.
- **Add download and tail rotor power before comparing with flight test.** Ideal momentum power is typically 60–70% of what the aircraft actually needs in the hover, and the gap is made of identifiable pieces rather than a fudge factor.
- **Use a dynamic stall model, not static tables**, anywhere near the thrust limit; static data will miss both the lift overshoot and the pitching moment that actually sizes the controls.

??? warning "Failure modes"
    **Momentum theory in descent.** The theory assumes a well-defined streamtube with flow in one direction. In moderate descent the rotor sits in its own wake, the streamtube concept collapses, and momentum theory gives complex or nonsensical inflow. Physically this is the **vortex ring state**: high descent rate, severe vibration, loss of thrust, and worse with more collective. A real and fatal hazard, not merely a modelling gap. The recovery is lateral or forward speed, not power.

    **Uniform inflow in forward flight.** Real inflow is strongly fore-aft asymmetric. Uniform inflow misses the resulting 1/rev flapping and blade loads, and predicts vibration levels far below reality.

    **Reverse flow region ignored.** At \(\mu = 0.4\), the reverse-flow circle covers 40% of the retreating blade radius. Blade-element codes that assume attached forward flow over the whole disk get retreating-side loads badly wrong.

    **Rotor thrust equated with aircraft weight.** The rotor also has to lift its own download on the fuselage, and on a tilt-rotor or compound with a wing in the wake that penalty is large. Hover performance computed from \(T = W\) is optimistic before anything else has gone wrong.

    **Ground effect assumed, or assumed away.** It is worth about a third more thrust at half a radius off the ground and essentially nothing by two radii. Quoting an in-ground-effect hover ceiling as if it were out-of-ground-effect is a standard way to oversell a design; measuring a rotor closer than \(2R\) to the floor is the test-rig version of the same error.

    **Tail rotor treated as an accessory.** It is a rotor, operating in the main rotor's wake and in sideways flow, with its own stall and its own vortex ring state. It takes real power, it sizes the tail boom, and loss of its effectiveness is a recognised handling hazard rather than a theoretical one.

    **Static airfoil data used at the retreating-blade limit.** Dynamic stall overshoots static \(C_{L,\max}\) and then produces a nose-down pitching moment that static tables cannot predict at all. Designs checked against static stall are checked against the wrong boundary — the real limit is torsional load and vibration.

    **Blade phase lag explained as gyroscopic precession.** The 90° lag between cyclic input and maximum flap response is a resonance: the flapping blade is a system whose natural frequency is almost exactly 1/rev, forced at 1/rev, and a lightly damped oscillator driven at resonance responds 90° out of phase. Gyroscopic precession is a different mechanism that happens to give the same number for the articulated case, and the resemblance breaks down as soon as hinge offset or stiffness moves the flap frequency away from 1/rev.

    **Hover figure of merit quoted for a forward-flight design.** FM is a hover metric only. Comparing rotors on FM tells you nothing about cruise efficiency.

    **Tip loss omitted.** Overpredicts thrust by 3–6% — enough to make a marginal design look adequate.

    **Ground resonance treated as an aerodynamic problem.** It is a mechanical instability coupling blade lead-lag with the airframe on its landing gear, and it can destroy an aircraft in seconds on the ground. It depends on damper condition, not on airflow.

    <!-- Add your own here. -->

## Worked example

### Why disk loading dominates hover efficiency

```python
import numpy as np

rho, T = 1.225, 50_000.0                # 5-tonne aircraft
for name, R in (("helicopter", 8.0), ("tiltrotor", 4.0), ("lift fan", 1.5)):
    A  = np.pi * R**2
    DL = T / A
    vi = np.sqrt(T / (2 * rho * A))
    P  = T * vi / 1e3
    print(f"{name:12s} R={R:4.1f} m  disk loading={DL:7.0f} N/m^2  "
          f"vi={vi:5.1f} m/s  ideal power={P:6.0f} kW")
```

```
helicopter   R= 8.0 m  disk loading=    249 N/m^2  vi= 10.1 m/s  ideal power=   504 kW
tiltrotor    R= 4.0 m  disk loading=    995 N/m^2  vi= 20.1 m/s  ideal power=  1007 kW
lift fan     R= 1.5 m  disk loading=   7074 N/m^2  vi= 53.7 m/s  ideal power=  2687 kW
```

The same aircraft weight needs five times the hover power on a small-diameter lift fan. Halving rotor radius doubles ideal power — the \(1/\sqrt{A}\) scaling, and the reason VTOL configurations live or die on disk loading.

### Where the hover power actually goes

Ideal momentum power is a lower bound that no aircraft meets. Assembling the pieces for a
UH-60-class machine shows how much of the gap is identifiable:

```python
import numpy as np

# A UH-60-class machine, the aircraft Leishman uses as a running example.
W     = 16_000 * 4.4482        # gross weight, N
R, VT = 8.18, 221.0            # rotor radius m, tip speed m/s
sigma, cd0 = 0.082, 0.008      # solidity, mean blade profile drag coefficient
kappa, fvA = 1.15, 0.04        # induced power factor, download area / disk area
A = np.pi * R**2

for label, rho in (("sea level", 1.225), ("5,200 ft", 1.048)):
    T  = W / (1 - fvA)                 # rotor lifts the weight PLUS its own download
    vh = np.sqrt(T / (2 * rho * A))
    P_ideal = T * vh
    P_i     = kappa * P_ideal
    P_0     = rho * A * VT**3 * sigma * cd0 / 8
    P_mr    = P_i + P_0
    P_tr    = 0.05 * P_mr              # tail rotor, Leishman's first-estimate fraction

    print(f"{label}  (rho = {rho} kg/m^3,  gross weight {W/1e3:.1f} kN,"
          f"  download = {100*fvA/(1-fvA):.1f}% extra thrust)")
    for name, P in (("ideal momentum power", P_ideal),
                    ("+ non-uniform inflow and tip loss", P_i),
                    ("+ blade profile drag", P_mr),
                    ("+ tail rotor", P_mr + P_tr)):
        print(f"    {name:<36}{P/1e3:7.0f} kW  {P/745.7:6.0f} hp")
    print(f"    {'figure of merit (rotor alone)':<36}{P_ideal/P_mr:7.2f}\n")
```

```
sea level  (rho = 1.225 kg/m^3,  gross weight 71.2 kN,  download = 4.2% extra thrust)
    ideal momentum power                    889 kW    1193 hp
    + non-uniform inflow and tip loss      1023 kW    1372 hp
    + blade profile drag                   1251 kW    1677 hp
    + tail rotor                           1313 kW    1761 hp
    figure of merit (rotor alone)          0.71

5,200 ft  (rho = 1.048 kg/m^3,  gross weight 71.2 kN,  download = 4.2% extra thrust)
    ideal momentum power                    962 kW    1290 hp
    + non-uniform inflow and tip loss      1106 kW    1483 hp
    + blade profile drag                   1301 kW    1745 hp
    + tail rotor                           1366 kW    1832 hp
    figure of merit (rotor alone)          0.74
```

Two checks make this more than an arithmetic exercise. The figure of merit falls out at
0.71–0.74, inside the 0.7–0.8 band quoted above rather than assumed to be there — and it
*rises* with altitude, because induced power scales as \(1/\sqrt{\rho}\) while profile
power scales as \(\rho\). More importantly, the 5,200 ft total of 1,832 hp lands within
about 2% of the roughly 1,800 hp that Leishman reports for this aircraft at this weight
and altitude, which is reassurance that the budget has the right pieces in it.

The shape of the result is the lesson: the ideal disk calculation accounts for only about
two thirds of installed hover power. The missing third is not a fudge factor — it is
non-uniform inflow and tip loss, blade profile drag, fuselage download and the tail
rotor, each of which can be designed against separately.

### Where momentum theory stops working

The page claims above that momentum theory fails in descent. It is worth seeing exactly
how it fails, because the mode of failure *is* the physics:

```python
import numpy as np

# Axial-flight momentum theory, normalised by the hover induced velocity v_h.
# Climb branch is valid for Vc/vh >= 0, windmill-brake branch for Vc/vh <= -2.
# In between, the descent square root sqrt((Vc/2vh)^2 - 1) has a negative argument.
kappa = 1.15                                    # measured hover induced power factor
KQ = (-1.125, -1.372, -1.718, -0.655)           # quartic fit to flight test, -2 <= x <= 0

def vi(x):
    if x >= 0:    return -x/2 + np.sqrt((x/2)**2 + 1), "normal working"
    if x <= -2:   return -x/2 - np.sqrt((x/2)**2 - 1), "windmill brake"
    fit = kappa + sum(k * x**(i+1) for i, k in enumerate(KQ))
    return fit, ("vortex ring" if x > -1.5 else "turbulent wake")

print(f"{'Vc/vh':>7}{'(Vc/2vh)^2-1':>14}{'vi/vh':>8}{'P/Ph':>8}   state")
for x in (2.0, 1.0, 0.0, -0.5, -1.0, -1.5, -1.8, -2.0, -3.0, -4.0):
    v, state = vi(x)
    disc = (x/2)**2 - 1
    flag = "" if x >= 0 or disc >= 0 else "   <- theory invalid, empirical fit"
    d = "   n/a (climb)" if x > 0 else f"{disc:14.2f}"
    print(f"{x:7.1f}{d}{v:8.3f}{x + v:8.3f}   {state}{flag}")

xs = np.arange(-2.0, 0.0, 1e-5)
fit = kappa + sum(k * xs**(i+1) for i, k in enumerate(KQ))
x0 = xs[np.argmin(np.abs(xs + fit))]
print(f"\nideal autorotation, P/Ph = 0, at Vc/vh = {x0:.2f}")
print(f"  momentum theory there: (Vc/2vh)^2 - 1 = {(x0/2)**2 - 1:+.3f}  ->  vi/vh imaginary")
```

```
  Vc/vh  (Vc/2vh)^2-1   vi/vh    P/Ph   state
    2.0   n/a (climb)   0.414   2.414   normal working
    1.0   n/a (climb)   0.618   1.618   normal working
    0.0         -1.00   1.000   1.000   normal working
   -0.5         -0.94   1.543   1.043   vortex ring   <- theory invalid, empirical fit
   -1.0         -0.75   1.966   0.966   vortex ring   <- theory invalid, empirical fit
   -1.5         -0.44   2.233   0.733   turbulent wake   <- theory invalid, empirical fit
   -1.8         -0.19   1.873   0.073   turbulent wake   <- theory invalid, empirical fit
   -2.0          0.00   1.000  -1.000   windmill brake
   -3.0          1.25   0.382  -2.618   windmill brake
   -4.0          3.00   0.268  -3.732   windmill brake

ideal autorotation, P/Ph = 0, at Vc/vh = -1.82
  momentum theory there: (Vc/2vh)^2 - 1 = -0.171  ->  vi/vh imaginary
```

Between \(V_c/v_h = 0\) and \(-2\) the descent-branch discriminant is negative, so the
induced velocity momentum theory returns is **imaginary**. This is not a numerical
difficulty to be worked around: the theory assumes a well-defined streamtube with flow in
one direction, and in that band the flow goes both ways through the disk, so no control
volume can be drawn. The empirical quartic is a curve fit to flight test, not a
derivation.

That invalid band is precisely where the **vortex ring state** lives, and the numbers show
why it is dangerous. At \(V_c/v_h = -0.5\) the rotor needs *more* power than it does in
the hover — the pilot's instinct to raise collective in a high descent rate makes the
condition worse, not better. Only past \(V_c/v_h \approx -1.8\), where the curve crosses
\(P/P_h = 0\), does the rotor start extracting energy from the air: the point of ideal
autorotation, and the far side of a region the theory cannot describe.

## Connections

- [Aerodynamics](aerodynamics.md) — blade section behaviour.
- [Aeroacoustics](aeroacoustics.md) — BVI and why descent is the noisiest condition.
- [Propulsion](propulsion.md) — the same mass-flow argument as bypass ratio.
- [Structures](structures.md) — blade dynamics, ground resonance.
- [Wind energy](wind-energy.md) — BEM again, with the flow going the other way; the windmill brake state is where a helicopter meets a turbine.
- [Propellers](propellers.md) — the same blade-element machinery loaded along its own axis.

## Sources

- Leishman, *Principles of Helicopter Aerodynamics* — momentum theory through the four working states, BEMT, dynamic stall, rotor wakes, and the aerodynamic design chapter.
- Watkinson, *The Art of the Helicopter* — rotor heads, hinges and axes, anti-torque, resonance, and the configuration taxonomy.
- Johnson, *Rotorcraft Aeromechanics*.
- Archive: `Others/2015RotaryWing`, `Others/LN_Shankar` — rotorcraft aerodynamics.
