import geopandas as gpd
import numpy as np

from spatial_kde import spatial_kernel_density


def test_spatial_kernel_density(data_dir):
    gdf = gpd.read_file(str(data_dir / "points.geojson"))
    out = spatial_kernel_density(
        points=gdf,
        radius=0.5,
        output_pixel_size=0.2,
        weight_col="weight",
    )

    assert isinstance(out, np.ndarray)
