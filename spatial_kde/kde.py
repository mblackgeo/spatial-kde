from typing import Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial.kdtree import cKDTree
from shapely.geometry import Point

from spatial_kde.kernels import quartic


def _kde_at(
    row: pd.Series,
    radius: float,
    weight_col: Optional[str] = None,
) -> float:
    """Helper function used by pandas.DataFrame.apply() to calculate the KDE"""
    return quartic(
        distances=np.array(row.distances),
        radius=radius,
        weights=np.array(row[weight_col]) if weight_col else None,
    )


def spatial_kernel_density(
    points: gpd.GeoDataFrame,
    radius: float,
    output_pixel_size: float,
    weight_col: Optional[str] = None,
    extent: Optional[Tuple[float, float, float, float]] = None,
    output_raster: str = None,
) -> np.ndarray:
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
    output_pixel_size : float
        Output cell/pixel size of the created array. Same units as the coordinate
        reference system of ``points``
    weight_col : Optional[str], optional
        A column in ``points`` to weight the kernel density by, any points that
        are NaN in this field will not contribute to the KDE.
        If None, the all points will have uniform weight of 1.
    extent : Optional[Tuple[float, ...]], optional
        Extent of output array as (minx, miny, maxx, maxy)
        If None, uses the total bounds of the ``points``

    Returns
    -------
    np.ndarray
        Numpy array containing the KDE / heatmap generated
    """
    if weight_col and weight_col not in points.columns:
        raise ValueError(f"`{weight_col}` column not found in `points` GeoDataFrame")

    if weight_col:
        # TODO need to copy `points` here?
        points = points.dropna(subset=[weight_col])

    # setup the extent from given or from the total bounds of the input data
    if extent is None:
        minx, miny, maxx, maxy = points.total_bounds
    else:
        minx, miny, maxx, maxy = extent

    # create mesh grid array of the correct extent and pixel size
    x_grid = np.arange(minx - radius, maxx + radius, output_pixel_size)
    y_grid = np.arange(miny - radius, maxy + radius, output_pixel_size)
    x_mesh, y_mesh = np.meshgrid(x_grid, y_grid)

    # Create x/y coordinate pairs for neighbour calculations on the kd-tree
    xy = np.column_stack((x_mesh.flatten(), y_mesh.flatten()))

    # Create a KDTree for all the points so we can more efficiently do a lookup
    # for nearby points when calculating the KDE
    kdt = cKDTree(
        np.column_stack(
            (
                points.geometry.apply(lambda g: g.centroid.x).to_numpy(),
                points.geometry.apply(lambda g: g.centroid.y).to_numpy(),
            )
        )
    )

    # Find all the points on the grid that have neighbours within the search
    # radius, these are the non-zero points of the KDE surface
    kde_pnts = pd.DataFrame(kdt.query_ball_point(xy, r=radius), columns=["idxs"])
    kde_pnts["num"] = kde_pnts.idxs.apply(len)

    # Filter out points that have no neighbours within the search radius
    # and therefore their KDE value will be 0
    kde_pnts = kde_pnts.query("num > 0").drop(columns=["num"]).reset_index()

    # Store the centroid (i.e. the KDE raster pixel centre), and calculate the
    # distances all neighbours that are within the radius
    # TODO geodesic distance support
    kde_pnts["centroid"] = kde_pnts["index"].apply(lambda i: Point(xy[i]))
    kde_pnts["distances"] = kde_pnts.apply(
        lambda r: [r.centroid.distance(Point(xy[i])) for i in r.idxs], axis=1
    )

    # add the weights array
    if weight_col is not None:
        kde_pnts[weight_col] = kde_pnts.apply(
            lambda r: [points.at[i, weight_col] for i in r.idxs],
            axis=1,
        )

    # Calculate the KDE value for each point
    kde_pnts["kde"] = kde_pnts.apply(lambda r: _kde_at(r, radius, weight_col), axis=1)

    # TODO
    # convert the KDE values into a 2D array
    # Optionally write to raster? Or separate function?

    return np.array()
