from game import Game, Board
import socket
from MCTS import MCTS


HANDICAP = 0
PORT = 6667
HOST = '10.180.47.12'
# HOST = '127.0.0.1'


class GamePlay(object):
    def __init__(self, policy_net_path, value_net_path):
        self.mcts = MCTS(policy_net_path, value_net_path, time_limit=20)

    def play(self, game):
        self.mcts.set_game(game)
        return self.mcts.start()


def client():
    s = socket.socket()
    host = HOST
    print('connecting to ' + host)
    port = PORT
    s.connect((host, port))
    game_play = GamePlay(
                         policy_net_path='../trained_models/policy',
                         value_net_path='../trained_models/value')

    game = Game(handicap=HANDICAP)
    while True:
        message = s.recv(4096)
        message = message.decode('utf-8')
        print(type(message), message)
        # board_mtx, next_to_move = message.split('|')
        move, next_to_move, current_board, is_search = message.split('|')
        print(move, next_to_move, current_board, is_search)
        if int(is_search) == 1:
            game_play.mcts.time_limit = 20
        else:
            game_play.mcts.time_limit = 0.5
        while Board.mtx2str(game.boards[-1].board_mtx) != current_board:
            print('roll_back')
            game.roll_back()
        print(len(game.boards))
        moves = move.split(',')
        x, y = int(moves[0][1:]), int(moves[1][1:-1])
        game.mk_move(x, y)

        output = game_play.play(game)
        game.mk_move(output[0], output[1])
        s.send(bytes(str(output), encoding='utf-8'))
        # s.send(str(output))

    s.close()


def server():
    import cv2
    s = socket.socket()
    host = socket.gethostname()
    print(host)
    print(socket.gethostbyname(socket.gethostname()))
    host = HOST
    port = PORT
    s.bind((host, port))

    s.listen(5)
    while True:
        print('listening...')
        game = Game(handicap=HANDICAP)
        board_img = game.get_current_board_img()
        cv2.imshow('board_img', board_img)
        param = {'MCTS': False}
        cv2.setMouseCallback('board_img', game.cap_click, param=param)
        cv2.waitKey(33)
        c, addr = s.accept()
        print('Got connection from', addr)

        while True:
            before_len = len(game.boards)
            board_img = game.get_current_board_img(last_move=game.current_moves[-1])
            cv2.imshow('board_img', board_img)
            cv2.waitKey(33)
            now_len = len(game.boards)
            if now_len > before_len:
                print(param['MCTS'])
                board_img = game.get_current_board_img(last_move=game.current_moves[-1])
                cv2.imshow('board_img', board_img)
                cv2.waitKey(33)
                latest_board = game.boards[-2]  # board before human move
                next_to_play = game.next_to_play
                board_str = Board.mtx2str(latest_board.board_mtx)
                next_to_play = str(next_to_play)

                print('next_to_play:', next_to_play)
                c.send(str.encode(str(game.current_moves[-1]) + '|' + next_to_play + '|' + board_str + '|'
                                  + str(int(param['MCTS']))))
                print(str(game.current_moves[-1]))

                move = c.recv(1024).decode('utf-8')
                print('move', move)
                temp = move.split(',')
                x, y = int(temp[0][1:]), int(temp[1][1:-1])
                print(x, y, game.next_to_play)
                game.mk_move(x, y)

        c.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--is_server")
    args = parser.parse_args()

    if args.is_server:
        server()
    else:
        client()
