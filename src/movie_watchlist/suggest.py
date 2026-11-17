"""Choose what to watch next from the movies not yet watched."""

from movie_watchlist.movies import Movie, Watchlist


def suggest_movie(movies: Watchlist) -> Movie | None:
    """Return the highest rated unwatched movie, ties broken by title, or None."""
    unwatched = [movie for movie in movies.values() if not movie.watched]
    if not unwatched:
        return None
    return min(unwatched, key=lambda movie: (-(movie.rating or 0), movie.title))
