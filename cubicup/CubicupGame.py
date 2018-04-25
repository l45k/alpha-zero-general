from __future__ import print_function
import sys
from Game import Game
from CubicupLogic import Board
import numpy as np

sys.path.append('..')


class CubicupGame(Game):
    def __init__(self, n):
        self.n = n
        self.player = 0

        self.pos_dict = {}
        self.action_dict = {}
        counter = 0
        # Create dict
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    if a + b + c >= self.n:
                        continue
                    else:
                        self.pos_dict[(a, b, c)] = counter
                        self.action_dict[counter] = (a, b, c)
                        counter += 1

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return b.board

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n * (self.n + 1) * (self.n + 2) / 6

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # convert action back to 3-position
        pos = self.action_dict[action]
        # create board
        b = Board(self.n)
        b.set_board(board)
        # action must be a valid move
        if pos not in b.playable:
            raise NameError('Not a playable position')
        b.execute_move(pos, player)
        self.player = -player
        return (b.board, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        # create board
        b = Board(self.n)
        b.set_board(board)
        legal = b.get_legal_moves(player)
        all_moves = np.zeros((self.getActionSize(),))
        for x in legal: all_moves[self.pos_dict[x]] = 1
        return all_moves

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # create board
        b = Board(self.n)
        b.set_board(board)
        # check draw
        if not self.getGameDraw(board):
            return -1
        # check 1 has moves
        if not b.get_legal_moves(1) or not b.get_legal_moves(-1):
            # normal end?
            if self.getScore(board, player) == 0:
                return b.get_board()[(0, 0, 0)]
            # don't fill the board. will not be used. just return -1 * sign of number of more cubes
            return -1 * np.sign(self.getScore(board, player))
        return 0


    def getGameDraw(self, board):
        """Check if the game is a draw"""
        # It is a draw if supporting color != 0 and supporting color != board[(0,0,0)]
        return Board.supporting_color(board, (0, 0, 0)) + board[(0, 0, 0)] == 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player * board

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
        return []

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        small_board = np.zeros((self.getActionSize(),))
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    if a + b + c >= self.n:
                        continue
                    else:
                        small_board[self.pos_dict[(a, b, c)]] = board[(a, b, c)]
        return small_board.tostring()

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
                            print(str((a, b, c)) + ": " + str(board[a, b, c]))

        print("--------------end-------------")
