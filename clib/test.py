import sys
import cv2
sys.path.append('./build/lib.macosx-10.7-x86_64-3.6/')
sys.path.append('/Users/joshua/Coding/go/JoshieGo/src/')
from game import Board
import gofeat
import numpy as np
import pickle
games = pickle.load(open('go_test.pkl', 'rb'))
cnt = 0
import time

def py_iter():
    for it in range(10000):
        for x in range(19):
            for y in range(19):
                pass

def numpy_create():
    for it in range(10000):
        a = np.zeros((19, 19), dtype=np.int)
        a[10][10] = 1

for board_mtx, move in zip(games[0], games[1]):
    cnt += 1
    if cnt % 200 != 0:
        continue
    mtx = board_mtx
    string = Board.mtx2str(mtx)
    tic = time.time()
    string = gofeat.random(string)
    toc = time.time()
    print(toc-tic)

    tic = time.time()
    py_iter()
    toc = time.time()
    print(toc-tic)

    tic = time.time()
    numpy_create()
    toc = time.time()
    print(toc-tic)
    exit()

    ret_mtx = np.fromstring(string, sep=' ', dtype=np.int).reshape(19, 19)
    print(mtx - ret_mtx)
    board = Board(board_mtx=board_mtx)
    canvas = board.visualize_board(grid_size=35)
    cv2.imshow('board', canvas)
    cv2.waitKey()
