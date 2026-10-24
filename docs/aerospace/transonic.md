---
title: Transonic aerodynamics
status: working
tags: [pillar-1, aerospace, discretization, scaling]
updated: 2026-10-24
---

# Transonic aerodynamics

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Transonic flow is where **both subsonic and supersonic regions exist at once**, so the governing equation is of **mixed type** and the sonic line is a free boundary found as part of the solution.
    - It is not a Mach band. It is a band in \(M_\infty\) *and* thickness *and* lift — a thick wing is transonic at a Mach number where a thin one is not.
    - The equation is **nonlinear**: the coefficient that decides elliptic versus hyperbolic contains the solution. No superposition, no scaling rule, no closed form.
    - **Drag divergence** is the design quantity, not \(M_{crit}\). Sweep, thinning and supercritical sections are the three ways to buy it, and they are roughly interchangeable.
    - The limit is not the shock itself but **shock-induced separation**: buffet onset is what actually bounds the cruise envelope.

## Key results

### Why this regime is genuinely different

Write the small-disturbance potential equation without discarding the term that vanishes in the linear limit:

<div class="result" markdown>

\[
\left[1 - M_\infty^2 - (\gamma+1)M_\infty^2\,\phi_x\right]\phi_{xx} + \phi_{yy} = 0
\]

</div>

Compare this with the linear form in [aerodynamics](aerodynamics.md). Two things have changed, and both are fatal to the usual toolkit:

- The bracket contains \(\phi_x\), the **solution itself**. The equation is nonlinear, so solutions cannot be superposed and incompressible results cannot be rescaled onto compressible ones.
- When \(M_\infty \approx 1\) the first two terms nearly cancel, so the sign of the bracket is set by the perturbation. The equation is **elliptic in part of the field and hyperbolic in another**, with a **sonic line** separating them whose position is not known until the problem is solved.

A free boundary inside a mixed-type PDE is why transonic flow resisted theory for fifty years while subsonic and supersonic aerodynamics were essentially finished. It is also why the numerical breakthrough — Murman and Cole's **type-dependent differencing** in 1970, switching between central differences in subsonic points and upwind differences in supersonic ones — mattered so much: the physics requires the discretisation to change character pointwise.

### Critical and drag-divergence Mach

\(M_{crit}\) is where the flow first reaches sonic *somewhere* on the surface. Nothing happens there. What matters comes a little later:

| Quantity | Meaning |
|---|---|
| \(M_{crit}\) | Local flow first reaches \(M = 1\). No drag penalty yet. |
| \(M_{dd}\) | **Drag divergence**: \(\mathrm{d}C_D/\mathrm{d}M = 0.1\), or \(\Delta C_D = 0.002\) |
| \(M_{\text{buffet}}\) | Shock-induced separation becomes unsteady; the practical ceiling |

Between \(M_{crit}\) and \(M_{dd}\) a supersonic pocket grows and terminates in a weak shock that costs little. Past \(M_{dd}\) the shock is strong enough that entropy generation — and usually separation behind it — turns into real drag, very fast.

The **Korn equation** is the standard correlation, and is useful precisely because it makes the trade explicit:

\[
M_{dd}\cos\Lambda + \frac{C_L}{10\cos^2\Lambda} + \frac{t/c}{\cos\Lambda} = \kappa_A
\]

with \(\kappa_A \approx 0.87\) for a conventional section and \(\approx 0.95\) for a supercritical one. Thickness, lift and sweep all trade against the same budget.

### Sweep, and what it costs

Sweep works because only the velocity component normal to the leading edge matters for the pressure field: \(M_{\text{eff}} \approx M_\infty\cos\Lambda\). It is the most powerful transonic lever available, and the bill is long:

- **Spanwise flow** drives the boundary layer outboard, thickening it near the tip.
- **Tip stall** follows, and because the tip is behind the centre of gravity on a swept wing, it produces a **nose-up pitch-up** at exactly the wrong moment. Fences, notches, vortilons and washout all exist to manage this.
- **Aeroelastic divergence** in forward sweep; **bending–torsion coupling** that washes out an aft-swept wing under load.
- Structural weight, root and tip effects that spoil the simple \(\cos\Lambda\) rule where the wing meets the fuselage and where it ends.

