from typer.testing import CliRunner

from movies_watchlist67.cli import app

runner = CliRunner()


def test_add_reports_the_movie_title() -> None:
    result = runner.invoke(app, ["add", "Interstellar"])

    assert result.exit_code == 0
    assert "Interstellar" in result.stdout


def test_add_rejects_an_empty_title() -> None:
    result = runner.invoke(app, ["add", "   "])

    assert result.exit_code == 1
