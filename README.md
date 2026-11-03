# Movie Watchlist

A small terminal app for keeping track of films you want to watch.

## Getting started

Clone the repository and install the dependencies:

```bash
git clone https://github.com/esade-swdev-2026/movie-watchlist.git
cd movie-watchlist
uv sync
```

Add a movie, show your list, mark it as watched, and filter movies by genre:


```bash
uv run movie_watchlist add "Interstellar"
uv run movie_watchlist add "Arrival" --watched
uv run movie_watchlist list
uv run movie_watchlist watch "Interstellar"
uv run movie_watchlist filter-genre "Sci-Fi"
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

## Filter by actor

Find movies featuring one of their three main actors:

```bash
uv run movie_watchlist list --actor "Anne Hathaway"
```

## Filter by running time

You can specify the runtime of a movie in minutes when adding it:

```bash
uv run movie_watchlist add "Interstellar" --runtime 169
uv run movie_watchlist add "Toy Story" --runtime 81
```

To show only movies that are 120 minutes long or less:

```bash
uv run movie_watchlist list --max-runtime 120
```

You can combine `--max-runtime` with other filters,
such as `--director` and `--actor`.

Movies with unknown runtime are excluded when filtering.
Runtime values must be positive integers.
