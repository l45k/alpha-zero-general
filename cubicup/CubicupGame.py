from __future__ import print_function
import sys
from Game import Game
from CubicupLogic import Board
# import numpy as np
sys.path.append('..')


class CubicupGame(Game):
    def __init__(self, n):
        self.n = n
        self.board = Board(self.n)
        self.player = 0

    def getInitBoard(self):
        # return initial board (numpy board)
        return self.board.get_board()

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.board.playable.count()

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        if action not in self.board.playable:
            raise NameError('Not a playable position')
        self.board.execute_move(action, player)
        self.player = -player
        return (self.board, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        return self.board.playable

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        if not self.board.get_legal_moves(player) and not self.board.get_legal_moves(-player):
            return 0
        return -1

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player*board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        # assert(len(pi) == self.n**2+1)  # 1 for pass
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
        return

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    def getScore(self, board, player):
        return self.board.count_diff(player)

    def display(self):
        n = self.board.n

        print("-------------start------------")
        for i in range(n):
            print("Layer: " + str(i))
            for a in range(i+1):
                for b in range(i+1):
                    for c in range(i+1):
                        if a+b+c == i:
                            print(str((a, b, c)) + ": " + str(self.board.board[a, b, c]))

        print("--------------end-------------")
