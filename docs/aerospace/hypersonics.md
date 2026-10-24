---
title: Hypersonic aerodynamics
status: working
tags: [pillar-1, aerospace, radiation, scaling]
updated: 2026-10-24
---

# Hypersonic aerodynamics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Hypersonic is **not a Mach number**. It is the regime where a specific set of physical effects becomes dominant; \(M = 5\) is a rule of thumb, and each effect arrives at its own Mach number depending on the body.
    - Five effects define it: **thin shock layers, entropy layers, viscous interaction, high-temperature chemistry, and low-density effects**.
    - **Mach-number independence**: above roughly \(M = 10\) the pressure coefficients, and therefore \(C_L\) and \(C_D\), stop changing with Mach altogether.
    - **Newtonian impact theory**, \(C_p = 2\sin^2\theta\), is useless at low speed and remarkably good here — because it becomes exact as \(M \to \infty\) *and* \(\gamma \to 1\), and real high-temperature air moves \(\gamma\) toward 1.
    - The design driver is **heating, not drag**. Stagnation heating scales as \(1/\sqrt{R_N}\), which is why re-entry vehicles are blunt — a deliberate choice, not a compromise.

## Key results

### What makes a flow hypersonic

Anderson's definition is a list of phenomena rather than a threshold, because they do not all switch on together:

| Effect | What happens | Consequence |
|---|---|---|
| **Thin shock layer** | Density ratio across the shock approaches \((\gamma+1)/(\gamma-1)\) | Shock lies close to the body; shock and boundary layer may merge |
| **Entropy layer** | A blunt nose makes a strongly curved shock, so streamlines cross it at different angles | Strong entropy gradients, vorticity in the inviscid flow, and an ill-defined boundary-layer edge |
| **Viscous interaction** | Boundary layer thickens as \(M^2/\sqrt{Re}\) and displaces the outer flow | Surface pressure and heating raised well above inviscid values |
| **High-temperature flow** | Vibrational excitation, dissociation, ionisation behind the shock | \(\gamma\) is no longer 1.4; perfect-gas relations fail badly |
| **Low density** | Mean free path comparable with the body | Slip and temperature jump at the wall, then free-molecular flow |

The practical consequence: a slender body at \(M = 8\) may be well handled by perfect-gas methods, while a blunt capsule at \(M = 8\) is already deep into high-temperature chemistry. The Mach number alone does not tell you which tools apply — the **velocity–altitude map** does, because altitude sets density and velocity sets the energy available to excite the gas.

### Hypersonic shock relations

As \(M_1 \to \infty\), the normal-shock relations approach limits that depend only on \(\gamma\):

<div class="result" markdown>

\[
\frac{\rho_2}{\rho_1} \to \frac{\gamma+1}{\gamma-1},
\qquad
\frac{p_2}{p_1} \to \frac{2\gamma M_1^2}{\gamma+1},
\qquad
\frac{T_2}{T_1} \to \frac{2\gamma(\gamma-1)M_1^2}{(\gamma+1)^2}
\]

</div>

The density ratio **saturates** at 6 for \(\gamma = 1.4\) — the shock layer can only get so thin on a perfect gas. Real air at re-entry conditions dissociates, which lowers the effective \(\gamma\) and pushes the density ratio to 10 or more, moving the shock closer still. Pressure and temperature, by contrast, keep growing as \(M^2\), and it is the temperature growth that drives everything in the second half of the subject.

### Mach-number independence

Written in terms of \(C_p\) rather than pressure, the shock relations lose their Mach dependence as \(M \to \infty\). Above roughly \(M = 10\) the **pressure distribution, and hence \(C_L\), \(C_D\) and \(L/D\), become essentially independent of Mach number** — a startling simplification, and the reason hypersonic aerodynamic data is often quoted as a single number rather than a curve. It fails for anything driven by temperature: heating, chemistry and the boundary layer continue to change.

### Newtonian theory

Treat the flow as a stream of particles that lose their normal momentum on impact and slide along the surface:

\[
C_p = 2\sin^2\theta
\]

with \(\theta\) the local surface inclination to the free stream. It contains no Mach number, which is Mach independence built in from the start. **Modified Newtonian** replaces the leading 2 with the actual stagnation value,

\[
C_p = C_{p,\max}\sin^2\theta,
\qquad
C_{p,\max} = \frac{p_{0_2}/p_\infty - 1}{\tfrac{1}{2}\gamma M_\infty^2}
\]

which for \(\gamma = 1.4\) tends to 1.839 rather than 2, and is markedly better on blunt bodies.

Why does a theory discarded in the eighteenth century work here? Because it is the exact limit of the shock relations as \(M \to \infty\) **and** \(\gamma \to 1\) simultaneously — both of which the shock layer approaches, the second because high-temperature air has a much lower effective \(\gamma\). The worked example below separates the two conditions and shows that the Mach limit alone is not enough.