### Supercritical sections

A conventional section accelerates hard around the leading edge, so the supersonic pocket forms early and terminates in a strong shock. A **supercritical** section instead:

- flattens the upper surface, spreading the suction over a long weak supersonic region rather than a sharp peak;
- terminates it with a **weak, far-aft shock**;
- recovers the lost lift with pronounced **aft camber** on the lower surface near the trailing edge.

The result is a higher \(M_{dd}\) for the same thickness, or the same \(M_{dd}\) at greater thickness — which is usually taken as thicker wings: lighter structure, more fuel volume and more span for the same weight. The costs are a large nose-down pitching moment from the aft camber, which the tail must trim, and a narrower off-design envelope.

### Area rule

Wave drag depends, to first order, on the **streamwise distribution of total cross-sectional area**, not on which component contributes it. Whitcomb's transonic area rule follows: make the total area distribution smooth, and if the wing adds area, take it out of the fuselage — the "coke bottle" waist. The supersonic version generalises this to area cut by oblique Mach planes rather than normal ones, so the optimum shaping depends on design Mach number.

### Shock–boundary-layer interaction and buffet

The shock imposes a steep adverse pressure gradient on a boundary layer that is already decelerating. Depending on its strength and the state of the boundary layer, the result ranges from a small thickening, through a separation bubble, to full trailing-edge separation.

When the separation becomes unsteady, the shock oscillates and the wing shakes: **buffet**. The buffet boundary in the \((M, C_L)\) plane is the real limit on a transport's cruise envelope, and certification requires a margin to it — typically 1.3 g — which is why aircraft cruise below the Mach number at which they are most efficient.

## Mental model

Subsonic flow is elliptic: every point feels every other point, and the field is smooth. Supersonic flow is hyperbolic: information travels along characteristics, disturbances stay inside Mach cones, and discontinuities are allowed. Transonic flow is both at once, in different parts of the same field, with the boundary between them free to move.

That is the whole difficulty in one sentence, and it explains the rest. No superposition, because the equation is nonlinear. No compressibility correction, because there is no linear solution to correct. No closed-form airfoil theory. And a numerical method must detect, pointwise, which kind of equation it is currently solving.

The design story is more cheerful: three independent levers — thin the section, sweep the wing, reshape the pressure distribution — all buy the same thing, so a designer short of one can spend another.

## Numerics / practice

- **Type-dependent differencing is not optional** in potential methods. Central differencing at supersonic points violates the domain of dependence and the scheme will not converge to the right answer, if at all.
- **Potential methods permit non-physical shocks.** The full-potential formulation is isentropic and irrotational by construction, so it admits expansion shocks and overpredicts shock strength above about \(M_n = 1.3\). Use Euler or RANS past that.
- **Transonic cases need viscous coupling** to place the shock. Shock position is extremely sensitive to boundary-layer displacement, and an inviscid calculation typically puts it too far aft.
- **Resolve the shock region.** Shock position error translates directly into pitching-moment error, which is what sizes the tail.
- **Wind tunnel walls must be slotted or perforated.** Solid walls choke the test section near \(M = 1\), and the blockage correction diverges with them — the reason transonic testing was impossible until the mid-1950s.
- Grid convergence and the rest of the [CFD failure modes](../fluids/cfd/index.md) apply with more force here, because the solution contains a discontinuity whose *location* is an output.

