"""Read and write the watchlist as JSON."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from movie_watchlist.movies import (
    MAX_MAIN_ACTORS,
    MAX_RATING,
    MIN_RATING,
    Movie,
    Watchlist,
    clean_title,
    find_saved_title,
)


def load_watchlist(path: Path) -> Watchlist:
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Could not read watchlist file.") from error
    if not isinstance(records, list):
        raise ValueError("Invalid watchlist file: expected a list of movies.")
    movies: Watchlist = {}
    for record in records:
        movie = _movie_from_record(record)
        if find_saved_title(movies, movie.title) is not None:
            raise ValueError(f"Invalid watchlist file: '{movie.title}' appears twice.")
        movies[movie.title] = movie
    return movies


def _movie_from_record(record: object) -> Movie:
    if not isinstance(record, dict):
        raise ValueError("Invalid watchlist file: each movie must be an object.")
    title = clean_title(_field(record, "title", str, ""))
    if not title:
        raise ValueError("Invalid watchlist file: a movie has no title.")
    runtime = _field(record, "runtime", int, 0)
    if runtime < 0:
        raise ValueError(f"Invalid watchlist file: runtime of '{title}' is negative.")
    rating = _field(record, "rating", int, None)
    if rating is not None and not MIN_RATING <= rating <= MAX_RATING:
        raise ValueError(f"Invalid watchlist file: rating of '{title}' is out of range.")
    actors = _without_legacy_padding(_field(record, "actors", list, []))
    if not all(isinstance(name, str) and name.strip() for name in actors):
        raise ValueError(f"Invalid watchlist file: actors of '{title}' must be names.")
    if len(actors) > MAX_MAIN_ACTORS:
        raise ValueError(f"Invalid watchlist file: '{title}' has more than three actors.")
    return Movie(
        title=title,
        watched=_field(record, "watched", bool, False),
        genre=_field(record, "genre", str, ""),
        mood=_field(record, "mood", str, ""),
        runtime=runtime,
        director=_field(record, "director", str, ""),
        actors=tuple(actors),
        rating=rating,
        year=_field(record, "year", int, None),
        overview=_field(record, "overview", str, ""),
        poster_url=_field(record, "poster_url", str, ""),
    )


LEGACY_ACTOR_SLOTS = 3


def _without_legacy_padding(actors: list[Any]) -> list[Any]:
    """Drop the "" padding that older versions saved after the actors.

    Older versions always stored exactly three actors, filling the empty slots with ""
    (for example ["Ed Asner", "", ""]). Only that shape is cleaned up; a blank name in
    any other list is left in place so the loader still rejects it.
    """
    if len(actors) != LEGACY_ACTOR_SLOTS:
        return actors
    trimmed = list(actors)
    while trimmed and trimmed[-1] == "":
        trimmed.pop()
    return trimmed


def _field(record: dict[str, object], name: str, kind: type, default: object) -> Any:
    """Return the stored value if it has the expected type; booleans are not accepted as numbers."""
    value = record.get(name, default)
    if value is None and default is None:
        return None
    is_number_field = kind is int
    wrong_type = not isinstance(value, kind) or (is_number_field and isinstance(value, bool))
    if wrong_type:
        raise ValueError(f"Invalid watchlist file: '{name}' has the wrong type.")
    return value


def save_watchlist(path: Path, movies: Watchlist) -> None:
    saved_movies = [asdict(movie) for movie in movies.values()]
    path.write_text(json.dumps(saved_movies, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
