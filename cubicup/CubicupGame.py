from __future__ import print_function
import sys


from Game import Game
from cubicup.CubicupLogic import Board
import numpy as np

sys.path.append('..')


class CubicupGame(Game):
    def __init__(self, n):
        self.n = n

        directions = np.array([(1, 0, 0), (0, 1, 0), (0, 0, 1)])

        self.pos_dict = {}  # number to 3d
        self.action_dict = {}  # 3d to number
        self.supporting_dict = {}  # supports
        self.supported_dict = {}  # supported by
        self.rotation1 = np.zeros(self.getActionSize(), dtype=int)  # first rotation
        self.rotation2 = np.zeros(self.getActionSize(), dtype=int)  # second rotation

        counter = 0
        # Create dict
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    if a + b + c >= self.n:
                        continue
                    else:
                        self.pos_dict[(a, b, c)] = int(counter)
                        self.action_dict[int(counter)] = (a, b, c)
                        counter += 1

        # Create rotation
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    if a + b + c >= self.n:
                        continue
                    else:
                        self.rotation1[self.pos_dict[(a, b, c)]] = self.pos_dict[(b, c, a)]
                        self.rotation2[self.pos_dict[(a, b, c)]] = self.pos_dict[(c, a, b)]

        for x in range(self.getActionSize()):
            pos = self.action_dict[x]
            if sum(pos) < self.n - 1:
                self.supported_dict[x] = [self.pos_dict[g] for g in tuple(map(tuple, pos + directions))]
            supports = pos - directions
            checks = [-1 in y for y in supports]
            neg_pos = [self.pos_dict[tuple(supports[i])] for i, y in enumerate(checks) if y is False]
            self.supporting_dict[x] = neg_pos

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n, self.supporting_dict, self.supported_dict)
        return b.boards

    def getBoardSize(self):
        # (a,b) tuple
        return self.getActionSize()

    def getActionSize(self):
        # return number of actions
        return self.n * (self.n + 1) * (self.n + 2) / 6

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # create board
        b = Board(self.n, self.supporting_dict, self.supported_dict)
        b.set_board(board)
        # action must be a valid move
        if action not in b.playable:
            raise NameError('Not a playable position')
        b.execute_move(action, player)
        return (b.boards, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        # create board
        b = Board(self.n, self.supporting_dict, self.supported_dict)
        b.set_board(board)
        legal = b.get_legal_moves(player)
        all_moves = np.zeros((self.getActionSize(),))
        all_moves[legal] = 1
        return all_moves

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # create board
        b = Board(self.n, self.supporting_dict, self.supported_dict)
        b.set_board(board)
        # check draw
        if self.getGameDraw(board):
            # fill board for debug TODO remove for run
            # board[0] = np.sign(self.getScore(board, player))
            return -2
        # check 1 has moves
        if not b.get_legal_moves(1) or not b.get_legal_moves(-1):
            # normal end?
            if self.getScore(board, player) == 0:
                return b.get_board()[0]
            # don't fill the board. will not be used. just return -1 * sign of number of more cubes
            return -1 * np.sign(self.getScore(board, player))
        return 0

    def getGameDraw(self, board):
        """Check if the game is a draw"""
        # It is a draw if supporting color != 0 and supporting color != board[(0,0,0)]
        return Board.supporting_color(board[self.supported_dict[0]]) != 0  # and board[0] == 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player * board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        # assert(len(pi) == self.n**2+1)  # 1 for pass
        if sum(board) != 0:
            board_rot1 = board[self.rotation1]
            board_rot2 = board[self.rotation2]
            pi_rot1 = np.array(pi)[self.rotation1].tolist()
            pi_rot2 = np.array(pi)[self.rotation2].tolist()
            return [(board, pi), (board_rot1, pi_rot1), (board_rot2, pi_rot2)]
        # pi_board = np.reshape(pi[:-1], (self.n, self.n))
        # l = []

        # for i in range(1, 5):
        #    for j in [True, False]:
        #        newB = np.rot90(board, i)
        #        newPi = np.rot90(pi_board, i)
        #        if j:
        #            newB = np.fliplr(newB)
        #            newPi = np.fliplr(newPi)
        #        l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return [(board, pi)]

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    def getScore(self, board, player):
        return Board.count_diff(board)

    def display(self, board):
        n = self.n

        print("-------------start------------")
        for i in range(n):
            print("Layer: " + str(i))
            for a in range(i + 1):
                for b in range(i + 1):
                    for c in range(i + 1):
                        if a + b + c == i:
                            print(str((a, b, c)) + ": " + str(board[self.pos_dict[(a, b, c)]]))

        print("--------------end-------------")
