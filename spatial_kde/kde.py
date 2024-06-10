from typing import Optional

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.crs import CRS

from scipy.spatial.kdtree import cKDTree
from scipy.spatial import distance

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

    # stack the coordinates so we can do vectorised nearest neighbour ops
    xy = np.column_stack((xc.flatten(), yc.flatten()))

    # Create a KDTree for all the points so we can more efficiently do a lookup
    # for nearby points when calculating the KDE
    points_np_array = np.column_stack(
        (
            points.geometry.apply(lambda g: g.centroid.x).to_numpy(),
            points.geometry.apply(lambda g: g.centroid.y).to_numpy(),
        )
    )
    kdt = cKDTree(points_np_array)

    # Find all the points on the grid that have neighbours within the search
    # radius, these are the non-zero points of the KDE surface
    kde_pnts = pd.DataFrame(kdt.query_ball_point(xy, r=radius), columns=["nn"])

    # Filter out points that have no neighbours within the search radius
    kde_pnts["num"] = kde_pnts.nn.apply(len)
    kde_pnts = kde_pnts.query("num > 0").drop(columns=["num"])

    # create an array to store the KDE values
    ndv = -9999
    z_scalar = (ndv + np.zeros_like(xc)).flatten()

    # calculate the KDE value for every point that has neighbours
    for row in kde_pnts.itertuples():
        centre = [xy[row.Index]]
        corresponding_points = points_np_array[row.nn]
        distances = distance.cdist(centre, corresponding_points, 'euclidean').flatten()

        weights = None
        if weight_col:
            weights = [points.at[i, weight_col] for i in row.nn]

        z_scalar[row.Index] = quartic(
            distances=distances,
            radius=radius,
            weights=weights,
            scaled=scaled,
        )

    # create the output raster
    z = z_scalar.reshape(xc.shape)
    with rasterio.open(
        fp=output_path,
        mode="w",
        driver=output_driver,
        height=z.shape[0],
        width=z.shape[1],
        count=1,
        dtype=z.dtype,
        crs=CRS.from_user_input(points.crs),
        transform=rasterio.transform.from_bounds(
            west=bounds.min_x,
            south=bounds.min_y,
            east=bounds.max_x,
            north=bounds.max_y,
            width=z.shape[1],
            height=z.shape[0],
        ),
        nodata=ndv,
    ) as dst:
        # numpy arrays start at the "bottom left", whereas rasters are written
        # from the "top left", hence flipping the array up-down before writing
        dst.write(np.flipud(z), 1)