### Aerodynamic heating, and why blunt

Stagnation-point heat transfer scales as

\[
\dot q_s \propto \frac{\rho_\infty^{1/2} V_\infty^3}{\sqrt{R_N}}
\]

Two things follow, and they are the whole shape of a re-entry vehicle. Heating goes as **velocity cubed**, so almost all the heating happens in a narrow band of the trajectory. And it goes as **\(1/\sqrt{R_N}\)**, so a *larger* nose radius means *less* heating.

This is Allen and Eggers' insight from 1953 and it is counter-intuitive enough to be worth stating plainly: the blunt re-entry capsule is not a concession to manufacturing or packaging. A blunt body puts most of the kinetic energy into a strong bow shock that heats the air and leaves it behind, rather than into a boundary layer that heats the vehicle. Sharp is right for drag and wrong for survival.

Working estimates come from **Fay–Riddell** at the stagnation point and the **reference temperature method** downstream, which evaluates flat-plate correlations at an intermediate temperature chosen to absorb the property variation across a highly non-isothermal boundary layer.

### High-temperature gas dynamics

Behind a strong shock, energy goes into modes a calorically perfect gas does not have:

| \(T\) (K, approx.) | What activates |
|---|---|
| 800+ | Vibrational excitation; \(c_p\) and \(\gamma\) become temperature-dependent |
| 2500+ | \(\mathrm{O_2}\) dissociation |
| 4000+ | \(\mathrm{N_2}\) dissociation |
| 9000+ | Ionisation — and radio blackout |

Each absorbs energy, so the temperature rises far less than perfect-gas theory predicts while the composition changes completely. Two further distinctions decide how hard the problem is:

- **Equilibrium vs non-equilibrium.** If the chemistry is fast relative to the flow residence time, composition is a local function of two state variables. If not — typical at high altitude — species must be transported and reacted individually, and the flow carries a memory of its history.
- **Catalytic walls.** A surface that recombines dissociated atoms releases their energy locally. A fully catalytic wall can see several times the heating of a non-catalytic one, which makes thermal protection material choice an *aerothermodynamic* decision rather than a materials one.

### The L/D barrier and waveriders

Hypersonic \(L/D\) is low, and bounded: the empirical correlation \(L/D_{\max} \approx 4(M+3)/M\) gives about 5 at \(M = 10\). **Waveriders** — shapes designed inversely from a known supersonic flow field so the bow shock attaches along the entire leading edge, trapping high pressure beneath — beat it, at the cost of being optimal at exactly one Mach number and needing a sharp leading edge that is hard to cool.

## Mental model

Think of the shock layer as a thin, hot, chemically active blanket wrapped close to the body. Everything distinctive follows from "thin" and "hot".

*Thin* gives the geometric results: the shock follows the body, so surface pressure depends mainly on local inclination and barely on the rest of the shape. That is why Newtonian impact theory works, why Mach independence holds, and why hypersonic configuration design is unusually local.

*Hot* gives everything else. Kinetic energy that is merely large at supersonic speeds becomes, at orbital speeds, enough to pull molecules apart. The air stops being a fixed gas with \(\gamma = 1.4\) and becomes a reacting mixture whose properties depend on where it has been. At that point the aerodynamicist's problem has become a thermochemistry problem, and the vehicle is designed around heat rather than around drag.

## Numerics / practice

- **Check the perfect-gas assumption against the stagnation temperature** before anything else. Above about 800 K vibrational excitation is already significant, and \(\gamma = 1.4\) is an error rather than an approximation.
- **Use modified Newtonian, not Newtonian**, on blunt bodies: \(C_{p,\max}\) from the actual normal-shock stagnation pressure, 1.839 rather than 2 for \(\gamma = 1.4\).
- **Watch for the carbuncle instability.** Strong bow shocks captured on blunt-body grids are prone to it, and it corrupts exactly the stagnation region you care about; grid alignment with the bow shock and a suitable flux function matter more than formal order.
- **Grid the wall for heating, not for pressure.** Surface heat flux needs cell Reynolds numbers near 1 at the wall — often an order of magnitude finer than a pressure-converged grid.
- **Transition location is a first-order uncertainty**, not a refinement. Turbulent heating can be several times laminar, and hypersonic transition prediction remains unreliable; carry it as an uncertainty band rather than a number.
- **Ground testing cannot match everything at once.** No facility reproduces Mach number, Reynolds number and total enthalpy together, so hypersonic validation is always partial and always an argument about which parameters matter for the question at hand.

