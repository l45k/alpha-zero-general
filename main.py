from Coach import Coach
from cubicup.CubicupGame import CubicupGame as Game
from utils import *
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

args = dotdict({
    'numIters': 1000,
    'numEps': 100,
    'tempThreshold': 15,
    'updateThreshold': 0.6,
    'maxlenOfQueue': 400000,
    'numMCTSSims': 15,
    'arenaCompare': 80,
    'cpuct': .8,
    'numSelfPlayPool': 2,
    'numTestPlayPool': 2,
    'multiGPU': False,
    'setGPU': '0',
    'checkpoint': './temp/',
    'load_model': True,
    'load_folder_file': ('./temp/','best.pth.tar'),
    'numItersForTrainExamplesHistory': 40,
})

if __name__ == "__main__":
    c = Coach(Game(6), args)
    if args.load_model:
        print("Load trainExamples from file")
        c.load_train_examples()
    c.learn()
