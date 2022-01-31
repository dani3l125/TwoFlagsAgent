import chess
import numpy as np
import chess.svg
import re
import copy


class FBoard:
    def __init__(self, white_turn=True, white=np.zeros((10, 10), dtype=bool), black=np.zeros((10, 10), dtype=bool)):
        self.white = white
        self.black = black
        self.white_turn = white_turn
        self.moves = []
        self.opp_moves = []
        self.legal_moves_boards()

    def legal_moves_boards(self):
        '''
        Method return a list of tuples, where each tuple is a pair of bit-boards,
        black and white respectively
        '''
        self.moves = []
        self.opp_moves = []
        #  not possible to move into(or over) used cell:
        constrained = np.logical_or(self.white, self.black)
        movers = np.transpose(np.nonzero(self.white))  # indexes of movers
        for idxs in movers:
            if not constrained[idxs[0] - 1, idxs[1]]:
                move = self.white.copy()
                # replacing pawn and appending move:
                move[idxs[0], idxs[1]] = False
                move[idxs[0] - 1, idxs[1]] = True
                self.moves.append((move, self.black))
                # double step for initial position:
                if idxs[0] == 7 and not constrained[idxs[0] - 2, idxs[1]]:
                    move = self.white.copy()
                    move[idxs[0], idxs[1]] = False
                    move[idxs[0] - 2, idxs[1]] = True
                    self.moves.append((move, self.black))
        # killing move is possible iff there is an enemy pawn on the diagonals "shifts":
        eating_left = np.logical_and(np.roll(self.white, shift=(-1, -1), axis=(0, 1)), self.black)
        eating_right = np.logical_and(np.roll(self.white, shift=(-1, 1), axis=(0, 1)), self.black)
        targets = np.transpose(np.nonzero(eating_left))
        for idxs in targets:
            move = self.white.copy()
            move[idxs[0], idxs[1]] = True
            black_cpy = self.black.copy()
            black_cpy[idxs[0], idxs[1]] = False
            move[idxs[0] + 1, idxs[1] + 1] = False
            self.moves.append((move, black_cpy))

        targets = np.transpose(np.nonzero(eating_right))
        for idxs in targets:
            move = self.white.copy()
            move[idxs[0], idxs[1]] = True
            black_cpy = self.black.copy()
            black_cpy[idxs[0], idxs[1]] = False
            move[idxs[0] + 1, idxs[1] - 1] = False
            self.moves.append((move, black_cpy))

        # opponent moves
        constrained = np.logical_or(self.white, self.black)
        movers = np.transpose(np.nonzero(self.black))  # indexes of movers
        for idxs in movers:
            if not constrained[idxs[0] + 1, idxs[1]]:
                move = self.black.copy()
                # replacing pawn and appending move:
                move[idxs[0], idxs[1]] = False
                move[idxs[0] + 1, idxs[1]] = True
                self.opp_moves.append((self.white, move))
                # double step for initial position:
                if idxs[0] == 2 and not constrained[idxs[0] + 2, idxs[1]]:
                    move = self.black.copy()
                    move[idxs[0], idxs[1]] = False
                    white_cpy = self.white.copy()
                    white_cpy[idxs[0], idxs[1]] = False
                    move[idxs[0] + 2, idxs[1]] = True
                    self.opp_moves.append((white_cpy, move))
        # killing move is possible iff there is an enemy pawn on the diagonals "shifts":
        eating_left = np.logical_and(np.roll(self.black, shift=(1, -1), axis=(0, 1)), self.white)
        eating_right = np.logical_and(np.roll(self.black, shift=(1, 1), axis=(0, 1)), self.white)
        targets = np.transpose(np.nonzero(eating_left))
        for idxs in targets:
            move = self.black.copy()
            move[idxs[0], idxs[1]] = True
            white_cpy = self.white.copy()
            white_cpy[idxs[0], idxs[1]] = False
            move[idxs[0] - 1, idxs[1] + 1] = False
            self.opp_moves.append((white_cpy, move))

        targets = np.transpose(np.nonzero(eating_right))
        for idxs in targets:
            move = self.black.copy()
            move[idxs[0], idxs[1]] = True
            white_cpy = self.white.copy()
            white_cpy[idxs[0], idxs[1]] = False
            move[idxs[0] - 1, idxs[1] - 1] = False
            self.opp_moves.append((white_cpy, move))

        self.moves = np.array(self.moves)
        self.opp_moves = np.array(self.opp_moves)

        if not self.white_turn:
            tmp = self.moves.copy()
            self.moves = self.opp_moves.copy()
            self.opp_moves = tmp
        return self.moves

    def is_checkmate(self):
        '''
        Method returns tuple of two booleans.
         If current board state is checkmate, first boolean is true.
         If white won, second boolean is True.
        '''
        if len(self.moves) == 0:
            return True, not self.white_turn
        if True in self.white[1]:
            return True, True
        if True in self.black[8]:
            return True, False
        return False, False

    def make_move(self, new_board):
        '''
        Method updates boards according to index in self.moves list.
        :param new_board: a board legal moves list. given by legal_moves_board
        '''
        if self.moves is None:
            raise Exception("No moves computed")
        if not new_board in self.moves:
            raise Exception("Move is illegal")

        # update our data structure:
        self.white = new_board[0]
        self.black = new_board[1]
        self.moves = []
        self.white_turn = not self.white_turn

        self.legal_moves_boards()

    def key(self):
        return self.white, self.black, self.white_turn

    def copy(self):
        return copy.deepcopy(self)


