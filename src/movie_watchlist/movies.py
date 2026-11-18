"""Watchlist operations independent of files and command-line output."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Movie:
    title: str
    watched: bool = False
    genre: str = ""
    mood: str = ""
    runtime: int = 0
    director: str = ""
    actors: tuple[str, ...] = ()
    rating: int | None = None
    year: int | None = None
    overview: str = ""
    poster_url: str = ""


type Watchlist = dict[str, Movie]


def clean_title(title: str) -> str:
    return title.strip()


MAX_MAIN_ACTORS = 3
MIN_RATING = 1
MAX_RATING = 10


def find_saved_title(movies: Watchlist, title: str) -> str | None:
    """Return the saved key for a title, ignoring case and surrounding spaces."""
    wanted = clean_title(title).casefold()
    return next((saved for saved in movies if saved.casefold() == wanted), None)


def is_duplicate(movies: Watchlist, title: str) -> bool:
    return find_saved_title(movies, title) is not None


def add_movie(
    movies: Watchlist,
    title: str,
    watched: bool = False,
    director: str = "",
    runtime: int | None = None,
    mood: str = "",
    genre: str = "",
    actors: list[str] | None = None,
    rating: int | None = None,
) -> Watchlist:
    title = clean_title(title)
    if not title:
        raise ValueError("Movie title cannot be empty.")
    if is_duplicate(movies, title):
        raise ValueError("Movie already exists.")
    if runtime is not None and runtime <= 0:
        raise ValueError("Runtime must be positive.")
    if watched and rating is None:
        raise ValueError("A watched movie needs a rating.")
    if rating is not None and not MIN_RATING <= rating <= MAX_RATING:
        raise ValueError(f"Rating must be between {MIN_RATING} and {MAX_RATING}.")
    cast = [name.strip() for name in (actors or [])]
    if not all(cast):
        raise ValueError("Actor names cannot be blank.")
    if len(cast) > MAX_MAIN_ACTORS:
        raise ValueError("At most three actors.")

    return {
        **movies,
        title: Movie(
            title=title,
            watched=watched,
            director=director.strip(),
            runtime=runtime if runtime is not None else 0,
            mood=mood.strip(),
            genre=genre.strip(),
            actors=tuple(cast),
            rating=rating,
        ),
    }


def mark_watched(movies: Watchlist, title: str) -> Watchlist:
    saved = find_saved_title(movies, title)
    if saved is None:
        raise ValueError("Movie not found.")
    return {**movies, saved: replace(movies[saved], watched=True)}


def rate_movie(movies: Watchlist, title: str, rating: int) -> Watchlist:
    if not MIN_RATING <= rating <= MAX_RATING:
        raise ValueError(f"Rating must be between {MIN_RATING} and {MAX_RATING}.")
    saved = find_saved_title(movies, title)
    if saved is None:
        raise ValueError("Movie not found.")
    return {**movies, saved: replace(movies[saved], rating=rating)}


def unwatched_titles(movies: Watchlist) -> list[str]:
    return [title for title, movie in movies.items() if not movie.watched]


def average_rating(ratings: list[float]) -> float:
    return sum(ratings) / len(ratings) if ratings else 0.0


def update_details(
    movies: Watchlist,
    title: str,
    *,
    year: int | None = None,
    overview: str | None = None,
    poster_url: str | None = None,
) -> Watchlist:
    """Update only the details that are given; the others keep their saved value."""
    saved = find_saved_title(movies, title)
    if saved is None:
        raise ValueError("Movie not found.")
    current = movies[saved]
    updated = replace(
        current,
        year=current.year if year is None else year,
        overview=current.overview if overview is None else overview.strip(),
        poster_url=current.poster_url if poster_url is None else poster_url.strip(),
    )
    return {**movies, saved: updated}
