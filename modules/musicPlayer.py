import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

# главное окно музыкального плеера.
class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()

        # настройка параметров окна:
        self.setWindowTitle("music player")
        self.setGeometry(0, 0, 400, 400)

# запускает приложение музыкального плеера.
def runApplication():
    musicPlayerApplication = QApplication(sys.argv)

    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())