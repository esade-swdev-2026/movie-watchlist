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
