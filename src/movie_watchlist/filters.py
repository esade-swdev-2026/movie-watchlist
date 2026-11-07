"""Functions for filtering movies in a watchlist."""

from movie_watchlist.movies import Watchlist


def filter_by_director(movies: Watchlist, director: str) -> Watchlist:
    """Return movies matching the selected director."""
    normalized_director = director.strip().casefold()

    if not normalized_director:
        raise ValueError("Director cannot be empty.")

    return {
        title: movie
        for title, movie in movies.items()
        if movie.director.strip().casefold() == normalized_director
    }


def filter_by_max_runtime(movies: Watchlist, max_runtime: int) -> Watchlist:
    """Return movies with a known runtime up to the given limit."""
    if max_runtime <= 0:
        raise ValueError("Maximum runtime must be positive.")

    return {title: movie for title, movie in movies.items() if 0 < movie.runtime <= max_runtime}
