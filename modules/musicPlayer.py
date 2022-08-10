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
        self.buttonAddToMusicTracksTable = self.getConfiguredButton(
            BUTTON_ADDTOFILEBASE_X,
            BUTTON_ADDTOFILEBASE_Y,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            "add to filebase")

        # настройка табличного списка музыкальных композиций:
        TABLELIST_X, TABLELIST_Y = 0, 60
        TABLELIST_WIDTH, TABLELIST_HEIGHT = 400, 300
        self.tableList = QTableWidget(self)
        self.tableList.setGeometry(TABLELIST_X, TABLELIST_Y,
                                   TABLELIST_WIDTH, TABLELIST_HEIGHT)
        self.tableList.setColumnCount(2)
        self.tableList.setHorizontalHeaderLabels(["title", "artist"])
        self.loadTracksFromMusicTracksTableToTableList()

        # настройка соединений сигналов со слотами:
        self.buttonAddToMusicTracksTable.clicked.connect(self.addToMusicTracksTable)

    def getConfiguredButton(self, x, y, width, height, text):
        """
        возвращает настроенную кнопку.
        :param x: положение кнопки по горизонтали относительно
        левого верхнего угла (показывает, на сколько пунктов
        кнопка расположена правее левого верхнего угла);
        :param y: положение кнопки по вертикали относительно
        левого верхнего угла (показывает, на сколько пунктов
        кнопка расположена ниже левого верхнего угла);
        :param width: ширина кнопки;
        :param height: высота кнопки;
        :param text: текст на кнопке.
        :return: кнопка button (объект класса QPushButton).
        """

        button = QPushButton(self)
        button.setGeometry(x, y, width, height)
        button.setText(text)

        return button

    def setRowInTableList(self, row, track):
        """
        заполняет строку табличного списка музыкальных композиций
        информацией о треке.
        :param row: индекс строки табличного списка музыкальных композиций,
        которая будет заполнена информацией о треке;
        :param track: кортеж с данными из контректной строки таблицы
        музыкальных композиций, находящейся в базе данных приложения.
        """

        TITLE_INDEXINTABLELIST, TITLE_INDEXINFILEBASE = 0, 2
        ARTIST_INDEXINTABLELIST, ARTIST_INDEXINFILEBASE = 1, 4

        self.tableList.setItem(row, TITLE_INDEXINTABLELIST,
                               QTableWidgetItem(track[TITLE_INDEXINFILEBASE]))

        self.tableList.setItem(row, ARTIST_INDEXINTABLELIST,
                               QTableWidgetItem(track[ARTIST_INDEXINFILEBASE]))

    def loadTracksFromMusicTracksTableToTableList(self):
        """
        загружает в табличный список плеера треки из
        таблицы музыкальных композиций, находящейся в
        базы данных приложения.
        """

        tracksInFilebaseList = filebase.getListOfAllRowsOfMusicTracksTable()

        self.tableList.setRowCount(len(tracksInFilebaseList))

        currentRow = 0
        for track in tracksInFilebaseList:
            self.setRowInTableList(currentRow, track)

            currentRow += 1

    def incTableListRowCount(self):
        """
        увеличивает количество строк в табличном списке
        музыкальных композиций на 1.
        """

        self.tableList.setRowCount(self.tableList.rowCount() + 1)

    def appendRowToTableList(self):
        """
        добавляет строку в табличный список музыкальных
        композиций.
        """

        self.incTableListRowCount()

        lastRowInFilebase, lastRowInFilebaseIndex = \
            filebase.getLastRowOfMusicTracksTableAndItsIndex()

        self.setRowInTableList(lastRowInFilebaseIndex,
                               lastRowInFilebase)

    def addToMusicTracksTable(self):
        """
        добавляет трек в таблицу музыкальных композиций,
        находящуюся в базе данных плеера.
        """

        filesToAddPaths = easygui.fileopenbox(filetypes="*.mp3, *.flac",
                                              multiple=True)

        for fileToAddPath in filesToAddPaths:
            filebase.addRowToMusicTracksTable(fileToAddPath)
            self.appendRowToTableList()

def runApplication():
    """
    запускает приложение музыкального плеера.
    """

    musicPlayerApplication = QApplication(sys.argv)

    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())