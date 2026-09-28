---
title: Thermodynamics
status: working
tags: [pillar-1, thermal, conservation, scaling]
updated: 2026-09-28
---

# Thermodynamics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - The first law is bookkeeping; the **second law is the one that constrains design**, because it says what you cannot have.
    - **Entropy generation is the currency of loss.** Every real component destroys availability, and exergy analysis tells you where.
    - Carnot efficiency is a ceiling set by two temperatures only. Beating it is impossible; approaching it is a materials problem.
    - Cycle analysis is mostly bookkeeping over state points — the judgement is in **which idealisations you keep**.
    - Statistical mechanics supplies the properties that classical thermodynamics assumes: \(c_p\), \(\gamma\), and the equation of state are outputs, not axioms.

## Key results

**The laws, in the form that gets used:**

<div class="result" markdown>

\[
dU = \delta Q - \delta W,
\qquad
dS \ge \frac{\delta Q}{T},
\qquad
\dot{S}_{\text{gen}} = \sum \dot{m}_e s_e - \sum \dot{m}_i s_i - \sum \frac{\dot{Q}_k}{T_k} \ge 0
\]

</div>

**Exergy** (availability) — the maximum useful work relative to a dead state at \(T_0\):

\[
\psi = (h - h_0) - T_0(s - s_0) + \tfrac{1}{2}V^2 + gz,
\qquad
\dot{X}_{\text{destroyed}} = T_0 \dot{S}_{\text{gen}}
\]

The Gouy–Stodola relation \(\dot X_{\text{dest}} = T_0\dot S_{\text{gen}}\) is the practical heart of second-law analysis: it converts entropy generation into lost work, in watts, component by component. An energy balance says a heat exchanger is 98% efficient; an exergy balance says where the useful work went.

**Cycle efficiencies:**

| Cycle | Ideal efficiency | Limited by |
|---|---|---|
| Carnot | \(1 - T_C/T_H\) | temperatures only |
| Brayton | \(1 - r_p^{-(\gamma-1)/\gamma}\) | pressure ratio, turbine inlet temperature |
| Otto | \(1 - r^{-(\gamma-1)}\) | compression ratio, knock |
| Diesel | \(1 - \frac{1}{r^{\gamma-1}}\frac{r_c^\gamma - 1}{\gamma(r_c-1)}\) | compression and cutoff ratio |
| Rankine | \(w_{net}/q_{in}\) | boiler pressure, condenser temperature |

**Property behaviour.** The ideal gas law fails where it matters: near saturation, at high pressure, and for dense or polar species. Compressibility \(Z = pv/RT\) departs from 1 with reduced pressure and temperature; cubic equations of state (Peng–Robinson, Soave–Redlich–Kwong) are the usual repair.

**Specific heats are not constant.** \(c_p(T)\) rises substantially with temperature — for air, about 1.005 kJ/kg·K at 300 K and 1.14 at 1200 K. Cycle calculations using cold-air-standard values overstate efficiency and understate turbine work.

**Statistical connection.** The partition function \(Z = \sum_i g_i e^{-\varepsilon_i/kT}\) gives everything:

\[
U = kT^2\frac{\partial \ln Z}{\partial T},
\qquad
S = k\ln \Omega,
\qquad
c_v = \frac{\partial U}{\partial T}
\]

Equipartition gives \(c_v = \tfrac{f}{2}R\) with \(f\) active degrees of freedom — 3 translational always, 2 rotational for a linear molecule above its rotational temperature, vibrational modes activating around 1000 K. That activation is exactly why \(c_p\) rises, and why \(\gamma\) falls from 1.4 toward 1.3 in hot combustion gases.

## Mental model

The first law tells you the books balance. The second tells you the books balance *while the world gets worse*, and by exactly how much. Design is the art of losing less.

That reframing makes exergy the natural tool. Energy is conserved, so an energy balance can never tell you which component to improve — everything "conserves". Exergy is destroyed, so an exergy balance ranks components by how much useful work each one costs you. It is the difference between knowing the total and knowing where to work.

## Numerics / practice

- **Use variable \(c_p\)** for anything above a few hundred kelvin. CoolProp or NASA polynomial fits; cold-air-standard is a hand calculation, not an analysis.
- **Do a second-law audit** on a cycle before optimising it. The component with the largest \(T_0\dot S_{\text{gen}}\) is where the design effort belongs.
- **Check \(Z\)** before assuming ideal gas. At reduced pressure above ~0.3 the error is percent-level and systematic.
- **Fix the dead state** \((T_0, p_0)\) explicitly and state it — exergy values are meaningless without it.

