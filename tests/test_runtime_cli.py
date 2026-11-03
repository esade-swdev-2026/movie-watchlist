from pathlib import Path

import pytest
from typer.testing import CliRunner

from movie_watchlist.cli import app
from movie_watchlist.movies import Movie
from movie_watchlist.storage import load_watchlist, save_watchlist


def test_add_stores_runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))

    result = CliRunner().invoke(app, ["add", "Interstellar", "--runtime", "169"])

    assert result.exit_code == 0
    assert load_watchlist(path)["Interstellar"].runtime == 169


@pytest.mark.parametrize("runtime", ["0", "-5"])
def test_add_rejects_invalid_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runtime: str
) -> None:
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(tmp_path / "movies.json"))

    result = CliRunner().invoke(app, ["add", "Interstellar", "--runtime", runtime])

    assert result.exit_code == 1
    assert "Runtime must be positive." in result.output


def test_list_filters_by_max_runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "movies.json"
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(path))

    save_watchlist(
        path,
        {
            "Interstellar": Movie(title="Interstellar", runtime=169),
            "Toy Story": Movie(title="Toy Story", runtime=81),
            "Unknown": Movie(title="Unknown", runtime=0),
        },
    )

    result = CliRunner().invoke(app, ["list", "--max-runtime", "120"])

    assert result.exit_code == 0
    assert "Toy Story" in result.output
    assert "Interstellar" not in result.output
    assert "Unknown" not in result.output


def test_list_rejects_invalid_max_runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOVIE_WATCHLIST_FILE", str(tmp_path / "movies.json"))

    result = CliRunner().invoke(app, ["list", "--max-runtime", "0"])

    assert result.exit_code == 1
    assert "Maximum runtime must be positive." in result.output
