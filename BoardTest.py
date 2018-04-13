from cubicup.CubicupGame import CubicupGame as Game

player = -1
game = Game(4)
while 0 == game.getGameEnded(game.board, player):
    moves = game.getValidMoves(game.board, player)
    if moves:
        b, player = game.getNextState(game.board, player, moves[0])


print 'done'
game.display()
