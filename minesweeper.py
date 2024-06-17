import random

class MinesweeperBoard:
    def __init__(self,
                 size_x: int,
                 size_y: int,
                 number_of_mines: int,
                 random_seed: int = None):

        self.size_x = size_x
        self.size_y = size_y
        self.number_of_mines = number_of_mines
        self.revealed_cells = 0

        self.random_seed = random_seed

        self.board = []

        self.generate_board()

    def generate_board(self):
        for i in range(self.number_of_mines):
            self.board.append(MinesweeperCell(bomb=True))
        for i in range(self.size_x * self.size_y - self.number_of_mines):
            self.board.append(MinesweeperCell(bomb=False))

        if self.random_seed:
            random.seed(self.random_seed)
        random.shuffle(self.board)

        for i in range(self.size_x * self.size_y):
            if self.board[i].bomb:
                continue

            x = i % self.size_x
            y = i // self.size_x

            for y_offset in range(-1, 2):
                for x_offset in range(-1, 2):
                    if x + x_offset < 0 or x + x_offset >= self.size_x:
                        continue
                    if y + y_offset < 0 or y + y_offset >= self.size_y:
                        continue

                    cell = self.board[i]
                    adjacent_cell = self.board[(y + y_offset) * self.size_x + x + x_offset]
                    if adjacent_cell.bomb:
                        cell.adjacent_bombs += 1
                    if cell is not adjacent_cell:
                        cell.adjacent_cells.append(adjacent_cell)

    def reveal_cell(self,
                    x: int,
                    y: int):
        cell = self.board[y * self.size_x + x]
        cell.revealed = True
        self.revealed_cells += 1

        if cell.bomb:
            return False

        if cell.adjacent_bombs == 0:
            for adjacent_cell in cell.adjacent_cells:
                if not adjacent_cell.revealed:
                    self.reveal_cell(adjacent_cell)

        return True

    def flag_cell(self,
                  x: int,
                  y: int):
        cell = self.board[y * self.size_x + x]
        cell.flagged = not cell.flagged

class MinesweeperCell:
    def __init__(self,
                 bomb: bool = False):
        self.bomb = bomb
        self.flagged = False
        self.revealed = False
        self.adjacent_bombs = 0

        self.adjacent_cells = []

    def __str__(self):
        if self.bomb:
            return "+"
        else:
            return f"{self.adjacent_bombs}"

if __name__ == "__main__":
    mboard = MinesweeperBoard(20, 10, 20)
    mboard = MinesweeperBoard(10, 10, 10, 1)
    for y in range(mboard.size_y):
        for x in range(mboard.size_x):
            print(f"{mboard.board[y * mboard.size_x + x]}", end=" ")
        print()