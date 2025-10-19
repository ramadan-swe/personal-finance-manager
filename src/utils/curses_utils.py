# src/utils/curses_utils.py
import curses

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # React to keys instantly, without waiting for Enter
    stdscr.keypad(True)  # Enable special keys like arrow keys
    return stdscr

def teardown_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def display_message(stdscr, message, y, x):
    stdscr.addstr(y, x, message)
    stdscr.refresh()

def get_user_input(stdscr, prompt, y, x, hide_input=False):
    stdscr.addstr(y, x, prompt)
    input_str = ""
    while True:
        if hide_input:
            stdscr.addstr(y, x + len(prompt), ' ' * len(input_str))
            stdscr.addstr(y, x + len(prompt), '*' * len(input_str))
        else:
            stdscr.addstr(y, x + len(prompt), ' ' * (len(input_str) + 10)) # Clear more space
            stdscr.addstr(y, x + len(prompt), input_str)
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_ENTER or key == 10 or key == 13: # Enter key
            break
        elif key == curses.KEY_BACKSPACE or key == 127: # Backspace key
            if len(input_str) > 0:
                input_str = input_str[:-1]
        elif 32 <= key <= 126: # Printable ASCII characters
            input_str += chr(key)
    return input_str