---
title: Mesoscale–microscale coupling
status: working
tags: [pillar-1, meteorology, turbulence, scaling, boundary-layer]
updated: 2026-10-24
---

# Mesoscale–microscale coupling

<span class="status status-working">working</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Wind energy, fire weather and urban flow all need **mesoscale forcing with microscale resolution**, and the two are built on incompatible assumptions about turbulence.
    - A mesoscale model **parameterises all** boundary-layer turbulence; an LES **resolves most** of it. Between them lies the **grey zone**, where neither assumption holds.
    - For the atmospheric boundary layer the grey zone is roughly \(\Delta \sim z_i\) — a few hundred metres to a few kilometres — which is exactly the resolution a wind-farm or fire nest wants to run at.
    - Nesting from mesoscale into LES does not spontaneously produce turbulence: the inflow arrives **smooth**, and the **fetch** needed to develop eddies can exceed the whole domain.
    - The standard fixes — cell perturbation, synthetic turbulence, precursor recycling — all inject turbulence that was never in the forcing data.

## Key results

### Two models, two assumptions

| | Mesoscale (e.g. WRF, ERF at coarse \(\Delta\)) | Microscale LES |
|---|---|---|
| Grid | 1–10 km | 1–50 m |
| BL turbulence | **Entirely parameterised** by a PBL scheme | **Mostly resolved**; subgrid model handles the rest |
| Closure assumes | All turbulence is subgrid, horizontally homogeneous | Filter is in the inertial subrange |
| Gives you | Synoptic forcing, diurnal cycle, real weather | Eddies, gusts, wakes, shear |

The PBL scheme is a one-dimensional column model: it assumes the grid cell is much larger than the energy-containing eddies, so their net effect can be written as a vertical flux. The LES subgrid model assumes the opposite — that the filter cuts within the inertial subrange, where the unresolved motions are universal and nearly isotropic.

### The boundary-layer grey zone

Neither assumption survives at \(\Delta \sim z_i\), the boundary-layer depth, because that is the scale of the energy-containing eddies themselves. Wyngaard named this **terra incognita**. The symptoms are specific and recognisable:

- The PBL scheme and the resolved dynamics **both** transport heat and momentum, so the total flux is double-counted.
- Resolved convective structures appear but are under-resolved — too few cells per thermal — so they are too large, too strong and too slow to break down.
- Results depend on resolution in a way that does not converge, because refining changes which model is doing the work.

**Scale-aware** PBL schemes attempt a partition that depends on \(\Delta/z_i\), handing flux from the parameterisation to the resolved field as the grid refines. They help, and they do not remove the problem — the worked example shows why the band is wide.

### Turbulence does not nest

The deeper problem with one-way nesting into LES is that the parent has **no resolved turbulence to give**. The nest's lateral boundary receives a smooth, slowly varying profile. Inside the nest, turbulence must grow from whatever instability the smooth inflow supports, and that takes distance:

<div class="result" markdown>

fetch to develop resolved turbulence \(\sim 10\)–\(50\,z_i\)

</div>

For a 1 km boundary layer that is 10–50 km of domain consumed before the LES is doing its job — often larger than the region of interest, and sometimes larger than the nest.

Three standard remedies:

- **Cell perturbation method.** Add small potential-temperature perturbations in a band near the inflow boundary. Cheap, easy, and now the common default; it accelerates transition by a large factor.
- **Synthetic turbulence inflow.** Generate a fluctuating field with the right spectrum and coherence and impose it. Better spectra, but the coherence structure is invented.
- **Precursor / recycling.** Run a separate periodic LES to equilibrium and feed its planes in. Most physical, most expensive, and hard to reconcile with a real, evolving mesoscale state.

All three share the same caveat: **the injected turbulence is not the turbulence the mesoscale model had**, because the mesoscale model had none. It is turbulence consistent with the mean profile, which is a weaker statement than it sounds.

### Coupling strategies

| Strategy | How | When |
|---|---|---|
| **One-way nesting** | Parent drives child boundaries | Default; cheap; no feedback |
| **Two-way nesting** | Child feeds back to parent | When the microscale changes the mesoscale — large farms, big fires |
| **Offline / profile forcing** | Extract time-varying profiles, drive a periodic LES | Clean, idealised, loses horizontal heterogeneity |
| **Internal nesting in one code** | Same solver across scales, e.g. AMR | Avoids model mismatch at the interface entirely |

That last row is the direction of travel. A single solver with [adaptive refinement](../computing/amr.md) removes the discontinuity in numerics, closure and even code between parent and child — one reason exascale atmospheric codes are built on block-structured AMR rather than on nested separate models.

