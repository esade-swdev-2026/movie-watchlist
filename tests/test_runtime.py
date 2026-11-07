from copy import deepcopy

import pytest

from movie_watchlist.filters import filter_by_max_runtime
from movie_watchlist.movies import Movie


@pytest.fixture
def movies() -> dict[str, Movie]:
    return {
        "Interstellar": Movie(title="Interstellar", runtime=169),
        "Inception": Movie(title="Inception", runtime=148),
        "Toy Story": Movie(title="Toy Story", runtime=81),
        "Unknown": Movie(title="Unknown", runtime=0),
    }


def test_filter_includes_movies_within_limit(
    movies: dict[str, Movie],
) -> None:
    result = filter_by_max_runtime(movies, 148)

    assert list(result) == ["Inception", "Toy Story"]


def test_filter_excludes_unknown_runtime(
    movies: dict[str, Movie],
) -> None:
    result = filter_by_max_runtime(movies, 200)

    assert "Unknown" not in result


@pytest.mark.parametrize("limit", [0, -10])
def test_filter_rejects_invalid_limit(movies: dict[str, Movie], limit: int) -> None:
    with pytest.raises(ValueError):
        filter_by_max_runtime(movies, limit)


def test_filter_does_not_modify_original(
    movies: dict[str, Movie],
) -> None:
    original_movies = deepcopy(movies)

    filter_by_max_runtime(movies, 100)

    assert movies == original_movies
