---
title: Reinforcement learning and control
status: working
tags: [pillar-9, machine-learning, optimization, extrapolation]
updated: 2026-10-24
---

# Reinforcement learning and control

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - RL solves sequential decision problems **without a model**, and that is the entire trade: you pay in samples for what a model would have given you free.
    - If you have a model and the dynamics are roughly linear, **LQR or MPC will beat RL** — faster, provably stable, and with no training.
    - The honest comparison is **sample complexity**. The worked example needs ~1,000 episodes to match what a Riccati solve gets exactly from the model, on a one-parameter problem.
    - **Model-based RL** is the middle ground and where engineering applications usually land: learn the dynamics, then plan.
    - The blocker in physical systems is rarely the algorithm. It is the **simulator gap**, safety during exploration, and the absence of a reward function anyone agrees on.

## Key results

### The problem, and the classical answer

A Markov decision process is states, actions, transitions and a reward; the goal is a policy maximising discounted return. Before reaching for RL, note what classical control already solves:

| Method | Needs | Gives | When it is the right answer |
|---|---|---|---|
| **LQR** | Linear model, quadratic cost | Optimal gain in closed form, stability guarantee | Linear-ish dynamics near an operating point |
| **LQG / Kalman + LQR** | Also a noise model | Optimal under Gaussian noise, with [state estimation](../foundations/estimation-filtering.md) | Partial observation |
| **MPC** | A model, a horizon, a solver | Constraint handling, re-planning each step | Constraints matter; model is decent |
| **Gain scheduling** | Models at several points | Covers an envelope | Smooth parameter variation |
| **RL** | A simulator or a real system, and patience | A policy, no guarantees | **No usable model**, or dynamics too complex to write down |

That table is the most useful thing on this page. RL's advantage is not performance, it is applicability where no model exists.

### The algorithm families

**Value-based** — learn \(Q(s,a)\), act greedily. Q-learning and DQN. Discrete actions; sample-efficient relative to vanilla policy gradient; brittle to the deadly triad below.

**Policy gradient** — parameterise the policy and ascend \(\nabla_\theta J\):

\[
\nabla_\theta J = \mathbb{E}\!\left[\nabla_\theta \log \pi_\theta(a|s)\,A(s,a)\right]
\]

REINFORCE is this with Monte Carlo returns and enormous variance. **Actor–critic** learns a value baseline to reduce it. **PPO** clips the policy update so a single batch cannot move the policy too far, which is most of why it is the default.

