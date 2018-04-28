"""
Author: Leonhard Kunczik
Date: Apr 7, 2018.
Board class.
Board data:
  1=green, -1=blue, 0=empty
  Every position is a triple (a,b,c).
  The array pieces holds all positions from the board
  The playable positions are stored in the playable positions
  And green and blue hold the positions from the player
"""

import numpy as np


class Board:
    __directions = np.array([(1, 0, 0), (0, 1, 0), (0, 0, 1)])

    def __init__(self, n, supporting_dict, supported_dict):
        """Set up initial board configuration.
        With color green = 1, blue = -1"""
        self.n = n
        self.moves_pp = n * (n + 1) * (n + 2) / 12
        self.supporting_dict = supporting_dict
        self.supported_dict = supported_dict

        # Create the empty board array.
        self.boards = np.zeros((self.moves_pp * 2,), dtype=int)
        self.playable = self.get_playable()

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.boards[index]

    def set_board(self, board):
        self.boards = np.array(board, copy=True)
        self.playable = self.get_playable()

    def get_playable(self):
        playable = []
        for x in np.where(self.boards == 0)[0]:
            if self._supported(x):
                playable.append(x)
        return playable

    @staticmethod
    def count_diff(board):
        """Counts the # pieces of the given color
        (1 for green, -1 for blue, 0 for empty spaces)"""
        return np.sum(board)

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
        return sum(self.boards == color) < self.moves_pp

    def get_board(self):
        return self.boards

    def get_winner(self):
        return self.boards[0]

    def execute_move(self, move, color):
        """Perform the given move on the board.
        color gives the color pf the piece to play (1=green,-1=blue)
        """
        supports = self.supporting_dict[move]

        # place cube
        self.boards[move] = color

        # check for cup
        for position in supports:
            # fill cups
            if self.supporting_color(self.boards[self.supported_dict[position]]) == color and self.has_moves(-color):
                self.execute_move(position, -color)
                # do not check if the force fill is playable
                continue
            # add playable positions
            if self._supported(position) and self.boards[position] == 0:
                self.playable.append(position)

        # remove played positions
        if move in self.playable:
            self.playable.remove(move)

    def _supported(self, position):
        """ Checks if the position is supported """
        if position not in self.supported_dict.keys():
            return self.boards[position] == 0
        return (self.boards[self.supported_dict[position]] != 0).all()

    @staticmethod
    def supporting_color(colors):
        """ Checks if the position is supported by only one color"""
        cube_sum = sum(colors)
        return (cube_sum == 3) * 1 - (cube_sum == -3) * 1
