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

    def reveal_cell(self, cell: "MinesweeperCell"):
        if cell.revealed or cell.flagged:
            return True

        cell.revealed = True
        self.revealed_cells += 1

        if cell.bomb:
            for cell in self.board:
                if not cell.revealed:
                    self.reveal_cell(cell)

        if cell.adjacent_bombs == 0:
            for adjacent_cell in cell.adjacent_cells:
                if not adjacent_cell.revealed:
                    self.reveal_cell(adjacent_cell)

        return True

    def flag_cell(self, cell: "MinesweeperCell"):
        cell.flagged = not cell.flagged
    
    def get_cell(self, x: int, y: int):

        index = y * self.size_x + x
        if index < 0 or index >= self.size_x * self.size_y:
            return None
        return self.board[index]

    def print(self):
        for y in range(self.size_y):
            for x in range(self.size_x):
                print(f"{self.get_cell(x, y)}", end="")
            print()
    
    def game_print(self):
        for y in range(self.size_y):
            for x in range(self.size_x):
                cell = self.get_cell(x, y)
                if cell.revealed:
                    print(f"{cell}", end="")
                else:
                    char = 'F' if cell.flagged else '\u2588'
                    print(f"{char}", end="")
            print()

class MinesweeperCell:
    textures_file_paths = {0: "textures/0.png",
                          1: "textures/1.png",
                          2: "textures/2.png",
                          3: "textures/3.png",
                          4: "textures/4.png",
                          5: "textures/5.png",
                          6: "textures/6.png",
                          7: "textures/7.png",
                          8: "textures/8.png",
                          9: "textures/mine.png",
                          10: "textures/flag.png",
                          11: "textures/unrevealed.png"}
    textures_size = (128, 128)

    texture_atlas_path = "textures/atlas.png"
    texture_atlas_size = (512, 384)
    texture_atlas_positions = {0: [(0, 0), (128, 0), (0, 128), (128, 128)],
                               1: [(128, 0), (256, 0), (128, 128), (256, 128)],
                               2: [(256, 0), (384, 0), (256, 128), (384, 128)],
                               3: [(384, 0), (512, 0), (384, 128), (512, 128)],
                               4: [(0, 128), (128, 128), (0, 256), (128, 256)],
                               5: [(128, 128), (256, 128), (128, 256), (256, 256)],
                               6: [(256, 128), (384, 128), (256, 256), (384, 256)],
                               7: [(384, 128), (512, 128), (384, 256), (512, 256)],
                               8: [(0, 256), (128, 256), (0, 384), (128, 384)],
                               9: [(128, 256), (256, 256), (128, 384), (256, 384)],
                               10:[(256, 256), (384, 256), (256, 384), (384, 384)],
                               11:[(384, 256), (512, 256), (384, 384), (512, 384)]}

    @staticmethod
    def get_atlas_coords(cell: "MinesweeperCell"):
        vt = []
        for coord in MinesweeperCell.texture_atlas_positions[cell.get_texture_index()]:
            vt.append((coord[0] / MinesweeperCell.texture_atlas_size[0], coord[1] / MinesweeperCell.texture_atlas_size[1]))
        return vt

    def __init__(self,
                 bomb: bool = False):
        self.bomb = bomb
        self.flagged = False
        self.revealed = False
        self.adjacent_bombs = 0

        self.adjacent_cells = []

    def get_texture_index(self):
        if self.revealed:
            if self.bomb:
                return 9
            else:
                return self.adjacent_bombs
        if self.flagged:
            return 10
        return 11

    def __str__(self):
        if self.bomb:
            return '\u00A4'
        else:
            if self.adjacent_bombs == 0:
                return '\u2591'
            return f"{self.adjacent_bombs}"



if __name__ == "__main__":

    mboard = MinesweeperBoard(20, 10, 20, 1)
    # mboard = MinesweeperBoard(10, 10, 10, 1)
    mboard.print()
    print()
    mboard.game_print()
    print()
    mboard.reveal_cell(mboard.get_cell(0, 0))
    mboard.game_print()
    print()
    mboard.reveal_cell(mboard.get_cell(8, 0))
    mboard.game_print()
    print()
    mboard.reveal_cell(mboard.get_cell(13, 0))
    mboard.game_print()
