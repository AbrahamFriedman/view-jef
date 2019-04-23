import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, qApp, QMessageBox

import jef
from ui.renderer import Renderer
from colors.color_models import PatternColorModel
from ui.canvas import Canvas, CanvasView
from ui.color_dock_widget import ColorDockWidget


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        # TODO Changed the way __init__ is called, verify this is equivalent
        # QMainWindow.__init__(self, parent)
        super(MainWindow, self).__init__()

        self.setWindowTitle("Viewer for Janome Embroidery Files [*]")

        # Pattern-related attributes
        self.stitches_only = True
        self.path = ""
        self.pattern = None
        self.canvas = None
        self.area = None
        self.colorModel = PatternColorModel(QColor(Qt.white))
        # TODO SIGNAL
        # self.connect(self.colorModel, SIGNAL("colorChanged()"), self.setModified)

        self.create_ui()

    def create_ui(self):
        self.canvas = Canvas(self.colorModel)

        self.create_menu_bar()
        self.statusBar()

        self.area = CanvasView(self.canvas)
        self.area.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(self.area)

    def create_menu_bar(self):
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("&File")
        viewMenu = main_menu.addMenu("&View")
        toolsMenu = main_menu.addMenu("&Tools")

        # File menu - Open File
        open_file_action = QAction("Open File...", self)
        open_file_action.setStatusTip("Open a JEF file")
        open_file_action.setShortcut(QKeySequence.Open)
        # TODO Change method self.close
        open_file_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_file_action)

        # File menu - Save As
        save_file_action = QAction("Save &As...", self)
        save_file_action.setStatusTip("Save a JEF file")
        save_file_action.setShortcut("Cmd-S")
        # TODO Change method self.close
        save_file_action.triggered.connect(self.close)
        file_menu.addAction(save_file_action)

        # File menu - Quit
        quit_action = QAction("Quit", self)
        quit_action.setStatusTip("Exit application")
        quit_action.setShortcut(QKeySequence.Close)
        # TODO Change method self.close
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu - Zoom
        zoom_reset_action = QAction("&Zoom", self)
        zoom_reset_action.setStatusTip("Reset Zoom")
        zoom_reset_action.setShortcut('Z')
        zoom_reset_action.triggered.connect(self.canvas.zoom_reset)
        viewMenu.addAction(zoom_reset_action)

        # View menu - Zoom In
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setStatusTip("Zoom in closer")
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        viewMenu.addAction(zoom_in_action)

        # View menu - Zoom Out
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setStatusTip("Zoom out wider")
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        viewMenu.addAction(zoom_out_action)

        # Tools menu - color dock
        # TODO add tools menu options
        toolsMenu.addAction(self._create_color_dock_widget())

    def _create_color_dock_widget(self):
        self.colorDockWidget = ColorDockWidget(self.colorModel, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorDockWidget)
        self.colorDockWidget.hide()
        return self.colorDockWidget.toggleViewAction()

    def open_file_dialog(self):
        # TODO check for no file selected on open
        # TODO unicode
        path = None
        # path = unicode(
        #     QFileDialog.getOpenFileName(
        #         self, self.tr("Open File"), os.path.split(self.path)[0],
        #         self.tr("Janome Embroidery Files (*.jef *.JEF)"))
        # )
        # getOpenFileName() returns a tuple with [0[ = absolute filename, [1] = filter. We only want the name.
        path = QFileDialog.getOpenFileName(self, "Open File", os.path.dirname(self.path),
                                           "Janome Embroidery Files (*.jef *.JEF)")
        if path:

            self.open_file(path[0])

    def open_file(self, path):
        # TODO unicode
        # path = unicode(path)
        self.pattern = jef.Pattern(path)

        qApp.setOverrideCursor(Qt.WaitCursor)
        self.path = path
        self.colorDockWidget.set_pattern(self.pattern)
        self.canvas.setRenderer(Renderer(self.pattern, self.colorModel, self.stitches_only))
        self.setWindowTitle("{} - Viewer for Janome Embroidery Files [*]".format(path))
        qApp.restoreOverrideCursor()

    def save_file_dialog(self):
        # TODO unicode
        path = None
        # path = unicode(
        #     QFileDialog.getSaveFileName(
        #         self, self.tr("Save File"), os.path.split(self.path)[0],
        #         self.tr("Janome Embroidery Files (*.jef *.JEF)"))
        # )

        if path:
            self.save_file(path)

    def save_file(self, path):
        # TODO unicode
        path = None
        # path = unicode(path)

        qApp.setOverrideCursor(Qt.WaitCursor)
        saved = self.pattern.save(path)
        qApp.restoreOverrideCursor()

        if saved:
            self.setWindowModified(False)
            self.path = path
            self.setWindowTitle("%1 - Viewer for Janome Embroidery Files [*]".arg(path))
        else:
            QMessageBox.warning(self, "Failed to save file.")