??? warning "Failure modes"
    **A linear compressibility correction applied past \(M_{crit}\).** Prandtl–Glauert is the elliptic branch of a linearised equation, and it has no supersonic pocket in it. Applied transonically it returns smooth, plausible, badly wrong pressures, and it is singular at \(M = 1\) rather than merely inaccurate.

    **\(M_{crit}\) treated as the design limit.** Nothing happens at \(M_{crit}\); useful cruise generally sits beyond it. Designing to stay below it gives away performance, and quoting it as "the limit" hides the quantity that is actually binding.

    **Drag divergence treated as the limit instead of buffet.** \(M_{dd}\) is a drag bookkeeping definition. What ends the envelope is shock-induced separation and the buffet margin, and that boundary depends on \(C_L\) — so it moves in a turn, in gusts, and as the aircraft gets lighter.

    **Central differencing in the supersonic pocket.** A scheme that ignores the hyperbolic character at supersonic points is solving the wrong equation there. It will oscillate, converge slowly, or converge to a solution with the shock in the wrong place.

    **Inviscid shock position believed.** Shock location is set by the interaction with the boundary layer. Inviscid calculations place it too far aft and predict too much lift and the wrong pitching moment, and the error grows exactly as the shock strengthens.

    **\(\cos\Lambda\) applied to the whole wing.** Simple sweep theory holds for an infinite swept wing. At the root and the tip the flow is not swept, which is where the shocks actually form first and where supercritical designs need the most local attention.

    **Supercritical section adopted without budgeting for trim.** Aft camber produces a large nose-down pitching moment. The tail load that trims it costs lift, drag and structure, and it has to be carried in the design from the start rather than discovered later.

    **Transonic tunnel data used without wall-interference correction.** Near \(M = 1\) the corrections are large and model-dependent, and the classical blockage formulas break down in the same regime the test is probing.

    <!-- Add your own here. -->

## Worked example

Where the transonic regime starts, and the three ways to push it back:

```python
import numpy as np
g = 1.4

def bisect(f, a, b, n=200):
    for _ in range(n):
        c = 0.5*(a + b)
        a, b = (c, b) if f(a)*f(c) > 0 else (a, c)
    return 0.5*(a + b)

def cp_sonic(M):            # Cp at which the LOCAL flow first reaches M = 1
    return 2/(g*M**2)*(((2 + (g-1)*M**2)/(g+1))**(g/(g-1)) - 1)

def Mcrit(cp0):             # Prandtl-Glauert peak suction meets the sonic Cp
    return bisect(lambda M: cp0/np.sqrt(1 - M**2) - cp_sonic(M), 0.05, 0.9999)

print("critical Mach: Prandtl-Glauert peak suction meets the isentropic sonic condition")
print(f"{'t/c':>6}{'cp_min,0':>10}{'M_crit':>9}{'cp* there':>11}")
for tc in (0.06, 0.08, 0.10, 0.12, 0.15, 0.18):
    cp0 = -2*tc                                  # thin symmetric section, zero lift
    Mc = Mcrit(cp0)
    print(f"{tc:6.2f}{cp0:10.2f}{Mc:9.3f}{cp_sonic(Mc):11.3f}")

# Korn equation, swept:  M_dd cosL + CL/(10 cos^2 L) + (t/c)/cosL = kappa
#   kappa = 0.87 conventional section, 0.95 supercritical
def Mdd(tc, CL, sweep_deg, kappa):
    c = np.cos(np.radians(sweep_deg))
    return (kappa - tc/c - CL/(10*c**2))/c

print("\ndrag-divergence Mach (Korn),  t/c = 0.12,  C_L = 0.5")
print(f"{'sweep':>9}{'conventional':>14}{'supercritical':>15}")
for L in (0, 10, 20, 25, 30, 35):
    print(f"{L:6d} deg{Mdd(0.12,0.5,L,0.87):14.3f}{Mdd(0.12,0.5,L,0.95):15.3f}")

base = Mdd(0.12, 0.5, 0, 0.87)
tc = bisect(lambda t: Mdd(t, 0.5, 0, 0.87) - (base + 0.06), 0.01, 0.12)
sw = bisect(lambda L: Mdd(0.12, 0.5, L, 0.87) - (base + 0.06), 0.0, 60.0)
print(f"\nthree ways to buy the same +0.060 in M_dd from the {base:.3f} baseline:")
print(f"   thin the section to t/c = {tc:.3f}   (structure and fuel volume pay)")
print(f"   sweep the wing by {sw:.1f} deg        (tip stall, aeroelastics and weight pay)")
print(f"   use a supercritical section:  {Mdd(0.12,0.5,0,0.95)-base:+.3f}  for no geometry change")
```

