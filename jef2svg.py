"""
jef2svg.py - Converts the contents of JEF files to SVG drawings.
"""

import os, sys

from PyQt5.Qt import QT_VERSION
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QApplication

import jef


class Convertor:

    def __init__(self, path, stitches_only=False):

        self.jef = jef.Pattern(path)
        self.stitches_only = stitches_only

    def bounding_rect(self):

        x, y = [], []
        for coordinates in self.jef.coordinates:
            # x.extend(map(lambda (op, i, j): i, coordinates))
            # y.extend(map(lambda (op, i, j): j, coordinates))
            x.extend(map(lambda op_i_j: op_i_j[1], coordinates))
            y.extend(map(lambda op_i_j: op_i_j[2], coordinates))

        return QRect(min(x), -max(y), max(x) - min(x), max(y) - min(y))

    def show(self, painter):

        i = 0
        for i in range(self.jef.threads):

            colour = QColor(*self.jef.colour_for_thread(i))
            coordinates = self.jef.coordinates[i]

            if not self.stitches_only:
                pen = QPen(QColor(200, 200, 200))
                painter.setPen(pen)

                for op, x, y in coordinates:
                    painter.drawEllipse(x - 2, -y - 2, 4, 4)

            pen = QPen(colour)
            painter.setPen(pen)

            path = QPainterPath()
            for op, x, y in coordinates:
                if op == "move":
                    path.moveTo(x, -y)
                elif op == "stitch":
                    path.lineTo(x, -y)

            if path.elementCount() > 0:
                painter.drawPath(path)

            i += 1


if __name__ == "__main__":

    if not 3 <= len(sys.argv) <= 4:
        sys.stderr.write("Usage: %s [--stitches-only] <JEF file> <SVG file>\n" % sys.argv[0])
        sys.exit(1)

    stitches_only = "--stitches-only" in sys.argv
    if stitches_only:
        sys.argv.remove("--stitches-only")

    jef_file = sys.argv[1]
    svg_file = sys.argv[2]

    app = QApplication(sys.argv)
    svg = QSvgGenerator()
    svg.setFileName(svg_file)

    if QT_VERSION >= (4, 5, 0):
        svg.setDescription(
            'Original JEF file "' + os.path.split(jef_file)[1] + '" converted '
                                                                 'to ' + os.path.split(svg_file)[1] + ' by jef2svg.py.'
        )

    convertor = Convertor(jef_file, stitches_only)
    rect = convertor.bounding_rect()
    if QT_VERSION >= (4, 5, 0):
        svg.setViewBox(rect)
    svg.setSize(rect.size())

    painter = QPainter()
    painter.begin(svg)
    convertor.show(painter)
    painter.end()

    sys.exit()
