import tensorflow as tf
import numpy as np
from input import InputData
from game import Board


class PolicyNet(object):
    def __init__(self, train_data_path, validate_data_path):
        self.train_data = InputData(train_data_path, batch_size=128)
        self.validate_data = validate_data_path

    def conv(self, feature_map, filters_in, filters_out, k_size, scope, padding='SAME', dilation_rate=1, is_activation=True):
        with tf.variable_scope(scope) as scope2:
            kernel = tf.get_variable('kernel', shape=[k_size, k_size, filters_in, filters_out],
                                     initializer=tf.contrib.layers.xavier_initializer())
            bias = tf.get_variable('b', shape=[filters_out], initializer=tf.contrib.layers.xavier_initializer())
            out = tf.nn.convolution(feature_map, kernel, padding, dilation_rate=[dilation_rate, dilation_rate],
                                    name='conv') + bias
            if is_activation:
                out = tf.nn.relu(out, name='out')
            return out

    def batch_norm(self, x, is_training, name):
        with tf.variable_scope(name):
            beta = tf.Variable(tf.constant(0.0, shape=[x.shape[-1]]), name='beta', trainable=True)
            gamma = tf.Variable(tf.constant(1.0, shape=[x.shape[-1]]), name='gamma', trainable=True)
            axises = np.arange(len(x.shape) - 1)
            batch_mean, batch_var = tf.nn.moments(x, axises, name='moments')
            ema = tf.train.ExponentialMovingAverage(decay=0.5)

            def mean_var_with_update():
                ema_apply_op = ema.apply([batch_mean, batch_var])
                with tf.control_dependencies([ema_apply_op]):
                    return tf.identity(batch_mean), tf.identity(batch_var)

            mean, var = tf.cond(is_training, mean_var_with_update,
                                lambda: (ema.average(batch_mean), ema.average(batch_var)))
            normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, 1e-3)
        return normed

    def residual_block(self, feat_map, num_in, num_out, scope_name, is_training, dilation_rate=(1, 1)):
        with tf.variable_scope(scope_name):
            bottleneck = self.conv(feat_map, num_in, num_out, k_size=3, scope='c1', dilation_rate=dilation_rate[0],
                                   is_activation=False)
            bottleneck = self.batch_norm(bottleneck, is_training=is_training, name='bn1')
            bottleneck = tf.nn.relu(bottleneck)

            bottleneck = self.conv(bottleneck, num_out, num_out, k_size=3, scope='c2', dilation_rate=dilation_rate[1],
                                   is_activation=False)
            bottleneck = self.batch_norm(bottleneck, is_training=is_training, name='bn2')
            out = tf.add(bottleneck, feat_map, name='add')
            out = tf.nn.relu(out)

        return out

    def inference(self, feat_map, is_training):
        with tf.variable_scope('net'):
            out = self.conv(feat_map, filters_in=21, filters_out=128, k_size=3, scope='c1', padding='SAME',
                            is_activation=False)
            out = self.batch_norm(out, is_training=is_training, name='bn1')
            out = tf.nn.relu(out)

            out = self.residual_block(out, 128, 128, scope_name='res1', is_training=is_training)
            out = self.residual_block(out, 128, 128, scope_name='res2', is_training=is_training)
            out = self.residual_block(out, 128, 128, scope_name='res3', is_training=is_training,
                                      dilation_rate=[2, 4])
            out = self.residual_block(out, 128, 128, scope_name='res4', is_training=is_training,
                                      dilation_rate=[8, 1])
            out = self.residual_block(out, 128, 128, scope_name='res5', is_training=is_training)

            out = self.conv(out, filters_in=128, filters_out=128, k_size=3, scope='c2', padding='SAME',
                            is_activation=False)
            out = self.batch_norm(out, is_training=is_training, name='bn2')
            out = tf.nn.relu(out)
            out = self.conv(out, filters_in=128, filters_out=1, k_size=3, scope='c3', padding='SAME',
                            is_activation=False)
            return out

    def loss(self, logits, labels):
        logits = tf.reshape(logits, shape=[-1, 361])
        labels = tf.reshape(labels, shape=[-1, 361])
        return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=logits))

    def train(self, learning_rate, save_path, resume_path=None):
        model_x = tf.placeholder(dtype=tf.float32, shape=(None, 19, 19, 21))
        model_y = tf.placeholder(dtype=tf.float32, shape=(None, 19, 19, 1))
        is_training = tf.placeholder(dtype=tf.bool)

        out = self.inference(model_x, is_training=is_training)
        loss = self.loss(logits=out, labels=model_y)

        train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)

        saver = tf.train.Saver(max_to_keep=20)
        loader = tf.train.Saver()
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        with tf.Session(config=config) as sess:
            if resume_path is None:
                sess.run(tf.global_variables_initializer())
            else:
                print('resume:', resume_path)
                loader.restore(sess, resume_path)
            step = 0
            # epoch = self.train_data.epoch + 1
            epoch = self.train_data.epoch
            while True:
                step += 1
                x, y = self.train_data.next_batch()
                x, y = PolicyNet.pre_process(x, y)
                if len(x) == 0:
                    continue
                feed_dict = {model_x: x, model_y: y, is_training: True}
                _, loss_ = sess.run([train_op, loss], feed_dict=feed_dict)
                print('loss:', loss_, 'step', step, 'epoch', self.train_data.epoch)
                if self.train_data.epoch > epoch:
                    epoch = self.train_data.epoch
                    print('save:')
                    saver.save(sess, save_path, global_step=epoch)

    @staticmethod
    def pre_process(x, y):
        x = np.asarray([PolicyNet.preprocess_board(xx, yy, contain_liberty=True) for (xx, yy) in zip(x, y)], dtype=np.float32)
        y = np.asarray([PolicyNet.preprocess_label(yy) for yy in y], dtype=np.float32)
        return x, y

    @staticmethod
    def preprocess_board(board_mtx, y, random=True, contain_liberty=False):
        # rand = np.random.randint(0, 2)
        # if rand == 1:
        #     board_mtx = board_mtx.T
        #     y['next_to_move'] = (y['next_to_move'][1], y['next_to_move'][0])
        #     y['current_move'] = (y['current_move'][1], y['current_move'][0])
        if random:
            rand = np.random.randint(0, 8)
            if rand <= 3:
                board_mtx = board_mtx.T
                y['current_move'] = (y['current_move'][1], y['current_move'][0])
                y['next_move'] = (y['next_move'][1], y['next_move'][0])
            i = rand % 4
            if i == 1:
                board_mtx = np.rot90(board_mtx)
                y['current_move'] = (18-y['current_move'][1], y['current_move'][0])
                y['next_move'] = (18-y['next_move'][1], y['next_move'][0])
                # print(a[2-idx[1]][idx[0]])

            if i == 2:
                board_mtx = np.rot90(board_mtx)
                board_mtx = np.rot90(board_mtx)
                y['current_move'] = (18-y['current_move'][1], y['current_move'][0])
                y['next_move'] = (18-y['next_move'][1], y['next_move'][0])
                y['current_move'] = (18-y['current_move'][1], y['current_move'][0])
                y['next_move'] = (18-y['next_move'][1], y['next_move'][0])
            if i == 3:
                board_mtx = np.rot90(board_mtx)
                board_mtx = np.rot90(board_mtx)
                board_mtx = np.rot90(board_mtx)
                y['current_move'] = (18-y['current_move'][1], y['current_move'][0])
                y['next_move'] = (18-y['next_move'][1], y['next_move'][0])
                y['current_move'] = (18-y['current_move'][1], y['current_move'][0])
                y['next_move'] = (18-y['next_move'][1], y['next_move'][0])
                y['current_move'] = (18-y['current_move'][1], y['current_move'][0])
                y['next_move'] = (18-y['next_move'][1], y['next_move'][0])

        black_stones = np.zeros((19, 19, 1), dtype=np.uint8)
        black_stones[board_mtx == 1] = 1
        white_stones = np.zeros((19, 19, 1), dtype=np.uint8)
        white_stones[board_mtx == 2] = 1

        if contain_liberty:
            black_liberty = np.zeros((19, 19, 8), dtype=np.uint8)
            white_liberty = np.zeros((19, 19, 8), dtype=np.uint8)
            visited = {}
            for i in range(19):
                for j in range(19):
                    if board_mtx[i][j] == 1 and (i, j) not in visited:
                        groups = Board.get_group(i, j, board_mtx, visited=visited)
                        num_liberty = Board.check_liberty(groups, board_mtx, cnt=True)
                        if num_liberty > 8:
                            num_liberty = 8
                        for stone in groups:
                            black_liberty[stone[0]][stone[1]][num_liberty-1] = 1

                    if board_mtx[i][j] == 2 and (i, j) not in visited:
                        groups = Board.get_group(i, j, board_mtx, visited=visited)
                        num_liberty = Board.check_liberty(groups, board_mtx, cnt=True)
                        if num_liberty > 8:
                            num_liberty = 8
                        for stone in groups:
                            white_liberty[stone[0]][stone[1]][num_liberty-1] = 1

            black_stones = np.concatenate((black_stones, black_liberty), axis=2)
            white_stones = np.concatenate((white_stones, white_liberty), axis=2)
            # for i in range(9):
            #     print(board_mtx)
            #     print('liberty:', i)
            #     print(black_stones[:, :, i])
            #     print('===')
            #
            # print('XXXXXX')
            # print('XXXXXX')
            # print('XXXXXX')
            #
            # for i in range(9):
            #     print(board_mtx)
            #     print('liberty:', i)
            #     print(white_stones[:, :, i])
            #     print('===')
            # exit()

        stones = np.concatenate((black_stones, white_stones), axis=2)

        ones = np.ones((19, 19, 1), dtype=np.uint8)
        last_move = np.zeros((19, 19, 1), dtype=np.uint8)
        if not y['ko_state:']:
            last_move[y['current_move'][0]][y['current_move'][1]] = 1
        else:
            last_move[y['current_move'][0]][y['current_move'][1]] = -1

        is_black_next = np.ones((19, 19, 1), dtype=np.uint8)
        if y['next_to_play'] == 2:
            is_black_next -= 1

        feat = np.concatenate((stones, last_move, is_black_next, ones), axis=2)

        return feat

    @staticmethod
    def preprocess_label(y):
        mtx = np.zeros((19, 19, 1), dtype=np.uint8)
        mtx[y['next_move'][0]][y['next_move'][1]] = 1
        return mtx


if __name__ == '__main__':
    train_dir = '/mnt/chenzhao/GoData/policy_kgs/'
    # train_dir = '/mnt/chenzhao/GoData/'
    net = PolicyNet(train_dir, '')
    net.train(1e-4, save_path='/mnt/chenzhao/GoCheck/policy/kgs/policy_kgs_liberty_feat1e-4_',
              resume_path='/mnt/chenzhao/GoCheck/policy/kgs/policy_kgs_liberty_feat-2')
