from constants import MAX_ROWS, MAX_COLS, EMPTY, ALPHABET

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