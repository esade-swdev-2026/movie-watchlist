"""Small TMDB client. A failed lookup must never prevent manual movie entry."""

import base64
import json
import os
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

BASE_URL = "https://api.themoviedb.org/3"
TIMEOUT = 1.5  # Seconds per request. Do not impose an artificial delay.
CACHE_ENV = "MOVIE_WATCHLIST_TMDB_CACHE"


class TMDBError(Exception):
    """Lookup or decryption failed; caller should continue offline."""


@dataclass(frozen=True)
class Candidate:
    id: int
    title: str
    year: str


@dataclass(frozen=True)
class Autofill:
    genre: str = ""
    runtime: int | None = None
    director: str = ""
    actors: tuple[str, ...] = ()


def credential_path() -> Path:
    """Find the encrypted credential in a clone or the Docker image."""
    candidates = (
        Path.cwd() / "config" / "tmdb-token.enc.json",
        Path(__file__).resolve().parents[2] / "config" / "tmdb-token.enc.json",
        Path("/app/config/tmdb-token.enc.json"),
    )
    return next((path for path in candidates if path.is_file()), candidates[0])


def unlock_token(path: Path, password: str) -> str:
    """Decrypt an AES-GCM token created by the v1.1.0 setup instructions."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Invalid encrypted credential")
        if (
            payload.get("version") != 1
            or payload.get("kdf") != "scrypt"
            or payload.get("cipher") != "AES-256-GCM"
            or (payload.get("n"), payload.get("r"), payload.get("p")) != (32768, 8, 1)
        ):
            raise ValueError("Unsupported encrypted credential")
        salt = base64.b64decode(payload["salt"], validate=True)
        nonce = base64.b64decode(payload["nonce"], validate=True)
        ciphertext = base64.b64decode(payload["ciphertext"], validate=True)
        if len(salt) != 16 or len(nonce) != 12:
            raise ValueError("Invalid encrypted credential")
        key = Scrypt(salt=salt, length=32, n=32768, r=8, p=1).derive(password.encode())
        token = AESGCM(key).decrypt(nonce, ciphertext, b"movie-watchlist-tmdb-v1").decode()
        if not token.strip():
            raise ValueError("Empty token")
        return token.strip()
    except (OSError, ValueError, KeyError, TypeError, UnicodeDecodeError) as error:
        raise TMDBError("Cannot unlock TMDB token") from error
    except Exception as error:
        # Authentication tag failures must not leak implementation details or secrets.
        raise TMDBError("Cannot unlock TMDB token") from error


def token_cache_path() -> Path:
    """Use one local file on macOS, Linux and Windows; Docker overrides its location."""
    return Path(os.environ.get(CACHE_ENV, str(Path.home() / ".movie_watchlist_tmdb_token")))


def request_token() -> str | None:
    """Ask for the decryption password once per computer, then reuse the local token."""
    cache = token_cache_path()
    try:
        token = cache.read_text(encoding="utf-8").strip()
        if token:
            return token
    except (OSError, UnicodeError):
        token = ""

    encrypted = credential_path()
    if not encrypted.is_file():
        return None
    try:
        password = getpass("TMDB password (Enter to skip): ")
    except (EOFError, KeyboardInterrupt):
        return None
    if not password:
        return None
    token = unlock_token(encrypted, password)

    # Best effort only: if the home folder is read-only, lookup still works.
    # 0600 restricts read/write access to the user on POSIX systems.
    try:
        fd = os.open(cache, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(token)
        if os.name == "posix":
            os.chmod(cache, 0o600)
    except OSError:
        return token
    return token


def _get(path: str, token: str, params: dict[str, str]) -> dict[str, Any]:
    url = f"{BASE_URL}{path}?{urlencode(params)}"
    req = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            data = json.load(response)
    except (OSError, ValueError, TypeError) as error:
        raise TMDBError("TMDB lookup failed") from error
    if not isinstance(data, dict):
        raise TMDBError("Unexpected TMDB response")
    return data


def search_movies(title: str, token: str) -> list[Candidate]:
    """Only exact title matches: never fill details from a merely similar film."""
    response = _get("/search/movie", token, {"query": title, "language": "en-US"})
    results = response.get("results", [])
    if not isinstance(results, list):
        raise TMDBError("Unexpected TMDB response")
    candidates: list[Candidate] = []
    wanted = title.strip().casefold()
    for item in results:
        if not isinstance(item, dict):
            continue
        name = item.get("title")
        original = item.get("original_title")
        movie_id = item.get("id")
        if not isinstance(name, str) or not isinstance(movie_id, int) or isinstance(movie_id, bool):
            continue
        if name.strip().casefold() != wanted and not (
            isinstance(original, str) and original.strip().casefold() == wanted
        ):
            continue
        release_date = item.get("release_date")
        year = release_date[:4] if isinstance(release_date, str) and len(release_date) >= 4 else "?"
        candidates.append(Candidate(id=movie_id, title=name, year=year))
    return candidates[:5]


def fetch_details(movie_id: int, token: str) -> Autofill:
    """Return only the four fields the form can use, no year/synopsis/poster."""
    data = _get(
        f"/movie/{movie_id}",
        token,
        {"append_to_response": "credits", "language": "en-US"},
    )
    genre = ""
    genres = data.get("genres")
    if isinstance(genres, list):
        for item in genres:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                genre = item["name"]
                break
    if genre == "Science Fiction":
        genre = "Sci-Fi"
    runtime = data.get("runtime")
    if not isinstance(runtime, int) or isinstance(runtime, bool) or runtime <= 0:
        runtime = None
    credits = data.get("credits")
    director = ""
    actors: list[str] = []
    if isinstance(credits, dict):
        crew = credits.get("crew", [])
        if isinstance(crew, list):
            for person in crew:
                if (
                    isinstance(person, dict)
                    and person.get("job") == "Director"
                    and isinstance(person.get("name"), str)
                ):
                    director = person["name"]
                    break
        cast = credits.get("cast", [])
        if isinstance(cast, list):
            for person in cast:
                if (
                    isinstance(person, dict)
                    and isinstance(person.get("name"), str)
                    and person["name"].strip()
                ):
                    actors.append(person["name"].strip())
                if len(actors) == 3:
                    break
    return Autofill(genre=genre, runtime=runtime, director=director, actors=tuple(actors))
