from dataclasses import dataclass

import geopandas as gpd
import numpy as np


@dataclass
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def x_coords(self, pixel_size: float) -> np.ndarray:
        """Calculate all x coordinates for given ``pixel_size``"""
        return np.arange(self.min_x, self.max_x, pixel_size)

    def y_coords(self, pixel_size: float) -> np.ndarray:
        """Calculate all y coordinates for given ``pixel_size``"""
        return np.arange(self.min_y, self.max_y, pixel_size)

    def width(self, pixel_size: float) -> int:
        """Return the width (x / cols) for given ``pixel_size``"""
        return len(self.x_coords(pixel_size))

    def height(self, pixel_size: float) -> int:
        """Return the height (y / rows) for given ``pixel_size``"""
        return len(self.y_coords(pixel_size))

    @classmethod
    def from_gdf(cls, gdf: gpd.GeoDataFrame, radius: float = 0) -> "Bounds":
        """Calculate the bounds of a GeoDataFrame padded by radius amount

        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            GeoDataFrame to extract the total_bounds from
        radius : float
            Radius amount in units of the ``gdf`` coordinate system to pad the
            bounds by

        Returns
        -------
        Bounds
            Bounding containing `min_x, min_y, max_x, max_y` offset by ``radius``
        """
        min_x, min_y, max_x, max_y = gdf.total_bounds
        return cls(
            min_x=min_x - radius,
            min_y=min_y - radius,
            max_x=max_x + radius,
            max_y=max_y + radius,
        )
