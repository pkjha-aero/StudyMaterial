---
title: Flight testing
status: working
tags: [pillar-10, aerospace, uncertainty, validation]
updated: 2026-10-24
---

# Flight testing

<span class="status status-working">working</span>
<span class="pillar">pillar 10 &middot; V&amp;V, research craft and communication</span>

!!! abstract "In one minute"
    - Flight test is a **data reduction** problem, not a data collection problem. The number the instrument shows is never the answer; it becomes one only after correction to a standard weight and a standard atmosphere.
    - **Predict everything you measure.** A prediction made before the flight turns a disagreement into information; without one, a surprise is indistinguishable from noise.
    - The **airspeed chain** — indicated to calibrated to equivalent to true — is the first thing to establish, because every other test depends on knowing the speed.
    - Test techniques are built to **cancel what cannot be controlled**: reciprocal headings cancel wind, sawtooth climbs isolate a single altitude, tower flybys bypass the static source entirely.
    - The atmosphere is never standard, the aircraft is lighter at the end of the sortie than the start, and both of those are corrections you apply rather than conditions you arrange.

## Key results

### The airspeed chain

Four speeds, and the corrections between them, in the order they are applied:

<div class="result" markdown>

\[
\text{IAS} \xrightarrow{\ \text{instrument error}\ } \text{CAS}
\xrightarrow{\ \text{compressibility}\ } \text{EAS}
\xrightarrow{\ \div\sqrt{\sigma}\ } \text{TAS}
\]

</div>

- **IAS** is what the dial says. The airspeed indicator is a differential pressure gauge whose face is graduated using *sea-level* density, so it reads true only at sea level on a standard day.
- **CAS** corrects for **instrument error** and, more importantly, **position error** — the static port cannot sense undisturbed static pressure at every speed and configuration. FAA Part 23 permits position error up to **3% of CAS or 5 knots, whichever is greater**, above 1.3 times the stalling speed, so it is a certified-in tolerance rather than a defect.
- **EAS** subtracts compressibility, negligible below about 200 kt and not below about 10,000 ft.
- **TAS** follows from the density ratio: \(V_{TAS} = V_{EAS}/\sqrt{\sigma}\).

Methods for finding position error, roughly in order of cost and accuracy:

| Method | How it works | Weakness |
|---|---|---|
| **Reciprocal headings** | Time a measured distance out and back | Wind cancels only to first order — see the worked example |
| **GPS triangle** | Three headings give TAS and the full wind vector | Needs steady wind over the three legs |
| **Tower flyby** | Fly past a tower at known height; ground observer reads true static | Low altitude only |
| **Trailing cone or bomb** | Tow a static source clear of the aircraft's pressure field | Equipment, drag, and its own calibration |
| **Pacer aircraft** | Formate on an already-calibrated aircraft | Needs the pacer |

### Pressure altitude and density

Set the altimeter to 29.92 inHg and it reads **pressure altitude** — the altitude at which the measured pressure would be standard. That is a *pressure* measurement dressed as a height, and the distinction matters constantly.

With pressure from the altimeter and temperature from the OAT gauge, density follows from the equation of state:

\[
\rho = \frac{p}{RT}, \qquad \sigma = \rho/\rho_{SL}
\]

### Reduction to standard conditions

This is the core of the subject. Two corrections recur in almost every performance test.

**Non-standard atmosphere.** The altimeter senses pressure, but the aircraft climbs through geometric height. For the same pressure change, warmer-than-standard air is less dense and spread over more height, so the true climb rate exceeds the indicated one:

\[
(R/C)_{\text{actual}} = (R/C)_{\text{measured}}\,\frac{T_{\text{actual}}}{T_{\text{standard}}}
\]

**Non-standard weight.** Test weight is whatever the fuel state gives; the chart is quoted at gross weight. Differentiating the climb equation \(R/C = (T-D)V/W\):

\[
\frac{\partial (R/C)}{\partial W} = -\frac{R/C}{W} - \frac{V}{W}\,\frac{2C_L}{\pi \mathrm{AR}\, e}
\]

Both terms are negative — heavier climbs worse — and the second, the induced-drag term, is not negligible. The worked example below runs the whole chain.

### The standard test techniques

