import modules.filebase as filebase

import sys
import enum

import easygui
import pygame

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6.QtGui import QMouseEvent

from PyQt6.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QTableWidget, QTableWidgetItem, QMenu, QWidgetAction, \
    QAbstractItemView

class geometryConstants(enum.IntEnum):
    WINDOW_X, WINDOW_Y = 0, 0
    WINDOW_WIDTH, WINDOW_HEIGHT = 450, 400

    BUTTON_WIDTH, BUTTON_HEIGHT = 217, 50

    BUTTON_ADDTOFILEBASE_X, BUTTON_ADDTOFILEBASE_Y = 0, 0
    BUTTON_PAUSETRACK_X, BUTTON_PAUSETRACK_Y = 227, 0

    TABLELIST_X, TABLELIST_Y = 0, 60
    TABLELIST_WIDTH, TABLELIST_HEIGHT = 217, 300
    TABLELIST_NUMBERSCOLUMN_WIDTH = 10
    TABLELIST_CELL_HEIGHT = 20

class tableListConstants(enum.IntEnum):
    TITLE_INDEXINTABLELIST, TITLE_INDEXINFILEBASE = 0, 2
    ARTIST_INDEXINTABLELIST, ARTIST_INDEXINFILEBASE = 1, 4

# главное окно музыкального плеера.
class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()

        # настройка параметров окна:
        self.setWindowTitle("music player")
        self.setGeometry(geometryConstants.WINDOW_X,
                         geometryConstants.WINDOW_Y,
                         geometryConstants.WINDOW_WIDTH,
                         geometryConstants.WINDOW_HEIGHT)

        # настройка кнопок:
        self.buttonAddTracks = self.getConfiguredButton(
            geometryConstants.BUTTON_ADDTOFILEBASE_X,
            geometryConstants.BUTTON_ADDTOFILEBASE_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "add to filebase")

        self.buttonPauseTrack = self.getConfiguredButton(
            geometryConstants.BUTTON_PAUSETRACK_X,
            geometryConstants.BUTTON_PAUSETRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "pause track")

        # настройка параметров списка музыкальных композиций:
        self.tableList = QTableWidget(self)
        self.tableList.setGeometry(geometryConstants.TABLELIST_X,
                                   geometryConstants.TABLELIST_Y,
                                   geometryConstants.TABLELIST_WIDTH,
                                   geometryConstants.TABLELIST_HEIGHT)

        self.tableList.setColumnCount(2)
        self.tableList.setHorizontalHeaderLabels(["title", "artist"])
        self.tableList.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.loadTracksFromMusicTracksTableToTableList()

        # настройка контекстного меню табличного списка музыкальных композиций:
        self.tableListContextMenu = QMenu(self)
        self.tableListContextMenuActionDeleteTrack = QWidgetAction(self)
        self.tableListContextMenuActionDeleteTrack.setText("delete")
        self.tableListContextMenu.addAction(self.tableListContextMenuActionDeleteTrack)

        # настройка плеера:
        pygame.init()
        pygame.mixer.init()
        self.playedTrackPosition = 0

        # настройка соединений сигналов со слотами:
        self.buttonAddTracks.clicked.connect(self.addTracks)
        self.buttonPauseTrack.clicked.connect(self.pauseTrack)
        self.tableListContextMenuActionDeleteTrack.triggered.connect(self.deleteTrack)
        self.tableList.itemDoubleClicked.connect(self.playDoubleClickedTrack)

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

        self.tableList.setItem(row, tableListConstants.TITLE_INDEXINTABLELIST,
                               QTableWidgetItem(
                                   track[tableListConstants.TITLE_INDEXINFILEBASE]))

        self.tableList.setItem(row, tableListConstants.ARTIST_INDEXINTABLELIST,
                               QTableWidgetItem(
                                   track[tableListConstants.ARTIST_INDEXINFILEBASE]))

    def loadTracksFromMusicTracksTableToTableList(self):
        """
        загружает в табличный список плеера треки из
        таблицы музыкальных композиций, находящейся в
        базы данных приложения.
        """

        listOfAllRowsOfMusicTracksTable = filebase.getListOfAllRowsOfMusicTracksTable()

        self.tableList.setRowCount(len(listOfAllRowsOfMusicTracksTable))

        currentRow = 0
        for track in listOfAllRowsOfMusicTracksTable:
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

        lastRowInMusicTracksTable, lastRowInMusicTracksTableIndex = \
            filebase.getLastRowOfMusicTracksTableAndItsIndex()

        self.setRowInTableList(lastRowInMusicTracksTableIndex,
                               lastRowInMusicTracksTable)

    def addTracks(self):
        """
        добавляет трек в таблицу музыкальных композиций,
        находящуюся в базе данных плеера.
        """

        filesToAddPaths = easygui.fileopenbox(filetypes="*.mp3, *.flac",
                                              multiple=True)

        if filesToAddPaths:
            for fileToAddPath in filesToAddPaths:
                filebase.addRowToMusicTracksTable(fileToAddPath)
                self.appendRowToTableList()

    def contextMenuEvent(self, event):
        """
        выводит контекстное меню табличного списка музыкальных
        композиций при нажатии на правую клавишу мыши; если в
        момент клика правой клавишей мыши её курсор находился
        на конкретной ячейке табличного списка, сохряняет в его
        атрибуте rightClickedCell эту ячейку (ячейка является
        объектом класса QTableWidgetItem).
        :param event: событие, после которого контекстное
        меню выводится на экран.
        """
        point = event.pos()

        mousePositionX = int(point.x()) - \
                         geometryConstants.TABLELIST_NUMBERSCOLUMN_WIDTH

        mousePositionY = int(point.y()) - (geometryConstants.TABLELIST_Y +
                                           geometryConstants.TABLELIST_CELL_HEIGHT)

        rightClickedCell = self.tableList.itemAt(mousePositionX, mousePositionY)

        if rightClickedCell is not None:
            self.tableList.choosedCell = rightClickedCell

        self.tableListContextMenu.exec(event.globalPos())

    def getTrackTitleAndArtistTupleFromRowIndex(self, rowIndex):
        """
        возвращает кортеж с названием трека и его исполнителем
        по индексу строки в табличном списке музыкальных композиций.
        :param rowIndex: индексу строки в табличном списке музыкальных
        композиций.
        :return: кортеж с названием трека и его исполнителем.
        """
        return (self.tableList.item(rowIndex,
                                    tableListConstants.TITLE_INDEXINTABLELIST).text(),
                self.tableList.item(rowIndex,
                                    tableListConstants.ARTIST_INDEXINTABLELIST).text())

    def deleteTrack(self):
        """
        удаляет трек из табличного списка музыкальных
        композиций (композиция также удаляется из
        таблицы треков в базе данных приложения).
        """

        listOfAllRowsOfMusicTracksTable = filebase.getListOfAllRowsOfMusicTracksTable()

        currentRowIndex = self.tableList.choosedCell.row()

        choosedCellRowIndex = currentRowIndex

        trackToDeleteTitleAndArtistTuple = self.getTrackTitleAndArtistTupleFromRowIndex(
            choosedCellRowIndex)

        nRewrites = self.tableList.rowCount() - choosedCellRowIndex - 1
        if nRewrites > 0:
            for i in range(nRewrites):
                self.setRowInTableList(currentRowIndex,
                                       listOfAllRowsOfMusicTracksTable[currentRowIndex + 1])

                currentRowIndex += 1

        self.tableList.setRowCount(self.tableList.rowCount() - 1)

        filebase.deleteTrackFromMusicTracksTable(trackToDeleteTitleAndArtistTuple)

    def playDoubleClickedTrack(self, item):
        """
        запускает проигрывание трека по двойному
        клику на связанную с ним ячейку в табличном
        списке музыкальных композиций; если двойной клик
        произошел по треку, который поставлен на паузу,
        возобновляет его проигрывание с момента паузы.
        :param item: ячейка табличного списка музыкальных
        композиций, связанная с конкретным треком, по которой
        пользователь кликнул два раза подряд (объект класса
        QTableWidgetItem).
        """

        trackTitleAndArtistTuple = self.getTrackTitleAndArtistTupleFromRowIndex(
            item.row())

        if pygame.mixer.music.get_pos() == -1 or \
                item != self.playingTrack:
            pygame.mixer.music.load(
                filebase.getTrackPathFromMusicTracksTable(
                    trackTitleAndArtistTuple))

            pygame.mixer.music.play()
        else:
            pygame.mixer.music.unpause()

        self.playingTrack = item

    def pauseTrack(self):
        """
        ставит проигрываемый трек на паузу.
        """

        pygame.mixer.music.pause()

def runApplication():
    """
    запускает приложение музыкального плеера.
    """

    musicPlayerApplication = QApplication(sys.argv)

    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())