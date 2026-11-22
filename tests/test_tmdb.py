"""TMDB lookup is optional, concise, and never stores unrelated movie metadata."""

import base64
import json
import os
from pathlib import Path
from typing import Any

import pytest
import typer
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from prompt_toolkit import Application
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

import movie_watchlist.interactive as interactive
import movie_watchlist.tmdb as tmdb
from movie_watchlist.interactive import MovieDetails
from movie_watchlist.tmdb import TMDBError


class StubResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def __enter__(self) -> "StubResponse":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, *_: object) -> bytes:
        return json.dumps(self.data).encode()


def test_exact_search_and_year_only_for_display(monkeypatch: pytest.MonkeyPatch) -> None:
    response = {
        "results": [
            {"id": 1, "title": "Dune", "release_date": "1984-12-14"},
            {"id": 2, "title": "Dune", "release_date": "2021-09-15"},
            {"id": 3, "title": "Dune: Part Two", "release_date": "2024-01-01"},
        ]
    }

    def fake_open(request: Any, timeout: float) -> StubResponse:
        assert "Authorization" not in str(request.full_url)
        assert request.get_header("Authorization") == "Bearer test-token"
        assert timeout == 1.5
        return StubResponse(response)

    monkeypatch.setattr(tmdb, "urlopen", fake_open)
    assert [(item.title, item.year) for item in tmdb.search_movies("Dune", "test-token")] == [
        ("Dune", "1984"),
        ("Dune", "2021"),
    ]


def test_details_only_retrieve_form_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    data = {
        "runtime": 169,
        "genres": [{"name": "Science Fiction"}, {"name": "Drama"}],
        "release_date": "2014-11-05",
        "overview": "Should not be saved",
        "poster_path": "/poster.jpg",
        "credits": {
            "crew": [
                {"job": "Producer", "name": "Someone"},
                {"job": "Director", "name": "Christopher Nolan"},
            ],
            "cast": [
                {"name": name}
                for name in ("Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Fourth")
            ],
        },
    }
    monkeypatch.setattr(tmdb, "urlopen", lambda *_, **__: StubResponse(data))
    result = tmdb.fetch_details(157336, "test-token")
    assert result.genre == "Sci-Fi"
    assert result.runtime == 169
    assert result.director == "Christopher Nolan"
    assert result.actors == ("Matthew McConaughey", "Anne Hathaway", "Jessica Chastain")
    assert not hasattr(result, "year")
    assert not hasattr(result, "overview")
    assert not hasattr(result, "poster_url")


def test_invalid_token_fails_without_leaking_password(tmp_path: Path) -> None:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    password = "long correct password for tests"
    key = Scrypt(salt=salt, length=32, n=32768, r=8, p=1).derive(password.encode())
    ciphertext = AESGCM(key).encrypt(nonce, b"test-token", b"movie-watchlist-tmdb-v1")
    payload = {
        "version": 1,
        "kdf": "scrypt",
        "cipher": "AES-256-GCM",
        "n": 32768,
        "r": 8,
        "p": 1,
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }
    path = tmp_path / "tmdb.enc.json"
    path.write_text(json.dumps(payload))
    assert tmdb.unlock_token(path, password) == "test-token"
    with pytest.raises(TMDBError, match="Cannot unlock TMDB token"):
        tmdb.unlock_token(path, "wrong password")


def test_prefilled_form_is_still_editable(monkeypatch: pytest.MonkeyPatch) -> None:
    original_application = Application
    starting = MovieDetails(
        genre="Sci-Fi",
        mood="",
        runtime=169,
        director="Christopher Nolan",
        actors=["Anne Hathaway"],
        watched=False,
        rating=None,
    )
    with create_pipe_input() as pipe:

        def stub_app(**kwargs: Any) -> Application[MovieDetails | None]:
            return original_application(**kwargs, input=pipe, output=DummyOutput())

        monkeypatch.setattr(interactive, "Application", stub_app)
        pipe.send_text("\r" * 7)
        result = interactive.collect_movie_details("Interstellar", initial=starting)
    assert result == starting


