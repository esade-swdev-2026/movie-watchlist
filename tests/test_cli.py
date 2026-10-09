from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Adjust to however your app decides where to save (env var, constant, etc.)
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(tmp_path / "watchlist.json"))
 
 
@pytest.fixture
def two_movies() -> None:
    """Data shared by several tests: a watchlist with two movies."""
    runner.invoke(app, ["add", "Interstellar"])
    runner.invoke(app, ["add", "Arrival"])
 
 
def test_add_reports_the_movie_title() -> None:
    result = runner.invoke(app, ["add", "Interstellar"])
 
    assert result.exit_code == 0
    assert "Interstellar" in result.stdout
 
 
@pytest.mark.parametrize("title", ["   ", "\t", " \t "])
def test_add_rejects_an_empty_title(title: str) -> None:
    result = runner.invoke(app, ["add", title])
 
    assert result.exit_code == 1
 
 
def test_add_rejects_a_duplicate_title(two_movies: None) -> None:
    result = runner.invoke(app, ["add", "Interstellar"])
 
    assert result.exit_code == 1
 
 
def test_list_shows_added_movies(two_movies: None) -> None:
    result = runner.invoke(app, ["list"])
 
    assert result.exit_code == 0
    assert "Interstellar" in result.stdout
    assert "Arrival" in result.stdout
 
 
def test_list_on_an_empty_watchlist_shows_no_movies() -> None:
    result = runner.invoke(app, ["list"])
 
    assert result.exit_code == 0
    assert "Interstellar" not in result.stdout
 
 
def test_add_accepts_two_different_titles() -> None:
    first = runner.invoke(app, ["add", "Interstellar"])
    second = runner.invoke(app, ["add", "Arrival"])
 
    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "Arrival" in second.stdout
 
 
def test_add_accepts_a_title_with_special_characters() -> None:
    result = runner.invoke(app, ["add", "Amélie"])
 
    assert result.exit_code == 0
    assert "Amélie" in result.stdout
 
 
def test_watch_marks_a_movie_as_watched(two_movies: None) -> None:
    result = runner.invoke(app, ["watch", "Interstellar"])
 
    assert result.exit_code == 0
    assert "Interstellar" in result.stdout