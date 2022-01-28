from typing import Optional

import geopandas as gpd
import typer

from spatial_kde import spatial_kernel_density

app = typer.Typer()


@app.command()
def kde_from_vector(
    vector: str = typer.Argument(..., help="Path to input vector file"),
    output: str = typer.Argument(..., help="Output path for created raster"),
    radius: float = typer.Option(
        default=1,
        help="Radius/Bandwith for the KDE. Same units as the CRS of `vector`.",
    ),
    output_pixel_size: float = typer.Option(
        default=1,
        help="Output pixel size (resolution). Same units as the CRS of `vector`.",
    ),
    output_driver: str = typer.Option(
        default="GTiff",
        help="Output driver (file format) used by rasterio (Default = GeoTiff).",
    ),
    weight_field: Optional[str] = typer.Option(
        default=None,
        help="Optional field in `vector` containing weights of each point.",
    ),
    scaled: bool = typer.Option(
        default=False,
        help="Set to True to scale the KDE values, leave false to use raw values.",
    ),
):
    """
    Create a Spatial Kernel Density / Heatmap raster from an input vector.

    The input vector file must be readable by GeoPandas and contain Point type
    geometry (for non-point geometries the centroid will be used for the KDE).
    """
    spatial_kernel_density(
        points=gpd.read_file(vector),
        radius=radius,
        output_path=output,
        output_pixel_size=output_pixel_size,
        output_driver=output_driver,
        weight_col=weight_field,
        scaled=scaled,
    )