| Test | Technique | What the technique buys |
|---|---|---|
| Airspeed calibration | Reciprocal legs, GPS triangle, tower flyby | Removes the wind |
| Climb performance | **Sawtooth climbs** — short WOT climbs at fixed IAS through one test altitude, repeated across speeds | Isolates a single altitude; gives \(V_y\) and \(V_x\) per altitude |
| Level performance | Stabilised points, reduced to \(P_{IW}\)–\(V_{IW}\) form | Collapses weight and altitude onto one curve |
| Takeoff and landing | Timed and measured ground roll, obstacle distance | Direct comparison with certification distances |
| Stall | Deceleration at about 1 kt/s | Standardises the dynamic lag in \(C_{L,\max}\) |
| Static stability | Elevator position and stick force versus speed, repeated at several CG positions | Extrapolates to the **neutral point** |
| Dynamic stability | Doublet or pulse excitation, then log decrement | Frequency and damping of each mode |

**Sawtooth climbs** deserve the name: trim level below the test altitude, open the throttle, hold a fixed indicated airspeed, record altitude over a timed interval through the test altitude, descend, and repeat at a new speed. Plotting climb rate against speed gives the best-climb speed at that altitude; repeating at several altitudes gives the ceiling.

**Neutral point from flight test** is the classic example of extracting a derivative the aircraft will not show you directly. The elevator deflection required to trim varies with speed, and the slope \(\mathrm{d}\delta_e/\mathrm{d}V\) flattens as the CG moves aft. Fly the speed sweep at three or four CG positions, plot the slope against CG, and extrapolate to zero slope: that intercept is the **stick-fixed neutral point**. The same construction on stick *force* gradient gives the stick-free neutral point. You never fly at the neutral point — you locate it by extrapolation, which is exactly why the CG range flown has to be wide enough to make the extrapolation honest.

## Mental model

Flight test is a subtraction problem. You cannot order a standard atmosphere, you cannot switch off the wind, and the aircraft is burning fuel while you work. Every technique in the subject exists to subtract one of those out — by symmetry (fly both directions), by design (hold one variable fixed and sweep another), or by arithmetic afterwards (reduce to standard day and standard weight).

The second idea is the one that makes a flight-test course different from a lab course: **predict first**. If you compute the expected climb rate before the sortie and measure 10% less, you have learned something about the aeroplane, or about your drag estimate, or about your data reduction — and you can go find out which. If you measure 10% less than nothing in particular, you have a number. Theory and experiment disagreeing is the normal and useful outcome; the disagreement is only informative if the prediction existed first.

## Numerics / practice

- **Record everything the reduction will need, at the instant of the data point**: pressure altitude, OAT, indicated airspeed, fuel state, power setting, configuration. A data point missing its OAT cannot be reduced and is simply lost.
- **Reduce before plotting.** Raw indicated numbers plotted against each other look convincing and mean nothing; the scatter you see is mostly uncorrected atmosphere.
- **Track weight through the sortie.** Fuel burn over an hour is a significant fraction of a light aircraft's useful load, so the first and last points of a series are not at the same weight.
- **Stabilise, then record.** Instrument and aircraft lag mean a point taken during a transient is a point taken at an unknown condition — the usual reason a sawtooth climb needs a settling leg before timing starts.
- **Repeat points deliberately.** Repeats separate random scatter from systematic bias; without them you cannot tell which kind of error you have. The [uncertainty machinery](experimental-methods.md) applies here unchanged.
- **Fly the speed sweep in both directions** where hysteresis is plausible, particularly near the stall and in trim tests.

