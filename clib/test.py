import sys
import cv2
sys.path.append('./build/lib.macosx-10.7-x86_64-3.6/')
sys.path.append('/Users/joshua/Coding/go/JoshieGo')
from game import Board
import gofeat
import numpy as np
# mtx = np.ones(shape=(19, 19), dtype=np.int)
# string = Board.mtx2str(mtx)
# print(string)
# print(dir(gofeat))
# string = gofeat.random(string)
# ret_mtx = np.fromstring(string, sep=' ', dtype=np.int).reshape(19, 19)
import pickle
games = pickle.load(open('go_test.pkl', 'rb'))
for board_mtx, move in zip(games[0], games[1]):
    board = Board(board_mtx=board_mtx)
    canvas = board.visualize_board(grid_size=35)
    cv2.imshow('board', canvas)
    cv2.waitKey()
