---
title: Estimation and filtering
status: working
tags: [pillar-8, foundations, statistics, uncertainty, validation]
updated: 2026-10-24
---

# Estimation and filtering

<span class="status status-working">working</span>
<span class="pillar">pillar 8 &middot; Data management, statistics and UQ</span>

!!! abstract "In one minute"
    - Filtering is **recursive Bayesian inference on a time series**: predict with a model, correct with a measurement, repeat, carrying a covariance throughout.
    - The Kalman filter is the **exact** solution when the model is linear and the noise Gaussian, and the best linear estimator when it is not.
    - The covariance is the point. An estimate without one is a number; an estimate with one can be **fused** with other sensors by relative confidence.
    - **Observability** decides what can be estimated at all. A bias that no measurement constrains will not be recovered no matter how good the filter.
    - The nonlinear extensions — EKF, UKF, particle filter — differ in **how they propagate uncertainty through a nonlinearity**, and that is the only thing that distinguishes them.

## Key results

### The recursion

<div class="result" markdown>

**Predict** \(\quad \hat{x}^- = F\hat{x} + Bu, \qquad P^- = FPF^{\mathsf T} + Q\)

**Correct** \(\quad K = P^- H^{\mathsf T}(HP^-H^{\mathsf T} + R)^{-1}\)
\(\qquad\qquad \hat{x} = \hat{x}^- + K(z - H\hat{x}^-), \qquad P = (I - KH)P^-\)

</div>

The gain \(K\) is a confidence ratio. Where the prediction is uncertain and the measurement sharp, \(K \to H^{-1}\) and the filter follows the data; where the reverse holds, \(K \to 0\) and the filter trusts its model. Everything the filter does is in that one expression.

\(Q\) is the **process noise** — how much you distrust the model per step. \(R\) is the **measurement noise**. Their ratio is the filter's only real tuning knob, and it is a statement about relative trust rather than about either quantity separately.

### Why fusion works

Two independent estimates of the same quantity combine with inverse-variance weighting:

\[
\frac{1}{\sigma^2} = \frac{1}{\sigma_1^2} + \frac{1}{\sigma_2^2}
\]

The fused variance is smaller than either input. That is the entire argument for sensor fusion, and the Kalman filter is this statement extended to vectors, to correlated errors, and across time.

The classic pairing is **complementary**: a sensor that is accurate at low frequency and one accurate at high frequency. GPS is absolute but noisy and slow; an IMU is smooth and fast but integrates its own bias into unbounded drift. Fused, each covers the other's weakness — and as the worked example shows, most of the gain comes from one specific mechanism.

### Observability

A state can only be estimated if the measurements constrain it. For a linear system the test is the rank of the observability matrix

\[
\mathcal{O} = \begin{bmatrix} H \\ HF \\ HF^2 \\ \vdots \\ HF^{n-1}\end{bmatrix}
\]

and full rank means every state is in principle recoverable. Practically more useful: an **unobservable state will show a covariance that does not decrease**, which is a diagnostic you can read off a running filter without any algebra.

This is why accelerometer bias is estimable when GPS is present and not otherwise — the bias enters position only through a double integration, so an absolute position measurement over a long enough baseline pins it down, and nothing else does.

### The nonlinear family

| Filter | Handles nonlinearity by | Cost | Breaks when |
|---|---|---|---|
| **EKF** | Linearising about the current estimate | Cheap | Strong nonlinearity, or a poor initial guess |
| **UKF** | Propagating sigma points through the true nonlinearity | \(2n+1\) evaluations | Very high dimension |
| **Particle filter** | Sampling the full posterior | Many evaluations | Dimension above ~10; particle depletion |
| **EnKF** | Propagating an ensemble, Gaussian update | Ensemble size | Non-Gaussian posteriors; needs inflation and localisation |

The ordering is by how much of the distribution is kept. An EKF keeps a mean and a covariance and assumes the nonlinearity is mild enough for a Jacobian; a particle filter keeps the shape of the distribution and pays for it. **EnKF** is the one that scales to geophysical state sizes and is the basis of ensemble [data assimilation](../meteorology/data-assimilation.md).

### Smoothing versus filtering

A **filter** estimates the state at time \(t\) using data up to \(t\) — the only option in real time. A **smoother** uses all the data, including later measurements, and is strictly better. If the analysis is offline, use a smoother (RTS for the linear case); using a filter offline throws away information for no reason, and it is a common habit.

## Mental model

A filter is a running argument between a model and a sensor, refereed by their covariances. The model says where the state should have gone; the sensor says where it appears to be; the gain decides who to believe, in proportion to who has been more reliable.

