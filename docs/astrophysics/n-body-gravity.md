---
title: N-body and gravitational dynamics
status: solid
tags: [pillar-1, pillar-3, astrophysics, discretization, conservation]
updated: 2026-09-26
---

# N-body and gravitational dynamics

<span class="status status-solid">solid</span>
<span class="pillar">pillar 1 &middot; Physical modeling and domain theory</span>

!!! abstract "In one minute"
    - Direct summation is \(O(N^2)\). Tree codes reach \(O(N\log N)\) and particle-mesh \(O(N\log N)\) with a much smaller constant — the choice depends on whether the problem is collisional.
    - **Softening** is mandatory for collisionless simulations: it removes the \(1/r^2\) singularity and suppresses spurious two-body scattering.
    - **Symplectic integrators** bound energy error over long integrations; ordinary Runge–Kutta drifts secularly. For orbital work this is decisive.
    - **Collisional and collisionless problems are different disciplines.** Star clusters need exact close encounters; cosmology needs a smooth potential.
    - Timestep criteria, not force accuracy, usually dominate the error budget.

## Key results

**The problem:**

<div class="result" markdown>

\[
\ddot{\mathbf{r}}_i = -G\sum_{j\ne i} m_j \frac{\mathbf{r}_i - \mathbf{r}_j}{\left(|\mathbf{r}_i-\mathbf{r}_j|^2 + \epsilon^2\right)^{3/2}}
\]

</div>

with \(\epsilon\) the softening length. Setting \(\epsilon = 0\) recovers exact Newtonian gravity and its singularity.

**Algorithms:**

| Method | Cost | Best for |
|---|---|---|
| Direct summation | \(O(N^2)\) | \(N \lesssim 10^5\), collisional systems, GPU-friendly |
| Barnes–Hut tree | \(O(N\log N)\) | clustered, collisionless |
| Particle-mesh (PM) | \(O(N_g\log N_g)\) | large-scale, periodic cosmology |
| P³M / TreePM | hybrid | cosmology needing small-scale resolution |
| Fast multipole | \(O(N)\) | very large \(N\), high accuracy demands |

Barnes–Hut opens a tree node when \(s/d > \theta\), with \(s\) the node size and \(d\) the distance. \(\theta\approx0.5\) is typical; larger is faster and less accurate.

**Two-body relaxation.** In a system of \(N\) particles, encounters cause the system to forget its initial conditions on

\[
t_{\text{relax}} \approx \frac{0.1\,N}{\ln N}\,t_{\text{cross}}
\]

A galaxy has \(N\sim10^{11}\), so \(t_{\text{relax}}\) far exceeds the Hubble time — it is **collisionless**. A simulation with \(N\sim10^6\) particles representing it has a relaxation time \(10^5\) times shorter, so numerical relaxation is a real and quantifiable artefact. Softening exists largely to suppress it.

**Symplectic integration.** Leapfrog (kick-drift-kick) is second order, time-reversible and symplectic:

\[
\mathbf{v}_{n+1/2} = \mathbf{v}_n + \tfrac{\Delta t}{2}\mathbf{a}_n,
\quad
\mathbf{r}_{n+1} = \mathbf{r}_n + \Delta t\,\mathbf{v}_{n+1/2},
\quad
\mathbf{v}_{n+1} = \mathbf{v}_{n+1/2} + \tfrac{\Delta t}{2}\mathbf{a}_{n+1}
\]

A symplectic integrator exactly conserves a *nearby* Hamiltonian, so energy error **oscillates with bounded amplitude** instead of drifting. RK4 is more accurate per step and loses energy monotonically — over \(10^6\) orbits that is the difference between a usable and a useless result.

The property is destroyed by adaptive individual timesteps, which is why long-term planetary integrations use fixed steps or carefully constructed reversible schemes.

**SPH.** Represents the fluid by particles with a smoothing kernel \(W(r,h)\):

\[
\rho_i = \sum_j m_j W(|\mathbf{r}_i-\mathbf{r}_j|, h_i)
\]

Naturally adaptive and conservative; classically poor at contact discontinuities and fluid instabilities, which modern formulations (pressure-entropy, Godunov-SPH, meshless finite mass) largely address.

## Mental model

Gravity is long-range and unshielded, so every particle feels every other — there is no cutoff radius to exploit, unlike molecular dynamics. Every fast algorithm is therefore a controlled approximation of *distant* contributions: a tree replaces a distant clump with its multipole expansion; a mesh replaces the far field with a Fourier-solved potential. What differs is which errors each is willing to make.

