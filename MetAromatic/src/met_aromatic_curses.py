import curses
from .primitives.consts import (
    EXIT_SUCCESS,
    HEADER_TEXT,
    FOOTER_TEXT,
    FORMATTED_HEADER
)
from .met_aromatic import MetAromatic


class MetAromaticCurses:

    def __init__(self, parameters: dict) -> None:
        self.parameters = parameters

        results = MetAromatic(
            self.parameters['cutoff_distance'],
            self.parameters['cutoff_angle'],
            self.parameters['chain'],
            self.parameters['model']
        ).get_met_aromatic_interactions(
            self.parameters['code']
        )

        self.parameters['cutoff_distance'] = str(self.parameters['cutoff_distance'])
        self.parameters['cutoff_angle'] = str(self.parameters['cutoff_angle'])

        self.results = results['results']
        self.exit_code = results['exit_code']
        self.exit_status = results['exit_status']

        self.stdscr = curses.initscr()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        self.stdscr.clear()
        self.stdscr.refresh()

        self.position = 1

    def __del__(self) -> None:
        # can also use curses.wrapper but I prefer OO approach
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

        if self.exit_code != EXIT_SUCCESS:
            print(self.exit_status)

    def show_header(self) -> None:
        _, stdscr_width = self.stdscr.getmaxyx()
        midline = int((stdscr_width // 2) - (len(HEADER_TEXT) // 2) - len(HEADER_TEXT) % 2)
        self.window_header = curses.newwin(3, 0, 0, 0)
        self.window_header.border(0)
        self.window_header.addstr(1, midline, HEADER_TEXT, curses.A_BOLD)
        self.window_header.refresh()

    def show_parameters_window(self) -> None:
        position = self.window_header.getbegyx()[0] + self.window_header.getmaxyx()[0]
        self.window_input = curses.newwin(7, 0, position, 0)
        self.window_input.border(0)

        self.window_input.addstr(1, 2, 'PDB Code:', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(2, 2, 'Cutoff distance (Angstroms):', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(3, 2, 'Cutoff angle (Degrees):', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(4, 2, 'Chain:', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(5, 2, 'Model:', curses.A_BOLD + curses.A_UNDERLINE)

        self.window_input.addstr(1, 35, self.parameters['code'])
        self.window_input.addstr(2, 35, self.parameters['cutoff_distance'])
        self.window_input.addstr(3, 35, self.parameters['cutoff_angle'])
        self.window_input.addstr(4, 35, self.parameters['chain'])
        self.window_input.addstr(5, 35, self.parameters['model'])

        self.window_input.refresh()

    def show_results_window(self) -> None:
        position = self.window_input.getbegyx()[0] + self.window_input.getmaxyx()[0]
        self.window_output = curses.newwin(len(self.results) + 3, 0, position, 0)
        self.window_output.addstr(1, 2, FORMATTED_HEADER, curses.A_BOLD + curses.A_UNDERLINE)
        self.window_output.border(0)

    def show_footer(self) -> None:
        stdscr_height, _ = self.stdscr.getmaxyx()
        self.window_footer = curses.newwin(1, 0, stdscr_height - 1, 0)
        self.window_footer.addstr(0, 1, FOOTER_TEXT)
        self.window_footer.bkgd(curses.A_REVERSE)
        self.window_footer.refresh()

    def navigate(self, increment: int) -> None:
        self.position += increment

        if self.position <= 2:
            self.position = 2
        elif self.position > len(self.results) + 1:
            self.position = len(self.results) + 1

    def event_loop(self) -> int:
        if self.exit_code != EXIT_SUCCESS:
            return self.exit_code

        self.show_header()
        self.show_parameters_window()
        self.show_results_window()
        self.show_footer()

        key_input = None

        while key_input != ord('q'):

            if key_input == curses.KEY_DOWN:
                self.navigate(1)
            elif key_input == curses.KEY_UP:
                self.navigate(-1)

            for index, line in enumerate(self.results, 2):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                formatted_line = '{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}'.format(*line.values())
                self.window_output.addstr(index, 2, formatted_line, mode)

            self.window_output.refresh()
            key_input = self.stdscr.getch()

        return self.exit_code
