from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QAction, QStatusBar
)
import chess.svg
from Board import GameBoard, FBoard

import random
import argparse
import Agents
import Socket

parser = argparse.ArgumentParser()
parser.add_argument("--server", type=int, default=1,
                    help="set True to play against server")
parser.add_argument("--port", type=str, default="9999",
                    help="port to connect")
parser.add_argument("--ip", type=str, default="localhost",
                    help="ip to connect")
parser.add_argument("--human", type=bool, default=0,
                    help="set True to play against human")
parser.add_argument("--color", type=str, default="R",
                    help="agent color:W/B/R")
parser.add_argument("--agent", type=str, default="best",
                    help="Type of agent:random/minimax/alpha/best")
parser.add_argument("--agent2", type=str, default="random",
                    help="Type of agent:random/minimax/alpha/best")
parser.add_argument("--pt", type=int, default=0,
                    help="Print times for each ply if True.")
parser.add_argument("--fen", type=str, default='8/pppppppp/8/8/8/8/PPPPPPPP/8',
                    help="Initialize board")


args = parser.parse_args()


class Game(QMainWindow):
    def __init__(self, board, socket, game_time=15):
        super().__init__()

        self.socket = socket
        self.setGeometry(100, 100, 900, 915)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 25, 880, 880)

        if args.color == "R":
            # Choose random color
            args.color = "B" if bool(random.getrandbits(1)) else "W"

        self.board = board
        self.game_time = game_time
        # Initialize agents
        self.agent = Agents.agentsDict[args.agent](self.board, args.color, self.game_time)
        self.agent2 = None

        if not args.human and not args.server:
            # 2 agents case
            color2 = "W" if args.color == "B" else "B"
            self.agent2 = Agents.agentsDict[args.agent2](self.board, color2, self.game_time)
        # Board visualization:
        self.widgetSvg.load(self.board.fboardSvg)
        self.toolbar = QToolBar("My main toolbar")
        self.addToolBar(self.toolbar)
        self.button_action = QAction("Make Move", self)
        self.button_action.triggered.connect(self.play)
        self.toolbar.addAction(self.button_action)

        self.agent2_move = True

        if args.color == "W" or (args.color == "B" and not self.board.white_turn):
            time_msg = self.agent.ply()  # If agent is first
            if args.pt:
                print(time_msg)
        self.update_board()

        # print(self.agent.calcBranchingFactor(depth=15))

    def play(self):
        # self.agent2.heuristic(self.agent2.graph.get_node(self.agent.board.key()))
        self.toolbar.removeAction(self.button_action)
        if args.human:
            self.board.player_move()
            if self.check_winner():
                return
            time_msg = self.agent.ply()  # If agent is first
            if args.pt:
                print(time_msg)
        elif args.server:
            move = self.socket.recieve()
            if move.endswith('1') or move.endswith('8'):
                # for our visualizing protocol for end of game
                move = move + 'q'
            self.board.make_move(move)
            self.update_board()
            if self.check_winner():
                return
            agent_msg = self.agent.ply()  # If agent is first
            if args.pt:
                print(agent_msg[0])
            if args.server:
                socket.send(agent_msg[1].rstrip("q"))
        else:  # If two agents- Make move is only on ply
            if self.agent2_move:
                time_msg = self.agent2.ply()  # If agent is first
                if args.pt:
                    print(time_msg)
                if self.check_winner():
                    return
            else:
                time_msg = self.agent.ply()  # If agent is first
                if args.pt:
                    print(time_msg)
                if self.check_winner():
                    return
            self.agent2_move = not self.agent2_move
        self.check_winner()
        self.toolbar.addAction(self.button_action)

    def update_board(self):
        self.widgetSvg.load(self.board.fboardSvg)

    def check_winner(self):
        self.update_board()
        result = self.board.is_checkmate()
        if result[0]:
            if (result[1] and args.color == "W") or (not result[1] and args.color == "B"):
                print("Player1 Won!")
            else:
                print("Player2 Won!")
        return result[0]


def handle_setup(setup):
    pawns = setup.split(' ')
    bitboard = GameBoard(fen='8/8/8/8/8/8/8/8')
    for pawn in pawns:
        if pawn.startswith('W'):
            bitboard.white[9 - int(pawn[2]), ord(pawn[1]) - ord('a') + 1] = True
        else:
            bitboard.black[9 - int(pawn[2]), ord(pawn[1]) - ord('a') + 1] = True
    return bitboard.bit2fen()


def server_game(board, game_time, socket):
    agent = Agents.agentsDict[args.agent](board, args.color, game_time)
    while not board.is_checkmate()[0]:  # make move
        agent_msg = agent.ply()  # agent ply
        if args.pt:
            print(agent_msg[0])
        if args.server:
            socket.send(agent_msg[1].rstrip("q"))

        move = socket.recieve()  # server ply
        if move.endswith('1') or move.endswith('8'):
            # for our protocol for end of game
            move = move + 'q'
        board.make_move(move)
    return


if __name__ == "__main__":

    socket = None
    fen = args.fen
    game_time = 10
    white_turn = True
    if args.server:
        socket = Socket.Socket()
        socket.connect(host=args.ip, port=args.port)
        # Handle initial messages:
        msg = socket.recieve()
        while msg != "Begin" and len(msg) != 4:
            if msg.startswith("Time"):
                game_time = int(msg[5:])
                socket.send("OK")
            if msg.startswith("Setup"):
                white_turn = True # Were able to start with black
                fen = handle_setup(msg[6:])
                socket.send("OK")
            msg = socket.recieve()
        # update color by server:
        args.color = "W" if msg == "Begin" else "B"
        board = GameBoard(fen=fen, white_turn=white_turn)
        if msg != "Begin":
            board.make_move(msg)
        server_game(board, game_time, socket)

    # visualized game if not against server:
    else:
        app = QApplication([])
        game = Game(board=GameBoard(fen=fen, white_turn=white_turn), game_time=game_time,
                    socket=socket)  # TODO: add support to predefined fen string
        game.show()
        app.exec()  # TODO: visualize moves and move with cursor when offline
