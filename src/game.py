import numpy as np
import cv2


class Game(object):
    def __init__(self, grid_size=35, handicap=0):
        if handicap == 0:
            self.boards = [Board()]
            self.next_to_play = 1
        else:
            board_mtx = np.zeros((19, 19), dtype=np.int)
            if handicap == 2:
                board_mtx[3][15] = 1
                board_mtx[15][3] = 1
            self.boards = [Board(board_mtx)]
            self.next_to_play = 2
        self.next_masks = [np.ones((19, 19), dtype=np.int)]
        self.grid_size = grid_size
        self.ko_state = [False]
        self.current_moves = [(-1, -1)]

    def add_board(self, board):
        self.boards.append(board)
        self.next_to_play = 3 - self.next_to_play

    def legal_place(self, x=None, y=None):
        board = self.boards[-1]
        legal = self.next_masks[-1]
        legal[board.board_mtx == 1] = 0
        legal[board.board_mtx == 2] = 0
        if x is None:
            return legal
        else:
            is_suicide, groups_captured, ko_cnt, forbidden = self.test_xy(x, y)
            if is_suicide and groups_captured == 0:
                legal[x][y] = 0

            return 0 <= x <= 18 and 0 <= y <= 18 and legal[x][y] == 1

    def mk_move(self, x, y):
        is_suicide, groups_captured, ko_cnt, forbidden = self.test_xy(x, y)

        legal = self.legal_place(x, y)
        # if is_suicide and groups_captured == 0:
        #     legal[x][y] = 0
        # if 0 <= x <= 18 and 0 <= y <= 18 and legal[x][y] == 1:
        if legal:
            if is_suicide and ko_cnt == 1:
                self.ko_state.append(True)
            else:
                self.ko_state.append(False)
            self.current_moves.append((x, y))
            mtx = self.boards[-1].board_mtx.copy()
            new_board = Board(mtx)
            new_board.add_move(move=None, x=x, y=y, move_color=self.next_to_play)
            self.add_board(new_board)

            # update next_masks
            self.next_masks.append(np.ones((19, 19), dtype=np.int))
            if is_suicide and ko_cnt == 1:
                self.next_masks[-1][forbidden[0]][forbidden[1]] = 0
        else:
            return

    def test_xy(self, x, y):
        board_mtx = self.boards[-1].board_mtx.copy()
        board_mtx[x][y] = self.next_to_play
        stones = Board.get_group(x, y, board_mtx)
        forbidden = None
        is_suicide = not Board.check_liberty(stones, board_mtx)  # does this move makes stones have no liberties
        groups_captured = 0  # if it is suicide, how many groups of enemy stones are captured
        ko_cnt = 0  # if it is suicide and our group size is 1, how many enemy groups of len == 1 are captured

        neighbors = Board.neighbor(x, y)
        if is_suicide:
            for pos in neighbors:
                if board_mtx[pos[0]][pos[1]] == 3 - self.next_to_play:
                    nei_group = Board.get_group(pos[0], pos[1], board_mtx)
                    if not Board.check_liberty(nei_group, board_mtx):
                        groups_captured += 1
                        if len(stones) == 1 and len(nei_group) == 1:
                            ko_cnt += 1
                            forbidden = nei_group[0]
        return is_suicide, groups_captured, ko_cnt, forbidden

    def cap_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            xx, yy = int(round(float(x)/self.grid_size))-1, int(round(float(y)/self.grid_size))-1
            self.mk_move(xx, yy)
            if 'MCTS' in param:
                param['MCTS'] = False

        if event == cv2.EVENT_RBUTTONDOWN:
            if len(self.boards) >= 2:
                self.roll_back()

        if event == cv2.EVENT_MBUTTONDOWN:
            xx, yy = int(round(float(x)/self.grid_size))-1, int(round(float(y)/self.grid_size))-1
            self.mk_move(xx, yy)
            if 'MCTS' in param:
                param['MCTS'] = True

    def get_current_board_img(self, choices=None, last_move=None):
        return self.boards[-1].visualize_board(grid_size=self.grid_size, choices=choices, last_move=last_move)

    def roll_back(self):
        self.boards.pop()
        self.next_masks.pop()
        self.ko_state.pop()
        self.current_moves.pop()
        self.next_to_play = 3 - self.next_to_play


