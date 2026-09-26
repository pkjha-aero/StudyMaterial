---
title: Skills Map
status: working
tags: [skills-map]
---

# Skills Map

<span class="status status-working">working</span>

Ten competency pillars for a computational physicist working across aerospace,
meteorology and astrophysics. Every note page on this site declares the pillar it serves,
so this page doubles as the site's table of contents and as an honest account of where the
gaps are.

The pillars are ordered roughly from physics to practice. Nobody is uniformly strong
across all ten, and the useful question is not "do I know this" but "how fast can I get
back to working competence."

## The pillars

### 1. Physical modeling and domain theory

Deriving governing equations from conservation laws; nondimensionalization and scaling;
identifying which regime you are in and which terms you are entitled to drop; closure
choices and what they cost.

Foundation: classical mechanics, thermodynamics, fluid dynamics, electromagnetism and
plasma physics, and quantum mechanics where it bites. Then per domain:

| Domain | Core theory |
|---|---|
| Aerospace | Aerodynamics, boundary layers, turbulence modelling (RANS/LES), propulsion, flight mechanics |
| Meteorology | Atmospheric dynamics and thermodynamics, radiative transfer, cloud physics, turbulence parameterization |
| Astrophysics | N-body and gravitational dynamics, MHD, radiative transfer |

→ [Fluids](fluids/index.md) · [Aerospace](aerospace/index.md) ·
[Meteorology](meteorology/index.md) · [Astrophysics](astrophysics/index.md)

### 2. Mathematical methods

PDE classification — hyperbolic, parabolic, elliptic — and what each implies about
numerical treatment, boundary conditions and domains of dependence. Analytical solutions
worth keeping in memory as sanity checks. Linear algebra and spectral theory. Tensors and
curvilinear coordinates. Asymptotics and perturbation methods.

→ [Foundations › Mathematical methods](foundations/math-methods.md)

### 3. Discretization and numerical analysis

Finite difference, finite volume, finite element and spectral methods, and the trade
each makes. Consistency, stability and convergence. Conservation and well-balancing.
Shock capturing, limiters, monotonicity. Dispersion and dissipation error — knowing what
your scheme does to a wave before you run it. Grid generation and adaptive mesh
refinement.

→ [Foundations › Numerical methods](foundations/numerical-methods.md)

### 4. Solvers, time integration and adjoints

Direct versus Krylov methods; preconditioning; multigrid. Stiffness, and the
explicit/implicit/IMEX decision. Operator splitting. CFL and the other step-size
constraints that actually bind. Adjoint methods and sensitivity analysis for design
optimization and for telling you which inputs your answer depends on.

→ [Foundations › Linear solvers](foundations/linear-solvers.md) ·
[Optimization and adjoints](foundations/optimization-adjoints.md)

### 5. Programming and software engineering

C++ for performance-critical code, Fortran for the numerical tradition and the large body
of working legacy, Python for analysis and ML and prototyping, Bash for everything that
glues them. Modular architecture and API design. Git, regression testing, code review.
Generated documentation. Profiling, memory management, SIMD.

→ [Computing › C++ and Fortran](computing/index.md) ·
[Python performance](computing/index.md)

### 6. HPC and parallelism

MPI, OpenMP, CUDA. Supercomputer architecture and the memory hierarchy that drives every
optimization decision. Schedulers — SLURM, PBS. Parallel file systems. Scaling analysis
and benchmarking, strong and weak. CPU/GPU hybrid and exascale paradigms.

→ [Computing › HPC](computing/index.md) · [GPU and CUDA](computing/index.md)

### 7. Domain codes and toolchains

The software you are expected to arrive already knowing, rather than to learn on the job.
This pillar is easy to underrate — it is not intellectually deep, but not knowing it is
immediately visible.

| Area | Tools |
|---|---|
| CFD | OpenFOAM, ANSYS FLUENT, AMReX |
| Meshing | Pointwise, Gmsh |
| Weather and climate | WRF, ERF, MPAS, GFDL models; RRTM, libRadtran |
| Astrophysics | FLASH, Athena, Gadget; SPH and N-body codes |
| Visualization | ParaView, VisIt, Tecplot, yt |
| Geospatial | GDAL, Xarray, GeoPandas, QGIS |
| CAD | Parasolid, CATIA |

→ [Toolchains](toolchains/index.md)

### 8. Data management, statistics and UQ

Terabyte-to-petabyte I/O and storage. Parallel I/O. NetCDF, GRIB, HDF5 — their layouts,
their chunking behaviour, and the performance cliffs hiding in both. Automated
post-processing pipelines. Statistical analysis, uncertainty quantification and
statistical emulation. Data version control.

→ [Computing › Data I/O](computing/index.md) ·
[Foundations › UQ](foundations/uncertainty-quantification.md) ·
[Toolchains › Data formats](toolchains/index.md)

### 9. Scientific machine learning

Surrogates and reduced-order models — POD, DMD, autoencoders. Physics-informed neural
networks. Operator learning: DeepONet, Fourier neural operators. Graph networks on
unstructured meshes. Feature engineering and dimensionality reduction. Computer vision on
scientific imagery. ML downscaling for weather and climate. Hybrid physics-ML coupling —
and the judgement to recognise when ML is the wrong tool.

→ [Scientific ML](sciml/index.md) · [Machine Learning](ml/index.md) ·
[Deep Learning](dl/index.md) · [Computer Vision](cv/index.md)

### 10. V&V, research craft and communication

Method of manufactured solutions, grid convergence studies, benchmark problems. Physics
insight: knowing when and why a model breaks, which is a skill and not a by-product of
knowing the equations. Literature review and hypothesis testing. Publication writing.
Presenting to mixed audiences. Working across multidisciplinary teams.

→ [Foundations › V&V](foundations/verification-validation.md) ·
[Research craft](foundations/research-craft.md)

## Cross-cutting: operations

Cloud (AWS, GCP, Azure), containers (Docker, and Singularity/Apptainer for HPC), CI/CD for
scientific codes, open-source contribution. Not a pillar of its own — it is the substrate
the other ten now run on.

→ [Computing › MLOps](computing/index.md)

## Self-assessment

`solid` — working competence, recap only. `working` — usable, actively being deepened.
`growing` — deliberate expansion area.

| # | Pillar | Standing | Why |
|---|---|---|---|
| 1 | Physical modeling | solid (aero/fluids), growing (meteorology) | Long training in aerospace and fluids; meteorology is a deliberate expansion |
| 2 | Mathematical methods | solid | Recap surface only |
| 3 | Discretization | solid | Recap surface only |
| 4 | Solvers and adjoints | solid | Adjoints worth a deeper pass |
| 5 | Programming | solid | C++/Fortran/Python all in active use |
| 6 | HPC | working | GPU and CUDA being deepened |
| 7 | Toolchains | working | Breadth varies sharply by tool |
| 8 | Data and UQ | working | Formats solid; UQ worth deepening |
| 9 | Scientific ML | growing | ML, DL, CV and SciML are the main growth areas |
| 10 | V&V and craft | solid | Recap surface only |

!!! note "This table is a placeholder for your own judgement"
    The standings above are inferred from the planning documents, not self-reported.
    Correct them — the value of this page depends on it being honest.
