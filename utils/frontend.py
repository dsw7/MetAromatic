#!/usr/bin/env python3
import curses

HEADER_TEXT = '--- CONTROL PANEL ---'
FOOTER_TEXT = "Press 'q' to exit | Use KEY_UP and KEY_DOWN to scroll through machines"


class ControlPanel:
    def __init__(self):
        self.machines = [
            {'machine': 'machine_{}.local'.format(i), 'status': False} for i in range(1, 10)
        ]

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

    def __del__(self):  # can also use curses.wrapper but I prefer OO approach
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
        # window is positioned +1 lines below bottom left of each of preceding window
        position = self.window_header.getbegyx()[0] + self.window_header.getmaxyx()[0]
        self.window_input = curses.newwin(len(self.machines) + 2, 0, position, 0)
        self.window_input.border(0)

    def show_output_window(self):
        # window is positioned +1 lines below bottom left of each of preceding window
        position = self.window_input.getbegyx()[0] + self.window_input.getmaxyx()[0]
        self.window_output = curses.newwin(len(self.machines) + 2, 0, position, 0)
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
        elif self.position > len(self.machines):
            self.position = len(self.machines)

    def event_loop(self):
        key_input = None

        while key_input != ord('q'):
            if key_input == curses.KEY_DOWN:
                self.navigate(1)
            elif key_input == curses.KEY_UP:
                self.navigate(-1)
            elif key_input == 10:
                self.machines[self.position - 1]['status'] = not self.machines[self.position - 1]['status']

            for index, machine in enumerate(self.machines, 1):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                if machine['status']:
                    status = '[x]'
                else:
                    status = '[ ]'

                self.window_input.addstr(index, 2, '{} {}'.format(status, machine['machine']), mode)
                self.window_output.addstr(index, 2, '[ ] {}'.format(machine['machine']), mode)

            self.window_input.refresh()
            self.window_output.refresh()
            key_input = self.stdscr.getch()
