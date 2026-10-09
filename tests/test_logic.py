import pytest

from movie_watchlist.logic import (
    add_movie,
    average_rating,
    clean_title,
    is_duplicate,
    mark_watched,
    unwatched_titles,
)


@pytest.fixture
def movies() -> dict[str, bool]:
    return {"Interstellar": False, "Arrival": True}


def test_clean_title_removes_surrounding_spaces() -> None:
    assert clean_title("  Amélie  ") == "Amélie"


def test_duplicate_title_ignores_case(movies: dict[str, bool]) -> None:
    assert is_duplicate(movies, "  interstellar  ")


def test_add_rejects_empty_title() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        add_movie({}, "   ")


def test_add_rejects_duplicate(movies: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="already exists"):
        add_movie(movies, "interstellar")


def test_add_accepts_different_titles(movies: dict[str, bool]) -> None:
    updated = add_movie(movies, "Amélie")
    assert updated["Amélie"] is False
    assert "Amélie" not in movies


def test_watch_marks_movie_and_keeps_original(movies: dict[str, bool]) -> None:
    updated = mark_watched(movies, "interstellar")
    assert updated["Interstellar"] is True
    assert movies["Interstellar"] is False


def test_unwatched_excludes_watched_movies(movies: dict[str, bool]) -> None:
    assert unwatched_titles(movies) == ["Interstellar"]


@pytest.mark.parametrize(
    ("ratings", "expected"),
    [([], 0.0), ([4.0, 5.0], 4.5)],
)
def test_average_rating_handles_empty_and_regular_lists(
    ratings: list[float], expected: float
) -> None:
    assert average_rating(ratings) == pytest.approx(expected)
