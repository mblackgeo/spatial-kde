from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).parent / "resources"


@pytest.fixture
def runner():
    yield CliRunner()
