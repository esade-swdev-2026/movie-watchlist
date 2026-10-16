"""Read and write the watchlist as JSON."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from movie_watchlist.movies import Movie, Watchlist


def load_watchlist(path: Path) -> Watchlist:
    try:
        saved_movies: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Could not read watchlist file.") from error

    try:
        movies: Watchlist = {}
        for movie_data in saved_movies:
            movie_data["actors"] = tuple(movie_data.get("actors", ("", "", "")))
            movie = Movie(**movie_data)
            movies[movie.title] = movie
        return movies
    except (TypeError, ValueError, KeyError, AttributeError) as error:
        raise ValueError("Invalid watchlist file.") from error


def save_watchlist(path: Path, movies: Watchlist) -> None:
    saved_movies = [asdict(movie) for movie in movies.values()]
    path.write_text(json.dumps(saved_movies, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
