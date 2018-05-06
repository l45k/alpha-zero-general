from keras.models import *
from keras.layers import *
from keras.optimizers import *
import sys
sys.path.append('..')


class CubicupNNet:
    def __init__(self, game, args):
        # game params
        self.action_size = game.getActionSize()
        self.args = args

        # Neural Net
        self.input_boards = Input(shape=(self.action_size, ))    # s: batch_size x board_x x board_y

        x_image = Reshape((self.action_size, 1))(self.input_boards)
        # batch_size  x board_x x board_y x 1
        h_conv1 = Dense(self.action_size, activation='relu')(self.input_boards)
        # batch_size  x board_x x board_y x num_channels
        h_conv2 = Dense(self.action_size, activation='relu')(h_conv1)
        # batch_size  x board_x x board_y x num_channels
        h_conv3 = Dense(self.action_size, activation='relu')(h_conv2)
        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4 = Dense(self.action_size, activation='relu')(h_conv3)
        h_conv5 = Dense(self.action_size, activation='relu')(h_conv4)
        # batch_size  x board_x x board_y x num_channels
        h_conv6 = Dense(self.action_size, activation='relu')(h_conv5)
        # batch_size  x board_x x board_y x num_channels
        h_conv7 = Dense(self.action_size, activation='relu')(h_conv6)
        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv8 = Dense(self.action_size, activation='relu')(h_conv7)
        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        # h_conv9_flat = Flatten()(h_conv8)
        s_fc1 = Dropout(args.dropout)(Dense(self.action_size, activation='relu')(h_conv8))
        s_fc2 = Dense(self.action_size, activation='relu')(s_fc1)
        # batch_size x 1024
        s_fc3 = Dense(self.action_size, activation='relu')(h_conv8)
        s_fc4 = Dense(self.action_size, activation='relu')(s_fc3)
        # batch_size x 1024
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc4)                    # batch_size x 1

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(args.lr))
