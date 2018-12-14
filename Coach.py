import multiprocessing
import os
from collections import deque
from pickle import Pickler, Unpickler

import numpy as np

from Arena import Arena
from MCTS import MCTS
from cubicup.tensorflow.NNet import NNetWrapper as nn
#from pytorch_classification.utils import Bar


def async_self_play(game, args, iter_num, iterr):
    import tensorflow as tf
    #bar.suffix = "iter:{i}/{x} | Total: {total:} | ETA: {eta:}".format(i=iter_num + 1, x=iterr,
    #                                                                   total=bar.elapsed_td, eta=bar.eta_td)
    #bar.next()
    # set gpu
    if args.multiGPU:
        if iter_num % 2 == 0:
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        else:
            os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.setGPU
    # set gpu memory grow
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    _ = tf.Session(config=config)
    # create nn and load
    net = nn(game)
    mcts = MCTS(game, net, args)
    try:
        net.load_checkpoint(folder=args.checkpoint, filename='best.pth.tar')
    except:
        pass
    train_examples = []
    board = game.getInitBoard()
    cur_player = 1
    episode_step = 0
    while True:
        episode_step += 1
        canonical_board = game.getCanonicalForm(board, cur_player)
        temp = int(episode_step < args.tempThreshold)
        pi = mcts.get_action_prob(canonical_board, temp=temp)
        sym = game.getSymmetries(canonical_board, pi)
        for b, p in sym:
            train_examples.append([b, cur_player, p, None])
        action = np.random.choice(len(pi), p=pi)
        board, cur_player = game.getNextState(board, cur_player, action)
        r = game.getGameEnded(board, cur_player)
        if r != 0:
            return [(x[0], x[2], r * ((-1) ** (x[1] != cur_player))) for x in train_examples]


def async_against(game, args, iter_num):
    import tensorflow as tf
    #bar.suffix = "iter:{i}/{x} | Total: {total:} | ETA: {eta:}".format(i=iter_num + 1, x=args.arenaCompare,
    #                                                                   total=bar.elapsed_td, eta=bar.eta_td)
    #bar.next()
    # set gpu
    if args.multiGPU:
        if iter_num % 2 == 0:
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        else:
            os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.setGPU
    # set gpu memory grow
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    _ = tf.Session(config=config)
    # create nn and load
    nnet = nn(game)
    pnet = nn(game)
    try:
        nnet.load_checkpoint(folder=args.checkpoint, filename='train.pth.tar')
    except:
        print("load train model fail")
        pass
    try:
        pnet.load_checkpoint(folder=args.checkpoint, filename='best.pth.tar')
    except:
        print("load old model fail")
        pass
    pmcts = MCTS(game, pnet, args)
    nmcts = MCTS(game, nnet, args)
    arena = Arena(lambda x: np.argmax(pmcts.get_action_prob(x, temp=0)),
                  lambda x: np.argmax(nmcts.get_action_prob(x, temp=0)), game)
    arena.displayBar = False
    pwins, nwins, draws = arena.playGames(2)
    return pwins, nwins, draws


def async_train_network(game, args, trainhistory):
    # set gpu
    os.environ["CUDA_VISIBLE_DEVICES"] = args.setGPU
    # create network for training
    nnet = nn(game)
    try:
        nnet.load_checkpoint(folder=args.checkpoint, filename='best.pth.tar')
    except:
        pass
    # ---load history file---
    model_file = os.path.join(args.checkpoint, "trainhistory.pth.tar")
    examples_file = model_file + ".examples"
    if not os.path.isfile(examples_file):
        print(examples_file)
    else:
        print("File with trainExamples found. Read it.")
        with open(examples_file, "rb") as f:
            for i in Unpickler(f).load():
                trainhistory.append(i)
    # ---delete if over limit---
    if len(trainhistory) > args.numItersForTrainExamplesHistory:
        print("len(trainExamplesHistory) =", len(trainhistory), " => remove the oldest trainExamples")
        del trainhistory[len(trainhistory) - 1]
    # ---extend history---
    train_examples = []
    for e in trainhistory:
        train_examples.extend(e)
    # ---save history---
    folder = args.checkpoint
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, 'trainhistory.pth.tar' + ".examples")
    with open(filename, "wb+") as f:
        Pickler(f).dump(trainhistory)
    print('Train with {} examples'.format(len(train_examples)))
    nnet.train(train_examples)
    nnet.save_checkpoint(folder=args.checkpoint, filename='train.pth.tar')


