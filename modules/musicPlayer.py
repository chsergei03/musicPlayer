import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

# главное окно музыкального плеера.
class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()

        # настройка параметров окна:
        WINDOW_WIDTH, WINDOW_HEIGHT = 400, 400
        self.setWindowTitle("music player")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        # настройка кнопок:
        BUTTON_WIDTH, BUTTON_HEIGHT = 400, 50
        self.buttonAddToFilebase = self.getConfiguredButton(0, 0,
                                                            BUTTON_WIDTH, BUTTON_HEIGHT,
                                                            "add to filebase")

    # возвращает кнопку, левый верхний угол которой расположен
    # на x пунктов правее и на y пунктов ниже левого верхнего
    # угла экрана; с шириной width, высотой height, подписью text.
    def getConfiguredButton(self, x, y, width, height, text):
        button = QPushButton(self)
        button.setGeometry(x, y, width, height)
        button.setText(text)

        return button

# запускает приложение музыкального плеера.
def runApplication():
    musicPlayerApplication = QApplication(sys.argv)

    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())