??? warning "Failure modes"
    **Indicated airspeed used as true airspeed.** At 5,000 ft on a warm day the density ratio is around 0.82, so TAS exceeds IAS by about 10%. Every dynamic-pressure-dependent quantity computed from the wrong speed is wrong, and the error grows with altitude.

    **Data not reduced to standard weight and atmosphere.** The raw reading is not a performance figure, it is a reading. Comparing it with a handbook chart — which is quoted at gross weight on a standard day — compares two different things and the disagreement gets blamed on the aeroplane.

    **Pressure altitude confused with geometric altitude.** The altimeter is a pressure gauge. On a hot day the aircraft gains more real height per unit of indicated altitude than the standard atmosphere assumes, and a climb rate read straight off the altimeter is understated by the temperature ratio.

    **Two-leg wind cancellation assumed exact.** Timing out-and-back legs returns the *harmonic* mean of the two ground speeds, which is below the true airspeed by \(w^2/V\). It is a second-order error, which is why it goes unnoticed, and it exceeds the Part 23 position-error tolerance in a wind that a test crew would happily fly in.

    **Position error treated as a single curve.** It depends on configuration as well as speed. Flaps and gear change the flow field at the static port, so a clean-configuration calibration applied to approach data is a systematic error exactly where approach speeds matter most.

    **Neutral point extrapolated from too narrow a CG range.** The construction is an extrapolation to zero slope. Two closely spaced CG positions give a slope with large uncertainty and an intercept with much larger uncertainty, and the result will look precise because it is a single number.

    **Instrument lag ignored in dynamic manoeuvres.** Altimeters, vertical speed indicators and pneumatic airspeed systems all lag. In a stall approach or a sawtooth climb entry this biases the measured quantity in a consistent direction, so repeating the test does not help.

    **A single run treated as data.** Atmospheric variability between runs is often larger than the effect being measured. One sawtooth climb is an anecdote; the point is the trend across a sweep, fitted and reduced.

    **Weight change within a test series ignored.** A series flown from full tanks to reserve spans a weight range large enough to tilt a performance trend on its own, which can be mistaken for a genuine dependence on the variable being swept.

    <!-- Add your own here. -->

## Worked example

### How completely does flying both directions cancel the wind?

The standard first flight test is an airspeed calibration by reciprocal headings: fly a measured distance on a heading, turn 180°, fly it back, and take \(V = 2s/(t_1+t_2)\) on the argument that the wind adds to one leg what it subtracts from the other.

```python
import numpy as np

# Two-leg reciprocal-heading calibration: fly a measured distance out and back,
# time each leg, take TAS = 2s/(t1+t2).  How completely does the wind cancel?
def two_leg(V, w, s=10.0):
    return 2*s/(s/(V - w) + s/(V + w))        # w = along-course wind component

V = 100.0
print(f"two-leg timing method, true TAS = {V:.0f} kt")
print(f"{'wind kt':>8}{'recovered':>11}{'error kt':>10}{'error %':>9}{'-w^2/V':>9}")
for w in (0, 5, 10, 15, 20, 30):
    r = two_leg(V, w)
    print(f"{w:8.0f}{r:11.3f}{r-V:10.3f}{100*(r/V-1):9.2f}{-w**2/V:9.2f}")

w = 20.0
print(f"\nwhy: timing returns the HARMONIC mean of the two ground speeds, not the mean")
print(f"   arithmetic mean of (V-w, V+w) = {((V-w)+(V+w))/2:7.3f}   <- equals V exactly")
print(f"   harmonic mean, which is 2s/(t1+t2) = {2/(1/(V-w)+1/(V+w)):7.3f}")
print(f"   exact bias = -w^2/V = {-w**2/V:.3f} kt")
print(f"   FAA Part 23 allows 3% of CAS or 5 kt, whichever is greater;")
print(f"   at {V:.0f} kt that is 5 kt, which this method reaches at "
      f"w = {np.sqrt(5*V):.1f} kt of wind")

# Three legs give three equations for three unknowns (TAS, wx, wy) -- no assumption
# about the wind at all. Ground velocity = TAS vector + wind vector.
def ground_speeds(V, wx, wy, hdg):
    return np.array([np.hypot(V*np.cos(h) + wx, V*np.sin(h) + wy) for h in hdg])

hdg = np.radians([0.0, 120.0, 240.0])
V_true, wx, wy = 100.0, 16.383, 11.472          # 20 kt wind on a 35 deg bearing
gs = ground_speeds(V_true, wx, wy, hdg)

p = np.array([90.0, 0.0, 0.0])                  # deliberately poor starting guess
for _ in range(60):                             # Newton, numerical Jacobian
    f0 = ground_speeds(*p, hdg) - gs
    J = np.zeros((3, 3))
    for k in range(3):
        dp = np.zeros(3); dp[k] = 1e-6
        J[:, k] = (ground_speeds(*(p + dp), hdg) - gs - f0)/1e-6
    p = p - np.linalg.solve(J, f0)

print(f"\nthree-leg GPS solve, same {np.hypot(wx,wy):.0f} kt wind:")
print(f"   ground speeds observed : {np.round(gs,2)}")
print(f"   recovered TAS  = {p[0]:.6f} kt   (true {V_true:.0f}, error {p[0]-V_true:+.1e})")
print(f"   recovered wind = {np.hypot(p[1],p[2]):.6f} kt   "
      f"(true {np.hypot(wx,wy):.3f}, error {np.hypot(p[1],p[2])-np.hypot(wx,wy):+.1e})")
```

