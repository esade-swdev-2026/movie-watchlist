"""Filter watchlist movies by mood."""

from movie_watchlist.movies import Watchlist


def filter_by_mood(movies: Watchlist, mood: str) -> Watchlist:
    wanted = mood.strip().casefold()
    if not wanted:
        raise ValueError("Mood cannot be empty.")
    return {
        title: movie for title, movie in movies.items() if movie.mood.strip().casefold() == wanted
    }
