---
title: Quantum computing
status: seed
tags: [pillar-6, computing, performance, scaling]
updated: 2026-10-24
---

# Quantum computing

<span class="status status-seed">seed</span>
<span class="pillar">pillar 6 &middot; HPC and parallelism</span>

!!! abstract "In one minute"
    - A quantum computer is **not a parallel classical computer**. Superposition explores all states; measurement returns one. The art is arranging **interference** so the wrong answers cancel.
    - The classical simulation cost is \(2^n\) amplitudes, which is why ~50 qubits is the edge of brute-force simulation — and why that number says nothing about useful computation.
    - **Noise is the binding constraint**, not qubit count. Gate error rate sets circuit depth directly, and today's depths are short.
    - The speedups are **specific, not general**: quadratic for unstructured search, superpolynomial for factoring and for simulating quantum systems. Most workloads get nothing.
    - For computational physics the credible near-term target is **simulating quantum systems** — chemistry, materials — not accelerating classical PDE solvers.

## Key results

### What a qubit is, and what it is not

A qubit's state is \(\alpha|0\rangle + \beta|1\rangle\) with \(|\alpha|^2+|\beta|^2=1\). An \(n\)-qubit register has \(2^n\) complex amplitudes, evolving under unitary operations, until measurement collapses it to one basis state with probability \(|\text{amplitude}|^2\).

The common description — "it tries all answers at once" — is half right and misleading. All \(2^n\) amplitudes do evolve together. You can read out only one sample. An algorithm is useful only if it arranges destructive interference on the wrong answers before measurement, and **that is the hard part**; it is why useful quantum algorithms are rare rather than ubiquitous.

**Entanglement** is what makes the state space genuinely large: a product state of \(n\) qubits needs \(2n\) numbers, while a general entangled state needs \(2^n\). Classical simulators exploit exactly this — tensor-network methods simulate lightly entangled circuits of hundreds of qubits, so "\(n\) qubits" alone is not a difficulty measure.

### The algorithms that matter

| Algorithm | Speedup | Status |
|---|---|---|
| **Shor** (factoring, discrete log) | Superpolynomial | Breaks RSA/ECC; needs full error correction |
| **Grover** (unstructured search) | Quadratic, \(\sqrt{N}\) | Provably optimal; quadratic rarely beats constant factors |
| **Quantum simulation** (Hamiltonian dynamics) | Exponential for some systems | **The natural application** — Feynman's original argument |
| **HHL** (linear systems) | Exponential, heavily caveated | Needs state preparation, sparsity, low condition number, and returns a *state* not a vector |
| **VQE / QAOA** (variational) | None proven | NISQ-era; interesting, no guarantee |

The caveats on HHL deserve emphasis because linear solves are what a computational physicist wants. It does not return \(x\); it returns a quantum state encoding \(x\), from which you can extract scalar functionals. Loading \(b\) can cost as much as the solve. For a general dense linear system from a discretised PDE, it is not a drop-in replacement for [a classical solver](../foundations/linear-solvers.md) and current consensus is that it will not be.

### Noise, and why it dominates

Every gate has an error. With \(G\) two-qubit gates at error rate \(\varepsilon\), circuit fidelity falls roughly as \((1-\varepsilon)^G\). Decoherence adds a wall-clock limit through \(T_1\) and \(T_2\). The worked example turns this into usable depths and the numbers are sobering.

**Error correction** is the answer, and it is expensive. The surface code encodes one logical qubit in many physical ones, with the ratio growing as the physical error rate approaches the threshold (~1% for the surface code). Representative estimates put factoring RSA-2048 at thousands of logical qubits and millions of physical ones. The gap to current hardware is the central fact of the field.

**NISQ** — noisy intermediate-scale quantum — names the present era: hundreds to thousands of noisy physical qubits, no error correction, shallow circuits. Variational algorithms are designed for it, and whether they offer any advantage remains open.

### Hardware

| Platform | Strength | Weakness |
|---|---|---|
| **Superconducting** | Fast gates (ns), lithographic scaling | Short coherence, millikelvin cryogenics |
| **Trapped ion** | Long coherence, all-to-all coupling, high fidelity | Slow gates (μs), harder to scale |
| **Neutral atom** | Large arrays, reconfigurable | Younger; gate fidelity improving |
| **Photonic** | Room temperature, networking | Probabilistic gates, loss |
| **Topological** | Error resistance in principle | Not yet demonstrated |

### What this means for computational physics

Honestly: little, in the near term, for classical PDE work. The credible targets are **simulating quantum systems** — electronic structure, strongly correlated materials, reaction dynamics — where the classical cost is genuinely exponential and the mapping to a quantum computer is natural.

