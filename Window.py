from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget
import chess.svg


class MainWindow(QWidget):
    def __init__(self, board):
        super().__init__()

        self.setGeometry(100, 100, 1100, 1100)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 1080, 1080)

        self.fboard = board

        self.fboardSvg = chess.svg.board(self.fboard).encode("UTF-8")
        self.widgetSvg.load(self.fboardSvg)
