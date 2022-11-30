import modules.database as db

import sys
import enum

import os
from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

import easygui

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import \
    QApplication, QMainWindow, \
    QLabel, \
    QMenu, QAbstractItemView, \
    QWidgetAction, QPushButton, \
    QTableWidget, QTableWidgetItem, \
    QListWidget, QListWidgetItem

PLAYBACK_START_POS = 0.115


class playbackControlConstants(enum.IntEnum):
    TRACK_POS_WHERE_THERE_IS_NO_PLAYBACK = -1
    MUSIC_END = pygame.USEREVENT + 1
    PLAY_PREVIOUS_TRACK = -1
    PLAY_NEXT_TRACK = 1


# средство воспроизведения треков.
class playbackTool:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(
            playbackControlConstants.MUSIC_END)

    @staticmethod
    def isBusy():
        """
        возвращает значение 'истина', если какой-либо
        трек в данный момент проигрывается, в противном
        случае - 'ложь'.
        """

        return pygame.mixer.music.get_busy()

    def isPlaybackPaused(self):
        """
        возвращает значение 'истина', если какой-либо
        трек проигрывается или поставлен на паузу, в
        противном случае - 'ложь'.
        """

        return not self.isBusy() and self.pos() != \
               playbackControlConstants.TRACK_POS_WHERE_THERE_IS_NO_PLAYBACK

    @staticmethod
    def load(filepath):
        """
        загружает трек в плеер pygame.
        :param filepath: строка, содержащая
        путь к файлу трека.
        """

        pygame.mixer.music.load(filepath)

    @staticmethod
    def loadToQueue(filepath):
        """
        загружает трек в очередь плеера pygame.
        :param filepath: строка, содержащая
        путь к файлу трека.
        """

        pygame.mixer.music.queue(filepath)

    @staticmethod
    def startPlayback():
        """
        запускает проигрывание плеером pygame
        трека, находящегося в очереди.
        """

        pygame.mixer.music.play(start=PLAYBACK_START_POS)

    @staticmethod
    def resumePlayback():
        """
        возобновляет проигрывание плеером pygame
        трека, находящегося в очереди.
        """

        pygame.mixer.music.unpause()

    @staticmethod
    def pausePlayback():
        """
        ставит на паузу проигрывание плеером pygame
        трека, находящегося в очереди.
        """

        pygame.mixer.music.pause()

    @staticmethod
    def stopPlayback():
        """
        останавливает проигрывание плеером pygame
        трека, находящегося в очереди.
        """

        pygame.mixer.music.stop()

    @staticmethod
    def rewindPlayback():
        """
        перезапускает проигрывание плеером pygame
        трека, находящегося в очереди.
        """

        pygame.mixer.music.rewind()

    @staticmethod
    def pos():
        """
        возвращает позицию в проигрываемом плеером
        pygame треке.
        """

        return pygame.mixer.music.get_pos()


class geometryConstants(enum.IntEnum):
    WINDOW_X, WINDOW_Y = 0, 0
    WINDOW_WIDTH, WINDOW_HEIGHT = 1372, 400

    BUTTON_WIDTH, BUTTON_HEIGHT = 217, 50

    BUTTON_ADDTODATABASE_X, BUTTON_ADDTODATABASE_Y = 10, 0
    BUTTON_REWINDTRACK_X, BUTTON_REWINDTRACK_Y = 237, 0
    BUTTON_PLAYTRACK_X, BUTTON_PLAYTRACK_Y = 464, 0
    BUTTON_PAUSETRACK_X, BUTTON_PAUSETRACK_Y = 691, 0
    BUTTON_PREVTRACK_X, BUTTON_PREVTRACK_Y = 1145, 0
    BUTTON_NEXTTRACK_X, BUTTON_NEXTTRACK_Y = 1145, 60

    TABLELIST_X, TABLELIST_Y = 10, 60
    TABLELIST_WIDTH, TABLELIST_HEIGHT = 217, 300
    TABLELIST_CELLSAREA_WIDTH, TABLELIST_CELLSAREA_HEIGHT = 207, 280
    TABLELIST_NUMBERSCOLUMN_WIDTH = 20
    TABLELIST_CELL_HEIGHT = 25

    ALBUMARTISTSLIST_X, ALBUMARTISTSLIST_Y = 237, 60
    ALBUMARTISTSLIST_WIDTH, ALBUMARTISTSLIST_HEIGHT = 217, 300

    ALBUMSOFARTISTLIST_X, ALBUMSOFARTISTLIST_Y = 464, 60
    ALBUMSOFARTISTLIST_WIDTH, ALBUMSOFARTISTLIST_HEIGHT = 217, 300

    TRACKSOFALBUMLIST_X, TRACKSOFALBUMLIST_Y = 691, 60
    TRACKSOFALBUMLIST_WIDTH, TRACKSOFALBUMLIST_HEIGHT = 217, 300

    TRACKONPLAYBACKALBUMARTISTLABEL_X, TRACKONPLAYBACKALBUMARTISTLABEL_Y = 918, 20
    TRACKONPLAYBACKALBUMARTISTLABEL_WIDTH, TRACKONPLAYBACKALBUMARTISTLABEL_HEIGHT = 217, 90

    TRACKONPLAYBACKTITLELABEL_X, TRACKONPLAYBACKTITLELABEL_Y = 918, 40
    TRACKONPLAYBACKTITLELABEL_WIDTH, TRACKONPLAYBACKTITLELABEL_HEIGHT = 217, 90


