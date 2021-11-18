import chess

class FBoard(chess.Board):
    def __init__(self, fen='8/pppppppp/8/8/8/8/PPPPPPPP/8'):
        super(FBoard, self).__init__(fen=fen)
