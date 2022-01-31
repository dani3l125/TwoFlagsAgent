import copy
import random
import threading
import time
import numpy as np
import math
import Board
from multiprocessing import Pool


class Graph:
    def __init__(self):
        self.graph = {}

    class Node:
        def __init__(self, board):
            self.board = board  # FBoard object
            self.is_terminal = board.is_checkmate()  # overridden
            self.is_computed = False
            self.is_exploited = False
            self.h = 0
            self.children = []
            self.parents = []
            self.h_time = 0

    def exploit(self, node_key):
        for move in self.graph[self.get_key(node_key)].board.moves:
            # copy board and move
            tmp_board = self.graph[self.get_key(node_key)].board.copy()
            tmp_board.make_move(move)
            # if first visited. append
            if not self.get_key(tmp_board.key()) in self.graph.keys():
                self.graph[self.get_key(tmp_board.key())] = Graph.Node(tmp_board)
            # if not in children list, append kid
            if not self.get_key(tmp_board.key()) in self.graph[self.get_key(node_key)].children:
                self.graph[self.get_key(node_key)].children.append(self.get_key(tmp_board.key()))
            # if parent not in list
            if not self.get_key(node_key) in self.graph[self.get_key(tmp_board.key())].parents:
                self.graph[self.get_key(tmp_board.key())].parents.append(self.get_key(node_key))
            self.graph[self.get_key(node_key)].is_exploited = True

    def add_node(self, board_key):
        self.graph[self.get_key(board_key)] = self.Node(
            Board.FBoard(white=board_key[0], black=board_key[1], white_turn=board_key[2]))

    def get_key(self, board_key):
        if isinstance(board_key, str):
            return board_key
        return np.array2string(board_key[0]) + np.array2string(board_key[1]) + str(board_key[2])

    def get_node(self, board_key):
        if not self.get_key(board_key) in self.graph.keys():
            self.add_node(board_key)
        if not self.graph[self.get_key(board_key)].is_exploited:
            self.exploit(board_key)
        return self.graph[self.get_key(board_key)]


class Agent:
    """
    An Agent that can return a legal chess action for the user or AI to take.
    :param board: a ChessGame to run the agent on
    :param color: the color that the agent will choose moves for
    :param threshold: hyper parameter for evaluation function
    :param warmup: hyper parameter for evaluation function
    """

    def __init__(self, board, color, game_time=15, threshold=5, warmup=3):
        self.board = board
        self.game_time = game_time
        self.warmup = warmup
        self.is_white = True if color == "W" else False  # W->P; B->p
        self.threshold = threshold

    def ply(self):
        """
        Gets the best action for the player to take.
        :return: the action
        """
        return (0, 0), (0, 0)

    def heuristic(self, node):
        if node.is_computed:
            return node.h

        # First option: winning by going straight to the final row
        idx_w = np.where(node.board.white)
        white_attackers = np.array([idx_w[0][i] - 1
                                    if idx_w[0][i] <= 4 and not np.sum(
            node.board.black[:idx_w[0][i], idx_w[1][i] - 1:idx_w[1][i] + 2]) else 10
                                    for i in range(len(idx_w[0]))])
        idx_b = np.where(node.board.black)
        black_attackers = np.array([8 - idx_b[0][i]
                                    if idx_b[0][i] >= 5 and not np.sum(
            node.board.white[idx_b[0][i] + 1:, idx_b[1][i] - 1:idx_b[1][i] + 2]) else 10
                                    for i in range(len(idx_b[0]))])

        closest_white_dist = np.min(white_attackers) if white_attackers.size != 0 else 10
        closest_black_dist = np.min(black_attackers) if black_attackers.size != 0 else 10
        if closest_white_dist == closest_black_dist and closest_black_dist != 10:  # look at next step
            closest_white_dist = closest_white_dist - node.board.white_turn
            closest_black_dist = closest_black_dist - (not node.board.white_turn)
        if self.is_white:
            if closest_white_dist < closest_black_dist:
                node.h = 1000 * (5 - closest_white_dist)
                node.is_computed = True
                return node.h
            if closest_white_dist > closest_black_dist:
                node.h = -1000 * (5 - closest_black_dist)
                node.is_computed = True
                return node.h
        else:
            if closest_white_dist < closest_black_dist:
                node.h = -1000 * (5 - closest_white_dist)
                node.is_computed = True
                return node.h
            if closest_white_dist > closest_black_dist:
                node.h = 1000 * (5 - closest_black_dist)
                node.is_computed = True
                return node.h

        # Second option: winning by disabling the opponent of moving
        legal_moves = self.threshold if node.board.moves.shape[0] > self.threshold \
            else node.board.moves.shape[0]

        if self.is_white:
            if node.board.white_turn:
                node.h = -5000 * (self.threshold - legal_moves) / self.threshold
            else:
                node.h = 5000 * (self.threshold - legal_moves) / self.threshold
        else:
            if node.board.white_turn:
                node.h = 5000 * (self.threshold - legal_moves) / self.threshold
            else:
                node.h = -5000 * (self.threshold - legal_moves) / self.threshold

        if node.h != 0:
            node.is_computed = True
            return node.h

        # Third option: kill as much pawns as possible
        if self.is_white:
            node.h = ((np.sum(node.board.white) - np.sum(node.board.black)) / np.sum(node.board.white)) * 5000
        else:
            node.h = ((np.sum(node.board.black) - np.sum(node.board.white)) / np.sum(node.board.black)) * 5000

        node.is_computed = True
        return node.h


