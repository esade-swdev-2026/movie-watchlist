"""Tests for the interactive add form and its optional inputs."""

from typing import Any

import pytest
from prompt_toolkit import Application
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

import movie_watchlist.interactive as interactive
from movie_watchlist.interactive import FormError, MovieDetails, _parse_answers


def test_form_parses_all_fields() -> None:
    result = _parse_answers(
        [
            " Sci-Fi ",
            " Thoughtful ",
            "169",
            " Christopher Nolan ",
            "Anne Hathaway, Matthew McConaughey",
            "n",
            "9",
        ]
    )
    assert result == MovieDetails(
        genre="Sci-Fi",
        mood="Thoughtful",
        runtime=169,
        director="Christopher Nolan",
        actors=["Anne Hathaway", "Matthew McConaughey"],
        watched=False,
        rating=9,
    )


def test_blank_fields_are_optional() -> None:
    assert _parse_answers([""] * 7) == MovieDetails(
        genre="", mood="", runtime=None, director="", actors=[], watched=False, rating=None
    )


@pytest.mark.parametrize(
    ("answers", "field_index"),
    [
        (["", "", "0", "", "", "", ""], 2),
        (["", "", "abc", "", "", "", ""], 2),
        (["", "", "", "", "A,,B", "", ""], 4),
        (["", "", "", "", "A,B,C,D", "", ""], 4),
        (["", "", "", "", "", "sometimes", ""], 5),
        (["", "", "", "", "", "y", ""], 6),
        (["", "", "", "", "", "", "11"], 6),
    ],
)
def test_invalid_field_is_identified(answers: list[str], field_index: int) -> None:
    with pytest.raises(FormError) as exc:
        _parse_answers(answers)
    assert exc.value.field_index == field_index


def test_form_accepts_keyboard_and_arrow_navigation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_application = Application
    with create_pipe_input() as pipe:

        def application_with_test_terminal(**kwargs: Any) -> Application[MovieDetails | None]:
            return original_application(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(interactive, "Application", application_with_test_terminal)
        pipe.send_text(
            "Sci-Fi\rThoughtful\x1b[A\x1b[B\r169\rChristopher Nolan\r"
            "Anne Hathaway, Matthew McConaughey\rn\r8\r"
        )
        result = interactive.collect_movie_details("Interstellar")
    assert result is not None
    assert result.runtime == 169
    assert result.actors == ["Anne Hathaway", "Matthew McConaughey"]
    assert result.rating == 8


def test_ctrl_c_cancels_without_saving(monkeypatch: pytest.MonkeyPatch) -> None:
    original_application = Application
    with create_pipe_input() as pipe:

        def application_with_test_terminal(**kwargs: Any) -> Application[MovieDetails | None]:
            return original_application(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(interactive, "Application", application_with_test_terminal)
        pipe.send_text("\x03")
        assert interactive.collect_movie_details("Interstellar") is None
