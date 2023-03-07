from board import Action, Direction, Rotation
from random import Random
import time
WAIT_TIME = 0 # A mark 17,426
from board import Board


class Player:   
    def choose_action(self, board):
        raise NotImplementedError

class BestPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def heights_of_columns(self, board): ## tends to not show correct heights around height = 21/22
        heights_of_columns = []
        for column in range(0, 10):
            max_height = 0
            for (x, y) in board.cells:
                if x == column: 
                    height = board.height - y
                    if height > max_height:
                        max_height = height
            heights_of_columns.append(max_height)

        return heights_of_columns

    def aggregate_height(self, board):
        return sum(self.heights_of_columns(board))

    def max_height(self, board):
        return max(self.heights_of_columns(board))

    def bumpiness(self, board): # sum of difference between heights of adjacent columns 
        bumpiness = 0
        list = self.heights_of_columns(board)[0:9]

        for index in range( len(list) - 1):
            bumpiness += abs( list[index] - list[index + 1] )
        return bumpiness

    def total_block_heights(self, board): # sums all the heights of all blocks - minimize # This is GOOD
        total_heights = 0
        for (x, y) in board.cells:
            total_heights += (board.height - y)
        return total_heights

    def matrix_board(self, board):
        matrix = [[0] * board.width for i in range(board.height)]
        for (x,y) in board.cells:
            matrix[y][x] = 1
        return matrix

    def completed_lines(self, board):
        matrix = self.matrix_board(board)
        complete_lines = 0
        for row in matrix:
            if all([x == 1 for x in row[0:9]]): # use if row[0:9] for checking just 9 rows
                complete_lines += 1
        return complete_lines

    def num_of_holes(self, board):
        matrix = self.matrix_board(board)
        num_of_holes = 0
        for column in range(board.width):
            Flag = False
            for row in range(board.height):
                if (column, row) in board.cells:
                    Flag = True
                if (column, row) not in board.cells and Flag:
                    num_of_holes += 1
        return num_of_holes

    def row_trans(self, board):
        transition = 0
        matrix = self.matrix_board(board)
        for i in range(len(matrix)):
            for j in range(len(matrix[0]) - 1):
                if matrix[i][j] == 0 and matrix[i][j + 1] != 0:
                    transition += 1
                if matrix[i][j] != 0 and matrix[i][j + 1] == 0:
                    transition += 1
        return transition

    def col_trans(self, board):
        transition = 0
        matrix = self.matrix_board(board)
        for j in range(len(matrix[0])):
            for i in range(len(matrix) - 1):
                if matrix[i][j] == 0 and matrix[i+1][j] != 0:
                    transition += 1
                if matrix[i][j] != 0 and matrix[i+1][j] == 0:
                    transition += 1
        return transition

# -0.0020066, -0.174483, -0.99963, 0.9950666, -0.42, -0.92 # 19707 ####### 26557
    def score_board(self, board):
        height_score = (-0.020066)*self.total_block_heights(board)  # -0.0020066, -0.184483, -0.99963, -0.9160666 # 13109
        bumpiness_score = (-0.174483)*self.bumpiness(board)
        holes_score = (-1.99963)*self.num_of_holes(board)
        complete_lines_score = (0.9950666)*self.completed_lines(board)
        rt = (-0.42)*self.row_trans(board)
        ct = (-0.92)*self.col_trans(board)
        return bumpiness_score + height_score + holes_score + complete_lines_score + rt + ct

    def try_move(self, board, xtarget, rtarget):
        cloneboard = board.clone()
        times_rotated = 0
        move_ans = []
        res = False
        trymove = None
        current_set_of_cells = board.cells.copy()
        while True:
            if times_rotated < rtarget:
                trymove = Rotation.Anticlockwise
                times_rotated += 1
            elif cloneboard.falling.left < xtarget:
                trymove = Direction.Right
            elif cloneboard.falling.left > xtarget:
                trymove = Direction.Left
            else:
                trymove = Direction.Drop

            if isinstance(trymove, Direction):
                res = cloneboard.move(trymove)
            elif isinstance(trymove, Rotation):
                res = cloneboard.rotate(trymove)
            move_ans.append(trymove)

            '''if res:
                score = self.score_board(cloneboard)
                return score, move_ans'''

            if res:
                score = self.score_board(cloneboard)
                for (x, y) in cloneboard.cells:
                    if (x == 9) and ((x,y) not in current_set_of_cells):
                        score =- 1000000000000000000

                if (self.num_of_holes(cloneboard)) > 0 and (cloneboard.discards_remaining > 0):
                    move_ans = [Action.Discard]
                    cloneboard.discards_remaining -= 1

                # discard if best move creates hole

                return score, move_ans


    def choose_action(self, board): # called by the autoplayer to decide how to move
        time.sleep(WAIT_TIME)
        best_score = -1000000000000
        best_move = None
        for xtarget in range(10):
            for rtarget in range(4):
                score, move = self.try_move(board, xtarget, rtarget)
                if score > best_score:
                    best_score = score
                    best_move = move

        if (self.completed_lines(board) > 3) and (board.falling.shape.value == "I") and (self.heights_of_columns(board)[-1] < 15): #<16 | 16126
            best_move = [Direction.Right]*5 +[Direction.Drop]

        return best_move #######




"""
class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])"""

SelectedPlayer = BestPlayer




"""
    def completed_lines0(self, board):
        completed_rows = 0
        for row in range( (board.height - 1), -1, -1 ): # 23, 22, 21, 20 ... 2, 1, 0
            block_exists = 0 # number of blocks that exist in each row
            for (x, y) in board.cells:
                if y == row:
                    block_exists += 1
            if block_exists == 9: # 10 blocks exist in current row - row is complete - add 1 to completed rows
                completed_rows += 1
        return completed_rows
"""
