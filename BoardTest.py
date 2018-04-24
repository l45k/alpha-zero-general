from cubicup.CubicupGame import CubicupGame as Game
import numpy as np

N = 10000

nums = np.zeros(N)
runs = np.zeros(N)
n = 6

counter = 0
stones = np.zeros((n*(n+1)*(n+2)/6, ))
#
# b = np.zeros((n,) * 3, dtype=int)
# for i in range(n):
#     for a in range(n):
#         for b in range(n):
#             for c in range(n):
#                 if a + b + c == i:
#                     print (a, b, c)
#                     print counter
#                     counter +=1

for i in range(N):
    player = -1
    game = Game(4)
    board = game.getInitBoard()
    while 0 == game.getGameEnded(board, player):
        moves = game.getValidMoves(board, player)
        if moves.any():
            posible = np.where(moves == 1)[0]
            rand_choice = np.random.randint(len(posible))
            b, player = game.getNextState(board, player, posible[rand_choice])
        else:
            player = -player
    runs[i] = game.getGameDraw(board)
    nums[i] = game.getScore(board, 1)

print 'done'
print sum(nums)
print sum(runs)