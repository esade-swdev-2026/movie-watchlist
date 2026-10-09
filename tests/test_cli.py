from typer.testing import CliRunner

from movie_watchlist.cli import app

runner = CliRunner()


def test_add_trims_title_and_reports_status() -> None:
    result = runner.invoke(app, ["add", "  Interstellar  "])
    assert result.exit_code == 0
    assert 'Added "Interstellar" — to watch.' in result.output


def test_add_rejects_empty_title() -> None:
    result = runner.invoke(app, ["add", "   "])
    assert result.exit_code == 1
    assert "Movie title cannot be empty." in result.output
