from six import b

from MCTS import MCTS
import numpy as np
from Coach import Coach
from cubicup.CubicupGame import CubicupGame as Game
from cubicup.tensorflow.NNet import NNetWrapper as nn
from utils import *

args = dotdict({
    'numIters': 1000,
    'numEps': 100,
    'tempThreshold': 15,
    'updateThreshold': 0.6,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 25,
    'arenaCompare': 40,
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': True,
    'load_folder_file': ('./temp/','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})


g = Game(6)
nnet = nn(g)

if args.load_model:
    nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

c = Coach(g, nnet, args)
board = g.getInitBoard()

player = 1

while g.getGameEnded(board, player) == 0:
    mcts = MCTS(g, nnet, args)
    action = mcts.get_action_prob(g.getCanonicalForm(board, 1))
    print(action)
    board , player = g.getNextState(board, 1, np.argmax(action))
    g.display(board)
    print([(g.action_dict[x], x) for x in np.where(g.getValidMoves(board, player) == 1)[0]])
    mode = -1
    while mode not in np.where(g.getValidMoves(board, player) == 1)[0]:
        try:
            mode = int(raw_input('Input:'))
        except ValueError:
            print "Not a number"
    board, player = g.getNextState(board, player, mode)
    g.display(board)
