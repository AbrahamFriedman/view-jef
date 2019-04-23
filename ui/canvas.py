"""
jefviewer.py - Display the contents of JEF files.
"""

from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QScrollArea

import ui


class Canvas(QWidget):

    def __init__(self, colorModel, parent=None):

        QWidget.__init__(self, parent)

        self.colorModel = colorModel
        # TODO SIGNAL
        # self.connect(colorModel, SIGNAL("colorChanged()"), self.update)
        # self.connect(colorModel, SIGNAL("backgroundChanged()"), self.update)

        self.renderer = None
        self.scale = 1.0

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        # painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.colorModel.background)
        painter.scale(self.scale, self.scale)
        if self.renderer:
            rect = painter.transform().inverted()[0].mapRect(event.rect())
            self.renderer.paint(painter, rect)
        painter.end()

    def sizeHint(self):

        if self.renderer:
            return self.renderer.bounding_rect().size() * self.scale
        else:
            return QSize(0, 0)

    def setRenderer(self, renderer):

        self.renderer = renderer
        self.resize(self.sizeHint())
        self.update()

    def zoom_reset(self):
        self.scale = 1

        self.resize(self.sizeHint())
        self.update()

    def zoom_in(self):

        if self.scale >= 1:
            self.scale = min(self.scale + 1, 10)
        else:
            self.scale = min(self.scale + 0.1, 1)

        self.resize(self.sizeHint())
        self.update()

    def zoom_out(self):

        if self.scale > 1:
            self.scale = max(1, self.scale - 1)
        else:
            self.scale = max(0.1, self.scale - 0.1)

        self.resize(self.sizeHint())
        self.update()


class CanvasView(QScrollArea):

    def __init__(self, canvas, parent=None):

        QScrollArea.__init__(self, parent)
        self.canvas = canvas
        self.setWidget(canvas)
        self.dragging = False
        self.dragStartPos = QPoint()
        canvas.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.canvas.dragging = True
            self.canvas.setCursor(Qt.ClosedHandCursor)
            self.dragStartPos = QPoint(event.pos())

    def mouseMoveEvent(self, event):

        if self.canvas.dragging:
            change = event.pos() - self.dragStartPos
            self.dragStartPos = QPoint(event.pos())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - change.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - change.y())

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.canvas.dragging = False
            self.canvas.setCursor(Qt.OpenHandCursor)

    def _zoom(self, method):

        xScroll = self.horizontalScrollBar().value() + self.horizontalScrollBar().pageStep() / 2
        yScroll = self.verticalScrollBar().value() + self.verticalScrollBar().pageStep() / 2
        fx = float(xScroll) / self.canvas.width()
        fy = float(yScroll) / self.canvas.height()

        method()

        self.horizontalScrollBar().setValue(
            fx * self.canvas.width() - self.horizontalScrollBar().pageStep() / 2)
        self.verticalScrollBar().setValue(
            fy * self.canvas.height() - self.verticalScrollBar().pageStep() / 2)

    def zoom_in(self):
        self._zoom(self.canvas.zoomIn)

    def zoom_out(self):
        self._zoom(self.canvas.zoomOut)

    def _create_color_dock_widget(self):

        self.colorDockWidget = ui.ColorDockWidget(self.colorModel, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorDockWidget)
        self.colorDockWidget.hide()
        return self.colorDockWidget.toggleViewAction()

    def setModified(self):

        self.setWindowModified(True)