```
two-leg timing method, true TAS = 100 kt
 wind kt  recovered  error kt  error %   -w^2/V
       0    100.000     0.000     0.00     0.00
       5     99.750    -0.250    -0.25    -0.25
      10     99.000    -1.000    -1.00    -1.00
      15     97.750    -2.250    -2.25    -2.25
      20     96.000    -4.000    -4.00    -4.00
      30     91.000    -9.000    -9.00    -9.00

why: timing returns the HARMONIC mean of the two ground speeds, not the mean
   arithmetic mean of (V-w, V+w) = 100.000   <- equals V exactly
   harmonic mean, which is 2s/(t1+t2) =  96.000
   exact bias = -w^2/V = -4.000 kt
   FAA Part 23 allows 3% of CAS or 5 kt, whichever is greater;
   at 100 kt that is 5 kt, which this method reaches at w = 22.4 kt of wind

three-leg GPS solve, same 20 kt wind:
   ground speeds observed : [116.95 103.68  82.31]
   recovered TAS  = 100.000000 kt   (true 100, error +1.4e-14)
   recovered wind = 20.000237 kt   (true 20.000, error +3.6e-15)
```

The wind does not cancel. Timing two legs gives the **harmonic** mean of the two ground speeds, and the harmonic mean of \(V-w\) and \(V+w\) is \(V - w^2/V\), not \(V\). The arithmetic mean would cancel exactly — but you cannot measure ground speeds directly with a stopwatch, only times, and times weight the slow leg more heavily because you spend longer on it.

The bias is second order in \(w/V\), which is why the method survives: in 5 knots of wind at 100 knots it is a quarter of a knot, far below anything else in the test. But it grows as the square. At 20 knots of wind the method reports 96 knots for a true 100, and by 22.4 knots the bias alone has consumed the entire Part 23 position-error allowance that the test is trying to measure. A calibration flown on a breezy day will find a "position error" that is mostly the test technique.

The three-leg GPS solve at the bottom is the modern answer, and it is exact to machine precision because it assumes nothing: three headings give three equations in three unknowns — true airspeed and both wind components — so the wind is solved for rather than cancelled. The only assumption left is that the wind is steady across the three legs.

### Reducing a sawtooth climb to standard conditions

A climb measured in a real atmosphere at a real weight, reduced to something that can be compared with a handbook chart:

```python
import numpy as np

# Cessna 172R sawtooth climb through a 5000 ft test altitude.
S, AR, e  = 174.0, 7.48, 0.70            # ft^2, aspect ratio, span efficiency
W_test    = 2300.0                       # lb, actual weight at the test point
W_std     = 2450.0                       # lb, standard gross weight for the POH chart
hp, OAT_F = 5090.0, 65.0                 # pressure altitude ft, outside air temp degF
KIAS      = 80.0
RC_meas   = 580.0                        # fpm, from the CHANGE IN PRESSURE ALTITUDE

RHO_SL, KT = 0.0023769, 1.68781          # slug/ft^3, ft/s per knot
T_act  = OAT_F + 459.67
T_std  = 518.67 - 0.00356616*hp                      # standard day at that altitude
p      = 2116.22*(1 - 6.87559e-6*hp)**5.25588
rho    = p/(1716.0*T_act)
sigma  = rho/RHO_SL

RC_atm = RC_meas*T_act/T_std             # altimeter measures PRESSURE, not height
V_tas  = KIAS/np.sqrt(sigma)
q      = 0.5*RHO_SL*(KIAS*KT)**2         # ASI is graduated on sea-level density
CL     = W_test/(q*S)

# d(R/C)/dW = -(R/C)/W - (V/W) * 2CL/(pi AR e)
dRC_dW = -(RC_atm/60)/W_test - (V_tas*KT/W_test)*(2*CL/(np.pi*AR*e))
RC_std = RC_atm + dRC_dW*(W_std - W_test)*60

print(f"standard temp at {hp:.0f} ft   {T_std:7.2f} R   ({T_std-459.67:5.1f} F)")
print(f"actual temp                 {T_act:7.2f} R   ({OAT_F:5.1f} F)")
print(f"pressure / density / sigma  {p:7.1f} psf  {rho:.5f} slug/ft3  {sigma:.4f}")
print(f"TAS from {KIAS:.0f} KIAS           {V_tas:7.2f} kt")
print(f"q, CL at test weight        {q:7.2f} psf  CL = {CL:.3f}")
print(f"d(R/C)/dW                   {dRC_dW:+.5f} fps/lb  "
      f"= {dRC_dW*60:+.3f} fpm/lb")
print()
print(f"  measured (pressure altitude) {RC_meas:7.1f} fpm")
print(f"  + non-standard atmosphere    {RC_atm:7.1f} fpm   ({RC_atm-RC_meas:+.1f})")
print(f"  + to standard gross weight   {RC_std:7.1f} fpm   ({RC_std-RC_atm:+.1f})")
print(f"\n  raw reading is {100*(RC_meas/RC_std-1):+.1f}% off the reportable number")
```