class RandomAgent(Agent):
    """
    A RandomAgent is an agent that randomly chooses a legal move to make.
    :param game: a ChessGame to run the agent on
    :param startColor: the color that the agent will choose moves for
    """

    def __init__(self, board, color, game_time):
        super().__init__(board, color, game_time)

    def ply(self):
        """
        Randomly chooses a legal action
        :return: the action
        """
        return "", self.board.make_move(random.choice(self.board.moves))


init_depth = 5


class MinimaxAgent(Agent):
    """
    A RandomAgent is an agent that randomly chooses a legal move to make.
    :param board: a ChessGame to run the agent on
    :param color: the color that the agent will choose moves for
    """

    def __init__(self, board, color, game_time):
        super().__init__(board, color, game_time)
        self.graph = Graph()

    def minimax(self, board_key, maximizing=True, depth=15):
        node = self.graph.get_node(board_key)
        if depth == 0 or node.is_terminal[0]:
            return self.heuristic(node)
        if maximizing:
            value = float('-inf')
            for child_key in node.children:
                value = max(value, self.minimax(child_key, False, depth - 1))
            return value
        else:
            value = float('inf')
            for child_key in node.children:
                value = min(value, self.minimax(child_key, True, depth - 1))
            return value

    def ply(self):
        """
        Randomly chooses a legal action
        :return: the action
        """
        start = time.time()
        if self.warmup > 0:
            move = random.choice(self.board.moves)
            san = self.board.make_move(move)
            self.warmup -= 1
            return "Color:{} ply time:{}".format("White." if self.is_white else "Black.", time.time() - start), san
        best_value = float('-inf')
        best_move = None
        for count, move in enumerate(self.board.moves):
            tmp_board = Board.FBoard(white=self.board.white, black=self.board.black, white_turn=self.board.white_turn)
            tmp_board.make_move(move)
            value = self.minimax(tmp_board.key())
            if best_value < value:
                best_value = value
                best_move = move
        san = self.board.make_move(best_move)
        return "Color:{} ply time:{}".format("White." if self.is_white else "Black.", time.time() - start), san


