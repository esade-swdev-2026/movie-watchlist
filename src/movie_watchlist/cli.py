"""Command-line interface: parses arguments, calls the core, and prints the results."""

import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer

from movie_watchlist.filters import apply_filters, filter_by_genre, filter_by_mood
from movie_watchlist.interactive import collect_movie_details
from movie_watchlist.movies import (
    MAX_RATING,
    MIN_RATING,
    Movie,
    Watchlist,
    add_movie,
    clean_title,
    mark_watched,
    rate_movie,
)
from movie_watchlist.storage import load_watchlist, save_watchlist
from movie_watchlist.suggest import suggest_movie

STATUS_WATCHED = "watched"
STATUS_TO_WATCH = "to watch"
EXIT_FAILURE = 1

WATCHLIST_ENV_VAR = "MOVIE_WATCHLIST_FILE"
DEFAULT_WATCHLIST_FILENAME = ".movie_watchlist.json"


def watchlist_path() -> Path:
    """The JSON file that stores the watchlist, from the environment or the home folder."""
    default = Path.home() / DEFAULT_WATCHLIST_FILENAME
    return Path(os.environ.get(WATCHLIST_ENV_VAR, str(default)))


app = typer.Typer(help="Keep track of movies you want to watch.")


@contextmanager
def exit_on_error() -> Iterator[None]:
    """Print a failure from the core or storage to stderr and exit with a failure code."""
    try:
        yield
    except (ValueError, OSError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=EXIT_FAILURE) from error


def format_movie_line(movie: Movie) -> str:
    status = STATUS_WATCHED if movie.watched else STATUS_TO_WATCH
    return f"{movie.title} — {status}"


def echo_movies(movies: Watchlist) -> None:
    for movie in movies.values():
        typer.echo(format_movie_line(movie))


@app.command()
def add(
    title: str,
    watched: bool = typer.Option(False, "--watched", help="Mark the movie as already watched."),
    director: str = typer.Option("", "--director", help="Movie director."),
    runtime: int | None = typer.Option(None, "--runtime", help="Movie runtime in minutes."),
    mood: str = typer.Option("", "--mood", help="The mood the movie fits, e.g. Emotional."),
    genre: str = typer.Option("", "--genre", help="Movie genre, e.g. Animation."),
    actor: Annotated[
        list[str] | None,
        typer.Option("--actor", help="A main actor. Repeat up to three times."),
    ] = None,
    rating: Annotated[
        int | None,
        typer.Option("--rating", help="Your rating from 1 to 10. Required with --watched."),
    ] = None,
    interactive: Annotated[
        bool | None,
        typer.Option(
            "--interactive/--no-interactive",
            help="Use the guided form; auto-opens for bare adds in a terminal.",
        ),
    ] = None,
) -> None:
    """Add a movie to your watchlist."""
    with exit_on_error():
        given_options = (
            watched
            or bool(director)
            or runtime is not None
            or bool(mood)
            or bool(genre)
            or actor is not None
            or rating is not None
        )
        tty = sys.stdin.isatty() and sys.stdout.isatty()
        use_form = interactive if interactive is not None else tty and not given_options
        if use_form:
            if given_options:
                raise ValueError("Do not combine --interactive with individual movie options.")
            if not tty:
                raise ValueError("Interactive mode requires a terminal.")
            details = collect_movie_details(title)
            if details is None:
                typer.echo("Cancelled.")
                return
            watched = details.watched
            director = details.director
            runtime = details.runtime
            mood = details.mood
            genre = details.genre
            actor = details.actors
            rating = details.rating
        movies = add_movie(
            load_watchlist(watchlist_path()),
            title,
            watched=watched,
            director=director,
            runtime=runtime,
            mood=mood,
            genre=genre,
            actors=actor,
            rating=rating,
        )
        save_watchlist(watchlist_path(), movies)

    status = STATUS_WATCHED if watched else STATUS_TO_WATCH
    typer.echo(f'Added "{clean_title(title)}" — {status}.')


@app.command("list")
def list_movies(
    director: str | None = typer.Option(None, "--director", help="Filter movies by director."),
    actor: str | None = typer.Option(None, "--actor", help="Filter movies by actor."),
    max_runtime: int | None = typer.Option(
        None, "--max-runtime", help="Maximum runtime in minutes."
    ),
    genre: str | None = typer.Option(None, "--genre", help="Filter movies by genre."),
    mood: str | None = typer.Option(None, "--mood", help="Filter movies by mood."),
) -> None:
    """Show the movies in your watchlist."""
    with exit_on_error():
        movies = apply_filters(
            load_watchlist(watchlist_path()),
            director=director,
            actor=actor,
            max_runtime=max_runtime,
            genre=genre,
            mood=mood,
        )

    if not movies:
        has_filter = any(value is not None for value in (director, actor, max_runtime, genre, mood))
        typer.echo("No matching movies." if has_filter else "Your watchlist is empty.")
        return
    echo_movies(movies)


@app.command()
def suggest(
    director: str | None = typer.Option(
        None, "--director", help="Only suggest this director's movies."
    ),
    actor: str | None = typer.Option(None, "--actor", help="Only suggest movies with this actor."),
    max_runtime: int | None = typer.Option(
        None, "--max-runtime", help="Maximum runtime in minutes."
    ),
    genre: str | None = typer.Option(None, "--genre", help="Only suggest this genre."),
    mood: str | None = typer.Option(None, "--mood", help="Only suggest this mood."),
) -> None:
    """Suggest what to watch next."""
    with exit_on_error():
        movies = apply_filters(
            load_watchlist(watchlist_path()),
            director=director,
            actor=actor,
            max_runtime=max_runtime,
            genre=genre,
            mood=mood,
        )

    movie = suggest_movie(movies)
    if movie is None:
        typer.echo("No movies to suggest.")
        return
    typer.echo(f"Suggestion: {movie.title}")


@app.command("mood")
def list_by_mood(mood: str) -> None:
    """Show the movies that fit a mood."""
    with exit_on_error():
        movies = filter_by_mood(load_watchlist(watchlist_path()), mood)

    if not movies:
        typer.echo(f'No movies with the mood "{mood.strip()}".')
        return
    echo_movies(movies)


@app.command()
def watch(
    title: str,
    rating: Annotated[
        int,
        typer.Option(
            "--rating",
            min=MIN_RATING,
            max=MAX_RATING,
            help="Your rating from 1 to 10. Required: marking a film as watched rates it too.",
        ),
    ],
) -> None:
    """Mark a movie as watched and rate it in the same step."""
    with exit_on_error():
        movies = mark_watched(load_watchlist(watchlist_path()), title)
        movies = rate_movie(movies, title, rating)
        save_watchlist(watchlist_path(), movies)

    typer.echo(f'Marked "{clean_title(title)}" as watched, rated {rating}/{MAX_RATING}.')


@app.command()
def rate(title: str, rating: int) -> None:
    """Rate a movie from 1 to 10."""
    with exit_on_error():
        movies = rate_movie(load_watchlist(watchlist_path()), title, rating)
        save_watchlist(watchlist_path(), movies)

    typer.echo(f'Rated "{clean_title(title)}" {rating}/{MAX_RATING}.')


@app.command("filter-genre")
def filter_movies_by_genre(genre: str) -> None:
    """Show movies matching a genre."""
    with exit_on_error():
        movies = filter_by_genre(load_watchlist(watchlist_path()), genre)

    if not movies:
        typer.echo(f'No movies found for genre "{genre}".')
        return
    echo_movies(movies)
