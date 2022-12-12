import math
from dataclasses import dataclass

from communicate.constants import (
    ALPHABET,
    EMPTY,
    MAX_COLS,
    MAX_ROWS,
    POSSIBLE_WORDS,
    SORT_LETTERS,
)
from communicate.make_grid import make_grid


@dataclass
class Communicator:
    start_grid: list[list[str]]
    smart: bool = False
    include_empty: bool = True

    def __post_init__(self) -> None:
        """Creates editable grid object."""
        self.total_frequency_map: dict[str, int] = self.frequency_map()
        self.reset_grid()

    @property
    def done(self) -> bool:
        """Done if only one word left or no letters left to suggest."""
        return len(self.filtered_words) == 1 or len(self.remain_letters) == 0

    @property
    def grid_size(self) -> int:
        """
        Calculates grid size of remaining letters excluding empty spaces.
        If empty spaces includes, make grid size start grid size since remain letters won't account for empty spaces.
        """
        if self.include_empty:
            return len([letter for row in self.start_grid for letter in row])
        return len([letter for row in self.remain_letters for letter in row])

    @property
    def max_dim(self) -> int:
        """Returns maximum dimension of grid."""
        return self.num_cols if self.num_cols > self.num_rows else self.num_rows

    @property
    def num_cols(self) -> int:
        """Gets approximately square grid number of columns based on ceil(sqrt(size))."""
        cols = math.ceil(math.sqrt(self.grid_size))
        return cols if cols <= MAX_COLS else MAX_COLS

    @property
    def num_rows(self) -> int:
        """Gets number of rows from claculated number of cols and grid size."""
        if self.num_cols == 0:
            return 0
        rows = math.ceil(self.grid_size / self.num_cols)
        return rows if rows <= MAX_ROWS else MAX_ROWS

    def frequency_map(self) -> dict[str, int]:
        """Function to take all possible words in corpuses and get frequency count of them
        Then sort map by most common to least common words."""
        filtered_words = [
            word
            for word in POSSIBLE_WORDS
            if all(letter in ALPHABET for letter in word)
        ]
        sorted_words = sorted(filtered_words)
        freq_map: dict[str, int] = {}
        for word in sorted_words:
            if word not in freq_map:
                freq_map[word] = 0
            freq_map[word] += 1
        freq_map_sorted = dict(
            sorted(freq_map.items(), key=lambda x: x[1], reverse=True)
        )
        return freq_map_sorted

    def choose_grid_item(self, row: int, col: int) -> str:
        """Chooses letter from grid given row/column, Col 0:SAMPLE_LENGTH-1, ROW:0:"""
        row_entries = self.choose_grid_row(row)
        if col > len(row_entries):
            raise ValueError("Col out of bounds")
        item = row_entries[col]
        if item == EMPTY:
            raise ValueError("Cannot pick blank space!")
        return item

    def choose_grid_row(self, row: int) -> list[str]:
        """Gets letters of chosen row from grid. Make sure row choice is allowable."""
        if row > len(self.remain_grid):
            raise ValueError("Row out of bounds")
        return self.remain_grid[row]

    def _choose_grid_col(self, col: int) -> list[str]:
        """Gets letters of chosen col from grid. Make sure col choice is allowable."""
        if any(col > len(row) for row in self.remain_grid):
            raise ValueError("Col out of bounds")
        return [row[col] for row in self.remain_grid]

    def choose_grid_row_reduce(self, row: int) -> list[str]:
        """Gets letters of chosen row from grid. Does not include mepty spaces."""
        row_raw = self.choose_grid_row(row)
        return [letter for letter in row_raw if letter != EMPTY]

    def choose_grid_row_reduce_idx(self, row: int) -> list[int]:
        """Get indices of non empty spaces in row."""
        row_raw = self.choose_grid_row(row)
        return [idx for idx, letter in enumerate(row_raw) if letter != EMPTY]

    def _choose_grid_col_reduce(self, col: int) -> list[str]:
        """Gets letters of chosen row from grid. Does not include mepty spaces."""
        col_raw = self._choose_grid_col(col)
        return [letter for letter in col_raw if letter != EMPTY]

    def reset_grid(self) -> None:
        """Creates editable grid object."""
        self.filtered_words: list[str] = []
        self.remain_letters: list[str] = [letter for letter in ALPHABET]
        self.remain_grid: list[list[str]] = make_grid(
            MAX_ROWS, MAX_COLS, self.remain_letters
        )

    def eval_grid(self, word: str) -> list[str]:
        """If smart system, use letter frequency to filter out impossible letters if not in frequency map.
        Order remaining words by frequency based on frequency in corpus."""
        frequency_map = self._next_letter_frequency(word)
        if not self.smart:
            return self.remain_letters
        ordered_letters = self._find_ordered_letters(frequency_map)
        self.remain_letters = ordered_letters
        return self.remain_letters

    def _find_invalid_letters(self, frequency_map: dict[str, int]) -> list[str]:
        """Method to explictly get invalid letters based on letters not in frequency map for word."""
        alphabet_set = {letter.lower() for letter in ALPHABET}
        invalid_letters = alphabet_set - set(frequency_map.keys())
        return [invalid_l for invalid_l in invalid_letters]

    def _find_ordered_letters(self, frequency_map: dict[str, int]) -> list[str]:
        """Method to explictly get letters in order of most common in frequency map for word.
        If sort letters, return letters in order of frequency, else alphabetical.
        """
        return (
            list(
                dict(
                    sorted(frequency_map.items(), key=lambda x: x[1], reverse=True)
                ).keys()
            )
            if SORT_LETTERS
            else sorted(frequency_map)
        )

    def _next_letter_frequency(self, word: str) -> dict[str, int]:
        """Method that filters all words for only words that begin with word substring.
        Then from those words creates frequency map of next letter to number of words with that letter to determine most likely next letter."""
        next_idx = len(word)
        self.filtered_word_dist: dict[str, int] = {
            poss_word: freq
            for poss_word, freq in self.total_frequency_map.items()
            if poss_word.startswith(word.lower())
        }
        self.filtered_words = list(self.filtered_word_dist.keys())
        next_letter_count: dict[str, int] = {}
        for filt_word, freq in self.filtered_word_dist.items():
            if len(filt_word) > len(word):
                next_letter = filt_word[next_idx]
                if next_letter not in ALPHABET:
                    continue
                if next_letter not in next_letter_count:
                    next_letter_count[next_letter] = 0
                next_letter_count[next_letter] += freq
        return next_letter_count

    def clear_grid(self) -> list[list[str]]:
        """Clears letter from grid without changing grid size.
        Set include empty to True to denote clearing not reducing.
        """
        self.include_empty = True
        clear_letters = [
            letter if letter in self.remain_letters else EMPTY for letter in ALPHABET
        ]
        self.remain_grid = make_grid(MAX_ROWS, MAX_COLS, clear_letters)
        return self.remain_grid

    def reduce_grid(self) -> list[list[str]]:
        """Given letters to remove, reduce number of letters in grid and reduce grid size if possible.
        Set include empty to False to denote reducing not clearing."""
        self.include_empty = False
        reduce_letters = [letter for letter in self.remain_letters]
        self.remain_grid = make_grid(self.num_rows, self.num_cols, reduce_letters)
        return self.remain_grid
