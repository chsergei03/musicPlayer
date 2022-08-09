import sys
import easygui
import modules.filebase as filebase

from PyQt6.QtWidgets import QApplication, QMainWindow, \
                            QPushButton, QTableWidget, QTableWidgetItem

# главное окно музыкального плеера.
class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()

        # настройка параметров окна:
        WINDOW_X, WINDOW_Y = 0, 0
        WINDOW_WIDTH, WINDOW_HEIGHT = 400, 400
        self.setWindowTitle("music player")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        # настройка кнопок:
        BUTTON_WIDTH, BUTTON_HEIGHT = 400, 50

        BUTTON_ADDTOFILEBASE_X, BUTTON_ADDTOFILEBASE_Y = 0, 0
        self.buttonAddToFilebase = self.getConfiguredButton(BUTTON_ADDTOFILEBASE_X,
                                                            BUTTON_ADDTOFILEBASE_Y,
                                                            BUTTON_WIDTH, BUTTON_HEIGHT,
                                                            "add to filebase")

        # настройка табличного списка музыкальных композиций:
        TABLELIST_X, TABLELIST_Y = 0, 60
        TABLELIST_WIDTH, TABLELIST_HEIGHT = 400, 300
        self.tableList = QTableWidget(self)
        self.tableList.setGeometry(TABLELIST_X, TABLELIST_Y, TABLELIST_WIDTH, TABLELIST_HEIGHT)
        self.tableList.setColumnCount(2)
        self.tableList.setHorizontalHeaderLabels(["title", "artist"])
        self.loadTracksInFilebaseToTableList()

        # настройка соединений сигналов со слотами:
        self.buttonAddToFilebase.clicked.connect(self.addToFilebase)

    # возвращает кнопку, левый верхний угол которой расположен
    # на x пунктов правее и на y пунктов ниже левого верхнего
    # угла экрана; с шириной width, высотой height, подписью text.
    def getConfiguredButton(self, x, y, width, height, text):
        button = QPushButton(self)
        button.setGeometry(x, y, width, height)
        button.setText(text)

        return button

    # заполняет строку под номером row табличного списка музыкальных композиций
    # информацией из кортежа track, содержащего информацию о вставляемом треке.
    def setRowInTableList(self, row, track):
        TITLE_INDEXINTABLELIST, TITLE_INDEXINFILEBASE = 0, 2
        ARTIST_INDEXINTABLELIST, ARTIST_INDEXINFILEBASE = 1, 4

        self.tableList.setItem(row, TITLE_INDEXINTABLELIST,
                               QTableWidgetItem(track[TITLE_INDEXINFILEBASE]))

        self.tableList.setItem(row, ARTIST_INDEXINTABLELIST,
                               QTableWidgetItem(track[ARTIST_INDEXINFILEBASE]))

    # загружает в табличный список плеера музыкальные композиции
    # из базы данных приложения
    def loadTracksInFilebaseToTableList(self):
        tracksInFilebaseList = filebase.getAllRowsOfFilebaseList()

        self.tableList.setRowCount(len(tracksInFilebaseList))

        currentRow = 0
        for track in tracksInFilebaseList:
            self.setRowInTableList(currentRow, track)

            currentRow += 1

    # увеличивает количество строк в табличном списке музыкальных
    # композиций на 1.
    def incTableListRowCount(self):
        self.tableList.setRowCount(self.tableList.rowCount() + 1)

    # добавляет строку в табличный список музыкальных композиций.
    def appendRowToTableList(self):
        self.incTableListRowCount()
        lastRowInFilebase, lastRowInFilebaseIndex = filebase.getLastRowInFilebaseAndItsIndex()
        self.setRowInTableList(lastRowInFilebaseIndex, lastRowInFilebase)

    # добавляет файл музыкальной композиции в базу данных плеера.
    def addToFilebase(self):
        filesToAddPaths = easygui.fileopenbox(filetypes="*.mp3, *.flac", multiple=True)

        for fileToAddPath in filesToAddPaths:
            filebase.addRowToFilebase(fileToAddPath)
            self.appendRowToTableList()

# запускает приложение музыкального плеера.
def runApplication():
    musicPlayerApplication = QApplication(sys.argv)

    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())