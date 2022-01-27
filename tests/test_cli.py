from spatial_kde.cli import app


def test_kde_from_vector(runner):
    result = runner.invoke(app, ["aaa", "bbb"])
    assert result.exit_code == 0
