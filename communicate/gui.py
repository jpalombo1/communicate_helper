import tkinter as tk
from functools import partial
from typing import Optional

from communicate.communicator import Communicator
from communicate.constants import (
    BLANK,
    EMPTY,
    GRID_PROMPT,
    GRIDPOINT_PROMPT,
    MAX_SUGGESTIONS,
    POINT_PROMPT,
    POSSIBLE_WORDS,
)
from communicate.letter_choice import LetterChoice

# GUI VALUES
TITLE: str = "LetterPicker"
WIDTH_PX: int = 1450
HEIGHT_PX: int = 800

LETTER_WIDTH: int = 6
LETTER_HEIGHT: int = 2
LETTER_BUTTON_FONT: int = 250

CHOOSE_BUTTON_WIDTH: int = 20
CHOOSE_BUTTON_HEIGHT: int = 3
CHOOSE_BUTTON_FONT: int = 100

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

    def _update_letters(self) -> None:
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
        self.grid_buttons = [
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
