from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app

runner = CliRunner()


@pytest.fixture
def watchlist_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))
    return path


def test_add_trims_title_and_saves_movie(watchlist_file: Path) -> None:
    result = runner.invoke(app, ["add", "  Interstellar  "])

    assert result.exit_code == 0
    assert 'Added "Interstellar" — to watch.' in result.output
    assert "Interstellar" in watchlist_file.read_text(encoding="utf-8")


def test_add_rejects_empty_title(watchlist_file: Path) -> None:
    result = runner.invoke(app, ["add", "   "])

    assert result.exit_code == 1
    assert "Movie title cannot be empty." in result.output
    assert not watchlist_file.exists()


def test_add_rejects_duplicate_across_commands(watchlist_file: Path) -> None:
    runner.invoke(app, ["add", "Interstellar"])
    result = runner.invoke(app, ["add", "interstellar"])

    assert result.exit_code == 1
    assert "Movie already exists." in result.output


def test_list_shows_saved_movies(watchlist_file: Path) -> None:
    runner.invoke(app, ["add", "Interstellar"])
    runner.invoke(app, ["add", "Arrival", "--watched"])
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Interstellar — to watch" in result.output
    assert "Arrival — watched" in result.output


def test_list_reports_empty_watchlist(watchlist_file: Path) -> None:
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Your watchlist is empty." in result.output


def test_watch_updates_saved_movie(watchlist_file: Path) -> None:
    runner.invoke(app, ["add", "Interstellar"])
    result = runner.invoke(app, ["watch", "interstellar"])
    listed = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Interstellar — watched" in listed.output


def test_watch_rejects_unknown_movie(watchlist_file: Path) -> None:
    result = runner.invoke(app, ["watch", "Unknown"])

    assert result.exit_code == 1
    assert "Movie not found." in result.output


def test_list_rejects_invalid_file(watchlist_file: Path) -> None:
    watchlist_file.write_text("not json", encoding="utf-8")
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 1
    assert "Could not read watchlist file." in result.output
