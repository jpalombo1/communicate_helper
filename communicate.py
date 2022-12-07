"""
This file is for a very real problem of limited communication with immobile people who may onyl be anle to use their arms to point or fingers 1-5.

To communicate efficiently, there are 3 methods:
    1. Point - In real life put 5 letters on each page, skim through pages until patient points to letter on page or finger up for index of letter on page.
    2. Grid - Get full view of grid 5x5 where patient uses one finger to choose row then next to choose column corresponding to letter in it.
    3. GridPoint - Patient can't use fingers so looks at grid and picks row by selecting 1-5 on paper, then within row 1-5 for letter

Efficiency gains of these methods are stark compared to verbal saying each letter (Is it A,B,C,D...) for every letter.
    1. (M letters, N in alphabet) Computational Complexity formerly M*N since do N letters M times, but now with grid/point it is on order of M*N^1/2 since square grid and indexing reduces space by square factor.
    2. Procedural complexity reduced as M iterations of N alphabet letters, average N/2 attempts per M letter yields M * 26/2 = 13M for M letter word, now really on order O(1) for lookup 1-5 and 2 lookups needed so 2M, so 13M->2M is 6.5x speedup
    3. Even more efficiencies in here using language corpus since we can eliminate non existent follow on letters to constructed word and reduce/tune space of lookups as we build word so lookup itself shortened 1-5, to 1-3 etc. as less letters become possible.
    4. Even can order letters in grid by common usage so lookup of common letters in (1,1) topleft corner of grid more often, giving more speedup and localization to used letters in setup.

Build Out Interfactive UI for Communication, first with CLI but for atual Patient Usage/visibility/ precision of pointing (if no fingers) we make GUI.

PreReqs: install python3, python3-pip, python3-tk, python3-venv. pip install nltk.
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial
from typing import Optional

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


class LetterChoice(Enum):
    """Ways to make letter choices."""

    GRID = auto()
    GRID_POINT = auto()
    POINT = auto()


@dataclass
class Communicator:
    start_grid: list[list[str]]
    smart: bool = False
    include_empty: bool = True

    def __post_init__(self):
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


def make_grid(
    num_rows: int = MAX_ROWS, num_cols: int = MAX_COLS, letters: list[str] = ALPHABET
) -> list[list[str]]:
    """Function to make grid object given a max sample length and list of letters.

    If number of columns exceeds max sample length, raise error. If no entries return 1 empty square.
    Add extra spaces as needed if dimensions of square grid exceed number of needed letters.
    Put letters into list of list or grid.
    """
    out_letters = [letter for letter in letters]
    if num_rows == 0 or num_cols == 0:
        return [[EMPTY]]
    extra_spaces = num_rows * num_cols - len(letters)
    if extra_spaces > 0:
        for _ in range(extra_spaces):
            out_letters.append(EMPTY)
    return [
        [out_letters[row * num_cols + col] for col in range(num_cols)]
        for row in range(num_rows)
    ]


@dataclass
class CLI:
    """Command line Interface UI. Has Communicator object to do letter selection, letter_choice for way to select."""

    comms: Communicator

    @property
    def grid(self) -> list[list[str]]:
        """Convenience method to get grid object itself directly."""
        return self.comms.remain_grid

    def display_grid(self) -> str:
        """Display grid of letters and associated rows/columns to Command Line."""
        grid = (
            "   | "
            + " | ".join(str(col + 1) for col in range(self.comms.num_cols))
            + "\n"
        )
        for row_num, row in enumerate(self.grid):
            grid += (
                f" {row_num+1} | " + " | ".join(letter.upper() for letter in row) + "\n"
            )
        return grid

    def display_row(self, row: int) -> str:
        """Display row with letters and associated numbers to Command Line"""
        row_vals = self.comms.choose_grid_row_reduce(row)
        row_str = " | ".join(str(col + 1) for col in range(len(row_vals))) + "\n"
        row_str += " | ".join(letter.upper() for letter in row_vals) + "\n"
        return row_str

    def _choose_method(self) -> LetterChoice:
        """Based on letter choice, choose type of game."""
        CHOICE_INPUT = {
            GRID_PROMPT.lower(): LetterChoice.GRID,
            GRIDPOINT_PROMPT.lower(): LetterChoice.GRID_POINT,
            POINT_PROMPT.lower(): LetterChoice.POINT,
        }
        while True:
            input_str = input(
                f"Choose Method to Pick Letters, Choices {list(CHOICE_INPUT.keys())}: "
            )
            if input_str.lower() not in CHOICE_INPUT:
                print("Invalid method, choose again!")
                continue
            return CHOICE_INPUT[input_str.lower()]

    def play(self) -> None:
        """Choose which type of way to get letters based on letter choice and play it. Keep adding onto word and give suggestions.
        If only 1 suggestion left, that is the word, stop! If no letters left to chose but multiple words, just return."""
        self.letter_choice = self._choose_method()
        PLAY_MAP = {
            LetterChoice.GRID: self._play_grid,
            LetterChoice.POINT: self._play_point,
            LetterChoice.GRID_POINT: self._play_gridpoint,
        }
        word = BLANK
        incomplete = True
        while incomplete:
            try:
                print(f"Word so far: {word}")
                print(
                    f"Suggestions: ({len(self.comms.filtered_words)}) {self.comms.filtered_words[:MAX_SUGGESTIONS]}"
                )
                incomplete, word = PLAY_MAP[self.letter_choice](word)
                if self.comms.done:
                    print(f"Done! Final word: {self.comms.filtered_words[0]}")
                    return
            except ValueError as e:
                print(e)
        print(f"Final word: {word}")

    def _play_point(self, word: str) -> tuple[bool, str]:
        """Point Method where 1 row at time shown, n to pass or choose number 1-#entries left in row.
        After reducing letter available as follow on to word.."""
        for row_num in range(self.comms.num_rows):
            row_vals = self.comms.choose_grid_row_reduce(row_num)
            sample_len = len(row_vals)
            point_choices = [CLI_NEXT] + [
                str(samp_num + 1) for samp_num in range(sample_len)
            ]
            print(self.display_row(row_num))
            input_str = input(
                f"Enter n/N if letter not on this page, else enter \nChoices {point_choices}: "
            )
            if input_str.lower() == CLI_NEXT:
                continue
            if input_str.lower() == CLI_DONE:
                return False, word
            if input_str not in point_choices or not input_str.isdigit():
                raise ValueError("Not a valid choice! Please choose again")

            index = int(input_str) - 1
            word += str(row_vals[index])
            self.comms.eval_grid(word)
            self.comms.reduce_grid()
            break

        return True, word

    def _play_gridpoint(self, word: str) -> tuple[bool, str]:
        """GridPoint Method where whole grid shown, choose row then index of letter.
        Grid then changes size based on available letters for follow letter to work
        and choice of new rows/cols of reduced size grid."""
        sample_len = self.comms.num_rows
        if sample_len == 1:
            row_num = 0
        else:
            print(self.display_grid())
            row_choices = [CLI_DONE] + [
                str(samp_num + 1) for samp_num in range(sample_len)
            ]
            input_str = input(
                f"Enter d/D for done making word, else enter row of word \nChoices {row_choices}: "
            )
            if input_str.lower() == CLI_DONE:
                return False, word
            if input_str not in row_choices or not input_str.isdigit():
                raise ValueError("Not a valid choice! Please choose again")
            row_num = int(input_str) - 1
        row_vals = self.comms.choose_grid_row_reduce(row_num)
        print(self.display_row(row_num))
        sample_len = len(row_vals)
        point_choices = [CLI_DONE] + [
            str(samp_num + 1) for samp_num in range(sample_len)
        ]
        input_str = input(
            f"Enter d/D for done making word, else enter 1-{sample_len}\nChoices {point_choices}: "
        )
        if input_str.lower() == CLI_DONE:
            return False, word
        if input_str not in point_choices or not input_str.isdigit():
            raise ValueError("Not a valid choice! Please choose again")
        index = int(input_str) - 1
        word += str(row_vals[index])
        self.comms.eval_grid(word)
        self.comms.reduce_grid()

        return True, word

    def _play_grid(self, word: str) -> tuple[bool, str]:
        """Grid Method where whole grid shown, choose row then index of letter.
        Grid then clears letters based on available letters for follow letter to work
        and choice between corresponding rows/cols where letters still exist."""
        row_len = self.comms.num_rows
        print(self.display_grid())
        row_choices = [CLI_DONE] + [
            str(row_num + 1)
            for row_num in range(row_len)
            if not len(self.comms.choose_grid_row_reduce(row_num)) == 0
        ]

        input_str = input(
            f"Enter d/D for done making word, else enter row of word \nChoices {row_choices}: "
        )
        if input_str not in row_choices or not input_str.isdigit():
            raise ValueError("Not a valid choice! Please choose again\n")
        if input_str.lower() == CLI_DONE:
            return False, word
        row = int(input_str) - 1
        col_choices = [CLI_DONE] + [
            str(idx + 1) for idx in self.comms.choose_grid_row_reduce_idx(row)
        ]
        input_str = input(
            f"Enter d/D for done making word, else enter col of word \nChoices {col_choices}: "
        )
        if input_str not in col_choices or not input_str.isdigit():
            raise ValueError("Not a valid choice! Please choose again\n")
        if input_str.lower() == CLI_DONE:
            return False, word
        col = int(input_str) - 1
        word += self.comms.choose_grid_item(row, col)
        self.comms.eval_grid(word)
        self.comms.clear_grid()
        return True, word


class GUI(tk.Tk):
    def __init__(self, comms: Communicator):
        """Constructor does Tkinter initialization then sets up GUI components.

        Starts with main window of given size. First frame inside of it is Choose Menu window, with 3 full size buttons for 3 methods
        3 frames corresponding to methods, each with Frame with grid subframe containing grid of buttons,
        textbox subframe of status/suggestions, nav buttons back/done subframe.

        """
        super().__init__()
        self.comms = comms
        self.word: str = BLANK
        self.sentence: str = BLANK
        self.letter_choice: LetterChoice = LetterChoice.GRID
        self.word_msg: Optional[tk.Message] = None
        self.grid_buttons: list[list[tk.Button]] = []
        self.suggest_buttons: list[tk.Button] = []

        # Main Window
        self.title(TITLE)
        self.geometry(f"{WIDTH_PX}x{HEIGHT_PX}")

        # Choose Method Page
        self.choose_method_frame = tk.Frame(self)
        self.current_frame: tk.Frame = self.choose_method_frame
        self.choose_method_frame.pack()
        self.choose_label = tk.Label(
            self.choose_method_frame, text="Choose Method to Pick Letters"
        )
        self.choose_label.pack()
        self.choose_grid = self._gen_choose_button(text=GRID_PROMPT)
        self.choose_grid.pack(side=tk.TOP)
        self.choose_gridpoint = self._gen_choose_button(text=GRIDPOINT_PROMPT)
        self.choose_gridpoint.pack(side=tk.TOP)
        # self.choose_point = self._gen_choose_button(text=POINT_PROMPT)
        # self.choose_point.pack(side=tk.BOTTOM)

        # Grid Page
        self.grid_frame = tk.Frame(self)
        self.grid_button_frame = self._gen_nav_buttons(self.grid_frame)
        self.grid_button_frame.grid(row=0, column=0, rowspan=5, columnspan=3)
        self.grid_letter_frame = tk.Frame(self.grid_frame)
        self.grid_letter_frame.grid(row=0, column=3, rowspan=5, columnspan=10)
        self.grid_word_frame = tk.Frame(self.grid_frame)
        self.grid_word_frame.grid(row=0, column=13, rowspan=1, columnspan=4)
        self.grid_suggest_frame = tk.Frame(self.grid_frame)
        self.grid_suggest_frame.grid(row=1, column=13, rowspan=4, columnspan=4)

        # GridPoint Page
        self.gridpoint_frame = tk.Frame(self)
        self.gridpoint_button_frame = self._gen_nav_buttons(self.gridpoint_frame)
        self.gridpoint_button_frame.grid(row=0, column=0, rowspan=5, columnspan=3)
        self.gridpoint_letter_frame = tk.Frame(self.gridpoint_frame)
        self.gridpoint_letter_frame.grid(row=0, column=3, rowspan=5, columnspan=10)
        self.gridpoint_word_frame = tk.Frame(self.gridpoint_frame)
        self.gridpoint_word_frame.grid(row=0, column=13, rowspan=1, columnspan=4)
        self.gridpoint_suggest_frame = tk.Frame(self.gridpoint_frame)
        self.gridpoint_suggest_frame.grid(row=1, column=13, rowspan=4, columnspan=4)

        # Point Page
        self.point_frame = tk.Frame(self)
        # self.point_button_frame = self._gen_nav_buttons(self.point_frame)
        # self.point_button_frame.pack(side=NAV_BUTTON_SIDE)
        # self.point_word_frame = tk.Frame(self.point_frame)
        # self.point_word_frame.pack(side=OUTPUT_SIDE)
        # self.point_letter_frame = tk.Frame(self.point_frame)
        # self.point_letter_frame.pack()

    def _choose_method(self, method: str) -> None:
        """Callback of button press in Choose Menu.

        Depending on button that forms incoming method string, sets the method's frame as visible.
        Also notes the method, clears the display text, updates the letter grid, and drops previous frame from view.
        """
        CHOICE_INPUT = {
            GRID_PROMPT.lower(): self.grid_frame,
            GRIDPOINT_PROMPT.lower(): self.gridpoint_frame,
            POINT_PROMPT.lower(): self.point_frame,
        }
        CHOICE_MAP = {
            GRID_PROMPT.lower(): LetterChoice.GRID,
            GRIDPOINT_PROMPT.lower(): LetterChoice.GRID_POINT,
            POINT_PROMPT.lower(): LetterChoice.POINT,
        }
        self.current_frame = CHOICE_INPUT[method]
        self.letter_choice = CHOICE_MAP[method]
        self._execute()
        self.current_frame.pack()
        self.choose_method_frame.pack_forget()

    def _execute(self) -> None:
        """Convenience method for evaluating and updating grid, updating prompt and suggestions, with word triggered by buttons."""
        self.comms.reset_grid()
        self.comms.eval_grid(self.word)
        if self.letter_choice == LetterChoice.GRID:
            self.comms.clear_grid()
        else:
            self.comms.reduce_grid()
        self._update_letters()
        self._update_prompt()
        self._update_suggestions()

    def _back(self) -> None:
        """Back Button Callback when pressed will reset and update grid.

        Set the choose menu frame in view and forgets former frame, also clear word and sentence.
        """
        self.word = BLANK
        self.sentence = BLANK
        self._execute()
        self.choose_method_frame.pack()
        self.current_frame.pack_forget()

    def _suggest_done(self, add_word: str) -> None:
        """Suggestion button callback if clicked, it will automatically add word to sentence.

        Resets word, also updates message for sentence so far and resets grid for next word and blanks suggestions.
        """
        self.word = BLANK
        self.sentence += f" {add_word}"
        self._execute()

    def _done(self) -> None:
        """Done with making single word and add word to sentence.

        Actual word used wither current word if possible, first option of possible words if substrign not possible, or just substring word if no possibilities.
        Resets word, also updates message for sentence so far and resets grid for next word."""
        add_word = (
            self.word
            if self.word in POSSIBLE_WORDS
            else self.comms.filtered_words[0]
            if len(self.comms.filtered_words) > 0
            else self.word
        )
        self.word = BLANK
        self.sentence += f" {add_word}"
        self._execute()

    def _undo(self) -> None:
        """When make erroneous addition to word, undo's it by reducing word by last character.

        It must also re-evaluate last word by resetting grid, evaluating it with short word, and clear/reduce depending on method.
        """
        self.word = self.word[:-1]
        self._execute()

    def _custom(self) -> None:
        """When want to make word thats not possible, toggle this option to access all letters.

        If toggled to not smart, just forces reset, if retoggled to smart does evaluation on current word.
        """
        self.comms.smart = not self.comms.smart
        self._execute()

    def _pick_letter(self, letter: str) -> None:
        """Callback of each letter button where press of it sends corresponding letter to arg.

        If not done and not empty letter picked, it will add letter to word, then run communicator.
        For Grid mode it will clear grid, leaving empty spots on board. For others it will reduce grid for smaller size.
        It will also check for done status if no words left and call updating the display .
        """
        if letter == EMPTY:
            return
        self.word += letter
        self._execute()
        if self.comms.done:
            self._done()

    def _gen_choose_button(self, text: str) -> tk.Button:
        """Method to form choose menu button to reduce repeatable code.

        Enter text of button as arg to choose_method callback
        so all similar buttons can use same function but get different results based on content of button.
        """
        return tk.Button(
            self.choose_method_frame,
            text=text,
            width=CHOOSE_BUTTON_WIDTH,
            height=CHOOSE_BUTTON_HEIGHT,
            font=tk.font.Font(size=CHOOSE_BUTTON_FONT),
            command=partial(self._choose_method, text.lower()),
        )

    def _gen_nav_buttons(self, frame: tk.Frame) -> tk.Frame:
        """Method to form frame of nav buttons Back/Done buttons to reduce repeatable code in all subframes that use them."""
        self.button_frame = tk.Frame(frame)
        self.done_button = tk.Button(
            self.button_frame,
            text=DONE_TEXT,
            width=NAV_BUTTON_WIDTH,
            height=NAV_BUTTON_HEIGHT,
            font=tk.font.Font(size=NAV_BUTTON_FONT),
            command=self._done,
        )
        self.done_button.grid(row=0, column=0)
        self.undo_button = tk.Button(
            self.button_frame,
            text=UNDO_TEXT,
            width=NAV_BUTTON_WIDTH,
            height=NAV_BUTTON_HEIGHT,
            font=tk.font.Font(size=NAV_BUTTON_FONT),
            command=self._undo,
        )
        self.undo_button.grid(row=1, column=0)
        self.custom_button = tk.Button(
            self.button_frame,
            text=CUSTOM_TEXT,
            width=NAV_BUTTON_WIDTH,
            height=NAV_BUTTON_HEIGHT,
            font=tk.font.Font(size=NAV_BUTTON_FONT),
            command=self._custom,
        )
        self.custom_button.grid(row=2, column=0)
        self.back_button = tk.Button(
            self.button_frame,
            text=BACK_TEXT,
            width=NAV_BUTTON_WIDTH,
            height=NAV_BUTTON_HEIGHT,
            font=tk.font.Font(size=NAV_BUTTON_FONT),
            command=self._back,
        )
        self.back_button.grid(row=3, column=0)

        return self.button_frame

    def _update_letters(self):
        """Function that adds buttons to grid subframe object of given choose method frame used for selecting letters

        It finds which choice frame the gird is applied to using choose method, then forget old buttons in frame if they exist.
        It then creates new buttons, one for each letter in grid object. If Grid keeps empty buttons, else doesn't add them.
        Finally, re-puts the new buttons into a grid.
        """
        FRAME_MAP = {
            LetterChoice.GRID: self.grid_letter_frame,
            LetterChoice.GRID_POINT: self.gridpoint_letter_frame,
            LetterChoice.POINT: self.point_frame,
        }
        frame = FRAME_MAP[self.letter_choice]
        for row in self.grid_buttons:
            for btn in row:
                btn.grid_forget()
        self.grid_buttons: list[list[tk.Button]] = [
            [
                tk.Button(
                    frame,
                    width=LETTER_WIDTH,
                    height=LETTER_HEIGHT,
                    font=tk.font.Font(size=int(LETTER_BUTTON_FONT / len(row))),
                    text=val.upper(),
                    command=partial(self._pick_letter, val),
                )
                for val in row
                if val != EMPTY or self.letter_choice == LetterChoice.GRID
            ]
            for row in self.comms.remain_grid
        ]

        for row_num, row in enumerate(self.grid_buttons):
            for col_num, btn in enumerate(row):
                btn.grid(row=row_num, column=col_num)

    def _update_suggestions(self, force_suggestions: Optional[list[str]] = None):
        """From given suggestions of smart algorithm, create buttons for each.

        It finds which choice frame the gird is applied to using choose method, then forget old suggestions in frame if they exists.
        Then adds current suggestions.
        """
        FRAME_MAP = {
            LetterChoice.GRID: self.grid_suggest_frame,
            LetterChoice.GRID_POINT: self.gridpoint_suggest_frame,
            LetterChoice.POINT: self.point_frame,
        }
        frame = FRAME_MAP[self.letter_choice]
        for btn in self.suggest_buttons:
            btn.grid_forget()
        suggestions = self.comms.filtered_words[:MAX_SUGGESTIONS]
        if force_suggestions is not None:
            suggestions = force_suggestions
        self.suggest_buttons = [
            tk.Button(
                frame,
                width=SUGGEST_WIDTH,
                height=int(SUGGEST_HEIGHT * MAX_SUGGESTIONS / len(suggestions)),
                font=tk.font.Font(size=SUGGEST_BUTTON_FONT),
                text=suggestion,
                command=partial(self._suggest_done, suggestion),
            )
            for suggestion in suggestions
        ]

        for row_num, btn in enumerate(self.suggest_buttons):
            btn.grid(row=row_num, column=0)

    def _update_prompt(self, force_text: Optional[str] = None) -> str:
        """Fuction that updates display prompt with current word created, word suggestions list, and if final word.

        It finds which choice frame the gird is applied to using choose method, then forget old message in frame if it exists.
        Then adds current word and sentence.
        """
        FRAME_MAP = {
            LetterChoice.GRID: self.grid_word_frame,
            LetterChoice.GRID_POINT: self.gridpoint_word_frame,
            LetterChoice.POINT: self.point_frame,
        }
        frame = FRAME_MAP[self.letter_choice]
        if self.word_msg:
            self.word_msg.pack_forget()
        display = f"Custom Mode: {'Off' if self.comms.smart else 'On'}\n"
        display += f"Sentence so far: {self.sentence}\n\n"
        display += f"Word So Far: {self.word}\n\n"
        self.word_msg = tk.Message(
            frame,
            text=force_text if force_text is not None else display,
            font=tk.font.Font(size=MSG_FONT),
            width=MSG_WIDTH,
        )
        self.word_msg.pack()
        return display


def main():
    """Execute Main Method. Make grid and intialize Communicator, which is used in CLI"""
    start_grid = make_grid(MAX_ROWS, MAX_COLS, ALPHABET)
    communicator = Communicator(start_grid=start_grid, smart=SMART)
    # cli = CLI(comms=communicator)
    # cli.play()
    gui = GUI(comms=communicator)
    gui.mainloop()


if __name__ == "__main__":
    main()
