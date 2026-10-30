# Movie Watchlist

A small terminal app for keeping track of films you want to watch.

## Getting started

Clone the repository and install the dependencies:

```bash
git clone https://github.com/esade-swdev-2026/movie-watchlist.git
cd movie-watchlist
uv sync
```

Add a movie, show your list, and mark it as watched:

```bash
uv run movie_watchlist add "Interstellar"
uv run movie_watchlist add "Arrival" --watched
uv run movie_watchlist list
uv run movie_watchlist watch "Interstellar"
```

### Filter movies by director

You can specify a director when adding a movie:

```bash
uv run movie_watchlist add "Inception" --director "Christopher Nolan"
uv run movie_watchlist add "Titanic" --director "James Cameron"
```

To display only movies by a specific director:

```bash
uv run movie_watchlist list --director "Christopher Nolan"
```

Director filtering is case-insensitive and ignores surrounding spaces.


Movies are saved in `~/.movie_watchlist.json`, so your list stays there between runs. Use `uv run movie_watchlist --help` to see the commands.

## Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```
