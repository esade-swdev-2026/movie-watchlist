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

## Interactive add form (v1.0.2)

From a normal terminal, add a movie by title to open the keyboard-navigable form:

```bash
uv run movie_watchlist add "Interstellar"
```

Use **Enter** to move to the next field or save on the final field, **Up/Down** to move
between fields, and **Esc** or **Ctrl-C** to cancel without saving. Empty fields are
optional, except that watched movies need a rating. Enter up to three actors separated
by commas, e.g. `Anne Hathaway, Matthew McConaughey`.

The original command-line flags still work and bypass the form:

```bash
uv run movie_watchlist add "Interstellar" --genre "Sci-Fi" --runtime 169
uv run movie_watchlist add "Up" --no-interactive
```

While editing **Genre**, **Director**, or **Actors**, the form suggests common values
from curated offline lists (30 genres, 100 actors, and 100 directors). Type a prefix
such as `Sci`, `Christopher`, or `Anne` to see a faint completion and matching
options in the footer. Press **Right Arrow** at the end of the text to accept the
first suggestion, or keep typing a different value. Suggestions never limit what
you can enter. Actor suggestions apply to the name after the most recent comma.
No API key or internet connection is needed.

Use `--interactive` to explicitly request the form. When input/output are not
connected to a terminal (for example in scripts or CI), a bare `add` stays
non-interactive for backwards compatibility.

## Optional TMDB lookup (v1.1.0)

From a terminal, `uv run movie_watchlist add "Interstellar"` can prefill genre,
runtime, director and up to three actors from TMDB. Enter your local encryption
password once per computer. After that, the token is saved to a local file in your
user profile (never to Git), so future runs do not prompt again. The local token
is plaintext and should be treated as a credential; on macOS/Linux the file is
restricted to the current user. In Docker, the existing `/app/data` volume stores
it alongside the movie list. If nothing matches or the API fails, choose **1** to search
again (and optionally correct the title) or **2** to open the offline form.
All fields remain editable, with offline suggestions as before.
Mood, watched status and rating are always yours to enter. Year is shown only to
distinguish films with the same title; no year, synopsis or poster is saved.

Skip the API entirely with:

```bash
uv run movie_watchlist add "Interstellar" --no-lookup
```

The repository includes an **encrypted** API Read Access Token at
`config/tmdb-token.enc.json`, not its plaintext value. You need its separate password
to use the online lookup; anyone without it can still use the offline program.
Do not share the password or any unencrypted credentials.

### Credits

[![TMDB official logo](https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg)](https://www.themoviedb.org)

This product uses the TMDB API but is not endorsed or certified by TMDB.
The logo is TMDB's official artwork. Run `uv run movie_watchlist credits` for the
terminal attribution. API use is subject to [TMDB's terms](https://developer.themoviedb.org/docs/faq).

## Browse your watchlist (v1.1.0)

Run `uv run movie_watchlist list` in a terminal to open a simple movie browser.
Use **Up/Down** to move between movies; the selected movie's saved details
(status, genre, runtime, director, actors, mood and rating) appear underneath.
**Home/End** jumps to the first/last movie; **Q/Esc** closes the viewer.
Browsing the watchlist never contacts TMDB.

Existing filters still work, such as `uv run movie_watchlist list --genre "Sci-Fi"`.
Use `uv run movie_watchlist list --plain` for the original one-line display.
Non-interactive terminals, scripts and Docker without `-it` also use plain output.

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

## Run with Docker

The image is built and published by our GitHub Actions pipeline, so nothing has to be built
locally. The package is private: log in to GitHub's registry first, with a personal access
token that has `read:packages`.

```bash
docker login ghcr.io -u <your-github-username>
docker pull ghcr.io/esade-swdev-2026/movie-watchlist:v1.1.0
docker run --rm ghcr.io/esade-swdev-2026/movie-watchlist:v1.1.0 --help
```

The watchlist is not stored in the image. The app writes it to `/app/data/watchlist.json`
(set with `MOVIE_WATCHLIST_FILE`), and we mount a named volume on that folder, so the
movies are still there after the container is removed:

```bash
docker run --rm -v movie-watchlist-data:/app/data ghcr.io/esade-swdev-2026/movie-watchlist:v1.1.0 add "Interstellar" --runtime 169
docker run --rm -v movie-watchlist-data:/app/data ghcr.io/esade-swdev-2026/movie-watchlist:v1.1.0 list
```

The second command still prints Interstellar, even though the first container is gone.
The file name can also be changed without rebuilding the image:

```bash
docker run --rm -e MOVIE_WATCHLIST_FILE=/app/data/other.json -v movie-watchlist-data:/app/data ghcr.io/esade-swdev-2026/movie-watchlist:v1.1.0 list
```

To remove the saved data: `docker volume rm movie-watchlist-data`.

To use the published container interactively, add `-it` and a data volume:

```bash
docker run -it --rm -v movie-watchlist-data:/app/data ghcr.io/esade-swdev-2026/movie-watchlist:v1.1.0 add "Interstellar"
```

## Use of AI

All four members of the group used AI tools, such as ChatGPT and Claude, during the project:

- Kenzo used AI tools, including Claude, throughout the project to assist with writing, coding, debugging and testing. He also used them to assess and correct his own code, evaluate different approaches, identify potential errors and ensure a smooth and reliable final deployment.
- Alvaro used ChatGPT as a learning and development assistant to better understand Python concepts, troubleshoot issues, identify potential bugs, review code quality, and explore possible solutions and improvements. He critically evaluated all suggestions and remained responsible for implementation decisions and for verifying the results.
- Jan used ChatGPT and Claude as learning and development assistants to understand errors, review code and improve comments, and to follow the steps for the release workflow, the Dockerfile data folder and the Run with Docker section. He ran and tested every command himself, checked the results, and remained responsible for the pull requests he opened.
- Russell used a combination of AI tools to help write text and code, check processes, troubleshoot documents and make sure the deployment was clean and bug-free.
