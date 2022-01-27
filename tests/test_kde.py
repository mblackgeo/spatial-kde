from pathlib import Path

import geopandas as gpd
import numpy as np

from spatial_kde import spatial_kernel_density


def test_spatial_kernel_density(data_dir, tmp_path):
    gdf = gpd.read_file(str(data_dir / "points_epsg_32630.gpkg"))
    out_file = str(tmp_path / "out.tif")

    out_arr = spatial_kernel_density(
        points=gdf,
        radius=100,
        output_pixel_size=1,
        weight_col="weight",
        output_raster=out_file,
    )

    assert isinstance(out_arr, np.ndarray)
    assert Path(out_file).exists()