class Board(object):

    def __init__(self, board_mtx=None):
        if board_mtx is None:
            self.board_mtx = np.zeros((19, 19)).astype(np.uint8)
        else:
            self.board_mtx = board_mtx

    def visualize_board(self, grid_size=40, line_thickness=2, choices=None, last_move=None):
        canvas = np.ones((grid_size*20, grid_size*20, 3), dtype=np.uint8) * 100

        for x in range(1, 20):
            cv2.line(canvas, (x*grid_size, grid_size), (x*grid_size, 19*grid_size), (0, 0, 0), line_thickness)
            cv2.line(canvas, (grid_size, x*grid_size), (19*grid_size, x*grid_size), (0, 0, 0), line_thickness)

        for x in range(3):
            for y in range(3):
                cv2.circle(canvas, (4*grid_size+6*x*grid_size, 4*grid_size+6*y*grid_size), int(grid_size/9), color=(0, 0, 0), thickness=int(grid_size/10))

        for x in range(19):
            for y in range(19):
                if self.board_mtx[x][y] == 1:
                    cv2.circle(canvas, ((x+1)*grid_size, (y+1)*grid_size), int(grid_size/2.2), color=(0, 0, 0), thickness=-1)
                if self.board_mtx[x][y] == 2:
                    cv2.circle(canvas, ((x+1)*grid_size, (y+1)*grid_size), int(grid_size/2.2), color=(200, 200, 200), thickness=-1)

        if choices is not None:
            letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
            for move, letter in zip(choices, letters):
                x, y, prob = move[0][0], move[0][1], move[1]
                cv2.putText(canvas, letter, (int((x+0.65)*grid_size), int((y+1.4)*grid_size)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), thickness=3)

        if last_move is not None and 0 <= last_move[0] <=18 and 0 <= last_move[1] <= 18:
            x, y = last_move[0], last_move[1]
            if self.board_mtx[x][y] == 1:
                cv2.circle(canvas, ((x+1)*grid_size, (y+1)*grid_size), int(grid_size/3), color=(200, 200, 200), thickness=2)
            if self.board_mtx[x][y] == 2:
                cv2.circle(canvas, ((x+1)*grid_size, (y+1)*grid_size), int(grid_size/3), color=(0, 0, 0), thickness=2)

        return canvas

    def add_move(self, move, x=None, y=None, move_color=None):
        if x is None:
            x, y = Board.letter2num(move)
            if move[0] == 'B':
                self.board_mtx[x][y] = 1
                move_color = 1
            else:
                self.board_mtx[x][y] = 2
                move_color = 2
        else:
            self.board_mtx[x][y] = move_color

        for cross in Board.neighbor(x, y):
            cross_color = self.board_mtx[cross[0]][cross[1]]
            if cross_color != 0 and cross_color != move_color:
                stones = Board.get_group(cross[0], cross[1], self.board_mtx)
                if not Board.check_liberty(stones, self.board_mtx):
                    for pos in stones:
                        self.board_mtx[pos[0]][pos[1]] = 0

    @staticmethod
    def mtx2str(mtx):
        string = np.array2string(mtx)
        string = string.replace('[', ' ')
        string = string.replace(']', ' ')
        return string

    @staticmethod
    def str2mtx(string):
        return np.fromstring(string, dtype=int, sep=' ').reshape((19, 19))

    @staticmethod
    def get_group(x, y, board_mtx, visited=None):
        stones = list()
        color = board_mtx[x][y]
        stones.append((x, y))
        is_visited = np.zeros((19, 19), dtype=np.uint8)
        is_visited[x][y] = 1

        for stone in stones:
            for pos in Board.neighbor(*stone):
                if color == board_mtx[pos[0]][pos[1]] and is_visited[pos[0]][pos[1]] == 0:
                    stones.append(pos)
                    is_visited[pos[0]][pos[1]] = 1
                    if visited is not None:
                        visited[pos] = 1
        return stones

    @staticmethod
    def check_liberty(stone_pos_list, board_mtx, cnt=False):
        if not cnt:
            for pos in stone_pos_list:
                for cross in Board.neighbor(*pos):
                    if board_mtx[cross[0]][cross[1]] == 0:
                        return True
            return False
        else:
            # num_liberty = 0
            d = {}
            for pos in stone_pos_list:
                for cross in Board.neighbor(*pos):
                    if board_mtx[cross[0]][cross[1]] == 0:
                        d[cross] = 1
            return len(d)

    @staticmethod
    def neighbor(x, y):
        result = []
        if 0 <= x-1:
            result.append((x-1, y))
        if x+1 <= 18:
            result.append((x+1, y))
        if 0 <= y-1:
            result.append((x, y-1))
        if y+1 <= 18:
            result.append((x, y+1))
        return result

    @staticmethod
    def letter2num(move):
        x = int(ord(move[2]) - ord('a'))
        y = int(ord(move[3]) - ord('a'))
        return x, y


if __name__ == '__main__':

    game = Game(handicap=0, grid_size=30)

    # m = np.random.randint(0, 19, size=(2,), dtype=np.int)
    # m = tuple(m)
    # for num in range(100):
    #     for i in range(10000):
    #         game.mk_move(*m)
    #         if i % 300 == 0:
    #             game = Game()
    #     print(num)

    board_img = game.get_current_board_img()
    cv2.imshow('board_img', board_img)
    cv2.setMouseCallback('board_img', game.cap_click)
    while True:
        board_img = game.get_current_board_img()
        cv2.imshow('board_img', board_img)
        cv2.waitKey(33)