def test_missing_movie_offers_retry_with_corrected_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from movie_watchlist import cli
    from movie_watchlist.tmdb import Autofill, Candidate

    searches: list[str] = []
    prompts = iter(["1", "Interstellar"])
    monkeypatch.setattr(cli, "request_token", lambda: "local-test-token")
    monkeypatch.setattr(typer, "prompt", lambda *_, **__: next(prompts))

    def search(title: str, token: str) -> list[Candidate]:
        assert token == "local-test-token"
        searches.append(title)
        return [Candidate(1, "Interstellar", "2014")] if title == "Interstellar" else []

    monkeypatch.setattr(cli, "search_movies", search)
    monkeypatch.setattr(
        cli, "fetch_details", lambda *_: Autofill("Sci-Fi", 169, "Christopher Nolan", ("A",))
    )
    final_title, details = cli.lookup_movie("Intersteler")
    assert searches == ["Intersteler", "Interstellar"]
    assert final_title == "Interstellar"
    assert details is not None and details.runtime == 169


def test_missing_movie_offers_manual_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    from movie_watchlist import cli

    monkeypatch.setattr(cli, "request_token", lambda: "local-test-token")
    monkeypatch.setattr(cli, "search_movies", lambda *_: [])
    monkeypatch.setattr(typer, "prompt", lambda *_, **__: "2")
    assert cli.lookup_movie("Not A Film") == ("Not A Film", None)


def test_api_failure_offers_manual_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    from movie_watchlist import cli

    monkeypatch.setattr(cli, "request_token", lambda: "local-test-token")

    def fail(*_: object) -> list[tmdb.Candidate]:
        raise TMDBError("Network timeout")

    monkeypatch.setattr(cli, "search_movies", fail)
    monkeypatch.setattr(typer, "prompt", lambda *_, **__: "2")
    assert cli.lookup_movie("Interstellar") == ("Interstellar", None)


def test_ambiguous_title_displays_year_for_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    from movie_watchlist import cli
    from movie_watchlist.tmdb import Autofill, Candidate

    monkeypatch.setattr(cli, "request_token", lambda: "local-test-token")
    monkeypatch.setattr(
        cli,
        "search_movies",
        lambda *_: [Candidate(10, "Dune", "1984"), Candidate(20, "Dune", "2021")],
    )
    monkeypatch.setattr(typer, "prompt", lambda *_, **__: "2")
    chosen_ids: list[int] = []

    def fetch(movie_id: int, token: str) -> Autofill:
        chosen_ids.append(movie_id)
        return Autofill("Sci-Fi", 155, "Denis Villeneuve", ("A", "B"))

    monkeypatch.setattr(cli, "fetch_details", fetch)
    title, details = cli.lookup_movie("Dune")
    assert title == "Dune"
    assert details is not None and details.director == "Denis Villeneuve"
    assert chosen_ids == [20]


def test_token_cached_after_first_unlock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    encrypted = tmp_path / "encrypted.json"
    encrypted.write_text("test encrypted data", encoding="utf-8")
    cache = tmp_path / "token-cache"
    monkeypatch.setattr(tmdb, "credential_path", lambda: encrypted)
    monkeypatch.setattr(tmdb, "token_cache_path", lambda: cache)
    monkeypatch.setattr(tmdb, "unlock_token", lambda *_: "test-token")
    prompted: list[str] = []

    def fake_password(_message: str) -> str:
        prompted.append("prompted")
        return "test-password"

    monkeypatch.setattr(tmdb, "getpass", fake_password)
    assert tmdb.request_token() == "test-token"
    assert tmdb.request_token() == "test-token"
    assert cache.read_text(encoding="utf-8") == "test-token"
    assert len(prompted) == 1
    if os.name == "posix":
        assert cache.stat().st_mode & 0o077 == 0


def test_cache_location_can_be_overridden_for_docker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / ".tmdb-token"
    monkeypatch.setenv(tmdb.CACHE_ENV, str(path))
    assert tmdb.token_cache_path() == path


def test_missing_encrypted_file_still_accepts_cached_token(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cache = tmp_path / "token-cache"
    cache.write_text("test-token", encoding="utf-8")
    monkeypatch.setattr(tmdb, "credential_path", lambda: tmp_path / "missing.json")
    monkeypatch.setattr(tmdb, "token_cache_path", lambda: cache)
    monkeypatch.setattr(tmdb, "getpass", lambda *_: pytest.fail("Cached token must not prompt"))
    assert tmdb.request_token() == "test-token"
