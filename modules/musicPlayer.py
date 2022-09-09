import modules.filebase as filebase

import sys
import enum
import easygui

from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, \
    QMenu, QWidgetAction, QAbstractItemView

class geometryConstants(enum.IntEnum):
    WINDOW_X, WINDOW_Y = 0, 0
    WINDOW_WIDTH, WINDOW_HEIGHT = 908, 400

    BUTTON_WIDTH, BUTTON_HEIGHT = 217, 50

    BUTTON_ADDTOFILEBASE_X, BUTTON_ADDTOFILEBASE_Y = 0, 0
    BUTTON_PAUSETRACK_X, BUTTON_PAUSETRACK_Y = 227, 0

    TABLELIST_X, TABLELIST_Y = 0, 60
    TABLELIST_WIDTH, TABLELIST_HEIGHT = 217, 300
    TABLELIST_CELLSAREA_WIDTH, TABLELIST_CELLSAREA_HEIGHT = 207, 280
    TABLELIST_NUMBERSCOLUMN_WIDTH = 20
    TABLELIST_CELL_HEIGHT = 25

    ALBUMARTISTSLIST_X, ALBUMARTISTSLIST_Y = 227, 60
    ALBUMARTISTSLIST_WIDTH, ALBUMARTISTSLIST_HEIGHT = 217, 300

    ALBUMSOFARTISTLIST_X, ALBUMSOFARTISTLIST_Y = 454, 60
    ALBUMSOFARTISTLIST_WIDTH, ALBUMSOFARTISTLIST_HEIGHT = 217, 300

    TRACKSOFALBUMLIST_X, TRACKSOFALBUMLIST_Y = 681, 60
    TRACKSOFALBUMLIST_WIDTH, TRACKSOFALBUMLIST_HEIGHT = 217, 300

class tableListConstants(enum.IntEnum):
    TITLE_INDEX = 0
    ARTIST_INDEX = 1
    N_COLUMNS = 2

class musicPlayerConstants(enum.IntEnum):
    TRACK_POS_WHERE_THERE_IS_NO_PLAYBACK = -1