??? warning "Failure modes"
    **Cold-air-standard blamed for the wrong error.** It is widely assumed to overstate thermal efficiency. For the *ideal* Brayton cycle it barely does — compressor and turbine shift together, and at \(r_p=20\), \(T_3=1600\) K the efficiency moves by well under a point. What it actually changes is the state points: compressor exit about 1% low, turbine exit about 2% low, specific work about 1.6% low. Those feed material limits and sizing, not efficiency. The efficiency error appears once component isentropic efficiencies and real product composition enter — so the idealisation is worth dropping, but not for the reason usually given.

    **Energy efficiency read as quality.** A heat exchanger transferring 98% of the energy can destroy most of its exergy if the temperature difference is large. Energy accounting cannot see this by construction — only a second-law balance can.

    **Carnot applied between the wrong temperatures.** The reservoir temperatures are the ones the device actually exchanges heat with, not the flame temperature and ambient. Quoting Carnot on the adiabatic flame temperature produces a ceiling no engine could ever approach and makes real efficiencies look disgraceful.

    **Sign conventions mixed.** \(W\) positive out of the system (engineering) versus positive into it (physics) differ by a sign throughout. Most first-law errors are this, not algebra.

    **Ideal gas near saturation.** Steam near the dome, refrigerants, and CO₂ near critical are all far from ideal. Symptom: a cycle that closes energetically but predicts impossible state points.

    **Isentropic efficiency confused with polytropic.** For a multistage compressor these differ measurably, and polytropic (small-stage) efficiency is the one that is roughly constant across pressure ratio. Comparing machines on the wrong one misranks them.

    **Neglecting the dead state's pressure.** Exergy depends on \(p_0\) as well as \(T_0\). Omitting it silently changes flow-exergy values.

    <!-- Add your own here. -->

## Worked example

Four components, all "100% energy efficient", ranked by what they actually cost:

```python
T0, Q = 288.0, 100e3        # dead state, and 100 kW through each component

cases = [("combustor, 2200 K -> 1600 K",       2200.0, 1600.0),
         ("turbine cooling, 1600 K -> 900 K",  1600.0,  900.0),
         ("recuperator, 800 K -> 700 K",        800.0,  700.0),
         ("oil cooler, 400 K -> 350 K",         400.0,  350.0)]

print(f"{'component':34s}{'energy eff.':>13}{'S_gen (W/K)':>14}{'exergy destroyed':>19}")
for name, Th, Tc in cases:
    S_gen = Q * (1/Tc - 1/Th)          # heat Q crossing a finite temperature difference
    X_dest = T0 * S_gen                # Gouy-Stodola
    print(f"{name:34s}{'100%':>13}{S_gen:14.1f}{X_dest/1e3:16.1f} kW")
```

```
component                           energy eff.   S_gen (W/K)   exergy destroyed
combustor, 2200 K -> 1600 K                100%          17.0             4.9 kW
turbine cooling, 1600 K -> 900 K           100%          48.6            14.0 kW
recuperator, 800 K -> 700 K                100%          17.9             5.1 kW
oil cooler, 400 K -> 350 K                 100%          35.7            10.3 kW
```

Every row passes 100 kW and loses none of it — an energy balance cannot tell them apart.
An exergy balance says the turbine cooling flow costs 14 kW of work and the combustor drop
costs 4.9 kW, so that is where the design effort belongs.

Note the oil cooler: a mere 50 K drop destroys **twice** what the 600 K combustor drop
does. Entropy generation goes as \(1/T_c - 1/T_h\), and that difference is far larger at
low temperature. Small temperature differences at low temperature are expensive; large
ones at high temperature are comparatively cheap. That is not obvious from the
temperatures alone, which is the whole argument for doing the second-law audit rather than
eyeballing it.

## Connections

- [Heat transfer](heat-transfer.md) — where the energy actually goes.
- [Combustion](combustion.md) — the heat addition step, done properly.
- [Aerospace › Propulsion](../aerospace/propulsion.md) — Brayton in an engine.
- [Fluids › Governing equations](../fluids/governing-equations.md) — the energy equation.

## Sources

- Moran, Shapiro et al., *Fundamentals of Engineering Thermodynamics*.
- Bejan, *Advanced Engineering Thermodynamics* — exergy and entropy generation.
- Sears & Salinger, *Thermodynamics, Kinetic Theory, and Statistical Thermodynamics*.
- Archive: `Mechanical/ME300_2`, `Mechanical/ME535`, and `Others/Turns_Thermodynamics`; see the [course archive](../resources/course-archive.md).