??? warning "Failure modes"
    **Perfect-gas relations used at re-entry conditions.** The familiar isentropic and shock tables assume constant \(\gamma = 1.4\). At \(M = 20\) they overpredict temperature enormously — the energy goes into dissociation instead — and get density, shock standoff and heating all wrong. They fail silently, returning numbers that look like answers.

    **Hypersonic treated as a Mach number threshold.** The effects arrive at different Mach numbers for different bodies. A slender vehicle at \(M = 8\) may be perfect-gas; a blunt one at \(M = 8\) is not. "Above \(M = 5\) use hypersonic methods" is a slogan, not a criterion.

    **Newtonian theory applied where its limit does not hold.** It is the \(M \to \infty\), \(\gamma \to 1\) limit. At \(M = 5\) with \(\gamma = 1.4\) it is poor, and on the leeward side — where the flow is shadowed and the theory simply predicts \(C_p = 0\) — it has no content at all. Base and leeward pressures are exactly where it must not be trusted.

    **Sharp nose chosen for low drag on a re-entry body.** Stagnation heating scales as \(1/\sqrt{R_N}\), so sharpening the nose increases it. The low-drag shape is the one that does not survive.

    **Equilibrium chemistry assumed at altitude.** At low density the reaction times are long compared with the residence time, and the flow is in non-equilibrium. Equilibrium models misplace the energy, giving wrong temperature, wrong composition and wrong heating — usually optimistic.

    **Wall catalycity ignored.** A fully catalytic surface recombines atoms and releases that energy into the wall, which can multiply heating several-fold over a non-catalytic one. Omitting it understates the thermal protection requirement.

    **Viscous interaction neglected on slender bodies.** The boundary layer grows as \(M^2/\sqrt{Re}\) and displaces the inviscid flow enough to change surface pressure materially. On a slender hypersonic vehicle this is a leading-order effect, not a correction.

    **Ground-test data extrapolated across the parameters it did not match.** A cold hypersonic tunnel matches Mach number but not enthalpy, so it reproduces the pressure field and not the chemistry or the heating. Treating such data as validation of a reacting-flow prediction is a category error.

    <!-- Add your own here. -->

## Worked example

Why Newtonian theory — discarded for every other flow regime — works here, and what exactly it needs:

```python
import numpy as np

def bisect(f, a, b, n=200):
    for _ in range(n):
        c = 0.5*(a + b)
        a, b = (c, b) if f(a)*f(c) > 0 else (a, c)
    return 0.5*(a + b)

def cp_wedge(M, th, g=1.4):          # exact oblique-shock surface Cp, weak solution
    f = lambda B: (2/np.tan(B)*(M**2*np.sin(B)**2 - 1)
                   / (M**2*(g + np.cos(2*B)) + 2) - np.tan(th))
    B = bisect(f, np.arcsin(1/M) + 1e-12, np.pi/2 - 1e-12)
    return 4*(M**2*np.sin(B)**2 - 1)/((g + 1)*M**2), B

def cp_max(M, g=1.4):                # stagnation Cp behind a normal shock (Rayleigh pitot)
    p02 = (((g+1)**2*M**2)/(4*g*M**2 - 2*(g-1)))**(g/(g-1)) * ((1 - g + 2*g*M**2)/(g+1))
    return (p02 - 1)/(0.5*g*M**2)

th = np.radians(20.0)
newt = 2*np.sin(th)**2
print(f"20 deg wedge, gamma = 1.4.   Newtonian says Cp = 2 sin^2(theta) = {newt:.4f}")
print(f"{'M':>5}{'exact Cp':>10}{'modified N.':>13}{'rho2/rho1':>11}{'Cp_max':>9}")
for M in (2, 3, 5, 10, 20, 40):
    cp, B = cp_wedge(M, th); Mn = M*np.sin(B)
    rho = 2.4*Mn**2/(0.4*Mn**2 + 2)
    print(f"{M:5d}{cp:10.4f}{cp_max(M)*np.sin(th)**2:13.4f}{rho:11.3f}{cp_max(M):9.4f}")

print("\nMach-number independence -- Cp stops changing, it does not approach Newtonian:")
prev = None
for M in (5, 10, 20, 40, 80):
    c = cp_wedge(M, th)[0]
    print(f"   M = {M:3d}:  Cp = {c:.4f}"
          + ("" if prev is None else f"    change on doubling M: {100*(c/prev-1):+.2f}%"))
    prev = c

print(f"\nNewtonian needs BOTH M -> inf and gamma -> 1 (M = 50 throughout):")
for g in (1.4, 1.2, 1.1, 1.05, 1.01):
    print(f"   gamma = {g:4.2f}:  exact Cp = {cp_wedge(50, th, g)[0]:.4f}"
          f"   Newtonian {newt:.4f}   error {100*(cp_wedge(50,th,g)[0]/newt - 1):+6.1f}%")
print(f"\n   limits:  rho2/rho1 -> (g+1)/(g-1) = {2.4/0.4:.1f} at gamma=1.4,"
      f"   Cp_max -> {cp_max(1e6):.4f} (Newtonian assumes 2)")
```

