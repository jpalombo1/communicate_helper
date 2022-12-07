from enum import Enum, auto

class LetterChoice(Enum):
    """Ways to make letter choices."""

    GRID = auto()
    GRID_POINT = auto()
    POINT = auto()