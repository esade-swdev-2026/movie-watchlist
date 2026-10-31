from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app
from movie_watchlist.movies import Movie
from movie_watchlist.storage import save_watchlist


def test_list_filters_by_actor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))

    save_watchlist(
        path,
        {
            "Interstellar": Movie(
                title="Interstellar",
                actors=("Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"),
            ),
            "Arrival": Movie(
                title="Arrival",
                actors=("Amy Adams", "Jeremy Renner", "Forest Whitaker"),
            ),
        },
    )

    result = CliRunner().invoke(app, ["list", "--actor", "anne hathaway"])

    assert result.exit_code == 0
    assert "Interstellar" in result.output
    assert "Arrival" not in result.output


def test_list_rejects_empty_actor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(tmp_path / "movies.json"))

    result = CliRunner().invoke(app, ["list", "--actor", "   "])

    assert result.exit_code == 1
    assert "Actor cannot be empty." in result.output
