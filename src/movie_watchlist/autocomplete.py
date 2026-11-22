"""Small, offline suggestion lists for the optional interactive form.

These are curated examples, not rankings or authoritative movie metadata.
Users can always enter a different value.
"""

from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

GENRES: tuple[str, ...] = (
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film Noir",
    "History",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western",
    "Superhero",
    "Psychological Thriller",
    "Romantic Comedy",
    "Historical Drama",
    "Science Fiction",
    "Anime",
    "Short",
    "Experimental",
    "Music",
)

ACTORS: tuple[str, ...] = (
    "Leonardo DiCaprio",
    "Tom Hanks",
    "Meryl Streep",
    "Denzel Washington",
    "Robert De Niro",
    "Al Pacino",
    "Brad Pitt",
    "Morgan Freeman",
    "Scarlett Johansson",
    "Jennifer Lawrence",
    "Emma Stone",
    "Natalie Portman",
    "Anne Hathaway",
    "Matthew McConaughey",
    "Christian Bale",
    "Ryan Gosling",
    "Emma Watson",
    "Daniel Radcliffe",
    "Keanu Reeves",
    "Sandra Bullock",
    "Julia Roberts",
    "Cate Blanchett",
    "Nicole Kidman",
    "Joaquin Phoenix",
    "Robert Downey Jr.",
    "Chris Evans",
    "Chris Hemsworth",
    "Chris Pratt",
    "Benedict Cumberbatch",
    "Tom Holland",
    "Samuel L. Jackson",
    "Harrison Ford",
    "Hugh Jackman",
    "Jake Gyllenhaal",
    "Amy Adams",
    "Jeremy Renner",
    "Jessica Chastain",
    "Florence Pugh",
    "Timothée Chalamet",
    "Zendaya",
    "Margot Robbie",
    "Cillian Murphy",
    "Emily Blunt",
    "John Krasinski",
    "Adam Driver",
    "Oscar Isaac",
    "Pedro Pascal",
    "Antonio Banderas",
    "Penélope Cruz",
    "Javier Bardem",
    "Ana de Armas",
    "Salma Hayek",
    "Gael García Bernal",
    "Diego Luna",
    "Saoirse Ronan",
    "Andrew Garfield",
    "Eddie Redmayne",
    "Michael B. Jordan",
    "Lupita Nyong'o",
    "Viola Davis",
    "Octavia Spencer",
    "Idris Elba",
    "Daniel Kaluuya",
    "John Boyega",
    "Dev Patel",
    "Riz Ahmed",
    "Mahershala Ali",
    "Lakeith Stanfield",
    "Awkwafina",
    "Michelle Yeoh",
    "Tony Leung",
    "Jackie Chan",
    "Donnie Yen",
    "Chow Yun-fat",
    "Song Kang-ho",
    "Choi Min-sik",
    "Lee Byung-hun",
    "Gong Yoo",
    "Tilda Swinton",
    "Ralph Fiennes",
    "Gary Oldman",
    "Colin Firth",
    "Hugh Grant",
    "Kate Winslet",
    "Helen Mirren",
    "Judi Dench",
    "Olivia Colman",
    "Brendan Fraser",
    "Paul Rudd",
    "Steve Carell",
    "Will Ferrell",
    "Bill Murray",
    "Robin Williams",
    "Eddie Murphy",
    "Jim Carrey",
    "Adam Sandler",
    "Mark Ruffalo",
    "Josh Brolin",
    "Edward Norton",
    "Forest Whitaker",
)

