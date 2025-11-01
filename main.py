"""Launcher for PixelMaker app (small, focused)."""

import sys
from PyQt5.QtWidgets import QApplication

from main_window import PixelMakerWindow
from stylesheet import dark_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    window = PixelMakerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()