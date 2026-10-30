import os
from pathlib import Path

import typer

from movie_watchlist.movies import (
    add_movie,
    clean_title,
    filter_by_genre,
    mark_watched,
)
from movie_watchlist.storage import load_watchlist, save_watchlist

app = typer.Typer(help="Keep track of movies you want to watch.")


def watchlist_path() -> Path:
    return Path(os.environ.get("MOVIE_WATCHLIST_FILE", str(Path.home() / ".movie_watchlist.json")))


@app.command()
def add(
    title: str,
    watched: bool = typer.Option(False, "--watched", help="Mark the movie as already watched."),
) -> None:
    """Add a movie to your watchlist."""
    try:
        movies = add_movie(load_watchlist(watchlist_path()), title, watched=watched)
        save_watchlist(watchlist_path(), movies)
    except (ValueError, OSError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    status = "watched" if watched else "to watch"
    typer.echo(f'Added "{clean_title(title)}" — {status}.')


@app.command("list")
def list_movies() -> None:
    """Show the movies in your watchlist."""
    try:
        movies = load_watchlist(watchlist_path())
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    if not movies:
        typer.echo("Your watchlist is empty.")
        return

    for movie in movies.values():
        status = "watched" if movie.watched else "to watch"
        typer.echo(f"{movie.title} — {status}")


@app.command()
def watch(title: str) -> None:
    """Mark a movie as watched."""
    try:
        movies = mark_watched(load_watchlist(watchlist_path()), title)
        save_watchlist(watchlist_path(), movies)
    except (ValueError, OSError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f'Marked "{clean_title(title)}" as watched.')


@app.command("filter-genre")
def filter_movies_by_genre(genre: str) -> None:
    """Show movies matching a genre."""
    try:
        movies = filter_by_genre(load_watchlist(watchlist_path()), genre)
    except (ValueError, OSError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    if not movies:
        typer.echo(f'No movies found for genre "{genre}".')
        return

    for movie in movies.values():
        status = "watched" if movie.watched else "to watch"
        typer.echo(f"{movie.title} — {status}")
