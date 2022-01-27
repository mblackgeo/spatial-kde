import typer

app = typer.Typer()


@app.command()
def kde_from_vector(
    vector: str = typer.Argument(..., help="Path to input vector file"),
    output: str = typer.Argument(..., help="Output path for created raster"),
):
    """
    Create a Spatial Kernel Density / Heatmap raster from an input vector.

    The input vector file must be readable by GeoPandas and contain Point type
    geometry (for non-point geometries the centroid will be used for the KDE).
    """
    pass
