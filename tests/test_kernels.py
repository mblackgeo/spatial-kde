import geopandas as gpd
import pytest

from spatial_kde.kernels import quartic


@pytest.fixture
def points_gdf(data_dir):
    gdf = gpd.read_file(str(data_dir / "points.geojson"))
    gdf["dist"] = 5  # dummy distance column for testing
    return gdf


def test_quartic_no_weight(points_gdf):
    out = quartic(distances=points_gdf.dist.to_numpy(), radius=1)
    assert out == pytest.approx(2750.1974, abs=1e4)


def test_quartic_with_weight(points_gdf):
    out = quartic(
        distances=points_gdf.dist.to_numpy(),
        radius=1,
        weights=points_gdf.weight.to_numpy(),
    )
    assert out == pytest.approx(8250.5922, abs=1e4)