The collisional/collisionless distinction decides everything else. If close encounters matter physically, you must resolve them, softening is a bug, and you need regularisation. If they do not, close encounters are pure numerical noise and softening is how you suppress them.

## Numerics / practice

- **Choose \(\epsilon\) deliberately**, typically a fraction of the mean interparticle spacing. Too small reintroduces two-body scattering and tiny timesteps; too large erases real structure.
- **Use leapfrog or a higher-order symplectic scheme** for long integrations; reserve RK for short, dissipative problems.
- **Timestep criterion** from the local dynamical time, \(\Delta t \propto \sqrt{\epsilon/|\mathbf{a}|}\), and check energy conservation as a diagnostic.
- **Report the opening angle and softening** — results are not comparable without them.

??? warning "Failure modes"
    **Non-symplectic integrator for long orbital runs.** RK4 loses energy monotonically; a planetary system integrated over millions of orbits will spiral inwards for purely numerical reasons. The result looks smooth and plausible throughout. This is the failure most likely to be mistaken for physics.

    **Softening too small.** Close pairs produce enormous accelerations, collapsing the timestep and injecting spurious energy. Symptom: the run grinds to a halt, or a few particles are ejected at implausible velocities.

    **Softening too large.** Erases genuine structure — halo cores are flattened, and the result is a numerical artefact that looks like a physical core. This has caused real confusion in the cusp–core debate.

    **Numerical two-body relaxation in a collisionless run.** With \(N\) far below the physical particle count, relaxation proceeds \(10^4\)–\(10^6\) times faster than reality. Symptom: a halo or disc that puffs up over time for no physical reason. Convergence testing in \(N\), not just in \(\Delta t\) and \(\epsilon\), is what exposes it.

    **Adaptive timesteps breaking symplecticity.** Individual per-particle timesteps are almost mandatory for efficiency and destroy the bounded-energy property. Use block timesteps with reversible criteria, and monitor energy explicitly.

    **Energy conservation used as the only check.** A symplectic integrator conserves energy well even when the trajectory is wrong — bounded energy error is necessary, not sufficient. Check angular momentum and, where possible, a known analytic solution.

    <!-- Add your own here. -->

## Worked example

Symplectic versus Runge–Kutta over many orbits:

```python
import numpy as np

def energy(r, v):
    return 0.5*np.dot(v, v) - 1.0/np.linalg.norm(r)

def accel(r):
    return -r / np.linalg.norm(r)**3

r0, v0 = np.array([1.0, 0.0]), np.array([0.0, 1.0])   # circular orbit, E = -0.5
dt, n_steps = 0.01, 200_000                            # ~318 orbits

# leapfrog (symplectic)
r, v = r0.copy(), v0.copy()
emax = 0.0
for _ in range(n_steps):
    v = v + 0.5*dt*accel(r); r = r + dt*v; v = v + 0.5*dt*accel(r)
    emax = max(emax, abs(energy(r, v) - (-0.5)))
print(f"leapfrog : final E = {energy(r,v):+.8f}   max |dE| = {emax:.2e}")

# explicit Euler (non-symplectic), same cost class
r, v = r0.copy(), v0.copy()
for _ in range(n_steps):
    a = accel(r); r, v = r + dt*v, v + dt*a
print(f"euler    : final E = {energy(r,v):+.8f}   drift  = {energy(r,v)-(-0.5):+.2e}")
```

```
leapfrog : final E = -0.49999375   max |dE| = 1.25e-05
euler    : final E = -0.00013856   drift  = +4.99e-01
```

Leapfrog's energy error stays bounded at \(10^{-5}\) over 318 orbits. Euler's drifts by the entire binding energy — the orbit has effectively unbound itself, purely numerically.

## Connections

- [MHD](mhd.md) — when gas matters as well as gravity.
- [Aerospace › Space environment](../aerospace/space-environment.md) — the same integrators for orbit propagation.
- [Foundations › Numerical methods](../foundations/numerical-methods.md) — stability and order.
- [Computing › HPC](../computing/index.md) — these are among the largest simulations run.

## Sources

- Aarseth, *Gravitational N-Body Simulations*.
- Springel (2005), *The cosmological simulation code GADGET-2*.
- Hairer, Lubich & Wanner, *Geometric Numerical Integration* — symplectic theory.
