---
title: Papers
status: working
tags: [resources]
updated: 2026-09-26
---

# Papers

<span class="status status-working">working</span>

Individual papers cited across the site, gathered by area. Each is one a page leans on
directly — a founding result, a definitive treatment, or a well-documented failure mode.

## Numerics and V&V

- Williams, Waterman & Patterson (2009), *Roofline: an insightful visual performance model* — [HPC](../computing/hpc.md)
- Salari & Knupp (2000), *Code verification by the method of manufactured solutions* — [V&V](../foundations/verification-validation.md)
- Daly (2006), *A higher order estimate of the optimum checkpoint interval* — [Data and I/O](../computing/data-io.md)
- Tóth (2000), *The \(\nabla\cdot B = 0\) constraint in shock-capturing MHD codes* — [MHD](../astrophysics/mhd.md)

## Fluids, aerodynamics, turbulence

- Chorin (1968), *Numerical solution of the Navier–Stokes equations* — [Incompressible](../fluids/incompressible.md)
- Menter (1994), *Two-equation eddy-viscosity turbulence models for engineering applications* — [RANS](../fluids/turbulence/rans.md)
- Germano et al. (1991), *A dynamic subgrid-scale eddy viscosity model* — [LES](../fluids/turbulence/les.md)
- Nicoud & Ducros (1999), *Subgrid-scale stress modelling based on the square of the velocity gradient tensor* (WALE) — [LES](../fluids/turbulence/les.md)
- Jameson (1988), *Aerodynamic design via control theory* — [Adjoints](../foundations/optimization-adjoints.md)
- Giles & Pierce (2000), *An introduction to the adjoint approach to design* — [Adjoints](../foundations/optimization-adjoints.md)
- Zhang (2000), *A flexible new technique for camera calibration* — [Classical CV](../cv/classical-cv.md)

## Meteorology and wildfire

- Hersbach et al. (2020), *The ERA5 global reanalysis* — [Observations](../meteorology/observations.md)
- Rothermel (1972), *A mathematical model for predicting fire spread in wildland fuels* — [Fire weather](../meteorology/fire-weather.md)
- Potter (2012), *Atmospheric interactions with wildland fire behaviour* (two-part review) — [Fire weather](../meteorology/fire-weather.md)
- Srock et al. (2018), *The Hot-Dry-Windy Index* — [Fire weather](../meteorology/fire-weather.md)
- Giglio et al. (2016), *The Collection 6 MODIS active fire detection algorithm* — [Scientific imagery](../cv/scientific-imagery.md)
- Hoskins, McIntyre & Robertson (1985), *On the use and significance of isentropic potential vorticity maps* — [Dynamics](../meteorology/dynamics.md)

## Machine learning

- Vaswani et al. (2017), *Attention Is All You Need* — [Architectures](../dl/architectures.md)
- He et al. (2016), *Deep Residual Learning for Image Recognition* — [Architectures](../dl/architectures.md)
- Ronneberger et al. (2015), *U-Net: Convolutional Networks for Biomedical Image Segmentation* — [Architectures](../dl/architectures.md)
- Loshchilov & Hutter (2019), *Decoupled Weight Decay Regularization* (AdamW) — [Training craft](../ml/training-craft.md)
- Kingma & Welling (2014), *Auto-Encoding Variational Bayes* — [Generative](../dl/generative.md)
- Goodfellow et al. (2014), *Generative Adversarial Networks* — [Generative](../dl/generative.md)
- Ho et al. (2020), *Denoising Diffusion Probabilistic Models* — [Generative](../dl/generative.md)
- Rombach et al. (2022), *High-Resolution Image Synthesis with Latent Diffusion Models* — [Generative](../dl/generative.md)
- Lin et al. (2017), *Focal Loss for Dense Object Detection* — [Detection](../cv/detection-segmentation.md)
- Carion et al. (2020), *End-to-End Object Detection with Transformers* — [Detection](../cv/detection-segmentation.md)
- Kirillov et al. (2023), *Segment Anything* — [Detection](../cv/detection-segmentation.md)
- Radford et al. (2021), *Learning Transferable Visual Models From Natural Language Supervision* (CLIP) — [VLMs](../cv/vlms.md)
- Lewis et al. (2020), *Retrieval-Augmented Generation* — [LLMs](../dl/llm-genai.md)
- Hu et al. (2021), *LoRA: Low-Rank Adaptation of Large Language Models* — [LLMs](../dl/llm-genai.md)
- Liu et al. (2023), *Lost in the Middle* — [LLMs](../dl/llm-genai.md)

