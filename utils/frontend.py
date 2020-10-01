#!/usr/bin/env python3
import curses
from .consts import EXIT_SUCCESS

HEADER_TEXT = '--- CONTROL PANEL ---'
FOOTER_TEXT = "Press 'q' to exit | Use KEY_UP and KEY_DOWN to scroll through parameters"


class MetAromaticTUI:
    def __init__(self):
        self.input_parameters = {
            'code': '1rcy',
            'cutoff_distance': '4.9',
            'cutoff_angle': '109.5',
            'chain': 'A',
            'model': 'cp'
        }

        self.stdscr = curses.initscr()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        self.stdscr.clear()
        self.stdscr.refresh()

        self.show_header()
        self.show_input_window()
        self.show_output_window()
        self.show_footer()

        self.position = 1

    def __del__(self):
        # can also use curses.wrapper but I prefer OO approach
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def show_header(self):
        _, stdscr_width = self.stdscr.getmaxyx()
        midline = int((stdscr_width // 2) - (len(HEADER_TEXT) // 2) - len(HEADER_TEXT) % 2)
        self.window_header = curses.newwin(3, 0, 0, 0)
        self.window_header.border(0)
        self.window_header.addstr(1, midline, HEADER_TEXT)
        self.window_header.refresh()

    def show_input_window(self):
        position = self.window_header.getbegyx()[0] + self.window_header.getmaxyx()[0]
        self.window_input = curses.newwin(7, 0, position, 0)
        self.window_input.border(0)

        self.window_input.addstr(1, 2, 'PDB Code:', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(2, 2, 'Cutoff distance (Angstroms):', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(3, 2, 'Cutoff angle (Degrees):', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(4, 2, 'Chain:', curses.A_BOLD + curses.A_UNDERLINE)
        self.window_input.addstr(5, 2, 'Model:', curses.A_BOLD + curses.A_UNDERLINE)

        self.window_input.addstr(1, 35, self.input_parameters['code'])
        self.window_input.addstr(2, 35, self.input_parameters['cutoff_distance'])
        self.window_input.addstr(3, 35, self.input_parameters['cutoff_angle'])
        self.window_input.addstr(4, 35, self.input_parameters['chain'])
        self.window_input.addstr(5, 35, self.input_parameters['model'])
        
        self.window_input.refresh()

    def show_output_window(self):
        position = self.window_input.getbegyx()[0] + self.window_input.getmaxyx()[0]
        self.window_output = curses.newwin(len(self.input_parameters) + 2, 0, position, 0)
        self.window_output.border(0)

    def show_footer(self):
        stdscr_height, _ = self.stdscr.getmaxyx()
        self.window_footer = curses.newwin(1, 0, stdscr_height - 1, 0)
        self.window_footer.addstr(0, 1, FOOTER_TEXT)
        self.window_footer.bkgd(curses.A_REVERSE)
        self.window_footer.refresh()

    def navigate(self, increment):
        self.position += increment
        if self.position <= 1:
            self.position = 1
        elif self.position > len(self.input_parameters):
            self.position = len(self.input_parameters)

    def event_loop(self):
        key_input = None

        while key_input != ord('q'):
            if key_input == curses.KEY_DOWN:
                self.navigate(1)
            elif key_input == curses.KEY_UP:
                self.navigate(-1)

            for index, parameter in enumerate(self.input_parameters, 1):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                label = parameter.capitalize().replace('_', ' ')

                self.window_output.addstr(index, 2, label, mode)

            self.window_output.refresh()
            key_input = self.stdscr.getch()

        return EXIT_SUCCESS
