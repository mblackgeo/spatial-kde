import math
from typing import Optional

import numpy as np


def quartic(
    distances: np.ndarray,
    radius: float,
    weights: Optional[np.ndarray] = None,
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

    Returns
    -------
    float
        KDE estimate
    """
    if weights is None:
        weights = np.ones_like(distances)

    # TODO vectorise this
    kde_vals = [
        (3 / math.pi) * w * ((1 - (d / radius) ** 2) ** 2)
        for w, d in zip(distances, weights)
    ]

    return (1 / (radius ** 2)) * sum(kde_vals)