```
standard temp at 5090 ft    500.52 R   ( 40.8 F)
actual temp                  524.67 R   ( 65.0 F)
pressure / density / sigma   1754.9 psf  0.00195 slug/ft3  0.8200
TAS from 80 KIAS             88.34 kt
q, CL at test weight          21.67 psf  CL = 0.610
d(R/C)/dW                   -0.00921 fps/lb  = -0.553 fpm/lb

  measured (pressure altitude)   580.0 fpm
  + non-standard atmosphere      608.0 fpm   (+28.0)
  + to standard gross weight     525.1 fpm   (-82.9)

  raw reading is +10.5% off the reportable number
```

Three numbers describe this climb, and only the last one means anything.

**580 fpm** is what the altimeter showed. It is a rate of change of *pressure altitude*, and the day is 24°R warmer than standard, so the aircraft was gaining real height faster than the altimeter suggested.

**608 fpm** is the actual climb rate the aircraft achieved, in that atmosphere, at that weight. It is a true statement about that afternoon and about nothing else.

**525 fpm** is the reportable figure: what the aircraft would do at standard gross weight. The test was flown 150 lb light, and the climb equation is sensitive enough — about \(-0.55\) fpm per pound here — that the weight correction is three times the size of the atmosphere correction and points the other way.

That cancellation is the lesson. The raw reading is 10% *above* the reportable number, having first been 5% *below* the true climb rate. A reduction that stopped after either correction would give an answer that looked plausible and was wrong, and applying them in the wrong direction — a sign error anyone can make — moves the result by nearly 200 fpm on a 525 fpm climb.

## Connections

- [Experimental methods](experimental-methods.md) — bias versus precision, uncertainty propagation, and the tunnel side of the same discipline.
- [Flight mechanics](flight-mechanics.md) — the performance and stability relations these tests measure, and the neutral point the trim sweep locates.
- [Aerodynamics](aerodynamics.md) — the drag polar a climb test implicitly tests.
- [Propellers](propellers.md) — thrust and power available, which set the excess power a climb measures.
- [Aircraft design](aircraft-design.md) — flight test is where the sizing loop's predictions are finally checked.
- [Foundations › Verification and validation](../foundations/verification-validation.md) — prediction before measurement, as a general principle.

## Sources

- McCormick, *Introduction to Aeronautics and Flight Testing* — the structure of this page: the airspeed calibration flight test, sawtooth climbs, reduction to standard atmosphere and weight, and the predict-everything-you-measure discipline.
- Kimberlin, *Flight Testing of Fixed-Wing Aircraft* — the standard modern reference on test techniques and data reduction.
- Ward, Strganac & Niewoehner, *Introduction to Flight Test Engineering*.
- FAA Part 23 airworthiness standards, for the certification tolerances these tests are measured against.
- Archive: `Aerospace/AERSP420` — techniques of flight testing, with the airspeed, climb and stall experiments flown on a Cessna 172R; see the [course archive](../resources/course-archive.md).
