import geopandas as gpd
import pytest

from spatial_kde.kernels import quartic, quartic_raw, quartic_scaled


@pytest.fixture
def points_gdf(data_dir):
    gdf = gpd.read_file(str(data_dir / "points.geojson"))
    gdf["dist"] = 1  # dummy distance column for testing
    gdf["weight"] = 2  # dummy weight column for testing
    return gdf


def test_quartic_raw_no_weight():
    out = quartic_raw(distance=1, radius=5)
    assert out == pytest.approx(0.9216, abs=1e-3)


def test_quartic_raw_with_weight():
    out = quartic_raw(distance=1, radius=5, weight=2)
    assert out == pytest.approx(0.9216 * 2, abs=1e-3)


def test_quartic_scaled_no_weight():
    out = quartic_scaled(distance=1, radius=5)
    assert out == pytest.approx(0.2552, abs=1e-3)


def test_quartic_scaled_with_weight():
    out = quartic_scaled(distance=1, radius=5, weight=2)
    assert out == pytest.approx(0.2552 * 2, abs=1e-3)


def test_quartic_no_weight_not_scaled(points_gdf):
    out = quartic(distances=points_gdf.dist.to_numpy(), radius=5, scaled=False)
    assert out == pytest.approx(0.9216 * 5, abs=1e-3)


def test_quartic_no_weight_scaled(points_gdf):
    out = quartic(distances=points_gdf.dist.to_numpy(), radius=5, scaled=True)
    assert out == pytest.approx(0.2552 * 5, abs=1e-3)


def test_quartic_weighted_not_scaled(points_gdf):
    out = quartic(
        distances=points_gdf.dist.to_numpy(),
        radius=5,
        weights=points_gdf.weight.to_numpy(),
        scaled=False,
    )
    assert out == pytest.approx(0.9216 * len(points_gdf) * 2, abs=1e-3)


def test_quartic_weighted_scaled(points_gdf):
    out = quartic(
        distances=points_gdf.dist.to_numpy(),
        radius=5,
        weights=points_gdf.weight.to_numpy(),
        scaled=True,
    )
    assert out == pytest.approx(0.2552 * len(points_gdf) * 2, abs=1e-3)
