import pytest

from movie_watchlist.filters import filter_by_director
from movie_watchlist.movies import Movie, Watchlist


@pytest.fixture
def movies() -> Watchlist:
    return {
        "Inception": Movie(title="Inception", director="Christopher Nolan"),
        "Interstellar": Movie(title="Interstellar", director="Christopher Nolan"),
        "Titanic": Movie(title="Titanic", director="James Cameron"),
    }


def test_filter_by_director_returns_matching_movies(movies: Watchlist) -> None:
    result = filter_by_director(movies, "Christopher Nolan")

    assert list(result) == ["Inception", "Interstellar"]


def test_filter_by_director_ignores_case_and_spaces(movies: Watchlist) -> None:
    result = filter_by_director(movies, "  christopher nolan  ")

    assert list(result) == ["Inception", "Interstellar"]


def test_filter_by_director_returns_empty_when_no_match(movies: Watchlist) -> None:
    result = filter_by_director(movies, "Steven Spielberg")

    assert result == {}


def test_filter_by_director_rejects_empty_name(movies: Watchlist) -> None:
    with pytest.raises(ValueError, match="Director cannot be empty"):
        filter_by_director(movies, "   ")
