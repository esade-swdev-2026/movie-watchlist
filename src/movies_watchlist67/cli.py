import typer

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
    """Add a movie to your watchlist."""
    title = title.strip()

    if not title:
        typer.echo("Movie title cannot be empty.", err=True)
        raise typer.Exit(code=1)

    status = "watched ✓" if watched else "to watch"
    typer.echo(f'🎬 Added "{title}" — {status}.')