The secondary and more immediate consequence is **post-quantum cryptography**: Shor breaks RSA and elliptic-curve cryptography, "harvest now, decrypt later" makes the threat present rather than future, and NIST's post-quantum standards exist for this reason. That is a real near-term engineering task, and it has nothing to do with owning a quantum computer.

## Mental model

A quantum computer is a machine for arranging interference. The state space is exponentially large, you can look at it exactly once per run, and an algorithm is a scheme for making the amplitudes you want survive and the rest cancel. Problems that admit such a scheme are few, and they are all problems with heavy algebraic structure — periodicity for Shor, a Hamiltonian for simulation.

The second idea is that **the resource that is scarce is depth, not width**. Qubit counts make headlines and gate fidelity sets what can be computed, because fidelity times depth is the budget. A machine with ten thousand noisy qubits and a hundred-gate coherent depth cannot run an algorithm that needs a million gates, however many qubits it has.

## Numerics / practice

- **Count two-qubit gates, not qubits**, when estimating feasibility. That is the error budget.
- **Check whether the classical baseline is actually exponential.** Tensor networks simulate low-entanglement circuits efficiently, and several "quantum advantage" claims have been narrowed or overturned by better classical simulation.
- **Account for state preparation and readout.** An algorithm with an exponential speedup in its core can be dominated by loading the input or by the shot count needed to estimate an expectation value.
- **Expect sampling cost.** Variational methods estimate expectations from measurements, and the shot count scales as \(1/\epsilon^2\) in the target precision.
- **Treat the resource estimate as the result.** For any proposed application the useful output is logical qubits, gate depth and physical-qubit overhead — not a demonstration on four qubits.

??? warning "Failure modes"
    **"Tries all answers in parallel."** All amplitudes evolve; one sample is returned. Without engineered interference a quantum computer is an expensive random number generator, and this misconception is what makes people expect general speedups.

    **Qubit count read as capability.** Depth, connectivity and gate fidelity matter at least as much. A high-fidelity 50-qubit machine can outperform a noisy 1,000-qubit one on anything requiring depth.

    **Quadratic speedup assumed to be useful.** Grover is \(\sqrt{N}\), and quantum gates are many orders of magnitude slower than classical ones. The crossover for realistic constants sits at problem sizes that are often beyond reach, so quadratic advantage is not automatically an advantage.

    **HHL treated as a linear solver.** It returns a state, not a solution vector; it needs sparsity and good conditioning; and reading out the answer destroys the speedup. Dequantisation results have removed the exponential advantage in several settings.

    **NISQ demonstrations extrapolated.** A variational result on a handful of qubits says nothing about scaling. Barren plateaus — exponentially vanishing gradients with system size — are a known obstruction specific to the scaling direction.

    **Classical baseline not taken seriously.** The honest comparison is against the best classical algorithm on the best classical hardware, and that baseline keeps improving in response.

    **Post-quantum migration deferred.** Encrypted traffic captured today can be decrypted once a cryptographically relevant machine exists. Data with a long confidentiality lifetime is already exposed, which makes this a present task.

    <!-- Add your own here. -->

## Worked example

The three numbers that bound what is currently possible:

```python
import numpy as np

# 1. Classical simulation of n qubits needs a 2^n complex amplitude vector.
print("classical memory to hold the state of n qubits (complex128):")
for n in (10, 20, 30, 40, 50, 60):
    b = 16*2**n
    u = ("B","KB","MB","GB","TB","PB","EB")
    i = 0
    while b >= 1024 and i < 6: b /= 1024; i += 1
    print(f"   n = {n:3d} qubits -> 2^{n} amplitudes = {b:8.1f} {u[i]}")

# 2. Noise is the real limit: fidelity ~ (1-eps)^G for G two-qubit gates at error rate eps.
print("\ncircuit depth before fidelity falls to 1/2, at two-qubit error rate eps:")
print(f"{'eps':>10}{'gates':>12}{'gates/qubit at n=100':>24}")
for eps in (1e-2, 3e-3, 1e-3, 1e-4, 1e-5, 1e-6):
    G = np.log(0.5)/np.log(1-eps)
    print(f"{eps:10.0e}{G:12,.0f}{G/100:24,.0f}")

# 3. What the algorithms actually promise.
print("\nasymptotic speedups, as operation counts:")
N = 10**12
print(f"   unstructured search over N = 1e12:")
print(f"      classical  O(N)        = {N:,.0f}")
print(f"      Grover     O(sqrt(N))  = {int(np.sqrt(N)):,.0f}   ({N/np.sqrt(N):,.0f}x fewer)")
print(f"   factoring a 2048-bit integer:")
b = 2048
gnfs = np.exp(1.923*(b*np.log(2))**(1/3)*(np.log(b*np.log(2)))**(2/3))
print(f"      GNFS   ~ exp(1.9 (ln N)^1/3 (ln ln N)^2/3) = 1e{np.log10(gnfs):.0f}")
print(f"      Shor   ~ O(b^3)                            = 1e{np.log10(b**3):.1f}")

print("\nbut Shor on 2048 bits needs error correction, and that is the real cost:")
phys_per_logical = 1000            # representative surface-code overhead at eps ~ 1e-3
logical = 4000                     # rough logical-qubit count quoted for RSA-2048
print(f"   ~{logical:,} logical qubits x ~{phys_per_logical:,} physical each "
      f"= ~{logical*phys_per_logical:,} physical qubits")
print(f"   today's largest devices are O(1e2-1e3) physical qubits, uncorrected.")
```

