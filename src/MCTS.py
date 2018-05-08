import numpy as np
from policy_net import PolicyNet
from value_net import ValueNet
import tensorflow as tf
import time


class MCTS(object):

    def __init__(self, policy_net_path, value_net_path, time_limit=20):
        self.time_limit = time_limit
        self.game = None
        self.root = None
        policy_model = PolicyNet('./train/', '/val/')
        value_model = ValueNet('./train/', '/val/')

        g_policy = tf.Graph()
        with g_policy.as_default():
            self.policy_board = tf.placeholder(dtype=tf.float32)
            self.p_is_training = tf.placeholder(dtype=tf.bool)
            self.policy_out = policy_model.inference(self.policy_board, is_training=self.p_is_training)
            self.policy_loader = tf.train.Saver()

            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            self.policy_sess = tf.Session(config=config)
            print('load policy model:', policy_net_path)
            self.policy_loader.restore(self.policy_sess, policy_net_path)

        g_value = tf.Graph()
        with g_value.as_default():
            self.value_board = tf.placeholder(dtype=tf.float32, shape=(None, 19, 19, 21))
            self.v_is_training = tf.placeholder(dtype=tf.bool)
            _, self.value_out = value_model.inference(self.value_board, self.v_is_training)
            self.value_loader = tf.train.Saver()

            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            self.value_sess = tf.Session(config=config)
            print('load value model:', value_net_path)
            self.value_loader.restore(self.value_sess, value_net_path)

    def set_game(self, game):
        self.game = game
        self.root = Node(move=game.current_moves[-1], p=None)

    def eval_node(self, node, game, is_value=True, width=8):
        board_mtx = game.boards[-1].board_mtx
        if is_value:

            t0 = time.time()
            value_query = ValueNet.preprocess_board(board_mtx, {'next_to_play': game.next_to_play,
                                                                'ko_state:': game.ko_state[-1],
                                                                'current_move': game.current_moves[-1]},
                                                    random=False, contain_liberty=True)
            value_query = np.asarray([value_query], dtype=np.float32)
            t1 = time.time()
            black_win_rate, = self.value_sess.run([self.value_out], feed_dict={self.value_board: value_query,
                                                                               self.v_is_training: False})

            black_win_rate = black_win_rate.reshape((1, ))[0]
            t2 = time.time()
            print('TIME', t1-t0, t2-t1)

            node.black_win_rate = black_win_rate

        else:
            label_y = {'next_to_play': game.next_to_play, 'ko_state:': game.ko_state[-1],
                       'current_move': game.current_moves[-1]}
            policy_query = PolicyNet.preprocess_board(board_mtx, label_y,
                                                      random=False, contain_liberty=True)
            policy_query = np.asarray([policy_query], dtype=np.float32)

            p, = self.policy_sess.run(self.policy_out, feed_dict={self.policy_board:policy_query, self.p_is_training: False})
            probs = np.reshape(p, (19, 19))
            probs -= np.max(probs)
            probs = np.exp(probs) / np.sum(np.exp(probs))

            ids = np.dstack(np.unravel_index(np.argsort(probs.ravel()), (19, 19)))[0]
            ids = ids[::-1][:width, :]
            moves = [([move[0], move[1]], probs[move[0]][move[1]]) for move in ids]
            node.moves = [move for move in moves if game.legal_place(*move[0])]

    def start(self):
        cnt = 0
        start = time.time()
        while True:
            cnt += 1
            print('prob No.', cnt)
            self.prob()
            print(time.time() - start)
            for child in self.root.children:
                print('b_win_rate / prior / visit_cnt / move:',
                      child.black_win_rate, child.p, child.visit_cnt, child.last_move)
            if time.time() - start > self.time_limit:
                self.root.children.sort(key=lambda c: -c.visit_cnt)
                for child in self.root.children:
                    print(child.visit_cnt, child.last_move)
                return self.root.children[0].last_move[0]

    def prob(self, expand_limit=1):
        path = [self.root]
        self.root.black_win_rate = -1

        value = -1
        for node in path:
            if not node.is_leaf:
                next_node = self.select(self.game, node)
                path.append(next_node)
                self.game.mk_move(next_node.last_move[0][0], next_node.last_move[0][1])
            else:
                value = node.black_win_rate
                if node.visit_cnt > expand_limit:
                    self.expand(self.game, node)
                    for child in node.children:
                        self.evaluate(self.game, child)
                    node.is_leaf = False
        print('length of path of this prob:', len(path))
        self.backup(path, value)
        while len(path) != 1:
            self.game.roll_back()
            path.pop()

    def select(self, game, node):  # A node has to be expanded before selected
        if game.next_to_play == 1:
            node.children.sort(key=lambda child: child.black_win_rate + child.p / (1 + child.visit_cnt))
        else:
            node.children.sort(key=lambda child: -child.black_win_rate + child.p / (1 + child.visit_cnt))
        return node.children[-1]

    def expand(self, game, node):  # A node has to be evaluated before expanded
        if node.next_moves is None:
            self.eval_node(node, game, is_value=False)

        for move in node.moves:
            child = Node(move, p=move[1])
            node.children.append(child)

    def evaluate(self, game, node):
        if node.black_win_rate is None:
            game.mk_move(node.last_move[0][0], node.last_move[0][1])
            self.eval_node(node, game, is_value=True)
            game.roll_back()
        return node.black_win_rate

    def backup(self, path, value):
        print('len of path', len(path))
        for node in path:
            node.visit_cnt += 1
            num = node.visit_cnt
            node.black_win_rate = (float(num-1) * node.black_win_rate + value) / num


class Node(object):

    def __init__(self, move, p):
        self.last_move = move
        self.next_moves = None
        self.children = []
        self.black_win_rate = None
        self.p = p
        self.is_leaf = True
        self.visit_cnt = 0


if __name__ == '__main__':
    import pickle
    from game import Game

    search = MCTS(
        policy_net_path='./trained_models/policy',
        value_net_path='./trained_models/value')

    test_game = Game()
    search.set_game(test_game)

    for i in range(100):
        search.set_game(test_game)
        search.start()




