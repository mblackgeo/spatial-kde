import math
from typing import Optional

import geopandas as gpd


def quartic(
    points: gpd.GeoDataFrame,
    distance_col: str,
    radius: float,
    weight_col: Optional[str] = None,
) -> float:
    """Quartic Kernel Density Estimation (after Silverman, 1986)

    Given a GeoDataFrame of points (that are already filtered to the search
    radius / bandwidth of the kernal), generate the kernel density estimate
    using the Quartic kernel equation. Optionally, points can be weighted by
    a column in the GeoDataFrame to increase the influence of specific features.

    Parameters
    ----------
    points : gpd.GeoDataFrame
        Points that contribute to the KDE, i.e. within the bandwith / search
        radius.
    distance_col : str
        Name of column in the points GeoDataFrame that holds the distance values.
        Units are in the CRS of the input ``points``.
    radius : Union[str, float]
        Seach radius used (also known as bandwidth).
        Units are in the CRS of the input ``points``.
    weight_col : Optional[str], optional
        Name of column containing weights for each point. This can be used to
        increase the influence certain features have on the resultant KDE.
        Known as `population_field` in Arcpy.

    Returns
    -------
    float
        KDE estimate
    """
    if weight_col is not None:
        if weight_col not in points.columns:
            raise ValueError(f"Input points data does not contain `{weight_col}`")

    # if there is no weight field then just assign it a constant weight of 1
    # i.e. the KDE is only weighted by the number of points in the radius
    if weight_col is None:
        weight_col = "__weight"
        points[weight_col] = 1

    kde_vals = [
        (3 / math.pi) * pnt[weight_col] * ((1 - (pnt[distance_col] / radius) ** 2) ** 2)
        for _, pnt in points.iterrows()
    ]

    return (1 / (radius ** 2)) * sum(kde_vals)
