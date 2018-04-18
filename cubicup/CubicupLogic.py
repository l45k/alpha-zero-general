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
        self.playable = []

        # create the playable positions
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    if a+b+c == self.n-1:
                        self.playable.append((a, b, c))
        self.played = []
        self.moves_pp = n*(n+1.)*(n+2.)/12.
        self.moves = self.moves_pp * 2.
        self.draw = 0

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.board[index]

    def get_move_count(self):
        """ Number of possible moves"""
        return self.moves

    def count_diff(self, color):
        """Counts the # pieces of the given color
        (1 for green, -1 for blue, 0 for empty spaces)"""
        return np.sum(self.board)

    def is_draw(self):
        """Check if the game is a draw"""
        return self.draw

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
        return np.shape(np.where(self.board == color))[1] < self.moves_pp

    def get_board(self):
        return self.board

    def get_winner(self):
        return self.board[(0, 0, 0)]

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
            if self._supporting_color(position) == color and self.has_moves(-color):
                self.execute_move(tuple(position), -color)
                # if it was the last possible move, the game is a draw
                self.draw = 1
                continue
            # add playable positions
            if self._supported(position):
                self.playable.append(tuple(position))

        # remove played positions
        if self.playable.__contains__(move):
            self.playable.remove(move)

        # Check if it really is a draw. Last step!
        if self.draw and self.playable:
            self.draw = 0

    def _supported(self, position):
        """ Checks if the position is supported """
        supports = position + self.__directions
        cubes = [self.board[tuple(x)] for x in supports]
        return not 0 in cubes

    def _supporting_color(self, position):
        """ Checks if the position is supported by only one color"""
        supports = position + self._Board__directions
        cubes_tuple = [tuple(x) for x in supports]
        cube_sum = sum([self.board[x] for x in cubes_tuple])
        return (cube_sum == 3)*1 - (cube_sum == -3)*1
