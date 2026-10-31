import pytest

from movie_watchlist.filter_actor import filter_by_actor
from movie_watchlist.movies import Movie


@pytest.fixture
def movies() -> dict[str, Movie]:
    return {
        "Interstellar": Movie(
            title="Interstellar",
            actors=("Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"),
        ),
        "Arrival": Movie(
            title="Arrival",
            actors=("Amy Adams", "Jeremy Renner", "Forest Whitaker"),
        ),
    }


def test_matches_all_three_actor_positions(movies: dict[str, Movie]) -> None:
    for actor in movies["Interstellar"].actors:
        assert list(filter_by_actor(movies, actor)) == ["Interstellar"]


def test_ignores_case_and_spaces(movies: dict[str, Movie]) -> None:
    assert list(filter_by_actor(movies, "  ANNE HATHAWAY  ")) == ["Interstellar"]


def test_no_matches(movies: dict[str, Movie]) -> None:
    assert filter_by_actor(movies, "Unknown Actor") == {}


def test_empty_actor(movies: dict[str, Movie]) -> None:
    with pytest.raises(ValueError, match="Actor cannot be empty"):
        filter_by_actor(movies, "   ")
