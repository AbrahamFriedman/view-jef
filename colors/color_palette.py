"""
colorpalette.py - Display thread colors in a palette widget.
"""

import os, sys

from colors.color_models import ColorModel
from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import QDialog, QTableView, QAbstractItemView, QDialogButtonBox, QVBoxLayout


class ColorPalette(QDialog):

    def __init__(self, parent=None):

        QDialog.__init__(self, parent)

        self.colorView = QTableView()
        self.colorModel = ColorModel()
        self.colorView.setModel(self.colorModel)
        self.colorView.setSelectionMode(QAbstractItemView.SingleSelection)

        # TODO SIGNAL
        # self.connect(self.colorView, SIGNAL("activated()"), self.accept)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # TODO SIGNAL
        # self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        # self.connect(buttonBox, SIGNAL("rejected()"), self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.colorView)
        layout.addWidget(buttonBox)

        self.setWindowTitle(self.tr("Color Palette"))

    def exec_(self, item):

        index = self.colorModel.getIndex(item.internalColor(), item.threadType())

        self.colorView.selectionModel().setCurrentIndex(index,
                                                         QItemSelectionModel.ClearAndSelect)

        self.colorView.setFocus(Qt.ActiveWindowFocusReason)
        return QDialog.exec_(self)

    def selectedInternalColor(self):

        index = self.colorView.selectionModel().currentIndex()
        if index.isValid():
            return self.colorModel.internalColor(index)
        else:
            return None

    def selectedThreadType(self):

        index = self.colorView.selectionModel().currentIndex()
        if index.isValid():
            return self.colorModel.threadType(index)
        else:
            return None