```
20 deg wedge, gamma = 1.4.   Newtonian says Cp = 2 sin^2(theta) = 0.2340
    M  exact Cp  modified N.  rho2/rho1   Cp_max
    2    0.6582       0.1939      2.042   1.6573
    3    0.4399       0.2054      2.418   1.7557
    5    0.3450       0.2116      3.315   1.8088
   10    0.2994       0.2143      4.748   1.8317
   20    0.2867       0.2149      5.599   1.8374
   40    0.2834       0.2151      5.892   1.8389

Mach-number independence -- Cp stops changing, it does not approach Newtonian:
   M =   5:  Cp = 0.3450
   M =  10:  Cp = 0.2994    change on doubling M: -13.20%
   M =  20:  Cp = 0.2867    change on doubling M: -4.24%
   M =  40:  Cp = 0.2834    change on doubling M: -1.15%
   M =  80:  Cp = 0.2826    change on doubling M: -0.29%

Newtonian needs BOTH M -> inf and gamma -> 1 (M = 50 throughout):
   gamma = 1.40:  exact Cp = 0.2830   Newtonian 0.2340   error  +21.0%
   gamma = 1.20:  exact Cp = 0.2585   Newtonian 0.2340   error  +10.5%
   gamma = 1.10:  exact Cp = 0.2465   Newtonian 0.2340   error   +5.4%
   gamma = 1.05:  exact Cp = 0.2406   Newtonian 0.2340   error   +2.8%
   gamma = 1.01:  exact Cp = 0.2359   Newtonian 0.2340   error   +0.8%

   limits:  rho2/rho1 -> (g+1)/(g-1) = 6.0 at gamma=1.4,   Cp_max -> 1.8394 (Newtonian assumes 2)
```

The first table shows Newtonian theory failing and then recovering. At \(M = 2\) the exact wedge \(C_p\) is nearly three times the Newtonian value, which is why the theory was abandoned for ordinary flows. By \(M = 20\) the two are within 20%, and the density ratio has climbed from 2.0 toward its perfect-gas ceiling of 6 — the shock layer thinning, which is the geometric assumption Newtonian theory rests on.

The second block is **Mach-number independence**, and it is worth reading carefully. Doubling the Mach number changes \(C_p\) by \(-13\%\), then \(-4\%\), then \(-1\%\), then \(-0.3\%\): the pressure field is converging to a constant. Above \(M \approx 20\) the aerodynamic coefficients of this wedge simply do not depend on Mach number any more. Note what it converges *to*, though — 0.282, not the Newtonian 0.234. Mach independence and Newtonian theory are two different statements, and only the first is exact.

The third block supplies the missing condition. Holding \(M = 50\) and lowering \(\gamma\), the error against Newtonian falls from \(+21\%\) at \(\gamma = 1.4\) to \(+0.8\%\) at \(\gamma = 1.01\). **Newtonian theory is the joint limit \(M \to \infty\) and \(\gamma \to 1\)**, and the reason it earns its place in real hypersonics is that high-temperature air obliges on the second condition: vibrational excitation and dissociation drive the effective \(\gamma\) well below 1.4, often toward 1.1–1.2. The approximation works in practice because the chemistry that ruins the perfect-gas tables is the same chemistry that rescues Newtonian theory.

The limitation is in the first table's unused column: on a wedge, every surface faces the flow. Newtonian theory assigns \(C_p = 0\) to any surface inclined away from the stream, so base pressure, leeward-side loads and anything governed by the wake lie entirely outside it.

## Connections

- [Transonic aerodynamics](transonic.md) — the other hard end of the compressible range.
- [Aerodynamics](aerodynamics.md) — the linear theory that both regimes leave behind.
- [Fluids › Compressible flow](../fluids/compressible.md) — shock capturing and the numerics of strong discontinuities.
- [Space environment and orbits](space-environment.md) — where re-entry trajectories come from, and the velocity–altitude map.
- [Thermal › Heat transfer](../thermal/heat-transfer.md) — the wall side of the aerothermal problem.
- [Thermal › Combustion](../thermal/combustion.md) — finite-rate chemistry, the same machinery as non-equilibrium air.
- [Propulsion](propulsion.md) — scramjets, where this flow has to be slowed, burned and re-expanded.

## Sources

- Anderson, *Hypersonic and High-Temperature Gas Dynamics* — the whole structure of this page: the definition by phenomena, local surface inclination methods, Mach independence, hypersonic similarity, viscous interaction, and the high-temperature half of the subject.
- Allen & Eggers, NACA Report 1381 — the blunt-body insight.
- Fay & Riddell (1958) — stagnation-point heat transfer in dissociated air.
- Bertin, *Hypersonic Aerothermodynamics*.