class GameBoard(FBoard):
    def __init__(self, fen='8/pppppppp/8/8/8/8/PPPPPPPP/8', white_turn=True):
        boards = self.fen2bit(fen)
        super().__init__(white_turn=white_turn, white=boards[0], black=boards[1])
        self.gameBoard = chess.Board(fen)
        self.fboardSvg = chess.svg.board(self.gameBoard).encode("UTF-8")

    def fen2bit(self, fen):
        white = np.zeros((8, 8), dtype=bool)
        black = np.zeros((8, 8), dtype=bool)
        rows = re.split('/|\n', fen)
        if len(rows) != 8:
            raise Exception("Invalid board")
        for i, row in enumerate(rows):
            effective_index = 0
            for j, char in enumerate(row):
                if char.isdigit():
                    effective_index += ord(char) - ord('0')
                    # digit is a number of cells to skip
                elif char == 'p' or char == 'q':  # Queen is used at the end of the game to represent winning
                    black[i][effective_index] = True
                    effective_index += 1
                elif char == 'P' or char == 'Q':
                    white[i][effective_index] = True
                    effective_index += 1
                elif char == '.':
                    effective_index += 1
        # Our convention is padded boards for shifting
        black = np.pad(black, [(1, 1), (1, 1)], mode='constant')
        white = np.pad(white, [(1, 1), (1, 1)], mode='constant')
        return white, black

    def bit2fen(self, white=None, black=None) -> str:
        white = self.white if white is None else white
        black = self.black if black is None else black
        fen = ""
        for row_i in range(8):
            counter_col = 0
            for col_i in range(8):
                if white[row_i + 1][col_i + 1]:
                    if counter_col > 0:
                        fen = fen + str(counter_col) + 'P'
                        counter_col = 0
                    else:
                        fen = fen + 'P'
                elif black[row_i + 1][col_i + 1]:
                    if counter_col > 0:
                        fen = fen + str(counter_col) + 'p'
                        counter_col = 0
                    else:
                        fen = fen + 'p'
                else:
                    counter_col += 1
            if counter_col > 0:
                fen += str(counter_col)
            if row_i != 7:
                fen = fen + '/'
        return fen

    def move2san(self, white=None, black=None) -> str:
        move = np.logical_xor(self.white, white)
        if np.sum(move) == 2:
            idx = np.transpose(np.nonzero(move))
            if chr(9 - idx[0, 0] + ord('0')) == '8':
                return "{0}{1}{2}{3}q".format(chr(idx[1, 1] + ord('a') - 1), chr(9 - idx[1, 0] + ord('0')),
                                              chr(idx[0, 1] + ord('a') - 1), chr(9 - idx[0, 0] + ord('0')))
            return "{0}{1}{2}{3}".format(chr(idx[1, 1] + ord('a') - 1), chr(9 - idx[1, 0] + ord('0')),
                                         chr(idx[0, 1] + ord('a') - 1), chr(9 - idx[0, 0] + ord('0')))
        move = np.logical_xor(self.black, black)
        if np.sum(move) == 2:
            idx = np.transpose(np.nonzero(move))
            if chr(9 - idx[1, 0] + ord('0')) == '1':
                return "{0}{1}{2}{3}q".format(chr(idx[0, 1] + ord('a') - 1), chr(9 - idx[0, 0] + ord('0')),
                                              chr(idx[1, 1] + ord('a') - 1), chr(9 - idx[1, 0] + ord('0')))
            return "{0}{1}{2}{3}".format(chr(idx[0, 1] + ord('a') - 1), chr(9 - idx[0, 0] + ord('0')),
                                         chr(idx[1, 1] + ord('a') - 1), chr(9 - idx[1, 0] + ord('0')))

    def make_move(self, move):
        # case of agent move
        if isinstance(move, np.ndarray):
            move = self.move2san(white=move[0], black=move[1])
        self.gameBoard.push_san(move)
        self.fboardSvg = chess.svg.board(self.gameBoard).encode("UTF-8")
        new_board = self.fen2bit(str(self.gameBoard))
        super().make_move(new_board)
        return move

    def player_move(self):
        legal = False
        # moves = [self.move2san(white=move[0], black=move[1]) for move in self.legal_moves_boards()]
        moves = list(self.gameBoard.legal_moves)
        move = moves[0]  # avoiding conflicts
        print(moves)
        while not legal:
            print("Enter move:")
            move = str(input())
            legal = True if chess.Move.from_uci(move) in moves else False
            if not legal:
                print("Move is illegal!")
        self.make_move(move)
