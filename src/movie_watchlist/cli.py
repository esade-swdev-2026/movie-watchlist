import typer

from movie_watchlist.logic import add_movie, clean_title

app = typer.Typer(help="A simple movie watchlist :)")


@app.callback()
def main() -> None:
    """Keep track of movies you want to watch."""


@app.command()
def add(
    title: str,
    watched: bool = typer.Option(
        False,
        "--watched",
        help="Mark the movie as already watched.",
    ),
) -> None:
    """Validate and report a movie added to the watchlist."""
    title = clean_title(title)
    try:
        add_movie({}, title)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    status = "watched ✓" if watched else "to watch"
    typer.echo(f'🎬 Added "{title}" — {status}.')
