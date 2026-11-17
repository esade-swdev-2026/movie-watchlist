"""Read and write the watchlist as JSON."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from movie_watchlist.movies import MAX_RATING, MIN_RATING, Movie, Watchlist


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
        movies[movie.title] = movie
    return movies


def _movie_from_record(record: object) -> Movie:
    if not isinstance(record, dict):
        raise ValueError("Invalid watchlist file: each movie must be an object.")
    title = _field(record, "title", str, "")
    if not title.strip():
        raise ValueError("Invalid watchlist file: a movie has no title.")
    rating = _field(record, "rating", int, None)
    if rating is not None and not MIN_RATING <= rating <= MAX_RATING:
        raise ValueError(f"Invalid watchlist file: rating of '{title}' is out of range.")
    actors = _field(record, "actors", list, [])
    if not all(isinstance(name, str) for name in actors):
        raise ValueError(f"Invalid watchlist file: actors of '{title}' must be names.")
    return Movie(
        title=title,
        watched=_field(record, "watched", bool, False),
        genre=_field(record, "genre", str, ""),
        mood=_field(record, "mood", str, ""),
        runtime=_field(record, "runtime", int, 0),
        director=_field(record, "director", str, ""),
        actors=tuple(actors),
        rating=rating,
        year=_field(record, "year", int, None),
        overview=_field(record, "overview", str, ""),
        poster_url=_field(record, "poster_url", str, ""),
    )


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
