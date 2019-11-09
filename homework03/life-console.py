import curses

from life import GameOfLife
from ui import UI


class Console(UI):

    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.addstr(0, 0, '+' + ''.join(['-' for _ in range(self.life.cols)]) + '+')
        for i in range(self.life.rows):
            screen.addch(i + 1, 0, '|')
            screen.addch(i + 1, self.life.cols + 1, '|')
        screen.addstr(self.life.rows + 1, 0, '+' + ''.join(['-' for _ in range(self.life.cols)]) + '+')

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j]:
                    screen.addch(i + 1, j + 1, '*')
                else:
                    screen.addch(i + 1, j + 1, ' ')

    def run(self) -> None:
        screen = curses.initscr()
        screen.clear()
        self.draw_borders(screen)
        screen.refresh()
        while not self.life.is_max_generations_exceeded and self.life.is_changing:
            self.draw_grid(screen)
            screen.refresh()
            self.life.step()
        curses.endwin()