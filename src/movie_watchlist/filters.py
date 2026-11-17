"""Filters that select movies from a watchlist. Each returns a new watchlist."""

from collections.abc import Callable, Iterable

from movie_watchlist.movies import Movie, Watchlist

MIN_RUNTIME_LIMIT = 1


def _filter_by_field(
    movies: Watchlist,
    wanted: str,
    label: str,
    values_of: Callable[[Movie], Iterable[str]],
) -> Watchlist:
    """Keep movies where one of their values equals the wanted text, ignoring case and spaces."""
    normalized = wanted.strip().casefold()
    if not normalized:
        raise ValueError(f"{label} cannot be empty.")
    return {
        title: movie
        for title, movie in movies.items()
        if normalized in {value.strip().casefold() for value in values_of(movie)}
    }


def filter_by_director(movies: Watchlist, director: str) -> Watchlist:
    return _filter_by_field(movies, director, "Director", lambda movie: (movie.director,))


def filter_by_actor(movies: Watchlist, actor: str) -> Watchlist:
    return _filter_by_field(movies, actor, "Actor", lambda movie: movie.actors)


def filter_by_mood(movies: Watchlist, mood: str) -> Watchlist:
    return _filter_by_field(movies, mood, "Mood", lambda movie: (movie.mood,))


def filter_by_genre(movies: Watchlist, genre: str) -> Watchlist:
    return _filter_by_field(movies, genre, "Genre", lambda movie: (movie.genre,))


def filter_by_max_runtime(movies: Watchlist, max_runtime: int) -> Watchlist:
    """Keep movies with a known runtime (above zero) up to the given limit in minutes."""
    if max_runtime < MIN_RUNTIME_LIMIT:
        raise ValueError("Maximum runtime must be positive.")
    return {title: movie for title, movie in movies.items() if 0 < movie.runtime <= max_runtime}


def apply_filters(
    movies: Watchlist,
    *,
    director: str | None = None,
    actor: str | None = None,
    max_runtime: int | None = None,
    genre: str | None = None,
    mood: str | None = None,
) -> Watchlist:
    """Apply every filter that was given; filters left as None do not change the result."""
    if director is not None:
        movies = filter_by_director(movies, director)
    if actor is not None:
        movies = filter_by_actor(movies, actor)
    if max_runtime is not None:
        movies = filter_by_max_runtime(movies, max_runtime)
    if genre is not None:
        movies = filter_by_genre(movies, genre)
    if mood is not None:
        movies = filter_by_mood(movies, mood)
    return movies
