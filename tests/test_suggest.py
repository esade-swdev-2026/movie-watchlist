from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app
from movie_watchlist.movies import Movie
from movie_watchlist.storage import save_watchlist
from movie_watchlist.suggest import suggest_movie


def test_suggest_returns_none_for_empty_watchlist() -> None:
    assert suggest_movie({}) is None


def test_suggest_ignores_watched_movies() -> None:
    movies = {"Arrival": Movie(title="Arrival", watched=True, rating=10)}

    assert suggest_movie(movies) is None


def test_suggest_prefers_the_highest_rated_unwatched_movie() -> None:
    movies = {
        "Interstellar": Movie(title="Interstellar", rating=7),
        "Arrival": Movie(title="Arrival", rating=9),
        "Up": Movie(title="Up"),
    }

    suggestion = suggest_movie(movies)

    assert suggestion is not None
    assert suggestion.title == "Arrival"


def test_suggest_breaks_ties_by_title() -> None:
    movies = {"Up": Movie(title="Up"), "Arrival": Movie(title="Arrival")}

    suggestion = suggest_movie(movies)

    assert suggestion is not None
    assert suggestion.title == "Arrival"


@pytest.fixture
def watchlist_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))
    return path


def test_suggest_command_prints_a_movie_to_watch(watchlist_file: Path) -> None:
    save_watchlist(watchlist_file, {"Arrival": Movie(title="Arrival", rating=9)})

    result = CliRunner().invoke(app, ["suggest"])

    assert result.exit_code == 0
    assert "Arrival" in result.output


def test_suggest_command_applies_filters(watchlist_file: Path) -> None:
    save_watchlist(
        watchlist_file,
        {
            "Arrival": Movie(title="Arrival", rating=9, genre="Sci-Fi", runtime=116),
            "Up": Movie(title="Up", rating=8, genre="Animation", runtime=96),
        },
    )

    result = CliRunner().invoke(app, ["suggest", "--genre", "Animation"])

    assert result.exit_code == 0
    assert "Up" in result.output
    assert "Arrival" not in result.output


def test_suggest_command_reports_no_match(watchlist_file: Path) -> None:
    save_watchlist(watchlist_file, {"Up": Movie(title="Up", genre="Animation")})

    result = CliRunner().invoke(app, ["suggest", "--genre", "Horror"])

    assert result.exit_code == 0
    assert "No movies to suggest." in result.output
