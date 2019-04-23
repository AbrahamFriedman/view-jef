import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from ui.main_window import MainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    if len(app.arguments()) > 1:
        window.openFile(app.arguments()[1])
    else:
        window.resize(QDesktopWidget().availableGeometry().size() * 0.75)
    window.show()
    sys.exit(app.exec_())