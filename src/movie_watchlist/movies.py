"""Watchlist operations independent of files and command-line output."""

from dataclasses import dataclass, replace


@dataclass
class Movie:
    title: str
    watched: bool = False
    genre: str = ""
    mood: str = ""
    runtime: int = 0
    director: str = ""
    actors: tuple[str, str, str] = ("", "", "")


type Watchlist = dict[str, Movie]


def clean_title(title: str) -> str:
    return title.strip()


def is_duplicate(movies: Watchlist, title: str) -> bool:
    return any(saved.casefold() == clean_title(title).casefold() for saved in movies)


def add_movie(movies: Watchlist, title: str, watched: bool = False) -> Watchlist:
    title = clean_title(title)
    if not title:
        raise ValueError("Movie title cannot be empty.")
    if is_duplicate(movies, title):
        raise ValueError("Movie already exists.")
    return {**movies, title: Movie(title=title, watched=watched)}


def mark_watched(movies: Watchlist, title: str) -> Watchlist:
    for saved in movies:
        if saved.casefold() == clean_title(title).casefold():
            return {**movies, saved: replace(movies[saved], watched=True)}
    raise ValueError("Movie not found.")


def unwatched_titles(movies: Watchlist) -> list[str]:
    return [title for title, movie in movies.items() if not movie.watched]


def average_rating(ratings: list[float]) -> float:
    return sum(ratings) / len(ratings) if ratings else 0.0
