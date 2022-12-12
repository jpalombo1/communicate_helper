from communicate.communicator import Communicator
from communicate.constants import ALPHABET, MAX_COLS, MAX_ROWS
from communicate.gui import GUI
from communicate.make_grid import make_grid

SMART: bool = True


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