### Where the turbine or the fire goes

The microscale domain is where the engineering model lives: [actuator disks or lines](../aerospace/actuator-line.md) for turbines, a fire-spread and plume model for wildfire. The coupling question becomes whether the forcing resolves what the device responds to. A turbine responds to shear and veer across the rotor disk and to gusts at rotor scale; a mesoscale cell delivers a single profile and no gusts, so the device model is fed exactly the quantity the coupling is least able to supply.

## Mental model

Think of it as a handover of responsibility for the energy-containing eddies. The mesoscale model owns them completely and never shows them to you. The LES owns almost none of them and shows you the rest. The coupling works when the handover happens cleanly — and the grey zone is the region where both models believe they own the same eddies.

The second idea is that **information flows down the scales but turbulence does not**. A parent can give its child the mean wind, the stratification and the pressure gradient. It cannot give what it never represented, so every microscale simulation manufactures its own turbulence and the honest question is whether that manufactured field is good enough for what the device responds to.

## Numerics / practice

- **Compute \(\Delta/z_i\) before choosing resolutions**, for the deepest boundary layer in the run, not the average. Afternoon convective depth can be three times the morning value, so a grid that is LES at dawn is grey zone by mid-afternoon.
- **Avoid the grey zone by jumping it.** Going from 3 km directly to 100 m through an intermediate nest that sits at 1 km puts a domain squarely in the worst place. Large nest ratios are usually better than a graded descent here.
- **Budget inflow fetch explicitly** and place the region of interest well downstream of it.
- **Report which turbulence injection was used.** Results in the first several \(z_i\) depend more on that choice than on the physics.
- **Check the resolved-flux fraction** rather than trusting the resolution. If the subgrid model is carrying most of the momentum flux, the run is not an LES whatever the cell size says.

??? warning "Failure modes"
    **Running a PBL scheme in the boundary-layer grey zone.** Both the scheme and the resolved motions transport flux, so transport is double-counted. The profiles look smooth and plausible, and the boundary layer is too well-mixed with too little variance — which is precisely wrong for a wind-energy or dispersion application.

    **Expecting turbulence at the nest inflow.** The parent has none to give. Without perturbation or synthetic inflow the first tens of kilometres of the nest are laminar, and any device placed there sees an atmosphere that does not exist.

    **Region of interest too close to the inflow boundary.** Related but distinct: even with perturbation methods the spectrum is not fully developed for several \(z_i\), and the high-frequency content a turbine or a fire responds to develops last.

    **Grid convergence study across the grey zone.** Refining from 2 km to 500 m to 100 m crosses a change in which model does the physics. The sequence does not converge, and reading it as convergence failure of the numerics misdiagnoses it.

    **Mesoscale turbulence statistics used as microscale inflow statistics.** The variance in a mesoscale field is mesoscale variability, not turbulence. Using it to set a turbulence intensity confuses two different quantities that share a symbol.

    **Two-way nesting left on without checking feedback.** A poorly resolved child can corrupt its parent, and the resulting degradation is slow and global, so it is usually attributed to something else.

    **Stable boundary layers treated like convective ones.** In stable conditions \(z_i\) can collapse to tens of metres, so a 100 m grid that was LES in the afternoon is coarser than the boundary layer at night. Nocturnal low-level jets and intermittent turbulence are exactly where wind-energy and dispersion forecasts are most wanted and least reliable.

    <!-- Add your own here. -->

## Worked example

How wide the grey zone actually is, using a von Kármán boundary-layer spectrum with its energy peak at the boundary-layer depth:

```python
import numpy as np

# Model ABL spectrum: energy peak near the boundary-layer depth z_i, Kolmogorov tail.
# E(k) ~ (k/k0)^4 / (1 + (k/k0)^2)^(17/6)   -- von Karman form, peak at k ~ k0 ~ 1/z_i
k  = np.logspace(-4, 4, 400001)
E  = (k)**4 / (1 + k**2)**(17/6)
TOT = np.sum(E*k)*(np.log(k[1])-np.log(k[0]))

def resolved(dz):                                   # dz = Delta / z_i
    kc = np.pi/dz                                   # filter cutoff wavenumber
    m  = k <= kc
    return np.sum(E[m]*k[m])*(np.log(k[1])-np.log(k[0]))/TOT

print("fraction of turbulent kinetic energy a grid of spacing Delta actually RESOLVES")
print(f"{'Delta/z_i':>11}{'resolved':>11}{'subfilter':>12}   regime")
for dz in (20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05):
    r = resolved(dz)
    reg = ("mesoscale: parameterise all of it" if r < 0.05 else
           "LES: resolve most of it"           if r > 0.80 else
           "GREY ZONE: neither assumption holds")
    print(f"{dz:11.2f}{r:11.3f}{1-r:12.3f}   {reg}")

lo = min(d for d in np.arange(0.01, 30, 0.01) if resolved(d) < 0.80)
hi = max(d for d in np.arange(0.01, 30, 0.01) if resolved(d) > 0.05)
print(f"\ngrey zone spans roughly Delta/z_i = {lo:.2f} to {hi:.1f}")
print(f"for a 1 km convective boundary layer that is Delta = {lo*1000:.0f} m to {hi*1000/1000:.1f} km")
print("-- which is exactly the resolution band of a wind-farm or fire-weather nest.")
```

