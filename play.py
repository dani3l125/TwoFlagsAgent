import chess
from Window import MainWindow
from PyQt5.QtWidgets import QApplication
from Board import FBoard
import numpy as np
import socket
import sys

if __name__ == "__main__":
    #

    # Initialize flags board
    board = FBoard()

    # Create GUI
    app = QApplication([])
    window = MainWindow(board)
    window.show()
    app.exec()



