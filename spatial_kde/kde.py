from typing import Optional

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.crs import CRS
from shapely.geometry import Point

from spatial_kde.kernels import quartic
from spatial_kde.utils import Bounds


def spatial_kernel_density(
    points: gpd.GeoDataFrame,
    radius: float,
    output_path: str,
    output_pixel_size: float,
    output_driver: str = "GTiff",
    weight_col: Optional[str] = None,
    scaled: bool = False,
) -> None:
    """Calculate Kernel Density / heatmap from ``points``

    .. note:: Distance calculations are planar so care should be taken with data
              that is in geographic coordinate systems

    Parameters
    ----------
    points : gpd.GeoDataFrame
        Input GeoDataFrame of points to generate a KDE from
    radius : float
        Radius of KDE, same units as the coordinate reference system of ``points``
        Sometimes referred to as search radius or bandwidth
    output_path : str
        Path to write output raster to
    output_pixel_size : float
        Output cell/pixel size of the created array. Same units as the coordinate
        reference system of ``points``
    output_driver : str
        Output format (driver) used to create image. See also
        https://rasterio.readthedocs.io/en/latest/api/rasterio.drivers.html
    weight_col : Optional[str], optional
        A column in ``points`` to weight the kernel density by, any points that
        are NaN in this field will not contribute to the KDE.
        If None, the all points will have uniform weight of 1.
    scaled : bool
        If True will output mathematically scaled values, else will output raw
        values.

    Returns
    -------
    np.ndarray
        Numpy array containing the KDE / heatmap generated
    """
    if weight_col and weight_col not in points.columns:
        raise ValueError(f"`{weight_col}` column not found in `points` GeoDataFrame")

    if weight_col:
        points = points.dropna(subset=[weight_col])

    # Get the bounding box extent for the new raster
    bounds = Bounds.from_gdf(gdf=points, radius=radius)

    # Create x/y coordinate pairs for neighbour calculations on the kd-tree
    # this is the "top left" coordinate, not the centre of the pixel
    x_mesh, y_mesh = np.meshgrid(
        bounds.x_coords(output_pixel_size),
        bounds.y_coords(output_pixel_size),
    )

    # create the coordinate grid of the pixel centre points
    xc = x_mesh + (output_pixel_size / 2)
    yc = y_mesh + (output_pixel_size / 2)

    # Slow implementation iterating over every pixel / point
    ndv = -9999
    Z = ndv + np.zeros_like(xc)

    for row in range(xc.shape[0]):
        for col in range(xc.shape[1]):

            distances = []
            weights = []
            for pnt in points.itertuples():
                # Euclidean distance (i.e. planar)
                # TODO add geodesic distance support
                centre = Point((xc[row][col], yc[row][col]))
                dist = centre.distance(pnt.geometry)

                if dist <= radius:
                    distances.append(dist)

                if weight_col:
                    weights.append(pnt[weight_col])

            if distances:
                Z[row, col] = quartic(
                    distances=distances,
                    radius=radius,
                    weights=weights if weight_col else None,
                    scaled=scaled,
                )

    # create the output raster
    with rasterio.open(
        fp=output_path,
        mode="w",
        driver=output_driver,
        height=Z.shape[0],
        width=Z.shape[1],
        count=1,
        dtype=Z.dtype,
        crs=CRS.from_user_input(points.crs),
        transform=rasterio.transform.from_bounds(
            west=bounds.min_x,
            south=bounds.min_y,
            east=bounds.max_x,
            north=bounds.max_y,
            width=Z.shape[1],
            height=Z.shape[0],
        ),
        nodata=ndv,
    ) as dst:
        # numpy arrays start at the "bottom left", whereas rasters are written
        # from the "top left", hence flipping the array up-down before writing
        dst.write(np.flipud(Z), 1)
