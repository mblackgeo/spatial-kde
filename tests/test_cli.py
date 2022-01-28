from pathlib import Path

import pytest
import rasterio

from spatial_kde.cli import app


def test_kde_from_vector(runner, tmp_path, data_dir):
    vector = str(data_dir / "points_epsg_32630.gpkg")
    output = str(tmp_path / "out.tif")
    result = runner.invoke(app, [vector, output])

    assert result.exit_code == 0
    assert Path(output).exists()

    with rasterio.open(output) as src:
        arr = src.read()
        assert src.nodata == pytest.approx(-9999.0)
        assert src.shape == (173, 150)
        assert arr.flatten().max() == pytest.approx(0.934, abs=1e-3)
