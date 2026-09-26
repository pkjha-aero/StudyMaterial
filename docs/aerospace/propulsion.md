---
title: Propulsion
status: solid
tags: [pillar-1, aerospace, brayton, turbofan, rockets]
updated: 2026-09-26
---

# Propulsion

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Thrust is momentum flux out minus in, plus a pressure term that only matters when the nozzle is not perfectly expanded.
    - Overall efficiency factorises: **thermal × propulsive**. Raising one usually costs the other, and the bypass ratio is exactly that trade.
    - **Propulsive efficiency rewards moving a lot of air slowly** — which is why high-bypass turbofans exist and why propellers beat jets at low speed.
    - The Brayton cycle sets the ceiling; component efficiencies, pressure losses and cooling flows set what you actually get.
    - **Specific impulse in seconds versus m/s** is the most common unit error in rocket work: they differ by \(g_0\).

## Key results

**Thrust:**

<div class="result" markdown>

\[
F = \dot{m}_e V_e - \dot{m}_0 V_0 + (p_e - p_\infty)A_e
\]

</div>

**Efficiencies:**

\[
\eta_{\text{th}} = \frac{\tfrac{1}{2}(\dot m_e V_e^2 - \dot m_0 V_0^2)}{\dot m_f Q_R},
\qquad
\eta_{\text{prop}} = \frac{F V_0}{\tfrac{1}{2}(\dot m_e V_e^2 - \dot m_0 V_0^2)}
\approx \frac{2}{1 + V_e/V_0},
\qquad
\eta_{\text{overall}} = \eta_{\text{th}}\,\eta_{\text{prop}}
\]

The propulsive efficiency form is the key design insight: \(\eta_{\text{prop}} \to 1\) as \(V_e \to V_0\), but thrust \(\to 0\). Useful thrust at high efficiency therefore requires large \(\dot m\) with small \(\Delta V\) — high bypass ratio.

**Ideal Brayton cycle**, pressure ratio \(r_p\):

\[
\eta_{\text{th}} = 1 - r_p^{-(\gamma-1)/\gamma}
\]

Real engines depart from this through compressor and turbine polytropic efficiencies, combustor pressure loss (3–6%), turbine cooling bleed, and nozzle losses.

**Bypass ratio** \(\mathrm{BPR} = \dot m_{\text{cold}}/\dot m_{\text{hot}}\):

| Engine class | BPR | Best at |
|---|---|---|
| Turbojet | 0 | \(M > 2\) |
| Low-bypass turbofan | 0.3–1 | military, supersonic |
| High-bypass turbofan | 5–12 | transonic cruise |
| Turboprop / open rotor | 25–100+ (effective) | \(M < 0.6\) |

**Rocket equation and specific impulse:**

\[
\Delta V = I_{sp}\,g_0 \ln\frac{m_0}{m_f},
\qquad
I_{sp}[\mathrm{s}] = \frac{c^*C_F}{g_0} = \frac{V_e^{\text{eff}}}{g_0}
\]

\(I_{sp}\) in seconds multiplied by \(g_0 = 9.80665\) gives effective exhaust velocity in m/s. Both conventions are in use; the factor of ~9.81 between them has destroyed more than one calculation.

**TSFC** \(= \dot m_f / F\). Lower is better; a modern high-bypass turbofan runs around 0.5–0.6 lb/(lbf·h) in cruise.

## Mental model

An air-breathing engine is a machine for adding energy to a stream of air and then converting that energy into momentum. Two separate conversions, each with its own efficiency, multiplied together.

The thermal side wants high pressure ratio and high turbine entry temperature — hotter and tighter is better, bounded by materials. The propulsive side wants the exhaust barely faster than the aircraft — minimum kinetic energy wasted in the wake. The bypass fan exists to satisfy the second without compromising the first: the core runs hot and efficient, and its power is used to accelerate a much larger, slower stream.

## Numerics / practice

- **Use consistent station numbering** (0 freestream, 2 fan face, 3 compressor exit, 4 turbine inlet, 9 nozzle exit) and label every state. Most cycle-analysis errors are bookkeeping errors.
- **Separate installed from uninstalled thrust.** Inlet spillage, bleed and nozzle boat-tail drag can cost several percent.
- **Check the nozzle pressure ratio** before assuming perfect expansion. Under-expanded and over-expanded nozzles lose thrust and change the pressure term.
- **Cite \(I_{sp}\) with its units** every single time.

??? warning "Failure modes"
    **Specific impulse unit confusion.** \(I_{sp}=450\) means seconds (a good hydrolox upper stage); \(I_{sp}=4400\) means m/s — the same engine. Mixing them into the rocket equation gives answers wrong by a factor of 9.81, which is large enough to look like a different mission and small enough to be plausible.

    **Ideal cycle used as a prediction.** The ideal Brayton efficiency is an upper bound. Real overall efficiency is typically 30–40% of the fuel's energy reaching the airframe, not the 60%+ the ideal cycle suggests.

    **Propulsive efficiency optimised in isolation.** Pushing \(V_e \to V_0\) maximises \(\eta_{\text{prop}}\) and drives thrust to zero. The real objective is minimum fuel for the required thrust, not maximum efficiency.

    **Ignoring turbine cooling flow.** Bleeding 15–25% of core flow for cooling is normal and it does not do work in the turbine. Cycle decks that omit it overpredict performance substantially.

    **Uninstalled thrust quoted as installed.** Test-stand numbers do not include inlet and nozzle installation losses. The gap is typically 2–8% and is the difference between meeting and missing a range requirement.

    **Ram drag forgotten.** The \(\dot m_0 V_0\) term grows with flight speed; net thrust falls as the aircraft accelerates even at constant fuel flow. Omitting it makes high-speed performance look impossible-good.

    <!-- Add your own here. -->

## Worked example

Why the bypass fan exists, in one calculation:

```python
V0 = 250.0                      # flight speed, m/s
thrust = 100_000.0              # N required

for name, mdot in (("turbojet-ish", 100.0), ("high-bypass", 600.0)):
    Ve = V0 + thrust / mdot     # from F = mdot*(Ve - V0)
    eta = 2.0 / (1.0 + Ve / V0)
    waste = 0.5 * mdot * (Ve - V0)**2
    print(f"{name:14s} mdot={mdot:5.0f} kg/s  Ve={Ve:6.1f} m/s  "
          f"eta_prop={eta:.3f}  wake loss={waste/1e6:.2f} MW")
```

```
turbojet-ish   mdot=  100 kg/s  Ve=1250.0 m/s  eta_prop=0.333  wake loss=50.00 MW
high-bypass    mdot=  600 kg/s  Ve= 416.7 m/s  eta_prop=0.750  wake loss=8.33 MW
```

Same thrust, six times the mass flow, and the energy thrown away in the wake drops by a factor of six. That is the entire argument for high bypass ratio.

## Connections

- [Flight mechanics](flight-mechanics.md) — thrust and TSFC in the range equation.
- [Fluids › Compressible flow](../fluids/compressible.md) — nozzles, inlets, shocks.
- [Space environment](space-environment.md) — rockets and delta-v budgets.

## Sources

- Mattingly, *Elements of Gas Turbine Propulsion*.
- Sutton & Biblarz, *Rocket Propulsion Elements*.
- Archive: `Others/Turbojet Engine`; see the [course archive](../resources/course-archive.md).