## Evaluation and methodology

- Kaufman et al. (2012), *Leakage in data mining: formulation, detection, and avoidance* — [Evaluation](../ml/evaluation.md)
- Guo et al. (2017), *On calibration of modern neural networks* — [Evaluation](../ml/evaluation.md)
- Saito & Rehmsmeier (2015), *The precision-recall plot is more informative than the ROC plot* — [Evaluation](../ml/evaluation.md)
- Grinsztajn et al. (2022), *Why do tree-based models still outperform deep learning on tabular data?* — [Classical ML](../ml/classical.md)
- Ploton et al. (2020), *Spatial validation reveals poor predictive performance of large-scale ecological mapping models* — [Scientific imagery](../cv/scientific-imagery.md)
- Sculley et al. (2015), *Hidden Technical Debt in Machine Learning Systems* — [MLOps](../computing/mlops.md)
- Wilson et al. (2017), *Good enough practices in scientific computing* — [Research craft](../foundations/research-craft.md)
- Crameri, Shephard & Heron (2020), *The misuse of colour in science communication* — [Research craft](../foundations/research-craft.md)

## Scientific ML

- Raissi, Perdikaris & Karniadakis (2019), *Physics-informed neural networks* — [PINNs](../sciml/pinns.md)
- Krishnapriyan et al. (2021), *Characterizing possible failure modes in physics-informed neural networks* — [PINNs](../sciml/pinns.md)
- Wang, Teng & Perdikaris (2021), *Understanding and mitigating gradient pathologies in PINNs* — [PINNs](../sciml/pinns.md)
- Li et al. (2021), *Fourier Neural Operator for Parametric Partial Differential Equations* — [Neural operators](../sciml/neural-operators.md)
- Lu, Jin & Karniadakis (2021), *Learning nonlinear operators via DeepONet* — [Neural operators](../sciml/neural-operators.md)
- Kovachki et al. (2023), *Neural Operator: Learning Maps Between Function Spaces* — [Neural operators](../sciml/neural-operators.md)
- Pfaff et al. (2021), *Learning Mesh-Based Simulation with Graph Networks* — [Mesh GNNs](../sciml/gnn-meshes.md)
- Sanchez-Gonzalez et al. (2020), *Learning to Simulate Complex Physics with Graph Networks* — [Mesh GNNs](../sciml/gnn-meshes.md)
- Battaglia et al. (2018), *Relational inductive biases, deep learning, and graph networks* — [Mesh GNNs](../sciml/gnn-meshes.md)
- Ling, Kurzawski & Templeton (2016), *Reynolds-averaged turbulence modelling using deep neural networks with embedded invariance* — [Hybrid coupling](../sciml/hybrid-coupling.md)
- Duraisamy, Iaccarino & Xiao (2019), *Turbulence modeling in the age of data* — [Hybrid coupling](../sciml/hybrid-coupling.md)
- Um et al. (2020), *Solver-in-the-loop* — [Hybrid coupling](../sciml/hybrid-coupling.md)
- Benner, Gugercin & Willcox (2015), *A survey of projection-based model reduction methods* — [Surrogates](../sciml/surrogates-rom.md)
- Kennedy & O'Hagan (2001), *Bayesian calibration of computer models* — [UQ](../foundations/uncertainty-quantification.md)

## Connections

- [Books](books.md) — the longer references.
- [Videos and playlists](videos-playlists.md) — lecture series.