That framing makes the failure modes obvious. If you tell the filter the model is perfect, it will stop listening to the sensors and diverge confidently. If you tell it the sensors are perfect, it becomes a noisy pass-through. And if you ask it for a quantity nothing measures, it will return whatever it was initialised with, with a covariance that quietly never shrinks.

## Numerics / practice

- **Use the Joseph form** \(P = (I-KH)P(I-KH)^{\mathsf T} + KRK^{\mathsf T}\) when conditioning is poor; it preserves symmetry and positive-definiteness where the short form does not.
- **Check \(P\) stays symmetric positive-definite.** Symmetrise with \((P+P^{\mathsf T})/2\) each step; it is free and it catches a lot.
- **Process noise for an acceleration-driven model is a correlated block**, not a diagonal: position and velocity noise come from the same acceleration and the cross terms matter.
- **Validate with the innovation sequence.** \(z - H\hat{x}^-\) should be zero-mean and white, with covariance \(HP^-H^{\mathsf T} + R\). The **normalised innovation squared** should average the measurement dimension; consistently above means the filter is overconfident. This is the main diagnostic and it needs no ground truth.
- **Initialise \(P\) generously.** Too small an initial covariance makes the filter reject early measurements that would have corrected it.
- **Watch for covariances that do not decrease** — the practical observability test.

??? warning "Failure modes"
    **Unobservable state estimated anyway.** The filter returns the initial guess with a covariance that never shrinks, and the number looks like an estimate. Check the covariance trajectory, not the value.

    **Process noise set too small.** The filter becomes overconfident, the gain collapses, and it stops responding to measurements — *filter divergence*, where the estimate drifts away while the reported covariance says everything is fine. The reported uncertainty is the thing that is wrong, which is what makes it dangerous.

    **\(Q\) and \(R\) tuned to minimise error against truth on one dataset.** They are noise statistics, not free parameters. Tuned against a single truth trace they encode that trace, and the filter is then miscalibrated on anything else. Tune against innovation consistency instead, which needs no truth.

    **Diagonal \(Q\) for a kinematic model.** Position, velocity and acceleration noise driven by one physical acceleration are correlated. A diagonal \(Q\) is a different, wrong model — usually survivable, occasionally not.

    **EKF used through a strong nonlinearity.** Linearising about a poor estimate gives a wrong Jacobian, a wrong gain, and an update that moves the estimate further from truth, which worsens the next linearisation. Divergence is rapid once it starts.

    **Correlated measurement errors treated as independent.** Two sensors sharing a clock, a mounting or a calibration do not give independent information, and assuming they do makes the fused covariance too small — overconfidence by construction.

    **Filter used where a smoother was available.** Offline analysis with a causal filter discards all the information in later measurements.

    **Outliers fed straight in.** One bad fix with a small assumed \(R\) moves the estimate a long way and corrupts the covariance with it. Gate on the normalised innovation before updating.

    <!-- Add your own here. -->

## Worked example

Fusing a 1 Hz GPS with a 100 Hz accelerometer that has an unknown constant bias:

```python
import numpy as np

# Fuse absolute position (GPS: 3 m, 1 Hz) with a biased accelerometer (IMU: 0.05 m/s^2,
# 100 Hz). State x = [position, velocity, accelerometer bias].
dt, N, GPS_EVERY = 0.01, 6000, 100
SIG_GPS, SIG_IMU, BIAS = 3.0, 0.05, 0.02          # m, m/s^2, m/s^2 (unknown constant)

F = np.array([[1, dt, -0.5*dt**2], [0, 1, -dt], [0, 0, 1]])   # bias subtracts from accel
B = np.array([0.5*dt**2, dt, 0.0])
H = np.array([[1.0, 0.0, 0.0]])
# process noise for an acceleration-driven model is a CORRELATED block, not diagonal
Q3 = SIG_IMU**2*np.array([[dt**4/4, dt**3/2, 0], [dt**3/2, dt**2, 0], [0, 0, 0]]) \
     + np.diag([0, 0, 1e-10])

def run(estimate_bias=True, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(N)*dt
    a_true = 0.5*np.sin(0.3*t)
    v = np.cumsum(a_true)*dt
    p = np.cumsum(v)*dt                                   # truth
    a_meas = a_true + BIAS + rng.normal(0, SIG_IMU, N)    # IMU: biased and noisy
    gps_noise = rng.normal(0, SIG_GPS, N)

    n = 3 if estimate_bias else 2
    Fm, Bm, Hm, Qm = F[:n, :n], B[:n], H[:, :n], Q3[:n, :n]
    x = np.zeros(n); P = np.diag([10.0, 1.0, 0.1][:n])
    est, held, last = [], [], 0.0
    for k in range(N):
        x = Fm @ x + Bm*a_meas[k]                         # IMU drives the prediction
        P = Fm @ P @ Fm.T + Qm
        if k % GPS_EVERY == 0:                            # GPS corrects, once a second
            z = p[k] + gps_noise[k]; last = z
            K = P @ Hm.T / (Hm @ P @ Hm.T + SIG_GPS**2)
            x = x + (K*(z - Hm @ x)).ravel()
            P = (np.eye(n) - K @ Hm) @ P
        est.append(x[0]); held.append(last)
    rmse = lambda s: np.sqrt(np.mean((np.array(s) - p)**2))
    return rmse(est), rmse(held), (x[2] if estimate_bias else None)

mean = lambda f: np.mean([f(s) for s in range(20)])
print("position RMSE over a 60 s run, averaged over 20 noise realisations")
print(f"   GPS alone, held between fixes : {mean(lambda s: run(seed=s)[1]):6.3f} m")
print(f"   IMU + GPS, bias estimated     : {mean(lambda s: run(seed=s)[0]):6.3f} m")
print(f"   IMU + GPS, bias NOT in state  : "
      f"{mean(lambda s: run(estimate_bias=False, seed=s)[0]):6.3f} m")

b = [run(seed=s)[2] for s in range(20)]
print(f"\naccelerometer bias: true {BIAS:.4f}, estimated {np.mean(b):.4f} "
      f"+/- {np.std(b):.4f} m/s^2")
print("the bias is observable only because GPS anchors the position it would otherwise")
print("corrupt -- integrate the IMU alone and a constant bias grows as 0.5*b*t^2:")
for T in (10, 60, 300):
    print(f"   after {T:3d} s of pure dead reckoning: {0.5*BIAS*T**2:8.1f} m of drift")
```