DIRECTORS: tuple[str, ...] = (
    "Christopher Nolan",
    "Steven Spielberg",
    "Martin Scorsese",
    "Quentin Tarantino",
    "Francis Ford Coppola",
    "Stanley Kubrick",
    "Alfred Hitchcock",
    "Ridley Scott",
    "James Cameron",
    "David Fincher",
    "Denis Villeneuve",
    "Greta Gerwig",
    "Sofia Coppola",
    "Kathryn Bigelow",
    "Chloé Zhao",
    "Jane Campion",
    "Wes Anderson",
    "Tim Burton",
    "Guillermo del Toro",
    "Bong Joon-ho",
    "Park Chan-wook",
    "Hayao Miyazaki",
    "Isao Takahata",
    "Makoto Shinkai",
    "Akira Kurosawa",
    "Yasujirō Ozu",
    "Hirokazu Kore-eda",
    "Wong Kar-wai",
    "Ang Lee",
    "Zhang Yimou",
    "John Woo",
    "Edward Yang",
    "Satoshi Kon",
    "Pedro Almodóvar",
    "Alejandro González Iñárritu",
    "Alfonso Cuarón",
    "Guillermo Arriaga",
    "Lucrecia Martel",
    "Pablo Larraín",
    "Fernando Meirelles",
    "Walter Salles",
    "Céline Sciamma",
    "Agnès Varda",
    "François Truffaut",
    "Jean-Luc Godard",
    "Éric Rohmer",
    "Claire Denis",
    "Jacques Audiard",
    "Luc Besson",
    "Michel Gondry",
    "Jean-Pierre Jeunet",
    "Leos Carax",
    "Michael Haneke",
    "Lars von Trier",
    "Thomas Vinterberg",
    "Ruben Östlund",
    "Ingmar Bergman",
    "Federico Fellini",
    "Michelangelo Antonioni",
    "Luchino Visconti",
    "Roberto Rossellini",
    "Sergio Leone",
    "Paolo Sorrentino",
    "Luca Guadagnino",
    "Giuseppe Tornatore",
    "Nanni Moretti",
    "Alice Rohrwacher",
    "Yorgos Lanthimos",
    "Richard Linklater",
    "Paul Thomas Anderson",
    "Robert Altman",
    "Terrence Malick",
    "Spike Lee",
    "Jordan Peele",
    "Ava DuVernay",
    "Barry Jenkins",
    "Steve McQueen",
    "Ryan Coogler",
    "Damien Chazelle",
    "Darren Aronofsky",
    "David Lynch",
    "David Cronenberg",
    "Robert Eggers",
    "Ari Aster",
    "Sam Raimi",
    "Peter Jackson",
    "Taika Waititi",
    "George Miller",
    "George Lucas",
    "J. J. Abrams",
    "Rian Johnson",
    "Ron Howard",
    "Clint Eastwood",
    "Joel Coen",
    "Ethan Coen",
    "Noah Baumbach",
    "Alexander Payne",
    "Todd Haynes",
    "Todd Phillips",
    "Chris Columbus",
)

SUGGESTIONS: dict[int, tuple[str, ...]] = {0: GENRES, 3: DIRECTORS, 4: ACTORS}


def _current_term(field_index: int, text: str) -> str:
    """For actors, complete only the name after the final comma."""
    raw = text.rsplit(",", 1)[-1] if field_index == 4 else text
    return raw.lstrip()


def matches(field_index: int, text: str, limit: int = 3) -> list[str]:
    """Return case-insensitive prefix matches, excluding an already-complete value."""
    term = _current_term(field_index, text)
    if not term or limit <= 0 or (field_index == 4 and text.count(",") >= 3):
        return []
    return [
        value
        for value in SUGGESTIONS.get(field_index, ())
        if value.casefold().startswith(term.casefold()) and value.casefold() != term.casefold()
    ][:limit]


def suffix(field_index: int, text: str) -> str:
    """Characters that Right Arrow can add to complete the first suggested value."""
    suggestions = matches(field_index, text, limit=1)
    return suggestions[0][len(_current_term(field_index, text)) :] if suggestions else ""


class MovieAutoSuggest(AutoSuggest):
    """Show a faded completion without constraining user-entered values."""

    def __init__(self, field_index: int) -> None:
        self.field_index = field_index

    def get_suggestion(self, buffer: Buffer, document: Document) -> Suggestion | None:
        if document.cursor_position != len(document.text):
            return None
        suggestion = suffix(self.field_index, document.text)
        return Suggestion(suggestion) if suggestion else None
