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

import nltk  # type: ignore
from nltk.corpus import abc, webtext, words  # type: ignore

# Parameters
MAX_ROWS: int = 6
MAX_COLS: int = 5
MAX_SUGGESTIONS: int = 5
SMART: bool = True
SORT_LETTERS: bool = False

# GUI VALUES
TITLE: str = "LetterPicker"
WIDTH_PX: int = 1450
HEIGHT_PX: int = 800
BLANK: str = ""

LETTER_WIDTH: int = 6
LETTER_HEIGHT: int = 2
LETTER_BUTTON_FONT: int = 250

CHOOSE_BUTTON_WIDTH: int = 20
CHOOSE_BUTTON_HEIGHT: int = 3
CHOOSE_BUTTON_FONT: int = 100
GRID_PROMPT: str = "Clear"
GRIDPOINT_PROMPT: str = "Reduce"
POINT_PROMPT: str = "Point"

SUGGEST_WIDTH: int = 12
SUGGEST_HEIGHT: int = 4
SUGGEST_BUTTON_FONT: int = 20

NAV_BUTTON_WIDTH: int = 4
NAV_BUTTON_HEIGHT: int = 3
NAV_BUTTON_FONT: int = 45
BACK_TEXT: str = "Back"
DONE_TEXT: str = "Done"
UNDO_TEXT: str = "Undo"
CUSTOM_TEXT: str = "Custom"

MSG_FONT: int = 20
MSG_WIDTH: int = 160

# CLI VALUES
CLI_DONE: str = "d"
CLI_NEXT: str = "n"
EMPTY: str = "_"