```
position RMSE over a 60 s run, averaged over 20 noise realisations
   GPS alone, held between fixes :  3.259 m
   IMU + GPS, bias estimated     :  1.693 m
   IMU + GPS, bias NOT in state  :  3.081 m

accelerometer bias: true 0.0200, estimated 0.0201 +/- 0.0034 m/s^2
the bias is observable only because GPS anchors the position it would otherwise
corrupt -- integrate the IMU alone and a constant bias grows as 0.5*b*t^2:
   after  10 s of pure dead reckoning:      1.0 m of drift
   after  60 s of pure dead reckoning:     36.0 m of drift
   after 300 s of pure dead reckoning:    900.0 m of drift
```

The headline comparison is the three-line block, and the interesting part is the third line. Fusing IMU with GPS improves position RMSE from 3.26 m to 1.69 m, a factor of 1.9 — but only when the accelerometer bias is **in the state vector**. Drop it, and the fused estimate is 3.08 m: essentially no better than GPS alone, despite the filter having all the same data.

That is the real lesson about sensor fusion. The gain did not come from averaging two sensors; it came from using one sensor to **identify and remove a systematic error in the other**. A bias of 0.02 m/s² sounds negligible and integrates into 36 m of drift in a minute and 900 m in five, because the error grows as \(\tfrac{1}{2}bt^2\). The IMU is only useful between fixes once that term is estimated away, and the filter recovers it to 0.0201 against a true 0.0200.

It is also a clean illustration of observability. The bias is never measured, and no instrument in the system reports it. It becomes estimable purely because it enters position through a double integration and GPS anchors position over a long baseline — so the filter can attribute a growing position discrepancy to a constant acceleration error. Remove GPS and the bias is unobservable; remove the bias state and GPS has nothing to correct.

One honest limitation: this example does not demonstrate \(Q\)/\(R\) tuning, which deserves its own treatment. The relationship between assumed noise statistics and achieved error is not monotone in a system where one sensor is much better than the other, and a table purporting to show "correctly tuned beats mis-tuned" would be a simplification of something subtler. Tune on innovation consistency, as above, rather than on a sweep.

## Connections

- [Probability and statistics](probability-statistics.md) — the Bayesian machinery underneath.
- [Uncertainty quantification](uncertainty-quantification.md) — covariance propagation in the static case.
- [Meteorology › Data assimilation](../meteorology/data-assimilation.md) — EnKF and 4D-Var, this at geophysical scale.
- [Fluids › FSI and 6-DOF](../fluids/fsi-6dof.md) — the rigid-body models whose states get estimated.
- [CV › Classical computer vision](../cv/classical-cv.md) — visual odometry and tracking, the other common fusion input.
- [Optimization and adjoints](optimization-adjoints.md) — the variational view of the same problem.

## Sources

- Simon, *Optimal State Estimation: Kalman, H∞, and Nonlinear Approaches*.
- Bar-Shalom, Li & Kirubarajan, *Estimation with Applications to Tracking and Navigation*.
- Särkkä, *Bayesian Filtering and Smoothing* — the unifying probabilistic treatment.
- Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*.
- Evensen, *Data Assimilation: The Ensemble Kalman Filter*.
