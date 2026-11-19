import json
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
            rating=8,
            director="Christopher Nolan",
            actors=("Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"),
        )
    }

    save_watchlist(path, movies)

    assert load_watchlist(path) == movies
    assert load_watchlist(path)["Interstellar"].rating == 8


def _write(path: Path, records: str) -> Path:
    path.write_text(records, encoding="utf-8")
    return path


def test_load_rejects_negative_runtime(tmp_path: Path) -> None:
    path = _write(tmp_path / "m.json", '[{"title": "Up", "runtime": -5}]')

    with pytest.raises(ValueError, match="runtime"):
        load_watchlist(path)


def test_load_allows_zero_runtime_as_unknown(tmp_path: Path) -> None:
    path = _write(tmp_path / "m.json", '[{"title": "Up", "runtime": 0}]')

    assert load_watchlist(path)["Up"].runtime == 0


def test_load_rejects_more_than_three_actors(tmp_path: Path) -> None:
    path = _write(tmp_path / "m.json", '[{"title": "Up", "actors": ["A", "B", "C", "D"]}]')

    with pytest.raises(ValueError, match="three actors"):
        load_watchlist(path)


def test_load_rejects_empty_actor_names(tmp_path: Path) -> None:
    path = _write(tmp_path / "m.json", '[{"title": "Up", "actors": ["A", "  "]}]')

    with pytest.raises(ValueError, match="actors"):
        load_watchlist(path)


def test_load_file_saved_by_previous_version(tmp_path: Path) -> None:
    # The previous version always padded actors to three with "".
    full_cast = ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"]
    records = [
        {"title": "Up", "watched": False, "actors": ["", "", ""]},
        {"title": "Big Fish", "watched": True, "actors": ["Ewan McGregor", "", ""]},
        {"title": "Arrival", "watched": True, "actors": ["Amy Adams", "Jeremy Renner", ""]},
        {"title": "Interstellar", "actors": full_cast},
    ]
    path = _write(tmp_path / "m.json", json.dumps(records))

    movies = load_watchlist(path)

    assert movies["Up"].actors == ()
    assert movies["Big Fish"].actors == ("Ewan McGregor",)
    assert movies["Arrival"].actors == ("Amy Adams", "Jeremy Renner")
    assert len(movies["Interstellar"].actors) == 3


@pytest.mark.parametrize("actors", [["", "Ed Asner", ""], ["Ed Asner", ""], [""], ["  ", "", ""]])
def test_load_still_rejects_blank_actors_outside_the_old_padding(
    tmp_path: Path, actors: list[str]
) -> None:
    path = _write(tmp_path / "m.json", json.dumps([{"title": "Up", "actors": actors}]))

    with pytest.raises(ValueError, match="actors"):
        load_watchlist(path)


def test_load_trims_titles(tmp_path: Path) -> None:
    path = _write(tmp_path / "m.json", '[{"title": "  Up  "}]')

    movies = load_watchlist(path)

    assert list(movies) == ["Up"]
    assert movies["Up"].title == "Up"


def test_load_rejects_titles_that_differ_only_in_case(tmp_path: Path) -> None:
    path = _write(tmp_path / "m.json", '[{"title": "Arrival"}, {"title": "arrival"}]')

    with pytest.raises(ValueError, match="twice"):
        load_watchlist(path)


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


def test_load_old_movie_without_rating(tmp_path: Path) -> None:
    path = tmp_path / "movies.json"
    path.write_text(
        '[{"title": "Arrival", "watched": true}]',
        encoding="utf-8",
    )

    movies = load_watchlist(path)

    assert movies["Arrival"].rating is None
