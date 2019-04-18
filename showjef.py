"""
showjef.py - Display the contents of JEF files.

"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter
from PyQt5.QtWidgets import QGraphicsView, QApplication, QGraphicsScene

import jef

ColorTable = {
    0x0a: QColor(255, 0, 0),
    0x3c: QColor(0, 0, 255),
    0x02: QColor(255, 255, 255),
    0x28: QColor(200, 0, 0),
    0x44: QColor(255, 240, 142),
    0x24: QColor(200, 160, 0),
    0x20: QColor(255, 0, 0),
    0x0e: QColor(0, 0, 0),
    0x37: QColor(0, 0, 0),
    0x01: QColor(0, 0, 0),
    0x0c: QColor(0, 0, 160),
    0x15: QColor(174, 176, 214),
    0x3e: QColor(159, 213, 127),
    0x0d: QColor(225, 244, 92),
    0x35: QColor(206, 166, 97),
    0x08: QColor(150, 94, 169),
    0x45: QColor(186, 153, 0),
    0x29: QColor(78, 41, 146),
    0x06: QColor(49, 125, 34),
    0x2d: QColor(128, 110, 0),
    0x05: QColor(67, 87, 2),
    0x2e: QColor(0, 57, 37),
}


class Convertor:

    def __init__(self, path, stitches_only=False, show_jumps=False):

        self.jef = jef.Pattern(path)
        self.stitches_only = stitches_only
        self.show_jumps = show_jumps
        self.move_pen = QPen()
        self.move_pen.setStyle(Qt.DotLine)

    def show_coords(self, coords, pen, scene):

        first = True
        mx, my = 0, 0
        for op, x, y in coords:

            if not self.stitches_only:
                scene.addEllipse(x - 2, -y - 2, 4, 4, QPen(QColor(200, 200, 200)))

            if op == "stitch":
                scene.addLine(mx, -my, x, -y, pen)
            elif self.show_jumps:
                if first:
                    scene.addLine(mx, -my, x, -y, QPen(Qt.DashLine))
                else:
                    scene.addLine(mx, -my, x, -y, self.move_pen)

            mx, my = x, y
            first = False

    def show(self, scene):

        i = 0
        for thread in range(self.jef.threads):
            colour = QColor(*self.jef.colour_for_thread(i))
            pen = QPen(colour)
            coordinates = self.jef.coordinates[i]
            self.show_coords(coordinates, pen, scene)
            i += 1


class View(QGraphicsView):

    def __init__(self):
        QGraphicsView.__init__(self)
        self.setRenderHint(QPainter.Antialiasing)

    def resizeEvent(self, event):
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

    def showEvent(self, event):
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)


if __name__ == "__main__":

    if not 2 <= len(sys.argv) <= 3:
        sys.stderr.write("Usage: %s [--stitches-only] <JEF file>\n" % sys.argv[0])
        sys.exit(1)

    stitches_only = "--stitches-only" in sys.argv
    if stitches_only:
        sys.argv.remove("--stitches-only")

    show_jumps = "--show-jumps" in sys.argv
    if show_jumps:
        sys.argv.remove("--show-jumps")

    jef_file = sys.argv[1]

    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    view = View()
    view.setScene(scene)
    view.show()

    convertor = Convertor(jef_file, stitches_only, show_jumps)
    convertor.show(scene)
    sys.exit(app.exec_())
