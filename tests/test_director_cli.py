from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app
from movie_watchlist.storage import load_watchlist

runner = CliRunner()


@pytest.fixture
def watchlist_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))
    return path


def test_add_movie_with_director(watchlist_file: Path) -> None:
    result = runner.invoke(
        app,
        ["add", "Interstellar", "--director", "Christopher Nolan"],
    )

    assert result.exit_code == 0

    movies = load_watchlist(watchlist_file)
    assert movies["Interstellar"].director == "Christopher Nolan"


def test_list_filters_movies_by_director(watchlist_file: Path) -> None:
    runner.invoke(app, ["add", "Interstellar", "--director", "Christopher Nolan"])
    runner.invoke(app, ["add", "Titanic", "--director", "James Cameron"])

    result = runner.invoke(app, ["list", "--director", "christopher nolan"])

    assert result.exit_code == 0
    assert "Interstellar" in result.output
    assert "Titanic" not in result.output


def test_list_rejects_empty_director(watchlist_file: Path) -> None:
    result = runner.invoke(app, ["list", "--director", "   "])

    assert result.exit_code == 1
    assert "Director cannot be empty." in result.output
