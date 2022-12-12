import nltk  # type: ignore
from nltk.corpus import abc, webtext, words  # type: ignore

# GLOBAL VALUES
nltk.download("webtext")
nltk.download("abc")
nltk.download("words")
ALPHABET: list[str] = [chr(char_num) for char_num in range(ord("a"), ord("z") + 1)]
POSSIBLE_WORDS: list[str] = (
    [word.lower() for word in words.words()]
    + [word.lower() for word in abc.words()]
    + [word.lower() for word in webtext.words()]
)

# Parameters
MAX_ROWS: int = 6
MAX_COLS: int = 5
MAX_SUGGESTIONS: int = 5
SORT_LETTERS: bool = False

# Interface Constsnts
EMPTY: str = "_"
BLANK: str = ""
GRID_PROMPT: str = "Clear"
GRIDPOINT_PROMPT: str = "Reduce"
POINT_PROMPT: str = "Point"
