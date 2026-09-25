# movies_watchlist67

A simple command-line movie watchlist for keeping track of films you want to watch or have already watched. It is designed for users who want a quick and lightweight way to manage movie titles from the terminal.

## Install

```bash
uv sync
```

This creates the project environment and installs the required dependencies.

## Run

Show the available commands:

```bash
uv run movies_watchlist67 --help
```

Add a movie to your watchlist:

```bash
uv run movies_watchlist67 add "Interstellar"
```

Add a movie and mark it as already watched:

```bash
uv run movies_watchlist67 add "Interstellar" --watched
```

## Develop

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src tests
uv run pytest
```

## Layout

```text
src/movies_watchlist67/
  cli.py          command-line interface
  __main__.py     allows the package to run as a module

tests/
  test_cli.py     tests for the command-line interface

pyproject.toml    project configuration and dependencies
uv.lock           locked dependency versions
```