```
critical Mach: Prandtl-Glauert peak suction meets the isentropic sonic condition
   t/c  cp_min,0   M_crit  cp* there
  0.06     -0.12    0.873     -0.246
  0.08     -0.16    0.849     -0.303
  0.10     -0.20    0.828     -0.357
  0.12     -0.24    0.809     -0.409
  0.15     -0.30    0.784     -0.483
  0.18     -0.36    0.761     -0.555

drag-divergence Mach (Korn),  t/c = 0.12,  C_L = 0.5
    sweep  conventional  supercritical
     0 deg         0.700          0.780
    10 deg         0.707          0.789
    20 deg         0.730          0.815
    25 deg         0.747          0.835
    30 deg         0.768          0.860
    35 deg         0.792          0.890

three ways to buy the same +0.060 in M_dd from the 0.700 baseline:
   thin the section to t/c = 0.060   (structure and fuel volume pay)
   sweep the wing by 28.3 deg        (tip stall, aeroelastics and weight pay)
   use a supercritical section:  +0.080  for no geometry change
```

The first table is the classical construction: the peak suction grows as \(1/\sqrt{1-M_\infty^2}\) while the \(C_p\) required to reach sonic conditions falls, and \(M_{crit}\) is where they meet. It shows at once that **"transonic" is a property of the body, not only of the flow** — a 6% section is still entirely subcritical at \(M = 0.87\), where an 18% section has been supercritical since 0.76.

The second table is the design trade, and the third line is the point. Starting from an unswept 12% conventional wing at \(M_{dd} = 0.70\), the same +0.06 in drag-divergence Mach can be bought by halving the thickness, by 28° of sweep, or — for free, in geometry terms — by switching to a supercritical section, which gives +0.08. That is why supercritical sections were adopted so quickly and so universally after 1970: the alternatives both cost structural weight, and thinning costs fuel volume as well.

Combining them gives the modern answer. A 35° swept supercritical wing at \(t/c = 0.12\) reaches \(M_{dd} = 0.89\), which is where large transports actually live, cruising a little below it for buffet margin.

Two honest limitations. \(c_{p,\min,0} \approx -2(t/c)\) is a thin-airfoil estimate, so the \(M_{crit}\) column is indicative rather than a design number — a real section needs its own pressure distribution. And the Korn equation is a correlation fitted to a family of sections, not a theory; it captures the trades correctly and should not be trusted to three decimals.

## Connections

- [Aerodynamics](aerodynamics.md) — the linearised equation this one extends, and why it fails at \(M = 1\).
- [Hypersonic aerodynamics](hypersonics.md) — the far end of the compressible range.
- [Fluids › Compressible flow](../fluids/compressible.md) — shock capturing, Riemann solvers and the numerics of discontinuities.
- [Aircraft design](aircraft-design.md) — where \(M_{dd}\) enters sizing, through the cruise constraint.
- [Turbomachinery](turbomachinery.md) — transonic compressor rotors run this physics in a rotating frame.
- [Aeroacoustics](aeroacoustics.md) — high-speed impulsive noise, the rotorcraft version of drag divergence.

## Sources

- Vos & Farokhi, *Transonic Aerodynamics* — similarity laws, supercritical sections, swept-wing aerodynamics and aeroelasticity.
- Cole & Cook, *Transonic Aerodynamics* — small-disturbance theory done systematically: mixed-type equations, weak solutions, hodograph methods.
- Chattot & Hafez, *Theoretical and Applied Aerodynamics* — transonic small-disturbance theory and transonic lifting line.
- McLean, *Understanding Aerodynamics* — airfoils in transonic flow, and high-speed stall.
- Whitcomb's NACA/NASA reports on the area rule and the supercritical airfoil.
