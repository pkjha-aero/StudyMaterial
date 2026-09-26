---
title: Meshing tools
status: seed
tags: [pillar-7, toolchains, gmsh, pointwise, amr]
updated: 2026-09-26
---

# Meshing tools

<span class="status status-seed">seed</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! note "Cheatsheet page"
    Gotchas, not tutorials. Write the entry the day you fight the tool.

## The landscape

| Tool | Type | Notes |
|---|---|---|
| Gmsh | open source, scriptable | `.geo` scripts or Python API; good for research |
| Pointwise / Fidelity | commercial | strong structured and hybrid meshing, glyph scripting |
| snappyHexMesh | OpenFOAM | castellate/snap/layer from an STL; awkward but free |
| cfMesh | OpenFOAM | often easier than snappy for the same job |
| AMReX / block AMR | in-code | no external mesh; refinement is a runtime criterion |

## Gmsh

```bash
gmsh model.geo -3 -format msh2 -o model.msh       # 3D mesh, MSH2 for older readers
gmsh -check model.geo                              # geometry sanity
```

```python
import gmsh
gmsh.initialize()
gmsh.model.add("duct")
gmsh.model.occ.addBox(0, 0, 0, 1, 0.2, 0.2)
gmsh.model.occ.synchronize()
gmsh.model.mesh.field.add("Distance", 1)           # refine near a surface
gmsh.model.mesh.field.setNumbers(1, "FacesList", [1])
gmsh.model.mesh.field.add("Threshold", 2)
gmsh.model.mesh.field.setNumber(2, "InField", 1)
gmsh.model.mesh.field.setNumber(2, "LcMin", 0.002)
gmsh.model.mesh.field.setNumber(2, "LcMax", 0.02)
gmsh.model.mesh.field.setAsBackgroundMesh(2)
gmsh.model.mesh.generate(3)
gmsh.write("duct.msh")
gmsh.finalize()
```

Mesh size **fields** are the right mechanism for graded meshes — setting characteristic
lengths point by point does not generalise and does not reproduce.

## snappyHexMesh

Three stages, each toggled in `snappyHexMeshDict`: `castellatedMesh` (cut the background
hex mesh to the STL), `snap` (move points onto the surface), `addLayers` (insert prism
layers). Layer insertion is the stage that fails, and it fails by *silently producing
fewer layers than requested* — always check the log for the achieved layer count per
patch, not just for success.

## Quality targets

Repeated from [meshing and grid quality](../fluids/cfd/meshing.md), because these are the
numbers to type into the tool:

| Metric | Target |
|---|---|
| Non-orthogonality | max \(< 60\)–70° |
| Skewness | max \(< 4\) (OpenFOAM) / \(< 0.85\) (normalised) |
| Aspect ratio | \(< 100\) in the bulk; \(10^3\)–\(10^4\) is normal in boundary layers |
| Expansion ratio | \(< 1.2\) between neighbours |
| Prism layers | enough to cover \(\delta\) — often 25–50, not the default 10 |

??? warning "Failure modes"
    **Prism layer count achieved, not requested.** snappyHexMesh reports how many layers it actually inserted; in tight corners it silently inserts fewer or none. The mesh looks fine in a slice and the boundary layer is unresolved exactly where the flow separates.

    **Prism stack ending inside the boundary layer.** Covered in [meshing and grid quality](../fluids/cfd/meshing.md) — a size jump where gradients are steepest.

    **STL not watertight.** Gaps or flipped normals cause the mesher to leak into the interior, producing a mesh of the wrong region. Check with `surfaceCheck` (OpenFOAM) or Gmsh's geometry check before meshing.

    **Characteristic lengths set per-point rather than by field.** Works for one geometry, does not survive a parameter change, and cannot be reproduced. Use size fields.

    **MSH format version mismatch.** Gmsh 4 writes MSH4 by default; many readers expect MSH2. The error is usually a parse failure far from the real cause. `-format msh2`.

    **Mesh independence never demonstrated.** A single mesh is a single data point. See [V&V](../foundations/verification-validation.md) — and note that refining a wall-function mesh changes the turbulence modelling, not just the discretization.

    **Units.** CAD in millimetres, solver in metres. A factor of 1000 in length changes Reynolds number by the same factor, and the run proceeds happily.

    <!-- Add your own here. -->

## Connections

- [Fluids › Meshing and grid quality](../fluids/cfd/meshing.md) — why these targets.
- [CFD codes](cfd-codes.md) — what consumes the mesh.
- [Visualization](visualization.md) — inspecting mesh quality fields.
