import geopandas as gpd

from spatial_kde.utils import Bounds


def test_bounds():
    bounds = Bounds(1, 1, 10, 10)
    assert bounds.height(pixel_size=0.5) == 18
    assert bounds.width(pixel_size=0.5) == 18
    assert bounds.x_coords(pixel_size=0.5).shape == (18,)
    assert bounds.y_coords(pixel_size=0.5).shape == (18,)


def test_calculate_bounds_from_gdf(data_dir):
    gdf = gpd.read_file(str(data_dir / "points_epsg_32630.gpkg"))
    bounds = Bounds.from_gdf(gdf, radius=100)
    assert bounds.height(pixel_size=1) == 371
    assert bounds.width(pixel_size=1) == 348
