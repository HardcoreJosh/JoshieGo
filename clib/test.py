import sys
sys.path.append('./build/lib.macosx-10.7-x86_64-3.6/')
sys.path.append('/Users/joshua/Coding/go/JoshieGo')
from game import Board
import gofeat
import numpy as np
mtx = np.asarray([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
string = Board.mtx2str(mtx)

print(dir(gofeat))
gofeat.random(string)

