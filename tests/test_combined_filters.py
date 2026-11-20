from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app
from movie_watchlist.movies import Movie
from movie_watchlist.storage import load_watchlist, save_watchlist


@pytest.fixture
def watchlist_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))
    return path


def test_add_stores_genre(watchlist_file: Path) -> None:
    result = CliRunner().invoke(app, ["add", "Up", "--genre", "Animation"])

    assert result.exit_code == 0
    assert load_watchlist(watchlist_file)["Up"].genre == "Animation"


def test_add_stores_up_to_three_actors(watchlist_file: Path) -> None:
    result = CliRunner().invoke(
        app, ["add", "Arrival", "--actor", "Amy Adams", "--actor", "Jeremy Renner"]
    )

    assert result.exit_code == 0
    assert load_watchlist(watchlist_file)["Arrival"].actors == ("Amy Adams", "Jeremy Renner")


def test_add_rejects_more_than_three_actors(watchlist_file: Path) -> None:
    result = CliRunner().invoke(
        app, ["add", "Arrival", "--actor", "A", "--actor", "B", "--actor", "C", "--actor", "D"]
    )

    assert result.exit_code == 1
    assert "At most three actors." in result.output
    assert not watchlist_file.exists()


def test_list_combines_genre_and_mood(watchlist_file: Path) -> None:
    save_watchlist(
        watchlist_file,
        {
            "Up": Movie(title="Up", genre="Animation", mood="Emotional"),
            "Shrek": Movie(title="Shrek", genre="Animation", mood="Funny"),
            "Arrival": Movie(title="Arrival", genre="Sci-Fi", mood="Emotional"),
        },
    )

    result = CliRunner().invoke(app, ["list", "--genre", "Animation", "--mood", "Emotional"])

    assert result.exit_code == 0
    assert "Up — to watch" in result.output
    assert "Shrek" not in result.output
    assert "Arrival" not in result.output


def test_list_combines_actor_and_max_runtime(watchlist_file: Path) -> None:
    save_watchlist(
        watchlist_file,
        {
            "Arrival": Movie(title="Arrival", runtime=116, actors=("Amy Adams", "Jeremy Renner")),
            "Enemy": Movie(title="Enemy", runtime=91, actors=("Jake Gyllenhaal",)),
            "Long Adams": Movie(title="Long Adams", runtime=150, actors=("Amy Adams",)),
        },
    )

    result = CliRunner().invoke(app, ["list", "--actor", "Amy Adams", "--max-runtime", "120"])

    assert result.exit_code == 0
    assert "Arrival" in result.output
    assert "Enemy" not in result.output  # excluded by the actor filter
    assert "Long Adams" not in result.output  # excluded by the runtime filter


def test_add_accepts_exactly_three_actors(watchlist_file: Path) -> None:
    result = CliRunner().invoke(
        app, ["add", "Arrival", "--actor", "A", "--actor", "B", "--actor", "C"]
    )

    assert result.exit_code == 0
    assert load_watchlist(watchlist_file)["Arrival"].actors == ("A", "B", "C")


def test_list_filters_by_genre_alone(watchlist_file: Path) -> None:
    save_watchlist(
        watchlist_file,
        {
            "Up": Movie(title="Up", genre="Animation"),
            "Arrival": Movie(title="Arrival", genre="Sci-Fi"),
        },
    )

    result = CliRunner().invoke(app, ["list", "--genre", "Animation"])

    assert result.exit_code == 0
    assert "Up" in result.output
    assert "Arrival" not in result.output


def test_list_rejects_empty_mood(watchlist_file: Path) -> None:
    save_watchlist(watchlist_file, {"Up": Movie(title="Up")})

    result = CliRunner().invoke(app, ["list", "--mood", "  "])

    assert result.exit_code == 1
    assert "Mood cannot be empty." in result.output


def test_list_rejects_empty_genre(watchlist_file: Path) -> None:
    save_watchlist(watchlist_file, {"Up": Movie(title="Up")})

    result = CliRunner().invoke(app, ["list", "--genre", ""])

    assert result.exit_code == 1
    assert "Genre cannot be empty." in result.output
