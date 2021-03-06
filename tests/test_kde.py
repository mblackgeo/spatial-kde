from pathlib import Path

import geopandas as gpd
import pytest
import rasterio

from spatial_kde import spatial_kernel_density


def test_spatial_kernel_density_no_weight_utm(data_dir, tmp_path):
    gdf = gpd.read_file(str(data_dir / "points_epsg_32630.gpkg"))
    out_file = str(tmp_path / "out.tif")

    spatial_kernel_density(
        points=gdf,
        radius=100,
        output_pixel_size=2,
        output_path=out_file,
        scaled=False,
    )

    assert Path(out_file).exists()

    with rasterio.open(out_file) as src:
        out_arr = src.read(1)
        assert max(out_arr.flatten()) == pytest.approx(1.58, abs=1e-2)


def test_spatial_kernel_density_weighted_utm(data_dir, tmp_path):
    gdf = gpd.read_file(str(data_dir / "points_epsg_32630.gpkg"))
    out_file = str(tmp_path / "out.tif")

    spatial_kernel_density(
        points=gdf,
        radius=100,
        output_pixel_size=2,
        output_path=out_file,
        scaled=False,
        weight_col="weight",
    )

    assert Path(out_file).exists()

    with rasterio.open(out_file) as src:
        out_arr = src.read(1)
        assert max(out_arr.flatten()) == pytest.approx(6.29, abs=1e-2)


def test_spatial_kernel_density_no_weight_wgs(data_dir, tmp_path):
    gdf = gpd.read_file(str(data_dir / "points.geojson"))
    out_file = str(tmp_path / "out.tif")

    spatial_kernel_density(
        points=gdf,
        radius=0.001,
        output_pixel_size=0.00001,
        output_path=out_file,
        scaled=False,
    )

    assert Path(out_file).exists()

    with rasterio.open(out_file) as src:
        out_arr = src.read(1)
        assert max(out_arr.flatten()) == pytest.approx(1.37363, abs=1e-2)


def test_spatial_kernel_density_missing_weight(data_dir, tmp_path):
    gdf = gpd.read_file(str(data_dir / "points_epsg_32630.gpkg"))
    out_file = str(tmp_path / "out.tif")

    with pytest.raises(ValueError):
        spatial_kernel_density(
            points=gdf,
            radius=100,
            output_pixel_size=2,
            output_path=out_file,
            scaled=False,
            weight_col="not_a_column",
        )
