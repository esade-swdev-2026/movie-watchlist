"""Pure watchlist decisions, kept separate from command-line output."""

type Watchlist = dict[str, bool]


def clean_title(title: str) -> str:
    return title.strip()


def is_duplicate(movies: Watchlist, title: str) -> bool:
    return any(saved.casefold() == clean_title(title).casefold() for saved in movies)


def add_movie(movies: Watchlist, title: str) -> Watchlist:
    title = clean_title(title)
    if not title:
        raise ValueError("Movie title cannot be empty.")
    if is_duplicate(movies, title):
        raise ValueError("Movie already exists.")
    return {**movies, title: False}


def mark_watched(movies: Watchlist, title: str) -> Watchlist:
    for saved in movies:
        if saved.casefold() == clean_title(title).casefold():
            return {**movies, saved: True}
    raise ValueError("Movie not found.")


def unwatched_titles(movies: Watchlist) -> list[str]:
    return [title for title, watched in movies.items() if not watched]


def average_rating(ratings: list[float]) -> float:
    return sum(ratings) / len(ratings) if ratings else 0.0
