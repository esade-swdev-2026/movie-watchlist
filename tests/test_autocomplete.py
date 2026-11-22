"""Offline suggestions must never block free-form movie metadata."""

from typing import Any

import pytest
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

import movie_watchlist.interactive as interactive
from movie_watchlist.autocomplete import (
    ACTORS,
    DIRECTORS,
    GENRES,
    MovieAutoSuggest,
    matches,
    suffix,
)
from movie_watchlist.interactive import MovieDetails


def test_curated_lists_have_expected_size_and_unique_names() -> None:
    assert len(GENRES) >= 20
    assert len(ACTORS) == 100
    assert len(DIRECTORS) == 100
    for choices in (GENRES, ACTORS, DIRECTORS):
        assert len({value.casefold() for value in choices}) == len(choices)


def test_genre_suggests_without_restricting_input() -> None:
    assert matches(0, "sci")[0] == "Sci-Fi"
    assert suffix(0, "Sci") == "-Fi"
    assert matches(0, "Very Unusual Genre") == []
    assert matches(0, "") == []


def test_director_and_actor_prefix_matching() -> None:
    assert matches(3, "christopher")[0] == "Christopher Nolan"
    assert matches(4, "anne")[0] == "Anne Hathaway"
    assert matches(4, "Amy Adams, matthew")[0] == "Matthew McConaughey"
    assert suffix(4, "Anne Hathaway, matthew") == " McConaughey"
    assert matches(4, "A, B, C, D") == []


def test_auto_suggest_does_not_change_what_user_typed() -> None:
    completer = MovieAutoSuggest(0)
    suggestion = completer.get_suggestion(Buffer(), Document("Sci"))
    assert suggestion is not None and suggestion.text == "-Fi"
    assert completer.get_suggestion(Buffer(), Document("Custom Genre")) is None
    assert completer.get_suggestion(Buffer(), Document("Sci", cursor_position=1)) is None


def test_right_arrow_accepts_suggestion_and_comma_actor_segment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_application = Application
    with create_pipe_input() as pipe:

        def application_with_test_terminal(**kwargs: Any) -> Application[MovieDetails | None]:
            return original_application(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(interactive, "Application", application_with_test_terminal)
        pipe.send_text("Sci\x1b[C\r\r\rChristopher N\x1b[C\rAnne H\x1b[C, Matthew M\x1b[C\r\r\r")
        result = interactive.collect_movie_details("Interstellar")

    assert result is not None
    assert result.genre == "Sci-Fi"
    assert result.director == "Christopher Nolan"
    assert result.actors == ["Anne Hathaway", "Matthew McConaughey"]


def test_can_type_custom_values_instead_of_accepting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_application = Application
    with create_pipe_input() as pipe:

        def application_with_test_terminal(**kwargs: Any) -> Application[MovieDetails | None]:
            return original_application(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(interactive, "Application", application_with_test_terminal)
        pipe.send_text("Experimental Biopic\r\r\rNew Director\rUnlisted Actor\r\r\r")
        result = interactive.collect_movie_details("Custom")

    assert result is not None
    assert result.genre == "Experimental Biopic"
    assert result.director == "New Director"
    assert result.actors == ["Unlisted Actor"]
