import sys
import cv2
sys.path.append('./build/lib.macosx-10.7-x86_64-3.6/')
sys.path.append('/Users/joshua/Coding/go/JoshieGo/src/')
from game import Board
import gofeat
import numpy as np
import pickle
import time

def py_get_liberty(matrix):
    black_liberty = np.zeros((19, 19, 8), dtype=np.uint8)
    white_liberty = np.zeros((19, 19, 8), dtype=np.uint8)
    visited = {}
    for i in range(19):
        for j in range(19):
            if matrix[i][j] == 1 and (i, j) not in visited:
                groups = Board.get_group(i, j, matrix, visited=visited)
                num_liberty = Board.check_liberty(groups, matrix, cnt=True)
                if num_liberty > 8:
                    num_liberty = 8
                for stone in groups:
                    black_liberty[stone[0]][stone[1]][num_liberty-1] = 1

            if matrix[i][j] == 2 and (i, j) not in visited:
                groups = Board.get_group(i, j, matrix, visited=visited)
                num_liberty = Board.check_liberty(groups, matrix, cnt=True)
                if num_liberty > 8:
                    num_liberty = 8
                for stone in groups:
                    white_liberty[stone[0]][stone[1]][num_liberty-1] = 1

    stones = np.concatenate((black_liberty, white_liberty), axis=2)
    return stones



games = pickle.load(open('go_test.pkl', 'rb'))
cnt = 0
for board_mtx, move in zip(games[0], games[1]):
    cnt += 1
    if cnt % 200 != 0:
        continue
    
    mtx = board_mtx
    tic = time.time()
    for i in range(20):
        py_ret_mtx = py_get_liberty(mtx)
    toc = time.time()
    print(toc-tic)

    tic = time.time()
    for i in range(20):
        string = Board.mtx2str(mtx)
        string = gofeat.get_liberty(string)
        ret_mtx = np.fromstring(string, sep=' ', dtype=np.int).reshape(16, 19, 19).transpose(1, 2, 0)
    toc = time.time()
    print(toc-tic)
    print(np.sum(py_ret_mtx - ret_mtx))
    print(ret_mtx.shape)

    # for i in range(16):
    #     print('num', i+1)
    #     li_b = Board(board_mtx=ret_mtx[i, :, :])
    #     li_canvas = li_b.visualize_board(grid_size=35)
    #     board = Board(board_mtx=board_mtx)
    #     canvas = board.visualize_board(grid_size=35)
    #     cv2.imshow('board', canvas)
    #     cv2.imshow('stones', li_canvas)
    #     cv2.waitKey()
