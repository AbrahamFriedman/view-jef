from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout


class InfoPopup(QWidget):
    def __init__(self, pattern):
        QWidget.__init__(self)

        # self.popup = QWidget(self)
        self.setWindowTitle("Information")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.create_label_fields()
        self.create_value_fields()

        close_button = QPushButton("Close")
        self.layout.addWidget(close_button)

        self.setGeometry(QRect(100, 100, 400, 200))

    def create_label_fields(self):
        file_name_label = QLabel()
        file_name_label.setText("File Name:")
        self.layout.addWidget(file_name_label, 0, 0)

        size_label = QLabel()
        size_label.setText("Size:")
        self.layout.addWidget(size_label, 1, 0)

        flags_label = QLabel()
        flags_label.setText("Flags:")
        self.layout.addWidget(flags_label, 2, 0)

        date_label = QLabel()
        date_label.setText("Date:")
        self.layout.addWidget(date_label, 3, 0)

        version_label = QLabel()
        version_label.setText("Version:")
        self.layout.addWidget(version_label, 4, 0)

        unknown_label = QLabel()
        unknown_label.setText("Unknown:")
        self.layout.addWidget(unknown_label, 5, 0)

        color_changes_label = QLabel()
        color_changes_label.setText("Color Changes:")
        self.layout.addWidget(color_changes_label, 6, 0)

        points_length_label = QLabel()
        points_length_label.setText("Points Length:")
        self.layout.addWidget(points_length_label, 7, 0)

        hoop_label = QLabel()
        hoop_label.setText("Hoop:")
        self.layout.addWidget(hoop_label, 8, 0)

        extends1_label = QLabel()
        extends1_label.setText("Extends (Distance from center of hoop):")
        self.layout.addWidget(extends1_label, 9, 0)

        extends2_label = QLabel()
        extends2_label.setText("Extends (Distance from default 110 x 110 Hoop):")
        self.layout.addWidget(extends2_label, 10, 0)

        extends3_label = QLabel()
        extends3_label.setText("Extends (Distance from default 50 x 50 Hoop):")
        self.layout.addWidget(extends3_label, 11, 0)

        extends4_label = QLabel()
        extends4_label.setText("Extends (Distance from default 140 x 200 hoop):")
        self.layout.addWidget(extends4_label, 12, 0)

        extends5_label = QLabel()
        extends5_label.setText("Extends (Distance from custom hoop):")
        self.layout.addWidget(extends5_label, 13, 0)

        # for color in colors:
        #     date_label = QLabel()
        #     date_label.setText("Color Number, Color Swatch, Thread Type:")
        #     v_box_self.layout.addWidget(date_label)

    def create_value_fields(self):
        self.file_name_value = QLabel()
        self.layout.addWidget(self.file_name_value, 0, 1)

        self.size_name_value = QLabel()
        self.layout.addWidget(self.size_name_value, 1, 1)

        self.flags_name_value = QLabel()
        self.layout.addWidget(self.flags_name_value, 2, 1)

        self.date_name_value = QLabel()
        self.layout.addWidget(self.date_name_value, 3, 1)

        self.version_name_value = QLabel()
        self.layout.addWidget(self.version_name_value, 4, 1)

        self.unknown_name_value = QLabel()
        self.layout.addWidget(self.unknown_name_value, 5, 1)

        self.color_changes_name_value = QLabel()
        self.layout.addWidget(self.color_changes_name_value, 6, 1)

        self.points_length_name_value = QLabel()
        self.layout.addWidget(self.points_length_name_value, 7, 1)

        self.hoop_name_value = QLabel()
        self.layout.addWidget(self.hoop_name_value, 8, 1)

        self.extends1_name_value = QLabel()
        self.layout.addWidget(self.extends1_name_value, 9, 1)

        self.extends2_name_value = QLabel()
        self.layout.addWidget(self.extends2_name_value, 10, 1)

        self.extends3_name_value = QLabel()
        self.layout.addWidget(self.extends3_name_value, 11, 1)

        self.extends4_name_value = QLabel()
        self.layout.addWidget(self.extends4_name_value, 12, 1)

        self.extends5_name_value = QLabel()
        self.layout.addWidget(self.extends5_name_value, 13, 1)

    def update_values(self, pattern):
        self.hoop_name_value.setText(pattern.hoop_name)
