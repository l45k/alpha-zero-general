import sys
sys.path.append('..')


class CubiNNet:
    def __init__(self, game, args):
        # game params
        self.action_size = game.getActionSize()
        self.args = args
        import tensorflow as tf
        # Renaming functions 
        relu = tf.nn.relu
        tanh = tf.nn.tanh
        batch_normalization = tf.layers.batch_normalization
        dropout = tf.layers.dropout
        dense = tf.layers.dense

        # Neural Net
        self.graph = tf.Graph()
        with self.graph.as_default(): 
            self.input_boards = tf.placeholder(tf.float32, shape=[None, self.action_size])  # s: batch_size x board_x x board_y
            self.dropout = tf.placeholder(tf.float32)
            self.isTraining = tf.placeholder(tf.bool, name="is_training")

            h_conv1 = relu(batch_normalization(dense(self.input_boards, args.num_channels), training=self.isTraining))     # batch_size  x board_x x board_y x num_channels
            h_conv2 = relu(batch_normalization(dense(h_conv1, args.num_channels), training=self.isTraining))     # batch_size  x board_x x board_y x num_channels
            h_conv3 = relu(batch_normalization(dense(h_conv2, args.num_channels), training=self.isTraining))    # batch_size  x (board_x-2) x (board_y-2) x num_channels
            h_conv4 = relu(batch_normalization(dense(h_conv3, args.num_channels), training=self.isTraining))    # batch_size  x (board_x-4) x (board_y-4) x num_channels
            s_fc1 = dropout(relu(batch_normalization(dense(h_conv4, 1024, use_bias=False), axis=1, training=self.isTraining)), rate=self.dropout) # batch_size x 1024
            s_fc2 = dropout(relu(batch_normalization(dense(s_fc1, 512, use_bias=False), axis=1, training=self.isTraining)), rate=self.dropout)         # batch_size x 512
            self.pi = dense(s_fc2, self.action_size)    # batch_size x self.action_size
            self.prob = tf.nn.softmax(self.pi)
            self.v = tanh(dense(s_fc2, 1))         # batch_size x 1

            self.target_pis = tf.placeholder(tf.float32, shape=[None, self.action_size])
            self.target_vs = tf.placeholder(tf.float32, shape=[None])
            self.loss_pi =  tf.losses.softmax_cross_entropy(self.target_pis, self.pi)
            self.loss_v = tf.losses.mean_squared_error(self.target_vs, tf.reshape(self.v, shape=[-1,]))
            self.total_loss = self.loss_pi + self.loss_v
            update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies(update_ops):
                self.train_step = tf.train.AdamOptimizer(self.args.lr).minimize(self.total_loss)
