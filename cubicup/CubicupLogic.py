"""
Author: Leonhard Kunczik
Date: Apr 7, 2018.
Board class.
Board data:
  1=green, -1=blue, 0=empty
  Every position is a triple (a,b,c).
  The array pieces holds all positions from the board
  The playable positions are stored in the palyable positions
  And green and blue hold the positions from the player
"""

import numpy as np


class Board:

    __directions = np.array([(1, 0, 0), (0, 1, 0), (0, 0, 1)])

    def __init__(self, n):
        """Set up initial board configuration.
        With color green = 1, blue = -1"""
        self.n = n

        # Create the empty board array.
        self.board = np.zeros((self.n,) * 3, dtype=int)
        # self.pieces = []
        # for i in range(self.n):
        #     for a in range(i):
        #         for b in range(i):
        #             for c in range(i):
        #                 self.pieces.append((a, b, c))

        # sum over all pieces to find the initial parts
        # level = np.sum(self.pieces, 1)
        # self.playable = np.where(level == self.n)[0]

        self.playable = []
        # create the playable positions
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    if a+b+c == self.n-1:
                        self.playable.append((a, b, c))
        self.played = []
        self.moves_pp = n*(n+1.)*(n+2.)/12.

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.board[index]

    def count_diff(self, color):
        """Counts the # pieces of the given color
        (1 for green, -1 for blue, 0 for empty spaces)"""
        return np.sum(self.board)

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black
        """
        if self.has_moves(color):
            return self.playable
        else:
            return []

    def has_moves(self, color):
        """Checks if a player has moves available"""
        return np.shape(np.where(self.board == color))[1] <= self.moves_pp

    def get_board(self):
        return self.board

    def execute_move(self, move, color):
        """Perform the given move on the board.
        color gives the color pf the piece to play (1=green,-1=blue)
        """
        # check for new playable position
        supports = move - self.__directions
        checks = [-1 in x for x in supports]
        neg_pos = [i for i,x in enumerate(checks) if x is False]
        supports = supports[neg_pos]

        # place cube
        self.board[move] = color

        # check for cup
        for position in supports:
            if self._supporting_color(position) == -color:
                self.execute_move(position, -color)
            # add playable positions
            if self._supported(position):
                self.playable.append(tuple(position))

        # remove played positions
        self.playable.remove(move)

        # Add the piece to the color and check cup
        # self.played.append(move)
        # if color == 1:
        #     self.green.append(move)
        #     for x in possible_cups:
        #         if self._supported(supports[x], self.green):
        #             self.execute_move(self, supports[x], color*-1)
        # else:
        #     self.blue.append(move)
        #     for x in possible_cups:
        #         if self._supported(supports[x], self.blue):
        #             self.execute_move(self, supports[x], color*-1)

        # check playable positions
        # for x in possible_cups:
        #     if supports[x] not in self.playable:
        #         if self._supported(self, supports[x], self.played):
        #             np.append(self.playable, supports[x])

    # def _discover_move(self, origin, direction):
    #     """ Returns the endpoint for a legal move, starting at the given origin,
    #     moving by the given increment."""

    def _supported(self, position):
        """ Checks if the position is supported """
        supports = position + self.__directions
        cubes = [self.board[tuple(x)] for x in supports]
        return not 0 in cubes

    def _supporting_color(self, position):
        """ Checks if the position is supported by only one color"""
        supports = position + self._Board__directions
        cubes = self.board[[tuple(x) for x in supports]]
        return all(cubes == 1) - all(cubes == -1)