class updateTableListRowCountConstants(enum.IntEnum):
    APPEND_ROW = 0
    REMOVE_ROW = 1

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
        self.buttonAddTracks = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_ADDTOFILEBASE_X,
            geometryConstants.BUTTON_ADDTOFILEBASE_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "add to filebase")

        self.buttonPauseTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_PAUSETRACK_X,
            geometryConstants.BUTTON_PAUSETRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "pause track")

        # настройка параметров табличного UI-списка музыкальных композиций:
        self.tableList = self.getConfiguredWidget(
            QTableWidget(self),
            geometryConstants.TABLELIST_X,
            geometryConstants.TABLELIST_Y,
            geometryConstants.TABLELIST_WIDTH,
            geometryConstants.TABLELIST_HEIGHT)

        self.tableList.setColumnCount(tableListConstants.N_COLUMNS)
        self.tableList.setHorizontalHeaderLabels(["title", "artist"])
        self.tableList.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.loadTracksFromMusicTracksTableToTableList()

        # настройка контекстного меню табличного UI-списка музыкальных композиций:
        self.tableListContextMenu = QMenu(self)
        self.tableListContextMenuActionDeleteTrack = QWidgetAction(self)
        self.tableListContextMenuActionDeleteTrack.setText("delete")
        self.tableListContextMenu.addAction(
            self.tableListContextMenuActionDeleteTrack)

        # настройка UI-списка исполнителей альбомов:
        self.albumArtistsList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.ALBUMARTISTSLIST_X,
            geometryConstants.ALBUMARTISTSLIST_Y,
            geometryConstants.ALBUMARTISTSLIST_WIDTH,
            geometryConstants.ALBUMARTISTSLIST_HEIGHT)

        self.setItemsOfListWidget(self.albumArtistsList,
                                  filebase.getListOfAllAlbumArtists())

        self.albumArtistsList.sortItems(QtCore.Qt.SortOrder.AscendingOrder)

        # настройка UI-списка альбомов исполнителя:
        self.albumsOfArtistList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.ALBUMSOFARTISTLIST_X,
            geometryConstants.ALBUMSOFARTISTLIST_Y,
            geometryConstants.ALBUMSOFARTISTLIST_WIDTH,
            geometryConstants.ALBUMSOFARTISTLIST_HEIGHT)

        self.albumsOfArtistList.sortItems(QtCore.Qt.SortOrder.AscendingOrder)

        # настройка UI-списка треков альбома:
        self.tracksOfAlbumList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.TRACKSOFALBUMLIST_X,
            geometryConstants.TRACKSOFALBUMLIST_Y,
            geometryConstants.TRACKSOFALBUMLIST_WIDTH,
            geometryConstants.TRACKSOFALBUMLIST_HEIGHT)

        self.albumsOfArtistList.sortItems(QtCore.Qt.SortOrder.AscendingOrder)

        # настройка плеера:
        pygame.init()
        pygame.mixer.init()
        self.trackOnPlaybackPosition = 0
        self.trackOnPlaybackTitle = ""
        self.choosedAlbumArtistName = ""

        # настройка соединений сигналов со слотами:
        self.buttonAddTracks.clicked.connect(self.addTracks)
        self.buttonPauseTrack.clicked.connect(self.pauseTrack)

        self.tableListContextMenuActionDeleteTrack.triggered.connect(
            self.deleteTrack)

        self.tableList.itemDoubleClicked.connect(self.playTrack)

        self.albumArtistsList.itemDoubleClicked.connect(self.loadAlbumsOfArtist)

        self.albumsOfArtistList.itemDoubleClicked.connect(self.loadTracksOfAlbum)

        self.tracksOfAlbumList.itemDoubleClicked.connect(self.playTrack)

    @staticmethod
    def getConfiguredWidget(widget,
                            x, y, width, height, text=None):
        """
        возвращает настроенный элемент интерфейса.
        :param widget: инструкция объявления объекта
        класса-наследника класса QWidget;
        :param x: положение элемента интерфейса по горизонтали
        относительно левого верхнего угла (показывает, на сколько
        пунктов элемент интерфейса расположен правее левого
        верхнего угла);
        :param y: положение элемента интерфейса по вертикали
        относительно левого верхнего угла (показывает, на сколько
        пунктов элемент интерфейса расположен ниже левого верхнего
        угла);
        :param width: ширина элемента интерфейса;
        :param height: высота элемента интерфейса;
        :param text: подпись на элементе интерфейса (необязательный
        параметр).
        :return: настроенный элемент интерфейса (объект класса-наследника
        класса QWidget).
        """

        widget.setGeometry(x, y, width, height)

        if text is not None:
            widget.setText(text)

        return widget

    def setRowInTableList(self, rowIndex, trackInfoTuple):
        """
        заполняет строку табличного UI-списка музыкальных
        композиций информацией о треке.
        :param rowIndex: индекс строки табличного UI-списка
        музыкальных композиций, которая будет заполнена
        информацией о треке;
        :param trackInfoTuple: кортеж с данными из контректной
        строки таблицы музыкальных композиций, находящейся в
        базе данных приложения.
        """

        self.tableList.setItem(rowIndex, tableListConstants.TITLE_INDEX,
                               QTableWidgetItem(
                                   trackInfoTuple[tableListConstants.TITLE_INDEX]))

        self.tableList.setItem(rowIndex, tableListConstants.ARTIST_INDEX,
                               QTableWidgetItem(
                                   trackInfoTuple[tableListConstants.ARTIST_INDEX]))

    def loadTracksFromMusicTracksTableToTableList(self):
        """
        загружает в табличный UI-список плеера треки из
        таблицы музыкальных композиций, находящейся в
        базы данных приложения.
        """

        listOfAllRowsOfMusicTracksTable = \
            filebase.getListOfAllRowsForTableList()

        self.tableList.setRowCount(len(listOfAllRowsOfMusicTracksTable))

        currentRow = 0
        for track in listOfAllRowsOfMusicTracksTable:
            self.setRowInTableList(currentRow, track)

            currentRow += 1

    @staticmethod
    def setItemsOfListWidget(listWidget, itemsNamesList):
        """
        заполняет UI-список элементами из списка c их названиями.
        :param listWidget: UI-список, который необходимо заполнить
        (объект класса QListWidget).
        :param itemsNamesList: список со строками, хранящими
        в себе названия элементов UI-списка.
        """

        listWidget.clear()

        for itemName in itemsNamesList:
            item = QListWidgetItem()
            item.setText(*itemName)

            listWidget.addItem(item)

    def loadAlbumsOfArtist(self, item):
        """
        загружает в UI-список альбомов
        исполнителя альбомы из таблицы
        музыкальных композиций, находящейся
        в базе данных приложения, по двойному
        клику на соответствующую выбранному
        артисту строку в списке исполнителей
        альбомов.
        :param item: строка UI-списка исполнителей
        альбомов (объект класса QListWidgetItem),
        по которой пользователь совершил
        двойной клик.
        """

        self.choosedAlbumArtistName = item.text()

        self.setItemsOfListWidget(self.albumsOfArtistList,
                                  filebase.getListOfAlbumsOfArtist(
                                      self.choosedAlbumArtistName))

    def loadTracksOfAlbum(self, item):
        """
        загружает в UI-список треков
        альбома треки из таблицы музыкальных
        композиций, находящейся в базе
        данных приложения, по двойному
        клику на соответствующую выбранной
        пластинке строку в UI-списке
        альбомов исполнителя.
        :param item: строка UI-списка
        альбомов исполнителя альбомов (объект
        класса QListWidgetItem), по которой
        пользователь совершил двойной клик.
        """

        self.setItemsOfListWidget(self.tracksOfAlbumList,
                                  filebase.getListsWithInfoAboutTracksOfAlbum(
                                      self.choosedAlbumArtistName,
                                      item.text())[0])

    def updateTableListRowCount(self, mode):
        """
        обновляет количество строк в табличном UI-списке
        музыкальных композиций в зависимости от режима
        mode; если это режим APPEND_ROW, увеличивает
        количество строк в нём на 1, если же это режим
        REMOVE_ROW - уменьшает на 1.
        :param mode: режим обновления табличного UI-списка
        музыкальных композиций (целочисленная константа
        из перечисления updateTableListRowCountConstants).
        """
        newRowCount = self.tableList.rowCount() + \
                      (mode == updateTableListRowCountConstants.APPEND_ROW) - \
                      (mode == updateTableListRowCountConstants.REMOVE_ROW)

        self.tableList.setRowCount(newRowCount)

    def addTrackToTableList(self):
        """
        добавляет трек в табличный UI-список музыкальных
        композиций.
        """

        trackToAppendRowIndex = self.tableList.rowCount()

        self.updateTableListRowCount(updateTableListRowCountConstants.APPEND_ROW)

        lastAddedToMusicTracksTableTrackInfoTuple = \
            filebase.getLastRow()

        self.setRowInTableList(
            trackToAppendRowIndex,
            lastAddedToMusicTracksTableTrackInfoTuple)

    def addTracks(self):
        """
        добавляет трек / треки в таблицу музыкальных
        композиций, находящуюся в базе данных плеера.
        """

        filesToAddPaths = easygui.fileopenbox(
            filetypes="*.mp3, *.flac",
            multiple=True)

        if filesToAddPaths:
            for fileToAddPath in filesToAddPaths:
                filebase.addRow(fileToAddPath)
                self.addTrackToTableList()

    def contextMenuEvent(self, event):
        """
        выводит контекстное меню табличного
        UI-списка музыкальных композиций при
        нажатии на правую клавишу мыши; если
        в момент клика правой клавишей мыши
        её курсор находился на конкретной ячейке
        табличного UI-списка, сохряняет в его
        атрибуте choosedCell эту ячейку (ячейка
        является объектом класса QTableWidgetItem).
        :param event: событие, после которого
        контекстное меню выводится на экран.
        """
        point = event.pos()

        mousePositionX = int(point.x()) - \
                         geometryConstants.TABLELIST_NUMBERSCOLUMN_WIDTH

        mousePositionY = int(point.y()) - (geometryConstants.TABLELIST_Y +
                                           geometryConstants.TABLELIST_CELL_HEIGHT)

        if (0 <= mousePositionX <= geometryConstants.TABLELIST_CELLSAREA_WIDTH) and \
                (0 <= mousePositionY <= geometryConstants.TABLELIST_CELLSAREA_HEIGHT):
            rightClickedCell = self.tableList.itemAt(mousePositionX, mousePositionY)

            if rightClickedCell is not None:
                self.tableList.choosedCell = rightClickedCell

            self.tableListContextMenu.exec(event.globalPos())

    def getTrackInfoTupleByRowIndex(self, rowIndex):
        """
        возвращает кортеж с названием трека и его
        исполнителем по индексу строки в табличном
        UI-списке музыкальных композиций.
        :param rowIndex: индексу строки в табличном
        UI-списке музыкальных композиций.
        :return: кортеж trackInfoTuple с названием
        трека и его исполнителем.
        """
        trackInfoTuple = (self.tableList.item(rowIndex,
                                              tableListConstants.TITLE_INDEX).text(),
                          self.tableList.item(rowIndex,
                                              tableListConstants.ARTIST_INDEX).text())

        return trackInfoTuple

    def deleteTrack(self):
        """
        удаляет трек из табличного UI-списка музыкальных
        композиций (композиция также удаляется из
        таблицы треков в базе данных приложения).
        """

        listOfAllRowsOfMusicTracksTable = \
            filebase.getListOfAllRowsForTableList()

        currentRowIndex = self.tableList.choosedCell.row()
        choosedCellRowIndex = currentRowIndex

        trackInfoTuple = self.getTrackInfoTupleByRowIndex(
            choosedCellRowIndex)

        nRewrites = self.tableList.rowCount() - choosedCellRowIndex - 1
        if nRewrites > 0:
            for i in range(nRewrites):
                self.setRowInTableList(
                    currentRowIndex,
                    listOfAllRowsOfMusicTracksTable[currentRowIndex + 1])

                currentRowIndex += 1

        self.updateTableListRowCount(updateTableListRowCountConstants.REMOVE_ROW)
        filebase.deleteRow(trackInfoTuple)

    def playTrack(self, item):
        """
        запускает проигрывание трека по двойному
        клику на связанную с ним строку в UI-списке
        треков альбома конкретного исполнителя (или
        ячейку табличного UI-списка музыкальных
        композиций); если двойной клик произошел по
        треку, который поставлен на паузу, возобновляет
        его проигрывание с момента паузы.
        :param item: строка UI-списка музыкальных
        композиций (или ячейка табличного UI-списка
        музыкальных композиций), по которой пользователь
        совершил двойной клик для проигрывания (объект
        класса QListWidgetItem или объект класса QTableWidgetItem).
        """

        if isinstance(item, QTableWidgetItem):
            trackInfoTuple = self.getTrackInfoTupleByRowIndex(item.row())
        elif isinstance(item, QListWidgetItem):
            trackInfoTuple = (item.text(),
                              self.choosedAlbumArtistName,)

        choosedTrackTitle = trackInfoTuple[0]

        if (pygame.mixer.music.get_pos() ==
            musicPlayerConstants.TRACK_POS_WHERE_THERE_IS_NO_PLAYBACK) or \
                (choosedTrackTitle != self.trackOnPlaybackTitle):
            pygame.mixer.music.load(filebase.getTrackPath(trackInfoTuple))
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.unpause()

        self.trackOnPlaybackTitle = choosedTrackTitle

    @staticmethod
    def pauseTrack():
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