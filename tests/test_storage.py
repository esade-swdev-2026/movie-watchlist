from pathlib import Path

import pytest

from movie_watchlist.movies import Movie
from movie_watchlist.storage import load_watchlist, save_watchlist


def test_missing_file_returns_empty_watchlist(tmp_path: Path) -> None:
    assert load_watchlist(tmp_path / "movies.json") == {}


def test_save_and_load_movies_with_details(tmp_path: Path) -> None:
    path = tmp_path / "movies.json"
    movies = {
        "Interstellar": Movie(
            title="Interstellar",
            watched=True,
            genre="Sci-Fi",
            mood="Thoughtful",
            runtime=169,
            director="Christopher Nolan",
            actors=("Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"),
        )
    }

    save_watchlist(path, movies)

    assert load_watchlist(path) == movies


def test_invalid_json_raises_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "movies.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not read watchlist file"):
        load_watchlist(path)


def test_invalid_movie_data_raises_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "movies.json"
    path.write_text('[{"watched": true}]', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid watchlist file"):
        load_watchlist(path)