class AlphaBetaAgent(Agent):
    """
    A RandomAgent is an agent that randomly chooses a legal move to make.
    :param board: a ChessGame to run the agent on
    :param color: the color that the agent will choose moves for
    """

    def __init__(self, board, color, game_time):
        super().__init__(board, color, game_time)
        self.graph = Graph()

    def alphabeta(self, board_key, a=float('-inf'), b=float('inf'), maximizing=True, depth=0):
        node = self.graph.get_node(board_key)
        if depth == 0 or node.is_terminal[0]:
            return self.heuristic(node)
        if maximizing:
            value = float('-inf')
            for child_key in node.children:
                value = max(value, self.alphabeta(child_key, a=a, b=b, maximizing=False, depth=depth - 1))
                if value >= b:
                    break
                a = max(a, value)
            return value
        else:
            value = float('inf')
            for child_key in node.children:
                value = min(value, self.alphabeta(child_key, a=a, b=b, maximizing=True, depth=depth - 1))
                if value <= a:
                    break
                b = min(b, value)
            return value

    def ply(self, depth=5, maximizing=True):
        """
        chooses action using alphabeta pruning
        :return: the action
        """
        start = time.time()
        if self.warmup > 0:
            move = random.choice(self.board.moves)
            san = self.board.make_move(move)
            self.warmup -= 1
            return "Color:{} ply time:{}".format("White." if self.is_white else "Black.", time.time() - start), san
        best_value = float('-inf')
        best_move = None
        for move in self.board.moves:
            tmp_board = Board.FBoard(white=self.board.white, black=self.board.black, white_turn=self.board.white_turn)
            tmp_board.make_move(move)
            value = self.alphabeta(tmp_board.key(), depth=depth, maximizing=not maximizing)
            if best_value < value:
                best_value = value
                best_move = move
        san = self.board.make_move(best_move)
        return "Color:{} ply time:{}".format("White." if self.is_white else "Black.", time.time() - start), san


class BestAgent(AlphaBetaAgent):
    def __init__(self, board, color, game_time):
        super().__init__(board, color, game_time)
        self.move_counter = -self.warmup
        # Permanent brain method
        self.ready = False
        self.move_time = -1
        self.search = threading.Thread(target=self.keepSearch, args=(self.board.key(), False))
        self.ids_consts = (20, 10, 200)
        self.search.start()
        self.game_time *= 60
        self.depth = 2

    def keepSearch(self, board_key, maximizing=True, a=float('-inf'), b=float('inf'), depth=200):
        # node = self.graph.get_node(board_key)
        # while not self.ready:
        #     for kid in node.children:
        #         if self.ready:
        #             break
        #         self.graph.get_node(kid)
        #     node = random.choice(node.children)
        #     node = self.graph.get_node(node)
        return

    def depth_scheduler(self):
        if self.move_counter <= 3:
            self.depth = 2
        elif self.move_counter == 4:
            self.depth = 3
        else:
            ratio = self.move_time / self.game_time
            if ratio >= 0.25:
                self.depth -= 1
            if 0.1 <= ratio:
                return self.depth
            elif 0.05 <= ratio:
                self.depth += 1
            else:
                if self.move_counter <= 15:
                    self.depth += 2
                else:
                    self.depth += 3
        self.depth = min(20, self.depth)
        return self.depth

    def ply(self, depth=3, maximizing=True):  # depth is used only by base class
        self.depth_scheduler()
        start = time.time()
        self.ready = True
        self.search.join()
        print("{} player will search at depth {}".format("White" if self.is_white else "Black", self.depth))
        san = super().ply(depth=self.depth, maximizing=maximizing)[1]
        self.move_counter += 1
        self.search = threading.Thread(target=self.keepSearch, args=(self.board.key(), False))
        self.move_time = time.time() - start
        self.game_time -= self.move_time
        self.search.start()
        self.ready = False

        return "Color:{} ply time:{}".format("White." if self.is_white else "Black.", time.time() - start), san

    def calcBranchingFactor(self, depth):
        num_moves = len(self.board.moves)
        num_of_boards = np.uint64(1)
        if depth == 0:
            return num_moves, num_of_boards
        node = self.graph.get_node(self.board.key())
        average = num_moves
        children = node.children
        tmp_board = self.board
        for child in children:
            child = self.graph.get_node(child)
            self.board = child.board
            tmp_moves, tmp_num_of_boards = self.calcBranchingFactor(depth - 1)
            num_moves = (num_moves * num_of_boards + tmp_moves * tmp_num_of_boards) / (
                    tmp_num_of_boards + num_of_boards)
            num_of_boards += tmp_num_of_boards
        self.board = tmp_board
        return num_moves, num_of_boards


agentsDict = {"random": RandomAgent, "minimax": MinimaxAgent, "alpha": AlphaBetaAgent, "best": BestAgent}
