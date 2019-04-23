import os, sys

from PyQt5.QtCore import Qt, QVariant, QAbstractTableModel, QModelIndex

from colors import jef_colors
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QColor
from PyQt5.QtWidgets import QApplication


class PatternColorItem(QStandardItem):

    def __init__(self, internal_color):

        QStandardItem.__init__(self)

        self.internal_color = internal_color
        self._colors = jef_colors.color_mappings[internal_color]

        for thread_type in jef_colors.color_groups:
            if thread_type in self._colors:
                self.thread_type = thread_type
                break
        else:
            # We should never have an undefined thread type.
            self.thread_type = None

        self.setColor(internal_color, self.thread_type)

    def color(self):

        code = self._colors[self.thread_type]
        name, color = jef_colors.known_colors[self.thread_type][code]
        return color

    def internalColor(self):

        return self.internal_color

    def threadType(self):

        return self.thread_type

    def isChecked(self):

        return self.checkState() == Qt.Checked

    def setColor(self, internal_color, thread_type):

        self.internal_color = internal_color
        self.thread_type = thread_type
        self._colors = jef_colors.color_mappings[internal_color]

        code = self._colors[thread_type]
        name, color = jef_colors.known_colors[thread_type][code]

        # self.setText(QApplication.translate("PatternColorItem", "%1: %2 (%3)").arg(code).arg(name, thread_type))
        self.setText(QApplication.translate("PatternColorItem", "{}: {} ({})").format(code, name, thread_type))
        self.setData(QVariant(QColor(color)), Qt.DecorationRole)
        self.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)


class PatternColorModel(QStandardItemModel):

    def __init__(self, background):
        QStandardItemModel.__init__(self)

        self.background = background
        self.pattern = None

        # TODO SIGNAL
        # self.connect(self, SIGNAL("itemChanged(QStandardItem *)"),
        #              self, SIGNAL("colourChanged()"))
        # self.connect(self, SIGNAL("itemChanged(QStandardItem *)"),
        #              self.updatePattern)

    def set_background(self, colour):
        self.background = colour
        # TODO SIGNAL
        # self.emit(SIGNAL("backgroundChanged()"))

    def set_pattern(self, pattern):
        self.pattern = pattern

        # Update the colors in the list with those from the pattern.
        self.clear()

        for internal_color in pattern.colors:
            item = PatternColorItem(internal_color)
            self.appendRow(item)

    def update_pattern(self, item):
        self.pattern.set_color(item.row(), item.internalColor())


class ColorItem:
    """ColorItem

    Represents an internal Janome color and its interpretations in different
    thread types.
    """

    def __init__(self, internal_color):
        self.internal_color = internal_color
        self._colors = jef_colors.color_mappings[internal_color]

    def data(self, thread_type):
        code = self._colors[thread_type]
        return code

    def hasThread(self, thread_type):
        return self._colors.has_key(thread_type)

    def color(self, thread_type=None):
        code = self.data(thread_type)
        name, color = jef_colors.known_colors[thread_type][code]
        return color

    def colors(self):
        return self._colors

    def name(self, thread_type=None):
        code = self.data(thread_type)
        name, color = jef_colors.known_colors[thread_type][code]
        return name


class ColorModel(QAbstractTableModel):

    def __init__(self):

        QAbstractTableModel.__init__(self)

        # TODO SIGNAL
        # self.connect(self, SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
        #              self, SIGNAL("colorChanged()"))

        # Create a list of rows for the model, each containing the thread
        # colors which correspond to a given internal color.
        self.colors = []
        self.headers = list(jef_colors.color_groups)

        keys = sorted(jef_colors.color_mappings)

        for internal_color in keys:
            item = ColorItem(internal_color)
            self.colors.append(item)

    def rowCount(self, parent):

        if parent.isValid():
            return -1
        else:
            return len(self.colors)

    def columnCount(self, parent):

        if parent.isValid():
            return -1
        else:
            return len(self.headers)

    def data(self, index, role):

        if not index.isValid():
            return QVariant()

        row = index.row()
        if not 0 <= row < self.colors:
            return QVariant()

        item = self.colors[row]
        if not 0 <= index.column() < len(self.headers):
            return QVariant()

        thread_type = self.headers[index.column()]

        try:
            if role == Qt.DisplayRole:
                return QVariant(item.name(thread_type))
            elif role == Qt.DecorationRole:
                return QVariant(QColor(item.color(thread_type)))
            else:
                return QVariant()
        except KeyError:
            return QVariant()

    def flags(self, index):

        if not index.isValid():
            return Qt.NoItemFlags

        item = self.colors[index.row()]
        thread_type = self.headers[index.column()]

        if item.hasThread(thread_type):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemFlags(Qt.ItemFlag(0))  # Qt.NoItemFlags

    def headerData(self, section, orientation, role):

        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Vertical:
            return QVariant(self.colors[section].internal_color)
        else:
            return QVariant(self.headers[section])

    def internalColor(self, index):

        """Returns the internal color of the item with the given index."""

        item = self.colors[index.row()]
        return item.internal_color

    def threadType(self, index):

        """Returns the thread type of the color represented by the given index."""
        return self.headers[index.column()]

    def getIndex(self, internal_color, thread_type):

        row = 0
        for item in self.colors:

            if item.internal_color == internal_color:

                try:
                    column = self.headers.index(thread_type)
                    return self.createIndex(row, column)
                except ValueError:
                    return QModelIndex()

            row += 1

        return QModelIndex()