**Model-based** — learn \(p(s'|s,a)\), then plan or generate synthetic rollouts. Orders of magnitude more sample-efficient, and limited by model error compounding over the planning horizon. This is the family that matters for engineering, because a learned dynamics model is reusable and inspectable in a way a policy is not.

**Offline RL** — learn from a fixed dataset with no further interaction. The central difficulty is distribution shift: the learned policy wants to take actions the dataset never contains, and value estimates there are extrapolations.

### The deadly triad

Function approximation, bootstrapping and off-policy learning. Any two are fine; all three can diverge, and most practical instability traces to this combination. Target networks, replay buffers and conservative updates are all mitigations rather than fixes.

### Reward design

The reward is the specification, and it is almost always wrong on the first attempt.

- **Reward hacking.** The agent optimises what you wrote, not what you meant. A circuit-racing agent that collects respawning pickups instead of finishing is the canonical example and it is not an exotic failure.
- **Sparse rewards** give no gradient until something works, which may be never. Shaping helps and changes the optimal policy unless done as a potential-based term.
- **Multi-objective** problems get collapsed into a weighted sum, and the weights quietly encode a preference nobody stated.

### Sim-to-real

For a physical system, training happens in simulation and deployment does not. The gap is bridged with **domain randomisation** — randomise masses, delays, friction, sensor noise during training so the policy is robust to a distribution that contains reality — plus system identification to centre that distribution, and often a residual policy on top of a classical controller so the baseline behaviour is never worse than the controller alone.

## Mental model

RL is optimisation where you cannot differentiate the objective, so you estimate the gradient by trying things. Everything expensive about it follows: the estimator is noisy, the noise needs averaging, and averaging needs samples. Model-based methods are cheaper precisely because a model restores differentiability — which is also why a [differentiable simulator](../sciml/hybrid-coupling.md) changes the economics completely.

The second idea is that classical control is not a weaker version of RL. It is the exact solution to the subset of problems where a model exists, and that subset includes most engineering systems. The useful question is never "RL or control" but "do I have a model, and is it good enough to plan with."

## Numerics / practice

- **Establish the classical baseline first.** LQR, MPC or a tuned PID. If RL does not beat it, that is the result.
- **Report sample count alongside performance.** A policy that beats MPC after \(10^8\) environment steps has not beaten MPC for most purposes.
- **Fix and report seeds, and run several.** RL results vary enormously across seeds, and single-seed comparisons are not evidence.
- **Normalise observations and rewards.** More RL instability comes from unnormalised inputs than from algorithm choice.
- **Log the entropy.** Premature entropy collapse means the policy stopped exploring; it is the earliest reliable warning of a run going nowhere.
- **Evaluate with exploration off**, separately from training returns.

??? warning "Failure modes"
    **RL used where a model exists.** If the dynamics are writable and roughly linear near the operating point, LQR gives the optimal policy in closed form with a stability proof. Reaching for RL throws that away and buys sampling noise.

    **Sample cost omitted from the comparison.** The worked example below needs about a thousand episodes to match what a Riccati solve obtains with none — on a scalar system with one policy parameter. Real systems have thousands of parameters and the cost grows accordingly.

    **Training return read as performance.** Training returns include exploration noise and, in off-policy methods, come from a replay distribution that is not the current policy's. Evaluate separately, deterministically.

    **Single-seed results compared.** Variance across seeds routinely exceeds the difference between algorithms. A comparison without several seeds and a spread is not a comparison.

    **Reward shaped without checking the optimum moved.** Arbitrary shaping changes which policy is optimal. Potential-based shaping provably does not; most hand-tuned shaping is not potential-based.

    **Simulator gap discovered at deployment.** A policy trained on an idealised model exploits exactly the idealisations — frictionless contacts, zero actuator delay, perfect sensors. Domain randomisation before deployment, not after.

    **Exploration run on hardware without a safety layer.** Early RL policies take arbitrary actions by construction. On a physical system that is a hazard, and the standard answer is a classical controller with RL as a bounded residual.

    **Offline RL evaluated on the behaviour policy's distribution.** The learned policy diverges from the data; its value estimates in that region are extrapolation. Offline evaluation is its own hard problem, not a free side effect.

    <!-- Add your own here. -->

## Worked example

What model-free learning costs, on the friendliest problem that exists — scalar linear dynamics, quadratic cost, a one-parameter policy:

```python
import numpy as np

# Scalar linear system  x' = a x + b u + noise,  cost  sum q x^2 + r u^2.
# LQR solves this in closed form FROM THE MODEL. Policy search finds the same
# answer FROM SAMPLES, and the comparison is about how many samples that takes.
a, b, q, r, T = 0.9, 1.0, 1.0, 1.0, 40

P = 1.0                                        # discrete algebraic Riccati, by iteration
for _ in range(2000):
    P = q + a**2*P - (a**2*P**2*b**2)/(r + b**2*P)
K_opt = (a*b*P)/(r + b**2*P)

def cost(K, n, seed):
    """Mean quadratic cost of the linear policy u = -Kx. Diverging policies are capped."""
    rng = np.random.default_rng(seed); tot = 0.0
    for _ in range(n):
        x, c = rng.normal(0, 1), 0.0
        for _ in range(T):
            u = -K*x
            c += q*x*x + r*u*u
            x = a*x + b*u + rng.normal(0, 0.1)
            if abs(x) > 1e3: c = 1e6; break
        tot += min(c, 1e6)
    return tot/n

J_opt = cost(K_opt, 2000, 99)
print(f"LQR, model known : K = {K_opt:.4f}   cost = {J_opt:.3f}   episodes used = 0")
print("\npolicy search from samples only (two-sided finite differences, common seeds):")
print(f"{'episodes':>10}{'K':>9}{'cost':>9}{'excess over LQR':>18}")

rng = np.random.default_rng(1)
K, used, sigma, lr = 0.0, 0, 0.1, 0.002
report = [200, 1000, 5000, 20000, 60000]
for it in range(1, 40001):
    eps = rng.normal(0, sigma)
    s = 10_000 + it                                   # common random numbers across +/-
    g = (cost(K+eps, 2, s) - cost(K-eps, 2, s))/(2*eps)   # divide by the ACTUAL step
    K -= lr*np.clip(g, -20, 20)                       # clipped: the estimator is very noisy
    used += 4
    if report and used >= report[0]:
        J = cost(K, 2000, 99)
        print(f"{used:10d}{K:9.4f}{J:9.3f}{100*(J/J_opt-1):17.1f}%")
        report.pop(0)
    if not report: break
```

```
LQR, model known : K = 0.5377   cost = 2.132   episodes used = 0

policy search from samples only (two-sided finite differences, common seeds):
  episodes        K     cost   excess over LQR
       200   0.4379    2.174              2.0%
      1000   0.5377    2.132              0.0%
      5000   0.5390    2.132              0.0%
     20000   0.5412    2.132              0.0%
     60000   0.5365    2.132             -0.0%
```

LQR obtains the optimal gain \(K = 0.5377\) from the Riccati equation using **zero** samples. It needs the model, and given the model the answer is exact.

Policy search reaches 2% of optimal after 200 episodes and matches LQR to four digits by about 1,000. That is a good result for RL and it is the point: a thousand episodes to recover what algebra gives immediately, on a problem with **one** parameter, linear dynamics, quadratic cost and full observation. Every one of those conditions is a best case.

The scaling is the part to carry away. Gradient estimation by sampling needs roughly enough samples to resolve the gradient against the return's variance, so the cost grows with the number of policy parameters and with the horizon. A neural policy with \(10^4\) parameters on a problem with contact, delay and partial observation is many orders of magnitude up from this, which is why published results quote \(10^6\)–\(10^9\) environment steps and why almost all of them run in simulation.

Two honest caveats. This example assumes the model is known *exactly* for the LQR side — with an uncertain model the comparison narrows, and robust or adaptive control is the fairer baseline. And the finite-difference estimator here is deliberately simple; PPO and friends are considerably more sample-efficient than this, though not by the orders of magnitude that would change the conclusion.

## Connections

- [Classical ML](classical.md) · [Training craft](training-craft.md) — the optimisation machinery underneath.
- [Foundations › Estimation and filtering](../foundations/estimation-filtering.md) — state estimation, the other half of LQG.
- [Foundations › Optimization and adjoints](../foundations/optimization-adjoints.md) — gradients when you *can* differentiate.
- [SciML › Hybrid coupling](../sciml/hybrid-coupling.md) — differentiable simulators, which change the trade entirely.
- [Fluids › FSI and 6-DOF](../fluids/fsi-6dof.md) — the plant models a controller acts on.
- [DL › Architectures](../dl/architectures.md) — policy and value network design.

## Sources

- Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. — the standard text.
- Bertsekas, *Reinforcement Learning and Optimal Control* — the control-theoretic framing used on this page.
- Schulman et al., "Proximal policy optimization algorithms", arXiv (2017).
- Recht, "A tour of reinforcement learning: the view from continuous control", *Annual Review of Control, Robotics, and Autonomous Systems* **2** (2019) — the LQR-baseline argument.
- Henderson et al., "Deep reinforcement learning that matters", AAAI (2018) — on seeds and reproducibility.
- Levine et al., "Offline reinforcement learning: tutorial, review, and perspectives on open problems", arXiv (2020).