class tableListConstants(enum.IntEnum):
    TITLE_INDEX = 0
    ARTIST_INDEX = 1
    N_COLUMNS = 2


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
            geometryConstants.BUTTON_ADDTODATABASE_X,
            geometryConstants.BUTTON_ADDTODATABASE_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "add")

        self.buttonRewindTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_REWINDTRACK_X,
            geometryConstants.BUTTON_REWINDTRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "rewind")

        self.buttonPlayTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_PLAYTRACK_X,
            geometryConstants.BUTTON_PLAYTRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "play")

        self.buttonPauseTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_PAUSETRACK_X,
            geometryConstants.BUTTON_PAUSETRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "pause")

        self.buttonPreviousTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_PREVTRACK_X,
            geometryConstants.BUTTON_PREVTRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "prev track")

        self.buttonNextTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_NEXTTRACK_X,
            geometryConstants.BUTTON_NEXTTRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            "next track")

        # настройка параметров табличного UI-списка
        # музыкальных композиций:
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

        # настройка контекстного меню табличного
        # UI-списка музыкальных композиций:
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
            geometryConstants.ALBUMARTISTSLIST_HEIGHT,
            None,
            QtCore.Qt.SortOrder.AscendingOrder)

        self.setItemsOfListWidget(self.albumArtistsList,
                                  db.getListOfAllAlbumArtists())

        # настройка UI-списка альбомов исполнителя:
        self.albumsOfArtistList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.ALBUMSOFARTISTLIST_X,
            geometryConstants.ALBUMSOFARTISTLIST_Y,
            geometryConstants.ALBUMSOFARTISTLIST_WIDTH,
            geometryConstants.ALBUMSOFARTISTLIST_HEIGHT,
            QtCore.Qt.SortOrder.AscendingOrder)

        # настройка UI-списка треков альбома:
        self.tracksOfAlbumList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.TRACKSOFALBUMLIST_X,
            geometryConstants.TRACKSOFALBUMLIST_Y,
            geometryConstants.TRACKSOFALBUMLIST_WIDTH,
            geometryConstants.TRACKSOFALBUMLIST_HEIGHT,
            QtCore.Qt.SortOrder.AscendingOrder)

        # настройка надписей:
        self.trackOnPlaybackAlbumArtistLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_X,
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_Y,
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_WIDTH,
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_HEIGHT)

        self.trackOnPlaybackTitleLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.TRACKONPLAYBACKTITLELABEL_X,
            geometryConstants.TRACKONPLAYBACKTITLELABEL_Y,
            geometryConstants.TRACKONPLAYBACKTITLELABEL_WIDTH,
            geometryConstants.TRACKONPLAYBACKTITLELABEL_HEIGHT)

        # настройка средства проигрывания треков:
        self.player = playbackTool()

        # инициализация атрибутов, связанных с
        # средством проигрывания трека:
        self.allTracksInDatabaseList = db.getListOfAllRowsForTableList()
        self.playbackQueue = self.allTracksInDatabaseList

        # инициализация атрибутов, связанных с выбором пользователя:
        self.trackOnPlaybackTitle = ""
        self.trackOnPlaybackAlbumArtist = ""
        self.trackOnPlaybackIndex = 0

        self.choosedAlbumArtistName = ""
        self.choosedAlbum = ""

        self.playbackDirection = playbackControlConstants.PLAY_NEXT_TRACK

        # настройка соединений сигналов со слотами:
        self.connectSignalWithSlot(
            self.buttonAddTracks.clicked,
            self.addTracks)

        self.connectSignalWithSlot(
            self.tableListContextMenuActionDeleteTrack.triggered,
            self.deleteTrack)

        self.connectSignalWithSlot(
            self.tableList.itemDoubleClicked,
            self.playTrackByDoubleClickOnTitle)

        self.connectSignalWithSlot(
            self.buttonPlayTrack.clicked,
            self.unpauseTrack)

        self.connectSignalWithSlot(
            self.buttonPauseTrack.clicked,
            self.pauseTrack)

        self.connectSignalWithSlot(
            self.buttonRewindTrack.clicked,
            self.rewindTrack)

        self.connectSignalWithSlot(
            self.buttonPreviousTrack.clicked,
            self.playPreviousTrack)

        self.connectSignalWithSlot(
            self.buttonNextTrack.clicked,
            self.playNextTrack)

        self.connectSignalWithSlot(
            self.buttonPlayTrack.clicked,
            self.playTrack)

        self.connectSignalWithSlot(
            self.tracksOfAlbumList.itemDoubleClicked,
            self.playTrackByDoubleClickOnTitle)

        self.connectSignalWithSlot(
            self.albumArtistsList.itemDoubleClicked,
            self.loadAlbumsOfArtist)

        self.connectSignalWithSlot(
            self.albumsOfArtistList.itemDoubleClicked,
            self.loadTracksOfAlbum)

    @staticmethod
    def getConfiguredWidget(widget,
                            x, y, width, height,
                            text=None,
                            sortOrder=None):
        """
        возвращает настроенный элемент интерфейса.
        :param widget: инструкция объявления объекта
        класса-наследника класса QWidget;
        :param x: положение элемента интерфейса по
        горизонтали относительно левого верхнего угла
        (показывает, на сколько пунктов элемент
        интерфейса расположен правее левого верхнего
        угла);
        :param y: положение элемента интерфейса по
        вертикали относительно левого верхнего угла
        (показывает, на сколько пунктов элемент
        интерфейса расположен ниже левого верхнего
        угла);
        :param width: ширина элемента интерфейса;
        :param height: высота элемента интерфейса;
        :param text: подпись на элементе интерфейса
        (необязательный параметр).
        :param sortOrder: порядок сортировки элементов
        (объект класса-наследника класса QtCore.Qt.SortOrder)
        [необазятельный параметр, используется в вызове,
        когда элемент интерфейса обладает элементами).
        :return: настроенный элемент интерфейса
        (объект класса-наследника класса QWidget).
        """

        widget.setGeometry(x, y, width, height)

        if isinstance(text, QtCore.Qt.SortOrder):
            text, sortOrder = sortOrder, text

        if text is not None:
            widget.setText(text)

        if sortOrder is not None:
            widget.sortItems(sortOrder)

        return widget

    @staticmethod
    def getConfiguredContextMenu(contextMenu,
                                 listOfActions):
        """
        возвращает настроенное контекстное меню.
        :param contextMenu:
        :param listOfActions:
        :return: настроенное контекстное меню
        """

        for action in listOfActions:
            contextMenu.addAction(action)

        return contextMenu

    @staticmethod
    def connectSignalWithSlot(signal, slot):
        """
        устанавливает связь между сигналом и
        слотом.
        :param signal: сигнал;
        :param slot: слот.
        """

        signal.connect(slot)

    def setRowInTableList(self,
                          rowIndex,
                          trackInfoList):
        """
        заполняет строку табличного UI-списка
        музыкальных композиций информацией о
        треке.
        :param rowIndex: индекс строки табличного
        UI-списка музыкальных композиций, которая
        будет заполнена информацией о треке;
        :param trackInfoList: кортеж с .
        """

        self.tableList.setItem(rowIndex, tableListConstants.TITLE_INDEX,
                               QTableWidgetItem(
                                   trackInfoList[tableListConstants.TITLE_INDEX]))

        self.tableList.setItem(rowIndex, tableListConstants.ARTIST_INDEX,
                               QTableWidgetItem(
                                   trackInfoList[tableListConstants.ARTIST_INDEX]))

    def loadTracksFromMusicTracksTableToTableList(self):
        """
        загружает в табличный UI-список плеера
        треки из таблицы музыкальных композиций,
        находящейся в базы данных приложения.
        """

        listOfAllRowsOfMusicTracksTable = \
            db.getListOfAllRowsForTableList()

        self.tableList.setRowCount(len(listOfAllRowsOfMusicTracksTable))

        currentRow = 0
        for track in listOfAllRowsOfMusicTracksTable:
            self.setRowInTableList(currentRow, track)

            currentRow += 1

    @staticmethod
    def addItemToListWidget(listWidget, itemText):
        """
        добавляет элемент в UI-список.
        :param listWidget: UI-список, в который
        добавляется элемент;
        :param itemText: подпись добавляемого в
        UI-список элемента.
        """

        item = QListWidgetItem()
        item.setText(itemText)

        listWidget.addItem(item)

    def setItemsOfListWidget(self, listWidget,
                             itemsNamesList):
        """
        заполняет UI-список элементами из списка
        c их названиями.
        :param listWidget: UI-список, который
        необходимо заполнить (объект класса
        QListWidget).
        :param itemsNamesList: список со строками,
        хранящими в себе названия элементов UI-списка.
        """

        listWidget.clear()

        for itemName in itemsNamesList:
            self.addItemToListWidget(listWidget, itemName)

    def loadAlbumsOfArtist(self, item):
        """
        загружает в UI-список альбомов
        исполнителя из таблицы музыкальных
        композиций, находящейся в базе
        данных приложения, по двойному
        клику на соответствующую выбранному
        артисту строку в списке  исполнителей
        альбомов.
        :param item: строка UI-списка исполнителей
        альбомов (объект класса QListWidgetItem),
        по которой пользователь совершил
        двойной клик.
        """

        self.choosedAlbumArtistName = item.text()

        self.setItemsOfListWidget(self.albumsOfArtistList,
                                  db.getListOfAlbumsOfArtist(
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
                                  db.getListsWithInfoAboutTracksOfAlbum(
                                      self.choosedAlbumArtistName,
                                      item.text())[0])

        self.choosedAlbum = item.text()

    def updateTableListRowCount(self, mode):
        """
        обновляет количество строк в табличном
        UI-списке музыкальных композиций в
        зависимости от режима mode; если это
        режим APPEND_ROW, увеличивает количество
        строк в нём на 1, если же это режим
        REMOVE_ROW - уменьшает на 1.
        :param mode: режим обновления табличного
        UI-списка музыкальных композиций
        (целочисленная константа из перечисления
        updateTableListRowCountConstants).
        """
        newRowCount = self.tableList.rowCount() + \
                      (mode == updateTableListRowCountConstants.APPEND_ROW) - \
                      (mode == updateTableListRowCountConstants.REMOVE_ROW)

        self.tableList.setRowCount(newRowCount)

    def addTrackToTableList(self):
        """
        добавляет трек в табличный
        UI-список музыкальных композиций.
        """

        trackToAppendRowIndex = self.tableList.rowCount()

        self.updateTableListRowCount(updateTableListRowCountConstants.APPEND_ROW)

        lastAddedToMusicTracksTableTrackInfoList = \
            db.getLastRow()

        self.setRowInTableList(
            trackToAppendRowIndex,
            lastAddedToMusicTracksTableTrackInfoList)

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
                db.addRow(fileToAddPath)

                self.allTracksInDatabaseList.append(
                    db.getTrackInfoListByPath(fileToAddPath))

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

    def getTrackInfoListByRowIndex(self, rowIndex):
        """
        возвращает кортеж с названием трека и его
        исполнителем по индексу строки в табличном
        UI-списке музыкальных композиций.
        :param rowIndex: индекс строки в табличном
        UI-списке музыкальных композиций.
        :return: список trackInfoList с названием
        трека и его исполнителем.
        """
        trackInfoList = [self.tableList.item(rowIndex,
                                             tableListConstants.TITLE_INDEX).text(),
                         self.tableList.item(rowIndex,
                                             tableListConstants.ARTIST_INDEX).text()]

        return trackInfoList

    def deleteTrack(self):
        """
        удаляет трек из табличного UI-списка
        музыкальных композиций (композиция
        также удаляется из таблицы треков в
        базе данных приложения).
        """

        choosedCellRow = self.tableList.choosedCell.row()
        currentRow = choosedCellRow

        trackInfoList = self.allTracksInDatabaseList[choosedCellRow]
        trackInfoList.pop(-1)

        nRewrites = self.tableList.rowCount() - choosedCellRow - 1
        if nRewrites > 0:
            for i in range(nRewrites):
                self.setRowInTableList(
                    currentRow,
                    self.allTracksInDatabaseList[currentRow + 1])

                currentRow += 1

        self.updateTableListRowCount(updateTableListRowCountConstants.REMOVE_ROW)

        self.allTracksInDatabaseList.pop(choosedCellRow)

        if self.player.isBusy():
            self.player.stopPlayback()

        db.deleteTrack(*trackInfoList)

    def playTrack(self):
        """
        загружает трек в средство проигрывания
        и запускает его воспрозведение.
        """

        if self.player.isPlaybackPaused():
            self.player.resumePlayback()
        else:
            trackInfoList = self.playbackQueue[self.trackOnPlaybackIndex]

            self.trackOnPlaybackTitle, \
            self.trackOnPlaybackAlbumArtist, \
            filepath = trackInfoList

            self.trackOnPlaybackTitleLabel.setText(
                self.trackOnPlaybackTitle)

            self.trackOnPlaybackAlbumArtistLabel.setText(
                self.trackOnPlaybackAlbumArtist)

            self.player.load(filepath)
            self.player.startPlayback()

            self.playbackToolEventFilter()

    def playbackToolEventFilter(self):
        """
        обрабатывает события средства
        воспроизведения треков (объекта
        player класса playbackTool).
        """

        isPlaybackRunning = True
        while isPlaybackRunning:
            for event in pygame.event.get():
                if event.type == playbackControlConstants.MUSIC_END:
                    if self.playbackDirection == \
                            playbackControlConstants.PLAY_NEXT_TRACK and \
                            len(self.playbackQueue) - self.trackOnPlaybackIndex > 1:
                        self.trackOnPlaybackIndex += 1

                        self.playTrack()
                    elif self.playbackDirection == \
                            playbackControlConstants.PLAY_PREVIOUS_TRACK:
                        if self.trackOnPlaybackIndex == 0:
                            self.rewindTrack()
                        else:
                            self.trackOnPlaybackIndex -= 1

                        self.playTrack()

                        self.playbackDirection = playbackControlConstants.PLAY_NEXT_TRACK
                    else:
                        isPlaybackRunning = False

                        self.trackOnPlaybackTitleLabel.setText("")
                        self.trackOnPlaybackAlbumArtistLabel.setText("")

    def playTrackByDoubleClickOnTitle(self, item):
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
        класса QListWidgetItem или объект класса
        QTableWidgetItem).
        """

        if isinstance(item, QTableWidgetItem):
            itemRow = item.row()
            self.playbackQueue = self.allTracksInDatabaseList
        elif isinstance(item, QListWidgetItem):
            itemRow = self.tracksOfAlbumList.row(item)
            self.playbackQueue = db.getListWithInfoAboutTracksOfAlbum(
                self.choosedAlbumArtistName,
                self.choosedAlbum)

        choosedTrackTitle = self.playbackQueue[itemRow][0]

        if choosedTrackTitle != self.trackOnPlaybackTitle:
            self.trackOnPlaybackIndex = itemRow

        self.playTrack()

    def unpauseTrack(self):
        """
        возобновляет проигрывание поставленного
        на паузу трека.
        """

        if self.player.isBusy():
            self.player.resumePlayback()

    def pauseTrack(self):
        """
        ставит проигрываемый трек на паузу.
        """

        if self.player.isBusy():
            self.player.pausePlayback()

    def rewindTrack(self):
        """
        перематывает проигрываемый трек
        или трек, поставленный на паузу,
        на его начало.
        """

        self.player.rewindPlayback()

    def stopTrack(self):
        """
        останавливает воспроизведение треков.
        """

        self.player.stopPlayback()

    def changeTrack(self, changeTrackFlagValue):
        """
        переключает воспроизведение треков на
        предыдущий или следующий в очереди трек
        в зависимости от значения переменной
        changeTrackFlagValue.
        :param changeTrackFlagValue: переменная,
        определяющая переключение воспроизведения
        треков на предыдущий или следующий в очереди
        трек.
        """

        self.trackOnPlaybackIndex += changeTrackFlagValue

        if self.player.isBusy():
            self.stopTrack()

    def playPreviousTrack(self):
        """
        запускает проигрывание трека,
        идущего в списке воспроизведения
        за проигрываемым.
        """

        if self.trackOnPlaybackIndex > 0:
            self.playbackDirection = playbackControlConstants.PLAY_PREVIOUS_TRACK
            self.stopTrack()
        else:
            self.rewindTrack()

    def playNextTrack(self):
        """
        запускает проигрывание трека,
        идущего в очереди воспроизведения
        за проигрываемым (если он есть).
        """

        if len(self.playbackQueue) - self.trackOnPlaybackIndex > 1:
            self.playbackDirection = playbackControlConstants.PLAY_NEXT_TRACK
            self.stopTrack()


def runApplication():
    """
    запускает приложение музыкального плеера.
    """

    musicPlayerApplication = QApplication(sys.argv)

    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())