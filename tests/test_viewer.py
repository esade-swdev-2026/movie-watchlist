"""The movie viewer shows details without changing stored data."""

from typing import Any

import pytest
from prompt_toolkit import Application
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

import movie_watchlist.viewer as viewer
from movie_watchlist.movies import Movie
from movie_watchlist.viewer import _details, _window_bounds


def test_details_show_watchlist_fields_only() -> None:
    movie = Movie(
        title="Oppenheimer",
        genre="Drama",
        runtime=181,
        director="Christopher Nolan",
        actors=("Cillian Murphy", "Emily Blunt", "Matt Damon"),
        watched=True,
        rating=9,
        mood="Intense",
        year=2023,
        overview="Do not show this text",
        poster_url="https://example.com/poster.jpg",
    )
    visible = _details(movie)
    for expected in (
        "Oppenheimer",
        "Drama",
        "181 min",
        "Christopher Nolan",
        "Cillian Murphy",
        "Watched",
        "9/10",
        "Intense",
    ):
        assert expected in visible
    assert "2023" not in visible
    assert "Do not show this text" not in visible
    assert "poster" not in visible


def test_missing_fields_have_clear_placeholders() -> None:
    visible = _details(Movie(title="Arrival"))
    assert "To watch" in visible
    assert "Rating: —" in visible
    assert "Runtime: —" in visible
    assert "Actors: —" in visible


def test_long_watchlist_scrolls_without_hiding_selection() -> None:
    assert _window_bounds(0, 20) == (0, 8)
    assert _window_bounds(10, 20) == (6, 14)
    assert _window_bounds(19, 20) == (12, 20)
    assert _window_bounds(1, 2) == (0, 2)


def test_arrow_keys_select_movies(monkeypatch: pytest.MonkeyPatch) -> None:
    original = Application
    movies = [Movie(title="Arrival"), Movie(title="Oppenheimer"), Movie(title="Dune")]
    with create_pipe_input() as pipe:

        def test_app(**kwargs: Any) -> Application[Movie]:
            return original(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(viewer, "Application", test_app)
        pipe.send_text("\x1b[B\x1b[Bq")
        selected = viewer.browse_movies(movies)
    assert selected == movies[2]


def test_esc_exits_without_modifying_movies(monkeypatch: pytest.MonkeyPatch) -> None:
    original = Application
    movies = [Movie(title="The Prestige", watched=True, rating=8)]
    before = movies[:]
    with create_pipe_input() as pipe:

        def test_app(**kwargs: Any) -> Application[Movie]:
            return original(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(viewer, "Application", test_app)
        pipe.send_text("\x1b")
        result = viewer.browse_movies(movies)
    assert result == movies[0]
    assert movies == before


def test_empty_input_is_noop() -> None:
    assert viewer.browse_movies([]) is None
