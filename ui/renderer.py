from PyQt5.QtCore import QRect, Qt, QLine
from PyQt5.QtGui import QPen, QColor


class Zone:

    def __init__(self, rect, color_item):

        self.rect = rect
        self.color_item = color_item
        self.subzones = []
        self.lines = []

    def paint(self, painter):

        if self.color_item.isChecked():
            pen = QPen(QColor(self.color_item.color()))
            painter.setPen(pen)
            # TODO TypeError: index 0 has type 'QLine' but 'QLineF' is expected
            # so switched from drawLines() to drawLine()
            # painter.drawLines(self.lines)
            for line in self.lines:
                painter.drawLine(line)

    def paintWithin(self, painter, rect):

        if self.rect.intersects(rect):

            self.paint(painter)
            for subzone in self.subzones:
                subzone.paintWithin(painter, rect)


class Renderer:

    def __init__(self, pattern, colorModel, stitches_only=False):

        self.pattern = pattern
        self.colorModel = colorModel
        self.stitches_only = stitches_only
        self.rect = QRect()
        self.zones = []
        self._arrange_data()

    def _arrange_data(self):

        self.rect = QRect()

        for i in range(len(self.pattern.coordinates)):

            coordinates = self.pattern.coordinates[i]
            color_item = self.colorModel.item(i)

            lines = []
            xb, yb = [], []
            mx, my = 0, 0

            for op, x, y in coordinates:
                xb.append(x)
                yb.append(y)
                if op == "move":
                    mx, my = x, y
                elif op == "stitch":
                    line = QLine(mx, -my, x, -y)
                    lines.append(line)
                    mx, my = x, y

            xb = [min(xb), max(xb)]
            yb = [min(yb), max(yb)]
            rect = QRect(min(xb), -max(yb), max(xb) - min(xb), max(yb) - min(yb))
            self.rect = self.rect.united(rect)

            zone = Zone(rect, color_item)
            zone.lines = lines
            self._partition_data(zone)
            self.zones.append(zone)

    def _partition_data(self, zone):

        subzone_width = zone.rect.width() / 2
        subzone_height = zone.rect.height() / 2

        if subzone_width < 100 or subzone_height < 100 or len(zone.lines) <= 10:
            return

        subzones = [
            Zone(QRect(zone.rect.x(), zone.rect.y(), subzone_width, subzone_height), zone.color_item),
            Zone(QRect(zone.rect.x() + subzone_width, zone.rect.y(), subzone_width, subzone_height), zone.color_item),
            Zone(QRect(zone.rect.x(), zone.rect.y() + subzone_height, subzone_width, subzone_height), zone.color_item),
            Zone(QRect(zone.rect.x() + subzone_width, zone.rect.y() + subzone_height, subzone_width, subzone_height),
                 zone.color_item)
        ]

        lines = []

        for line in zone.lines:
            for subzone in subzones:
                # If a line is completely within a subzone, add it to the
                # subzone and ignore all other subzones.
                if subzone.rect.contains(line.p1()) and subzone.rect.contains(line.p2()):
                    subzone.lines.append(line)
                    break
            else:
                # If a line is not completely within a zone, add it to the list
                # of lines to keep in the zone.
                lines.append(line)

        zone.lines = lines

        for subzone in subzones:
            if subzone.lines:
                zone.subzones.append(subzone)
                self._partition_data(subzone)

    def bounding_rect(self):

        if self.pattern.hoop_size:
            return QRect(-10 * self.pattern.hoop_size[0] / 2.0,
                         -10 * self.pattern.hoop_size[1] / 2.0,
                         10 * self.pattern.hoop_size[0],
                         10 * self.pattern.hoop_size[1])
        else:
            return self.rect

    def paint(self, painter, rect):

        # Transform the rectangle from window to pattern coordinates.
        rect = rect.translated(self.bounding_rect().topLeft())

        painter.save()
        painter.translate(-self.bounding_rect().topLeft())

        if self.pattern.hoop_size:
            painter.setPen(QPen(Qt.black))
            painter.drawRect(-10 * self.pattern.hoop_size[0] / 2.0,
                             -10 * self.pattern.hoop_size[1] / 2.0,
                             10 * self.pattern.hoop_size[0],
                             10 * self.pattern.hoop_size[1])

        for zone in self.zones:
            zone.paintWithin(painter, rect)
        painter.restore()