```
classical memory to hold the state of n qubits (complex128):
   n =  10 qubits -> 2^10 amplitudes =     16.0 KB
   n =  20 qubits -> 2^20 amplitudes =     16.0 MB
   n =  30 qubits -> 2^30 amplitudes =     16.0 GB
   n =  40 qubits -> 2^40 amplitudes =     16.0 TB
   n =  50 qubits -> 2^50 amplitudes =     16.0 PB
   n =  60 qubits -> 2^60 amplitudes =     16.0 EB

circuit depth before fidelity falls to 1/2, at two-qubit error rate eps:
       eps       gates    gates/qubit at n=100
     1e-02          69                       1
     3e-03         231                       2
     1e-03         693                       7
     1e-04       6,931                      69
     1e-05      69,314                     693
     1e-06     693,147                   6,931

asymptotic speedups, as operation counts:
   unstructured search over N = 1e12:
      classical  O(N)        = 1,000,000,000,000
      Grover     O(sqrt(N))  = 1,000,000   (1,000,000x fewer)
   factoring a 2048-bit integer:
      GNFS   ~ exp(1.9 (ln N)^1/3 (ln ln N)^2/3) = 1e35
      Shor   ~ O(b^3)                            = 1e9.9

but Shor on 2048 bits needs error correction, and that is the real cost:
   ~4,000 logical qubits x ~1,000 physical each = ~4,000,000 physical qubits
   today's largest devices are O(1e2-1e3) physical qubits, uncorrected.
```

The first block is why quantum computing is interesting at all. Holding an \(n\)-qubit state classically needs \(2^n\) amplitudes: 16 GB at 30 qubits, 16 PB at 50. Brute-force classical simulation runs out somewhere around 50 qubits, and that is the origin of the number. It is a statement about *simulating* a quantum computer, not about any useful computation.

The second block is the one that governs practice, and it is the reason headline qubit counts mislead. At a two-qubit error rate of \(10^{-3}\) — around the best demonstrated today — a circuit has roughly **693 gates** before fidelity reaches a half. Spread over 100 qubits that is seven gates per qubit. Error rates have to reach \(10^{-6}\) before circuits of a million gates are coherent, and no algorithm of interest is shorter than that.

The third block puts the algorithmic promise against the engineering reality. Shor's \(O(b^3)\) against the number field sieve's sub-exponential growth is a genuine superpolynomial gap — \(10^{10}\) operations against \(10^{35}\) for a 2048-bit key. But running it needs error correction, and the representative overhead of a thousand physical qubits per logical one puts RSA-2048 at millions of physical qubits against the hundreds available now.

That is the state of the field in three numbers: the physics is real, the algorithmic advantage is real and narrow, and the gap between them is error correction. The right posture for a computational physicist is to track resource estimates rather than qubit counts, and to treat post-quantum cryptography as the one consequence that is already actionable.

## Connections

- [HPC and parallelism](hpc.md) — the classical baseline any claim must beat.
- [GPU and CUDA](gpu-cuda.md) — where the accelerator analogy holds and where it breaks.
- [Foundations › Linear solvers](../foundations/linear-solvers.md) — what HHL would have to displace.
- [Foundations › Math methods](../foundations/math-methods.md) — the linear algebra underneath.
- [Thermal › Thermodynamics](../thermal/thermodynamics.md) — statistical mechanics, the natural simulation target.

## Sources

- Nielsen & Chuang, *Quantum Computation and Quantum Information* — the standard text.
- Preskill, "Quantum computing in the NISQ era and beyond", *Quantum* **2** (2018).
- Gidney & Ekerå, "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits", *Quantum* **5** (2021) — a careful resource estimate.
- Aaronson, "Read the fine print", *Nature Physics* **11** (2015) — on the caveats to HHL and quantum machine learning claims.
- Fowler et al., "Surface codes: towards practical large-scale quantum computation", *Phys. Rev. A* **86** (2012).
- NIST Post-Quantum Cryptography standards.
