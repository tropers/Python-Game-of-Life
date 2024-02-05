"""
gol.py

Originally written by Tristan Ropers in 2013,
refactored almost 11 years later in 2024.
"""

import random
import time
import math
import signal
import sys
from curses import *
from typing import List

# Delay used inbetween updates for game loop
DELAY = .05

MIN_RAND_CELLS = 3
MAX_RAND_CELLS = 1000

# Used to determine how big the game field can be in size
MAX_INFO_STR_LEN = 56

class GameOfLife():
    """
    GameOfLife implements John Conway's Game of Life in Python using
    the curses library.
    """
    def __init__(self, screen_offset: int = 1):
        self.alive = 0
        self.generation = 0
        self.max_x = 0
        self.max_y = 0
        self.screen_offset = screen_offset
        self.screen_buffer_offset = 10

        self.init_screen()

        self.gol_map: List[List[int]] = \
            [[0 for x in range(self.max_x)] for y in range(self.max_y)]

    def nodelay(self, on_off: bool):
        if on_off:
            self.stdscr.nodelay(1)
        else:
            self.stdscr.nodelay(0)

    def getch(self):
        return self.stdscr.getch()

    def init_screen(self):
        """
        init_screen initializes the curses environment
        """

        self.stdscr = initscr()
        self.stdscr.keypad(True)
        start_color()
        init_pair(1, COLOR_GREEN, COLOR_BLACK)
        init_pair(2, COLOR_CYAN, COLOR_BLACK)
        init_pair(3, COLOR_MAGENTA, COLOR_BLACK)
        init_pair(4, COLOR_BLUE, COLOR_BLACK)
        init_pair(5, COLOR_YELLOW, COLOR_BLACK)
        init_pair(6, COLOR_RED, COLOR_BLACK)
        init_pair(7, COLOR_CYAN, COLOR_CYAN)
        self.stdscr.attrset(color_pair(1) + A_BOLD)
        noecho()

        self.max_y, self.max_x = self.stdscr.getmaxyx()
        self.max_y -= self.screen_buffer_offset
        self.max_x -= (MAX_INFO_STR_LEN + 2 * self.screen_offset)

    def clear_map(self):
        self.generation = 0
        self.alive = 0

        self.gol_map: List[List[int]] = \
            [[0 for x in range(self.max_x)] for y in range(self.max_y)]

    def generate_random_map(self):
        rand = random.randint(MIN_RAND_CELLS, MAX_RAND_CELLS)
        fail_count = 0
        self.generation = 0

        for _ in range(rand):
            cell_set = False

            x = random.randint(0, self.max_x - 1)
            y = random.randint(0, self.max_y - 1)

            while not cell_set and fail_count < self.max_x * self.max_y:
                if self.gol_map[y][x] < 1:
                    self.alive += 1
                    self.gol_map[y][x] = 1
                    cell_set = True
                else:
                    x = random.randint(0, self.max_x - 1)
                    y = random.randint(0, self.max_y - 1)
                    fail_count += 1

    def print_key_hints(self):
        self.stdscr.move(self.max_y + 2, self.screen_offset)
        self.stdscr.addstr("Use arrow keys (or hjkl) to move and    ")
        self.stdscr.move(self.max_y + 3, self.screen_offset)
        self.stdscr.addstr("SPACEBAR to create / destroy cells.     ")
        self.stdscr.move(self.max_y + 4, self.screen_offset)
        self.stdscr.addstr("----------------------------------------")
        self.stdscr.move(self.max_y + 5, self.screen_offset)
        self.stdscr.addstr("Finish with q / RETURN.                 ")

    def draw_symbol(self, x, y, symbol, attr = 0):
        self.stdscr.move(y + self.screen_offset, x + self.screen_offset)
        self.stdscr.addstr(symbol, attr)

    def map_drawer_draw(self):
        for x in range(self.max_x):
            for y in range(self.max_y):
                if self.gol_map[y][x] == 0:
                    self.draw_symbol(x, y, '.')
                else:
                    self.draw_symbol(x, y, '#')

        self.stdscr.refresh()

    def map_drawer_loop(self):
        cur_x = math.floor(self.max_x / 2)
        cur_y = math.floor(self.max_y / 2)

        self.map_drawer_draw()
        self.print_key_hints()

        self.stdscr.move(cur_y + self.screen_offset, cur_x + self.screen_offset)

        com = self.stdscr.getch()
        while com != ord('\n'):

            if com == KEY_UP or com == ord('k'):
                if cur_y >= self.screen_offset:
                    cur_y -= 1
            elif com == KEY_DOWN or com == ord('j'):
                if cur_y <= self.max_y:
                    cur_y += 1
            elif com == KEY_LEFT or com == ord('h'):
                if cur_x >= self.screen_offset:
                    cur_x -= 1
            elif com == KEY_RIGHT or com == ord('l'):
                if cur_x <= self.max_x:
                    cur_x += 1
            elif com == ord(' '):
                if self.gol_map[cur_y][cur_x] == 0:
                    self.gol_map[cur_y][cur_x] = 1
                    self.draw_symbol(cur_x, cur_y, '#')
                    self.alive += 1
                else:
                    self.gol_map[cur_y][cur_x] = 0
                    self.draw_symbol(cur_x, cur_y, '.')
                    self.alive -= 1
            elif com == ord('q'):
                break
            else:
                pass

            self.stdscr.move(cur_y + self.screen_offset, cur_x + self.screen_offset)
            com = self.stdscr.getch()

        self.stdscr.clear()

    def game_setup(self):
        self.stdscr.addstr("Random? (y/n)")
        choice = self.stdscr.getch()

        # Wait until valid input is given
        while True:
            if choice == ord('y') or choice == ord('n'):
                break
            choice = self.stdscr.getch()

        self.stdscr.clear()

        if choice == ord('y'):
            self.generate_random_map()
        elif choice == ord('n'):
            self.map_drawer_loop()

    def draw_cell(self, x, y):
        self.stdscr.move(y + self.screen_offset, x + self.screen_offset)
        if self.gol_map[y][x] == 0:
            self.stdscr.addstr('.')
        else:
            if random.randint(0, 1) == 1:
                colpair = color_pair(1) + A_BOLD
            else:
                colpair = color_pair(1)

            self.draw_symbol(x, y, '@', colpair)

    def draw_map(self):
        for x in range(self.max_x):
            for y in range(self.max_y):
                self.draw_cell(x, y)

    def check_cell(self, x, y, new_gol_map):
        sum_neighbours = 0

        for i in range(-1, 2):
            for j in range(-1, 2):
                row = (y + i) % self.max_y
                column = (x + j) % self.max_x

                sum_neighbours += self.gol_map[row][column]

        sum_neighbours -= self.gol_map[y][x]

        if self.gol_map[y][x] == 1:
            if sum_neighbours < 2 or sum_neighbours > 3:
                new_gol_map[y][x] = 0
                self.alive -= 1
            elif 2 <= sum_neighbours <= 3:
                new_gol_map[y][x] = 1
        else:
            if sum_neighbours == 3:
                new_gol_map[y][x] = 1
                self.alive += 1

    def calculate_new_map(self) -> List[List[int]]:
        # new_gol_map = copy.deepcopy(self.gol_map)
        new_gol_map: List[List[int]] = \
            [[0 for x in range(self.max_x)] for y in range(self.max_y)]

        for x in range(self.max_x):
            for y in range(self.max_y):
                self.check_cell(x, y, new_gol_map)

        return new_gol_map

    def print_game_data(self):
        self.stdscr.attrset(color_pair(1) + A_BOLD)
        self.stdscr.move(self.max_y + 2, self.screen_offset)
        self.stdscr.addstr(f"Generation: {self.generation}      ")
        self.stdscr.move(self.max_y + 2, self.screen_offset + 30)
        self.stdscr.addstr("           ")
        self.stdscr.move(self.max_y + 2, self.screen_offset + 30)
        self.stdscr.addstr(f"Alive: {self.alive}")

        self.stdscr.move(int(self.max_y / 2), self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("GAME OF LIFE in Python      ")
        self.stdscr.move(int(self.max_y / 2) + 1, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("Tristan Ropers - 2013, 2024 ")
        self.stdscr.move(int(self.max_y / 2) + 2, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("-------------------------------------------------------")
        self.stdscr.move(int(self.max_y / 2) + 3, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("r - Reset game field (will randomly generate a new map)")
        self.stdscr.move(int(self.max_y / 2) + 4, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("c - Clear game field")
        self.stdscr.move(int(self.max_y / 2) + 5, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("e - Enter edit mode")
        self.stdscr.move(int(self.max_y / 2) + 6, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("q - Quit")
        self.stdscr.move(int(self.max_y / 2) + 7, self.max_x + self.screen_offset + 1)
        self.stdscr.addstr("SPACE - Pause the game.")

    def game_step(self):
        self.draw_map()
        self.print_game_data()
        self.stdscr.refresh()

        self.gol_map = self.calculate_new_map()
        self.generation += 1

def signal_handler(sig, frame):
    """
    signal_handler handles CTRL-C to gracefully exit curses
    """
    endwin()
    sys.exit(0)

def fetch_input(gol: GameOfLife, running: bool, is_paused: bool) -> (bool, bool):
    gol.nodelay(True)
    ch = gol.getch()
    if ch > -1:
        if ch == ord('r'):
            gol.generate_random_map()
            is_paused = False
        elif ch == ord('e'):
            gol.map_drawer_loop()
            is_paused = False
        elif ch == ord('c'):
            gol.clear_map()
            gol.draw_map()
            gol.print_game_data()
            is_paused = True
        elif ch == ord('q'):
            running = False
        elif ch == ord(' '):
            is_paused = not is_paused

    gol.nodelay(False)
    return running, is_paused

if __name__ == "__main__":
    # Setup CTRL-C handler
    signal.signal(signal.SIGINT, signal_handler)

    gol = GameOfLife()
    gol.game_setup()

    running = True
    is_paused = False

    while running:
        if not is_paused:
            gol.game_step()

        running, is_paused = fetch_input(gol, running, is_paused)
        time.sleep(DELAY)

    endwin()