def check_result_and_save_network(pwins, nwins, draws, game, args, iter_num):
    # set gpu
    os.environ["CUDA_VISIBLE_DEVICES"] = args.setGPU
    if pwins + nwins > 0 and float(nwins + (0.5 * draws)) / (pwins + nwins + draws) < args.updateThreshold:
        print('REJECTING NEW MODEL')
    else:
        print('ACCEPTING NEW MODEL')
        net = nn(game)
        net.load_checkpoint(folder=args.checkpoint, filename='train.pth.tar')
        net.save_checkpoint(folder=args.checkpoint, filename='best.pth.tar')
        net.save_checkpoint(folder=args.checkpoint, filename='checkpoint_' + str(iter_num) + '.pth.tar')


class Coach:
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, game, args):
        self.game = game
        self.args = args
        self.trainExamplesHistory = []
        # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()

    def parallel_self_play(self):
        pool = multiprocessing.Pool(processes=self.args.numSelfPlayPool)
        temp = []
        res = []
        result = []
        #bar = Bar('Self Play', max=self.args.numEps)
        for i in range(self.args.numEps):
            res.append(pool.apply_async(async_self_play, args=(self.game, self.args, i, self.args.numEps,)))
        pool.close()
        pool.join()
        for i in res:
            result.append(i.get())
        for i in result:
            temp += i
        return temp

    def parallel_train_network(self):
        print("Start train network")
        pool = multiprocessing.Pool(processes=1)
        pool.apply_async(async_train_network, args=(self.game, self.args, self.trainExamplesHistory,))
        pool.close()
        pool.join()

    def parallel_self_test_play(self, iter_num):
        pool = multiprocessing.Pool(processes=self.args.numTestPlayPool)
        print("Start test play")
        #bar = Bar('Test Play', max=self.args.arenaCompare)
        res = []
        result = []
        for i in range(self.args.arenaCompare):
            res.append(pool.apply_async(async_against, args=(self.game, self.args, i)))
        pool.close()
        pool.join()
        pwins = 0
        nwins = 0
        draws = 0
        for i in res:
            result.append(i.get())
        for i in result:
            pwins += i[0]
            nwins += i[1]
            draws += i[2]
        print("pwin: " + str(pwins))
        print("nwin: " + str(nwins))
        print("draw: " + str(draws))
        pool = multiprocessing.Pool(processes=1)
        pool.apply_async(check_result_and_save_network, args=(pwins, nwins, draws, self.game, self.args, iter_num,))
        pool.close()
        pool.join()

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximium length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters + 1):
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            iteration_train_examples = deque([], maxlen=self.args.maxlenOfQueue)
            temp = self.parallel_self_play()
            iteration_train_examples += temp
            self.trainExamplesHistory.append(iteration_train_examples)
            self.parallel_train_network()
            del self.trainExamplesHistory[:]
            self.parallel_self_test_play(i)

    @staticmethod
    def get_checkpoint_file(iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def delete_train_examples(self):
        model_file = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examples_file = model_file + ".examples"
        if os.path.isfile(examples_file):
            os.remove(examples_file)

    def save_train_examples(self):
        model_file = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examples_file = model_file + ".examples"
        folder = self.args.load_folder_file[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        # filename = os.path.join(folder + ".examples")
        with open(examples_file, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)

    def load_train_examples(self):
        model_file = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examples_file = model_file + ".examples"
        if not os.path.isfile(examples_file):
            print(examples_file)
            print("File with trainExamples not found.")  # Continue? [y|n]")
        else:
            print("File with trainExamples found. Read it.")
            with open(examples_file, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True
