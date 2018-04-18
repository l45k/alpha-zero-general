from cubicup.CubicupGame import CubicupGame as Game
import numpy as np

N = 10000

nums = np.zeros(N)
runs = np.zeros(N)
for i in range(N):
    player = -1
    game = Game(4)
    while 0 == game.getGameEnded(game.board, player):
        moves = game.getValidMoves(game.board, player)
        if moves:
            rand_choice = np.random.randint(len(moves))
            b, player = game.getNextState(game.board, player, moves[rand_choice])
        else:
            player = -player
    runs[i] = game.getGameDraw()
    nums[i] = game.getScore(game.board, 1)

print 'done'
print sum(nums)
print sum(runs)