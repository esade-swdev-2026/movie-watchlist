"""Keyboard-navigable terminal form for adding a movie."""

from dataclasses import dataclass
from functools import partial

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea


@dataclass(frozen=True)
class MovieDetails:
    genre: str
    mood: str
    runtime: int | None
    director: str
    actors: list[str]
    watched: bool
    rating: int | None


class FormError(ValueError):
    """An invalid form field and the message to show to the user."""

    def __init__(self, field_index: int, message: str) -> None:
        super().__init__(message)
        self.field_index = field_index


FIELDS = (
    "Genre",
    "Mood",
    "Runtime (minutes)",
    "Director",
    "Actors (comma-separated)",
    "Watched (y/N)",
    "Rating (1-10)",
)


def _parse_answers(answers: list[str]) -> MovieDetails:
    genre, mood, raw_runtime, director, raw_actors, raw_watched, raw_rating = (
        value.strip() for value in answers
    )

    runtime: int | None = None
    if raw_runtime:
        try:
            runtime = int(raw_runtime)
        except ValueError as error:
            raise FormError(2, "Runtime must be a whole number of minutes.") from error
        if runtime <= 0:
            raise FormError(2, "Runtime must be positive.")

    actors = [name.strip() for name in raw_actors.split(",")] if raw_actors else []
    if any(not name for name in actors):
        raise FormError(4, "Actor names cannot be blank between commas.")
    if len(actors) > 3:
        raise FormError(4, "At most three actors.")

    watched_text = raw_watched.casefold()
    if watched_text not in ("", "y", "yes", "n", "no"):
        raise FormError(5, "Watched must be yes/y or no/n (or left blank).")
    watched = watched_text in ("y", "yes")

    rating: int | None = None
    if raw_rating:
        try:
            rating = int(raw_rating)
        except ValueError as error:
            raise FormError(6, "Rating must be a whole number from 1 to 10.") from error
        if not 1 <= rating <= 10:
            raise FormError(6, "Rating must be between 1 and 10.")
    if watched and rating is None:
        raise FormError(6, "A watched movie needs a rating.")

    return MovieDetails(
        genre=genre,
        mood=mood,
        runtime=runtime,
        director=director,
        actors=actors,
        watched=watched,
        rating=rating,
    )


def collect_movie_details(title: str) -> MovieDetails | None:
    """Return entered details, or None if the user cancels with Esc/Ctrl-C."""
    inputs = [TextArea(height=1, multiline=False, wrap_lines=False) for _ in FIELDS]
    active = [0]
    error_message = [""]

    def label_for(index: int) -> StyleAndTextTuples:
        selected = active[0] == index
        prefix = "> " if selected else "  "
        return [("class:active" if selected else "class:label", f"{prefix}{FIELDS[index]}")]

    rows = [
        VSplit(
            [
                Window(
                    content=FormattedTextControl(partial(label_for, i)),
                    width=29,
                    dont_extend_width=True,
                ),
                inputs[i],
            ],
            height=1,
        )
        for i in range(len(FIELDS))
    ]

    def change_field(next_index: int) -> None:
        if 0 <= next_index < len(FIELDS):
            active[0] = next_index
            error_message[0] = ""
            app.layout.focus(inputs[next_index])
            app.invalidate()

    def finish() -> None:
        try:
            result = _parse_answers([field.text for field in inputs])
        except FormError as error:
            change_field(error.field_index)
            error_message[0] = str(error)
            app.invalidate()
            return
        app.exit(result=result)

    bindings = KeyBindings()

    @bindings.add("enter", eager=True)
    def _next_field(_event: KeyPressEvent) -> None:
        if active[0] == len(FIELDS) - 1:
            finish()
        else:
            change_field(active[0] + 1)

    @bindings.add("down", eager=True)
    @bindings.add("tab", eager=True)
    def _down(_event: KeyPressEvent) -> None:
        change_field(active[0] + 1)

    @bindings.add("up", eager=True)
    @bindings.add("s-tab", eager=True)
    def _up(_event: KeyPressEvent) -> None:
        change_field(active[0] - 1)

    @bindings.add("escape", eager=True)
    @bindings.add("c-c", eager=True)
    def _cancel(_event: KeyPressEvent) -> None:
        app.exit(result=None)

    def footer() -> StyleAndTextTuples:
        if error_message[0]:
            return [("class:error", error_message[0])]
        return [("class:hint", "Up/Down: move   Enter: next/save   Esc: cancel   Blank: skip")]

    header = Window(
        content=FormattedTextControl([("class:heading", f"Add movie: {title}")]),
        height=2,
    )
    footer_window = Window(content=FormattedTextControl(footer), height=1)
    root = HSplit([header, *rows, footer_window])
    style = Style.from_dict(
        {
            "heading": "bold",
            "label": "",
            "active": "bold ansicyan",
            "hint": "ansibrightblack",
            "error": "ansired bold",
        }
    )
    app: Application[MovieDetails | None] = Application(
        layout=Layout(root, focused_element=inputs[0]),
        key_bindings=bindings,
        style=style,
        full_screen=False,
        mouse_support=False,
    )
    return app.run()
