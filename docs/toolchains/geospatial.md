---
title: Geospatial tools
status: seed
tags: [pillar-7, toolchains, remote-sensing, data-formats]
updated: 2026-09-26
---

# Geospatial tools

<span class="status status-seed">seed</span>
<span class="pillar">pillar 7 &middot; Domain codes and toolchains</span>

!!! note "Cheatsheet page"
    Gotchas, not tutorials. Write the entry the day you fight the tool.

## The landscape

| Tool | For |
|---|---|
| GDAL/OGR | the substrate — format translation, warping, everything |
| rasterio | Pythonic raster I/O over GDAL |
| xarray + rioxarray | labelled N-D arrays with CRS awareness |
| GeoPandas | vector data as a DataFrame |
| Shapely | geometry operations |
| QGIS | interactive inspection; the fastest way to see what is wrong |
| PROJ | coordinate transformations underneath all of the above |

## GDAL command line

```bash
gdalinfo -stats raster.tif                 # CRS, transform, bands, stats
gdalwarp -t_srs EPSG:4326 -r near in.tif out.tif    # reproject; -r near for categorical
gdal_translate -of COG in.tif out.tif      # cloud-optimized GeoTIFF
gdalbuildvrt mosaic.vrt tiles/*.tif        # virtual mosaic, no data copied
ogrinfo -al -so vector.gpkg                # vector summary
ogr2ogr -t_srs EPSG:3857 out.gpkg in.shp   # vector reprojection
```

`gdalinfo` first, always. CRS, geotransform, no-data value and band count are the four
things that determine whether two products can be combined.

## Python

```python
import rioxarray, xarray as xr, geopandas as gpd

da = rioxarray.open_rasterio("scene.tif", masked=True)   # masked=True applies nodata
print(da.rio.crs, da.rio.transform(), da.rio.nodata)

da_ll = da.rio.reproject("EPSG:4326", resampling=rioxarray.enums.Resampling.nearest)
clipped = da.rio.clip(gdf.geometry, gdf.crs)

gdf = gpd.read_file("boundaries.gpkg").to_crs(da.rio.crs)   # match CRS before any join
```

**Reproject the vector to the raster**, not the other way round, when clipping — it avoids
resampling the raster twice.

## CRS, briefly

| Code | What |
|---|---|
| EPSG:4326 | WGS84 lat/lon, degrees — **not** a projection, areas and distances are wrong |
| EPSG:3857 | Web Mercator — display only, badly area-distorting at high latitude |
| EPSG:326xx / 327xx | UTM north/south zone xx — metres, good locally |
| EPSG:5070 | CONUS Albers equal-area — the right choice for US area statistics |

Axis order is the classic trap: EPSG:4326 is formally **latitude, longitude**, and many
tools use lon, lat. Check rather than assume.

??? warning "Failure modes"
    **Computing area or distance in EPSG:4326.** Degrees are not metres, and a degree of longitude varies from 111 km at the equator to zero at the pole. Any area computed in 4326 is wrong. Reproject to an equal-area CRS first.

    **Bilinear resampling of a categorical raster.** Land cover class 2 and class 6 average to class 4. See [image fundamentals](../cv/image-fundamentals.md) — and note `gdalwarp` defaults to nearest, while several Python paths default to bilinear.

    **No-data not masked.** `masked=True` in rioxarray, `-dstnodata` in gdalwarp. Otherwise the fill value enters every statistic, and \(0\) is a plausible-looking reflectance.

    **Axis order confusion in EPSG:4326.** Coordinates silently transposed; points land in the wrong hemisphere or in the ocean. Symptom: a map that is obviously wrong, which is at least a fast failure.

    **Joining layers in different CRS.** GeoPandas will happily do a spatial join between mismatched CRS in some versions and return nothing, or nonsense. Always `.to_crs()` first, explicitly.

    **Mosaicking products with different resolutions or grids.** Resampling is implicit and the result inherits the coarsest, with resampling artefacts. Be explicit about the target grid.

    **Reprojecting more than once.** Each warp resamples and loses information. Go from source CRS to the final CRS in one step.

    <!-- Add your own here. -->

## Connections

- [Data formats](data-formats.md) — GeoTIFF, NetCDF, Zarr.
- [CV › Scientific imagery](../cv/scientific-imagery.md) — radiometry and spatial CV.
- [Meteorology › Observations](../meteorology/observations.md) — the products.

## Sources

- GDAL, PROJ, rasterio, rioxarray and GeoPandas documentation.
- epsg.io for CRS lookup; the PROJ FAQ for axis-order questions.
