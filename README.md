# Movie Watchlist

A small terminal app for keeping track of films you want to watch.

## Getting started

Clone the repository and install the dependencies:

```bash
git clone https://github.com/esade-swdev-2026/movie-watchlist.git
cd movie-watchlist
uv sync
```

Movies are saved in `~/.movie_watchlist.json`, so your list stays there between runs.
Use `uv run movie_watchlist --help` to see the commands.

## Walkthrough

The examples below build on each other. Run them in order from an empty watchlist
and each command gives the result described.

### Add movies

A movie has a title and, optionally, a genre, a mood, a runtime in minutes, a director
and up to three main actors. Repeat `--actor` for each one:

```bash
uv run movie_watchlist add "Interstellar" --genre "Sci-Fi" --mood "Thoughtful" --runtime 169 --director "Christopher Nolan" --actor "Anne Hathaway" --actor "Matthew McConaughey"
uv run movie_watchlist add "Inception" --genre "Sci-Fi" --mood "Thoughtful" --runtime 148 --director "Christopher Nolan"
uv run movie_watchlist add "Up" --genre "Animation" --mood "Emotional" --runtime 96 --actor "Ed Asner"
uv run movie_watchlist add "Toy Story" --genre "Animation" --mood "Funny" --runtime 81
```

Titles are unique, ignoring case and surrounding spaces. Adding more than three actors
is rejected with `At most three actors.`, and a runtime must be a positive integer.

A movie you have already seen needs a rating from 1 to 10, so add it with both options:

```bash
uv run movie_watchlist add "Arrival" --genre "Sci-Fi" --runtime 116 --actor "Amy Adams" --watched --rating 9
```

Using `--watched` without `--rating` is rejected.
You can also rate a movie you have not watched yet, with `add --rating` or `rate`;
`suggest` uses those ratings to rank what to watch next.

### Show, watch and rate

```bash
uv run movie_watchlist list
uv run movie_watchlist watch "Interstellar" --rating 8
uv run movie_watchlist rate "Up" 9
```

`list` shows every movie as `title — watched` or `title — to watch`.
`watch` marks a movie as watched and needs `--rating`, the same rule as `add --watched`.
`rate` sets the rating of any movie, watched or not.

### Filter movies

`list` accepts `--genre`, `--mood`, `--director`, `--actor` and `--max-runtime`.
Matching ignores case and surrounding spaces:

```bash
uv run movie_watchlist list --genre "sci-fi"          # Interstellar, Inception, Arrival
uv run movie_watchlist list --mood "emotional"        # Up
uv run movie_watchlist list --director "Christopher Nolan"   # Interstellar, Inception
uv run movie_watchlist list --actor "Anne Hathaway"   # Interstellar
uv run movie_watchlist list --max-runtime 120         # Up, Toy Story, Arrival
```

Filters can be combined, and a movie must match all of them:

```bash
uv run movie_watchlist list --genre "Sci-Fi" --max-runtime 120   # Arrival
uv run movie_watchlist list --genre "Animation" --mood "Emotional" --max-runtime 120   # Up
```

Movies with an unknown runtime (added without `--runtime`) are left out whenever
`--max-runtime` is used.

### Suggest a movie

`suggest` picks the highest rated unwatched movie, ties broken by title ignoring case.
It applies the same filters as `list` first:

```bash
uv run movie_watchlist suggest --genre "Animation"   # Suggestion: Up
```

If nothing matches, it prints `No movies to suggest.`

## Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```
