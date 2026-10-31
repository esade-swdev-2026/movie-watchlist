"""Filter movies by actor."""

from movie_watchlist.movies import Watchlist


def filter_by_actor(movies: Watchlist, actor: str) -> Watchlist:
    actor = actor.strip().casefold()

    if not actor:
        raise ValueError("Actor cannot be empty.")

    return {
        title: movie
        for title, movie in movies.items()
        if any(name.strip().casefold() == actor for name in movie.actors)
    }
