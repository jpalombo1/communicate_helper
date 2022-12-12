from dataclasses import dataclass

from communicate.communicator import Communicator
from communicate.constants import (
    BLANK,
    GRID_PROMPT,
    GRIDPOINT_PROMPT,
    MAX_SUGGESTIONS,
    POINT_PROMPT,
)
from communicate.letter_choice import LetterChoice

# CLI VALUES
CLI_DONE: str = "d"
CLI_NEXT: str = "n"


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
