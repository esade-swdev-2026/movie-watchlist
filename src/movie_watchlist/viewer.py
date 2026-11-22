"""A small, read-only terminal browser for saved movies."""

from collections.abc import Sequence

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

from movie_watchlist.movies import Movie

VISIBLE_ROWS = 8


def _window_bounds(index: int, total: int) -> tuple[int, int]:
    """Keep the selected movie visible in a short scrolling list."""
    if total <= VISIBLE_ROWS:
        return 0, total
    start = min(max(0, index - VISIBLE_ROWS // 2), total - VISIBLE_ROWS)
    return start, start + VISIBLE_ROWS


def _details(movie: Movie) -> str:
    """Show only watchlist fields; no poster, synopsis or year."""
    status = "Watched" if movie.watched else "To watch"
    rating = f"{movie.rating}/10" if movie.rating is not None else "—"
    runtime = f"{movie.runtime} min" if movie.runtime else "—"
    actors = ", ".join(movie.actors) or "—"
    return (
        f"{movie.title}\n"
        f"Status: {status}     Rating: {rating}\n"
        f"Genre: {movie.genre or '—'}     Runtime: {runtime}\n"
        f"Director: {movie.director or '—'}\n"
        f"Actors: {actors}\n"
        f"Mood: {movie.mood or '—'}"
    )


def browse_movies(movies: Sequence[Movie]) -> Movie | None:
    """Browse saved movies with arrow keys; exit with q, Esc or Ctrl-C."""
    if not movies:
        return None

    selected = [0]
    total = len(movies)
    watched = sum(movie.watched for movie in movies)

    def render_list() -> StyleAndTextTuples:
        start, end = _window_bounds(selected[0], total)
        lines: StyleAndTextTuples = []
        for index in range(start, end):
            movie = movies[index]
            marker = "›" if index == selected[0] else " "
            status = "✓ Watched" if movie.watched else "· To watch"
            line = f"{marker} {index + 1:>2}. {movie.title}  [{status}]"
            if index < end - 1:
                line += "\n"
            lines.append(("class:selected" if index == selected[0] else "", line))
        return lines

    def render_details() -> StyleAndTextTuples:
        return [("class:details", _details(movies[selected[0]]))]

    def render_footer() -> StyleAndTextTuples:
        return [
            (
                "class:muted",
                f"↑/↓: browse   Home/End: jump   Q/Esc: close    {selected[0] + 1}/{total}",
            )
        ]

    bindings = KeyBindings()

    @bindings.add("down", eager=True)
    @bindings.add("j", eager=True)
    def _down(_event: KeyPressEvent) -> None:
        selected[0] = min(total - 1, selected[0] + 1)
        app.invalidate()

    @bindings.add("up", eager=True)
    @bindings.add("k", eager=True)
    def _up(_event: KeyPressEvent) -> None:
        selected[0] = max(0, selected[0] - 1)
        app.invalidate()

    @bindings.add("home", eager=True)
    def _home(_event: KeyPressEvent) -> None:
        selected[0] = 0
        app.invalidate()

    @bindings.add("end", eager=True)
    def _end(_event: KeyPressEvent) -> None:
        selected[0] = total - 1
        app.invalidate()

    @bindings.add("q", eager=True)
    @bindings.add("escape", eager=True)
    @bindings.add("c-c", eager=True)
    def _close(_event: KeyPressEvent) -> None:
        app.exit(result=movies[selected[0]])

    header = Window(
        content=FormattedTextControl(
            [("class:heading", f"MY WATCHLIST   {total} movies · {watched} watched")]
        ),
        height=2,
    )
    movie_list = Window(
        content=FormattedTextControl(render_list, focusable=True),
        height=min(total, VISIBLE_ROWS),
        wrap_lines=False,
    )
    divider = Window(content=FormattedTextControl("─" * 65), height=1)
    details = Window(content=FormattedTextControl(render_details), height=7, wrap_lines=True)
    footer = Window(content=FormattedTextControl(render_footer), height=1)

    app: Application[Movie] = Application(
        layout=Layout(
            HSplit([header, movie_list, divider, details, footer]),
            focused_element=movie_list,
        ),
        key_bindings=bindings,
        style=Style.from_dict(
            {
                "heading": "bold",
                "selected": "bold ansicyan",
                "details": "",
                "muted": "ansibrightblack",
            }
        ),
        full_screen=False,
        mouse_support=False,
    )
    return app.run()
