# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtCore import SIGNAL
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QDesktopWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main_window.color_dock_widget import ColorDockWidget
from colors.color_models import PatternColorModel


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle("Viewer for Janome Embroidery Files [*]")

        # Pattern-related attributes
        self.stitches_only = True
        self.path = ""
        self.pattern = None
        self.colorModel = PatternColorModel(QColor(Qt.white))
        # TODO SIGNAL
        # self.connect(self.colorModel, SIGNAL("colourChanged()"), self.setModified)

        self.colorDockAction = self._create_color_dock_widget()

        self.statusBar()

        self.mainMenu = self.menuBar()

        # File menu
        self.fileMenu = self.mainMenu.addMenu("&File")
        open_action = self.fileMenu.addAction("&Open")
        open_action.setShortcut(QKeySequence.Open)

        saveAsAction = self.fileMenu.addAction("Save &As...")

        quitAction = self.fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")

        # View menu
        self.viewMenu = self.menuBar().addMenu("&View")
        zoomInAction = self.viewMenu.addAction("Zoom &In")
        zoomInAction.setShortcut(QKeySequence.ZoomIn)
        zoomOutAction = self.viewMenu.addAction("Zoom &Out")
        zoomOutAction.setShortcut(QKeySequence.ZoomOut)

        # Tools menu
        self.toolsMenu = self.menuBar().addMenu("&Tools")
        self.toolsMenu.addAction(self.colorDockAction)

    def _create_color_dock_widget(self):
        self.colourDockWidget = ColorDockWidget(self.colorModel, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colourDockWidget)
        self.colourDockWidget.hide()
        return self.colourDockWidget.toggleViewAction()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(QDesktopWidget().availableGeometry().size() * 0.75)
    window.show()
    sys.exit(app.exec_())
