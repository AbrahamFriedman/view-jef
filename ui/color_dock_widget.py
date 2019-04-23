from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDockWidget, QTreeView, QPushButton, QWidget, QVBoxLayout, QColorDialog, QApplication, \
    QStyle, qApp, QDialog
from PySide2 import *
from colors.color_palette import ColorPalette


class ColorDockWidget(QDockWidget):

    def __init__(self, colorModel, parent = None):

        QDockWidget.__init__(self, "&Colors", parent)

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.colorModel = colorModel
        self.colorPalette = ColorPalette(self)

        colorList = QTreeView()
        colorList.header().hide()
        colorList.setRootIsDecorated(False)
        colorList.setModel(self.colorModel)

        # TODO SIGNAL
        # self.connect(colorList, SIGNAL("activated(QModelIndex)"),
        #              self.editColor)

        self.backgroundButton = QPushButton("&Background Color")
        # TODO SIGNAL
        # self.connect(self.backgroundButton, SIGNAL("clicked()"), self.selectBackground)
        self._set_background_button_color(colorModel.background)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(colorList)
        layout.addWidget(self.backgroundButton)

        self.setWidget(widget)

    def edit_color(self, index):

        item = self.colorModel.itemFromIndex(index)

        if self.colorPalette.exec_(item) == QDialog.Accepted:

            color = self.colorPalette.selectedInternalColor()
            thread_type = self.colorPalette.selectedThreadType()
            if color and thread_type:
                item.setColor(color, thread_type)

    def select_background(self):

        color = QColorDialog.getColor(self.colorModel.background, self)
        if color.isValid():
            self.set_background(color)

    def set_background(self, color):

        self._set_background_button_color(color)
        self.colorModel.set_background(color)

    def _set_background_button_color(self, color):

        icon_size = QApplication.style().pixelMetric(QStyle.PM_ButtonIconSize)
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(color)
        self.backgroundButton.setIcon(QIcon(pixmap))

    def set_pattern(self, pattern):

        self.colorModel.set_pattern(pattern)