from typing import Optional, Tuple

import geopandas as gpd
import numpy as np


def spatial_kernel_density(
    points: gpd.GeoDataFrame,
    radius: float,
    output_pixel_size: float,
    weight_col: Optional[str] = None,
    extent: Optional[Tuple[float, float, float, float]] = None,
) -> np.ndarray:
    """Calculate Kernel Density / heatmap from ``points``

    .. note:: Distance calcualtions are planar so care should be taken with data
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

    # TODO
    # create mesh grid array of the correct extent and pixel size
    # the KDE will be evaluated at each point of this array

    # Get x/y locations of the grid so we have coordinates of every point at
    # which to evaluate the KDE

    # get centroids of all geometries and create KDTree

    # create Z vector (i.e. the points of the KDE surface)
    # calculate the KDE value using the quartic kernel for points of Z that have
    # neighbours within the radius (i.e. the KDE will be non-zero)

    # reshape the output Z surface to 2D array
    return np.array([1])
