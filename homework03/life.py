import pathlib
import random
import copy

from typing import List, Optional, Tuple


Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:

    def __init__(
        self,
        size: Tuple[int, int],
        randomize: bool=True,
        max_generations: Optional[float]=float('inf')
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool=False) -> Grid:
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        if randomize:
            for i in range(self.rows):
                for j in range(self.cols):
                    grid[i][j] = random.randint(0, 1)
        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= cell[0] + i < self.rows and 0 <= cell[1] + j < self.cols and (i, j) != (0, 0):
                    neighbours.append(self.curr_generation[cell[0] + i][cell[1] + j])
        return neighbours

    def get_next_generation(self) -> Grid:
        new_grid = copy.deepcopy(self.curr_generation)
        for i in range(self.rows):
            for j in range(self.cols):
                n = 0
                for a in self.get_neighbours((i, j)):
                    if a:
                        n += 1
                if new_grid[i][j]:
                    if not 2 <= n <= 3:
                        new_grid[i][j] = 0
                else:
                    if n == 3:

                        new_grid[i][j] = 1
        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.prev_generation = copy.deepcopy(self.curr_generation)
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        if self.generations > self.max_generations:
            return True
        else:
            return False

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return not self.curr_generation == self.prev_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> 'GameOfLife':
        """
        Прочитать состояние клеток из указанного файла.
        """
        f = open(filename)
        grid = []
        row = []
        h = 0
        for line in f:
            row = [int(i) for i in line if i in '01']
            grid.append(row)
            h += 1
        w = len(row)
        game = GameOfLife((h, w), False)
        game.prev_generation = GameOfLife.create_grid(game)
        game.curr_generation = grid
        f.close()
        return game

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        f = open(filename, 'w')
        for i in range(self.rows):
            for j in range(self.cols):
                f.write(str(self.curr_generation[i][j]))
            f.write('\n')
        f.close()