import pytest

from movie_watchlist.filter_mood import filter_by_mood
from movie_watchlist.movies import Movie


@pytest.fixture
def movies() -> dict[str, Movie]:
    return {
        "Interstellar": Movie(title="Interstellar", mood="Emotional"),
        "Arrival": Movie(title="Arrival", mood="Thoughtful"),
        "Up": Movie(title="Up", mood="emotional"),
        "Amélie": Movie(title="Amélie"),
    }


def test_filter_keeps_matching_moods_ignoring_case(movies: dict[str, Movie]) -> None:
    assert list(filter_by_mood(movies, "  EMOTIONAL  ")) == ["Interstellar", "Up"]


def test_filter_returns_empty_when_nothing_matches(movies: dict[str, Movie]) -> None:
    assert filter_by_mood(movies, "Scary") == {}


def test_filter_rejects_empty_mood(movies: dict[str, Movie]) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        filter_by_mood(movies, "   ")


def test_filter_keeps_original(movies: dict[str, Movie]) -> None:
    filter_by_mood(movies, "Thoughtful")

    assert len(movies) == 4
