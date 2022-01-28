import math
from typing import List, Optional, Union

import numpy as np


def quartic_raw(distance: float, radius: float, weight: float = 1):
    """Calculate raw Quartic KDE value"""
    return weight * (math.pow(1.0 - math.pow(distance / radius, 2), 2))


def quartic_scaled(distance: float, radius: float, weight: float = 1):
    """Calculate mathematically scaled Quartic KDE value"""
    # Normalizing constant
    k = 116.0 / (5.0 * math.pi * math.pow(radius, 2))

    # Derived from Wand and Jones (1995), p. 175
    return weight * (
        k * (15.0 / 16.0) * math.pow(1.0 - math.pow(distance / radius, 2), 2)
    )


def quartic(
    distances: Union[List[float], np.ndarray],
    radius: float,
    weights: Optional[Union[List[float], np.ndarray]] = None,
    scaled: bool = False,
) -> float:
    """Quartic Kernel Density Estimation (after Silverman, 1986)

    Given an array of distances (i.e. points that are within the search
    radius / bandwidth of the kernal), generate the kernel density estimate
    using the Quartic kernel equation. Optionally, weights for each point can
    be provided.

    Parameters
    ----------
    distances : np.ndarray
        A 1D array containing distance values.
    radius : float
        Radius of the KDE.
    weights : Optional[np.ndarray]
        Optional weights (same shape as ``distance``) for each point in the KDE.
        If None, weights will be uniform (i.e. 1).
    scaled : bool
        If True will output mathematically scaled values, else will output raw
        values.

    Returns
    -------
    float
        KDE estimate
    """
    weights = np.ones_like(distances) if weights is None else weights
    kernel_func = quartic_scaled if scaled else quartic_raw

    # TODO vectorise this
    kde_vals = [
        kernel_func(distance=dist, radius=radius, weight=weight)
        for dist, weight in zip(distances, weights)
    ]

    return sum(kde_vals)