```
fraction of turbulent kinetic energy a grid of spacing Delta actually RESOLVES
  Delta/z_i   resolved   subfilter   regime
      20.00      0.000       1.000   mesoscale: parameterise all of it
      10.00      0.000       1.000   mesoscale: parameterise all of it
       5.00      0.010       0.990   mesoscale: parameterise all of it
       2.00      0.140       0.860   GREY ZONE: neither assumption holds
       1.00      0.368       0.632   GREY ZONE: neither assumption holds
       0.50      0.583       0.417   GREY ZONE: neither assumption holds
       0.20      0.771       0.229   GREY ZONE: neither assumption holds
       0.10      0.857       0.143   LES: resolve most of it
       0.05      0.911       0.089   LES: resolve most of it

grey zone spans roughly Delta/z_i = 0.17 to 3.1
for a 1 km convective boundary layer that is Delta = 170 m to 3.1 km
-- which is exactly the resolution band of a wind-farm or fire-weather nest.
```

Read the table as the handover. At \(\Delta/z_i = 10\) — a 10 km mesoscale cell over a 1 km boundary layer — the grid resolves essentially nothing, and a PBL scheme that parameterises all of the turbulence is exactly right. At \(\Delta/z_i = 0.05\), a 50 m LES cell, the grid carries over 90% and a subgrid model handling the last few percent is a reasonable thing to ask.

The band between is wide: roughly \(\Delta/z_i\) from 0.17 to 3, or **170 m to 3 km** over a 1 km convective boundary layer. At \(\Delta = z_i\) the split is 37/63 — the grid resolves a third of the energy and parameterises two thirds, and neither model was derived for that situation.

The uncomfortable part is the overlap with practice. A wind-farm nest, a fire-weather nest and an urban domain all want to run at a few hundred metres over a boundary layer of order a kilometre, which lands inside the band rather than beside it. The grey zone is not an exotic corner to be avoided; it is where the applications live, and scale-aware schemes exist because avoiding it is often not an option.

Two caveats. The von Kármán form is a model spectrum, so the exact bounds shift with stability — a stable boundary layer has its energy at smaller scales and the band moves down with \(z_i\). And a filter cutoff at \(\pi/\Delta\) is generous about what a real scheme resolves at the grid scale, where numerical dissipation is strongest, so the honest grey zone is somewhat wider than the one computed here.

## Connections

- [NWP](nwp.md) — nesting, the convective grey zone, and model configuration.
- [Boundary layer](boundary-layer.md) — \(z_i\), stability and surface-layer similarity.
- [Fire weather](fire-weather.md) — the other application that lives in this band.
- [Fluids › LES](../fluids/turbulence/les.md) — the subgrid assumption that fails here.
- [Aerospace › Actuator line](../aerospace/actuator-line.md) — the device model this coupling feeds.
- [Computing › Adaptive mesh refinement](../computing/amr.md) — spanning the scales in one solver instead.

## Sources

- Wyngaard, "Toward numerical modeling in the 'terra incognita'", *J. Atmospheric Sciences* **61** (2004) — the grey zone.
- Haupt, Kosović, … Jha, et al., "Lessons learned in coupling atmospheric models across scales for onshore and offshore wind energy", *Wind Energy Science* **8** (2023) 1251–1275.
- Muñoz-Esparza, Kosović, Mirocha & van Beeck, "Bridging the transition from mesoscale to microscale turbulence in numerical weather prediction models", *Boundary-Layer Meteorology* **153** (2014) — the cell perturbation method.
- Mirocha et al., on nested LES within mesoscale models and the fetch problem.
- Jha et al., "Actuator disk modeling of wind turbine in mesoscale–microscale coupling frameworks", AMS Annual Meeting (2023).
