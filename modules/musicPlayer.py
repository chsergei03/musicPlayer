import modules.database as db
import modules.trackDataExtraction as tde
import modules.trackcmp as tc
import modules.tagsParsing as tp

import sys
import enum

import os
from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

import easygui

from PyQt6 import QtCore
from PyQt6.QtCore import \
    Qt, QEvent, \
    QObject, QTimer, QSize

from PyQt6.QtGui import \
    QMouseEvent, QIcon, \
    QFont, QFontDatabase, \
    QMovie

from PyQt6.QtWidgets import \
    QApplication, QMainWindow, \
    QLabel, \
    QMenu, QAbstractItemView, \
    QWidgetAction, QPushButton, \
    QTableWidget, QTableWidgetItem, \
    QListWidget, QListWidgetItem, \
    QMessageBox

from threading import Thread

import time

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
    WINDOW_WIDTH, WINDOW_HEIGHT = 921, 417

    BUTTON_WIDTH, BUTTON_HEIGHT = 50, 50

    BUTTON_ADDTRACKS_X, BUTTON_ADDTRACKS_Y = 10, 10
    BUTTON_PREVTRACK_X, BUTTON_PREVTRACK_Y = 70, 10
    BUTTON_PLAYPAUSETRACK_X, BUTTON_PLAYPAUSETRACK_Y = 130, 10
    BUTTON_NEXTTRACK_X, BUTTON_NEXTTRACK_Y = 190, 10

    TABLELIST_X, TABLELIST_Y = 10, 100
    TABLELIST_WIDTH, TABLELIST_HEIGHT = 220, 305
    TABLELIST_CELLSAREA_WIDTH, TABLELIST_CELLSAREA_HEIGHT = 220, 280
    TABLELIST_NUMBERSCOLUMN_WIDTH = 0
    TABLELIST_CELL_HEIGHT = 25

    ALBUMARTISTSLIST_X, ALBUMARTISTSLIST_Y = 240, 100
    ALBUMARTISTSLIST_WIDTH, ALBUMARTISTSLIST_HEIGHT = 217, 305

    ALBUMSOFARTISTLIST_X, ALBUMSOFARTISTLIST_Y = 467, 100
    ALBUMSOFARTISTLIST_WIDTH, ALBUMSOFARTISTLIST_HEIGHT = 217, 305

    TRACKSOFALBUMLIST_X, TRACKSOFALBUMLIST_Y = 694, 100
    TRACKSOFALBUMLIST_WIDTH, TRACKSOFALBUMLIST_HEIGHT = 217, 305

    TRACKONPLAYBACKALBUMARTISTLABEL_X, TRACKONPLAYBACKALBUMARTISTLABEL_Y = 250, 15
    TRACKONPLAYBACKALBUMARTISTLABEL_WIDTH, TRACKONPLAYBACKALBUMARTISTLABEL_HEIGHT = 500, 20

    TRACKONPLAYBACKTITLELABEL_X, TRACKONPLAYBACKTITLELABEL_Y = 250, 35
    TRACKONPLAYBACKTITLELABEL_WIDTH, TRACKONPLAYBACKTITLELABEL_HEIGHT = 500, 20

    CURRENTTIMELABEL_X, CURRENTTIMELABEL_Y = 250, 55
    CURRENTTIMELABEL_WIDTH, CURRENTTIMELABEL_HEIGHT = 40, 20

    ALLTRACKSLABEL_X, ALLTRACKSLABEL_Y = 10, 75
    ALLTRACKSLABEL_WIDTH, ALLTRACKSLABEL_HEIGHT = 220, 20

    ALLALBUMARTISTSLABEL_X, ALLALBUMARTISTSLABEL_Y = 240, 75
    ALLALBUMARTISTSLABEL_WIDTH, ALLALBUMARTISTSLABEL_HEIGHT = 220, 20

    ALLALBUMSOFARTISTLABEL_X, ALLALBUMSOFARTISTLABEL_Y = 467, 75
    ALLALBUMSOFARTISTLABEL_WIDTH, ALLALBUMSOFARTISTLABEL_HEIGHT = 220, 20

    TRACKSOFALBUMLABEL_X, TRACKSOFALBUMLABEL_Y = 694, 75
    TRACKSOFALBUMLABEL_WIDTH, TRACKSOFALBUMLABEL_HEIGHT = 220, 20

    ICON_SIZE = 25


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

        # настройка иконок:
        self.appIcon = QIcon("data/resources/icons/app.png")
        self.addIcon = QIcon("data/resources/icons/plus.png")
        self.playIcon = QIcon("data/resources/icons/play.png")
        self.pauseIcon = QIcon("data/resources/icons/pause.png")
        self.prevIcon = QIcon("data/resources/icons/prev.png")
        self.nextIcon = QIcon("data/resources/icons/next.png")

        # настройка параметров окна:
        self.setWindowTitle("music player")
        self.move(geometryConstants.WINDOW_X,
                  geometryConstants.WINDOW_Y)

        self.setFixedSize(geometryConstants.WINDOW_WIDTH,
                          geometryConstants.WINDOW_HEIGHT)

        self.setWindowIcon(self.appIcon)

        # настройка шрифта:
        QFontDatabase.addApplicationFont("data/resources/fonts/golos.ttf")
        self.font = QFont('golos', 10)
        self.fontForTableList = QFont('golos', 9)

        # настройка кнопок:
        self.buttonStyleSheet = \
            """
            QPushButton{
                background-color: rgb(255, 255, 255);
                border-style:outline;
                border-radius:25px;
            }
            
            QPushButton:hover:enabled{
                background-color: rgb(220, 220, 220);
            }
            
            QPushButton:hover:pressed{
                background-color: rgb(190, 190, 190);
            }
            """

        self.buttonAddTracks = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_ADDTRACKS_X,
            geometryConstants.BUTTON_ADDTRACKS_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            self.addIcon)
        self.buttonAddTracks.setIconSize(QSize(
            geometryConstants.ICON_SIZE,
            geometryConstants.ICON_SIZE))
        self.buttonAddTracks.setStyleSheet(self.buttonStyleSheet)

        self.buttonPlayPauseTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_PLAYPAUSETRACK_X,
            geometryConstants.BUTTON_PLAYPAUSETRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            self.playIcon)
        self.buttonPlayPauseTrack.setIconSize(QSize(
            geometryConstants.ICON_SIZE,
            geometryConstants.ICON_SIZE))
        self.buttonPlayPauseTrack.setStyleSheet(self.buttonStyleSheet)

        self.buttonPreviousTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_PREVTRACK_X,
            geometryConstants.BUTTON_PREVTRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            self.prevIcon)
        self.buttonPreviousTrack.setIconSize(QSize(
            geometryConstants.ICON_SIZE,
            geometryConstants.ICON_SIZE))
        self.buttonPreviousTrack.setStyleSheet(self.buttonStyleSheet)

        self.buttonNextTrack = self.getConfiguredWidget(
            QPushButton(self),
            geometryConstants.BUTTON_NEXTTRACK_X,
            geometryConstants.BUTTON_NEXTTRACK_Y,
            geometryConstants.BUTTON_WIDTH,
            geometryConstants.BUTTON_HEIGHT,
            self.nextIcon)
        self.buttonNextTrack.setIconSize(QSize(
            geometryConstants.ICON_SIZE,
            geometryConstants.ICON_SIZE))
        self.buttonNextTrack.setStyleSheet(self.buttonStyleSheet)

        # настройка параметров табличного UI-списка
        # музыкальных композиций:
        self.tableListStyleSheet = \
            """
            QTableWidget{
                background-color:white;
                gridline-color:gray;
                border:1px solid gray;
            }
            
            QTableWidget::item{
                background-color:white;
                color:black;
                border-style:outset;
            }
            
            QTableWidget::item:hover:enabled{
                background-color: rgb(220, 220, 220);
            }
            
            QTableWidget::item:hover:pressed{
                background-color: rgb(190, 190, 190);
            }
            
            QTableWidget::item:selected:!active{
                background-color: rgb(190, 190, 190);
            }
            
            QTableWidget::item:selected{
                background-color: rgb(220, 220, 220);
            }
            
            QHeaderView{
                background-color:white;
                border-style:outset;
            }
            
            QHeaderView::section{
                background-color:white;
            }
            
            QHeaderView::section:hover:enabled{
                background-color:rgb(220, 220, 220);
            }
            
            QHeaderView::section:hover:pressed{
                background-color:rgb(190, 190, 190);
            }
            
            QHeaderView::section:selected:!active{
                background-color: rgb(190, 190, 190);
            }
            
            QHeaderView::section:selected{
                background-color: rgb(220, 220, 220);
            }
            """

        self.tableList = self.getConfiguredWidget(
            QTableWidget(self),
            geometryConstants.TABLELIST_X,
            geometryConstants.TABLELIST_Y,
            geometryConstants.TABLELIST_WIDTH,
            geometryConstants.TABLELIST_HEIGHT)
        self.tableList.setStyleSheet(self.tableListStyleSheet)

        self.tableList.setColumnCount(tableListConstants.N_COLUMNS)
        self.tableList.setHorizontalHeaderLabels(["Трек", "Исполнитель"])
        self.tableList.horizontalHeaderItem(
            tableListConstants.TITLE_INDEX).setFont(self.fontForTableList)
        self.tableList.horizontalHeaderItem(
            tableListConstants.ARTIST_INDEX).setFont(self.fontForTableList)
        self.tableList.verticalHeader().setVisible(False)
        self.tableList.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.tableList.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.loadTracksFromMusicTracksTableToTableList()

        # настройка контекстного меню табличного
        # UI-списка музыкальных композиций:

        self.contextMenuStyleSheet = \
            """
            QMenu{
                background-color:white;
                color:black;
                border:1px solid black;
            }
            
            QMenu::item:hover:enabled{
                background-color: rgb(220, 220, 220);
            }
            
            QMenu::item:hover:pressed{
                background-color: rgb(190, 190, 190);
            }
            
            QMenu::item:selected:!active{
                background-color: rgb(190, 190, 190);
            }
            
            QMenu::item:selected{
                background-color: rgb(220, 220, 220);
            }
            """

        self.tableListContextMenu = QMenu(self)
        self.tableListContextMenu.setStyleSheet(self.contextMenuStyleSheet)

        self.tableListContextMenuActionDeleteTrack = QWidgetAction(self)
        self.tableListContextMenuActionDeleteTrack.setText("delete")
        self.tableListContextMenuActionDeleteTrack.setFont(self.font)
        self.tableListContextMenu.addAction(
            self.tableListContextMenuActionDeleteTrack)

        self.listWidgetStyleSheet = \
            """
            QListWidget{
                border:1px solid gray;
            }
            
            QListWidget::item{
                background-color:white;
                color:black;
                border-style:outset;
            }

            QListWidget::item:hover:enabled{
                background-color: rgb(220, 220, 220);
            }
            
            QListWidget::item:hover:pressed{
                background-color: rgb(190, 190, 190);
            }
            
            QListWidget::item:selected:!active{
                background-color: rgb(190, 190, 190);
            }
            
            QListWidget::item:selected{
                background-color: rgb(220, 220, 220);
            }
            """

        # настройка UI-списка исполнителей альбомов:
        self.albumArtistsList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.ALBUMARTISTSLIST_X,
            geometryConstants.ALBUMARTISTSLIST_Y,
            geometryConstants.ALBUMARTISTSLIST_WIDTH,
            geometryConstants.ALBUMARTISTSLIST_HEIGHT,
            QtCore.Qt.SortOrder.AscendingOrder)
        self.albumArtistsList.setStyleSheet(self.listWidgetStyleSheet)
        self.albumArtistsList.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        self.loadAlbumArtists()

        # настройка UI-списка альбомов исполнителя:
        self.albumsOfArtistList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.ALBUMSOFARTISTLIST_X,
            geometryConstants.ALBUMSOFARTISTLIST_Y,
            geometryConstants.ALBUMSOFARTISTLIST_WIDTH,
            geometryConstants.ALBUMSOFARTISTLIST_HEIGHT,
            QtCore.Qt.SortOrder.AscendingOrder)
        self.albumsOfArtistList.setStyleSheet(self.listWidgetStyleSheet)
        self.albumsOfArtistList.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        # настройка UI-списка треков альбома:
        self.tracksOfAlbumList = self.getConfiguredWidget(
            QListWidget(self),
            geometryConstants.TRACKSOFALBUMLIST_X,
            geometryConstants.TRACKSOFALBUMLIST_Y,
            geometryConstants.TRACKSOFALBUMLIST_WIDTH,
            geometryConstants.TRACKSOFALBUMLIST_HEIGHT,
            QtCore.Qt.SortOrder.AscendingOrder)
        self.tracksOfAlbumList.setStyleSheet(self.listWidgetStyleSheet)
        self.tracksOfAlbumList.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        # настройка надписей:
        self.trackOnPlaybackAlbumArtistLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_X,
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_Y,
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_WIDTH,
            geometryConstants.TRACKONPLAYBACKALBUMARTISTLABEL_HEIGHT)
        self.trackOnPlaybackAlbumArtistLabel.setFont(self.font)

        self.trackOnPlaybackTitleLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.TRACKONPLAYBACKTITLELABEL_X,
            geometryConstants.TRACKONPLAYBACKTITLELABEL_Y,
            geometryConstants.TRACKONPLAYBACKTITLELABEL_WIDTH,
            geometryConstants.TRACKONPLAYBACKTITLELABEL_HEIGHT)
        self.trackOnPlaybackTitleLabel.setFont(self.font)

        self.currentTimeLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.CURRENTTIMELABEL_X,
            geometryConstants.CURRENTTIMELABEL_Y,
            geometryConstants.CURRENTTIMELABEL_WIDTH,
            geometryConstants.CURRENTTIMELABEL_HEIGHT)
        self.currentTimeLabel.setFont(self.font)
        self.currentTimeLabel.setText("")

        self.allTracksLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.ALLTRACKSLABEL_X,
            geometryConstants.ALLTRACKSLABEL_Y,
            geometryConstants.ALLTRACKSLABEL_WIDTH,
            geometryConstants.ALLTRACKSLABEL_HEIGHT)
        self.allTracksLabel.setFont(self.font)
        self.allTracksLabel.setText("Все треки")

        self.allAlbumArtistsLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.ALLALBUMARTISTSLABEL_X,
            geometryConstants.ALLALBUMARTISTSLABEL_Y,
            geometryConstants.ALLALBUMARTISTSLABEL_WIDTH,
            geometryConstants.ALLALBUMARTISTSLABEL_HEIGHT)
        self.allAlbumArtistsLabel.setFont(self.font)
        self.allAlbumArtistsLabel.setText("Все исполнители")

        self.allAlbumsOfArtistLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.ALLALBUMSOFARTISTLABEL_X,
            geometryConstants.ALLALBUMSOFARTISTLABEL_Y,
            geometryConstants.ALLALBUMSOFARTISTLABEL_WIDTH,
            geometryConstants.ALLALBUMSOFARTISTLABEL_HEIGHT)
        self.allAlbumsOfArtistLabel.setFont(self.font)
        self.allAlbumsOfArtistLabel.setText("Альбомы исполнителя")

        self.tracksOfAlbumLabel = self.getConfiguredWidget(
            QLabel(self),
            geometryConstants.TRACKSOFALBUMLABEL_X,
            geometryConstants.TRACKSOFALBUMLABEL_Y,
            geometryConstants.TRACKSOFALBUMLABEL_WIDTH,
            geometryConstants.TRACKSOFALBUMLABEL_HEIGHT)
        self.tracksOfAlbumLabel.setFont(self.font)
        self.tracksOfAlbumLabel.setText("Треки альбома")

        self.messageDuplicateOfLQ = QMessageBox(self)
        self.messageDuplicateOfLQ.setWindowTitle("music player")
        self.messageDuplicateOfLQ.setIcon(QMessageBox.Icon.Information)
        self.messageDuplicateOfLQ.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.messageDuplicateOfLQ.setFont(self.font)

        self.messageDuplicateOfHQ = QMessageBox(self)
        self.messageDuplicateOfHQ.setWindowTitle("music player")
        self.messageDuplicateOfHQ.setIcon(QMessageBox.Icon.Information)
        self.messageDuplicateOfHQ.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.messageDuplicateOfHQ.setFont(self.font)

        self.messageMP3 = QMessageBox(self)
        self.messageMP3.setWindowTitle("music player")
        self.messageMP3.setIcon(QMessageBox.Icon.Information)
        self.messageMP3.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.messageMP3.setFont(self.font)

        # настройка средства проигрывания треков:
        self.player = playbackTool()

        # инициализация атрибутов, связанных с
        # средством проигрывания трека:
        self.allTracksInDatabaseList = db.getListOfAllRowsForTableList()
        self.playbackQueue = self.allTracksInDatabaseList

        # настройка таймера для отображения текущего времени
        # воспроизведения:
        self.timerSecondsValue = 0
        self.timerMinutesValue = 0

        self.timer = QTimer(self)

        # инициализация атрибутов, связанных с выбором пользователя:
        self.trackOnPlaybackTitle = ""
        self.nextTrackOnPlaybackTitle = ""
        self.trackOnPlaybackAlbumArtist = ""
        self.trackOnPlaybackIndex = 0
        self.choosedTrackIndex = 0

        self.choosedAlbumArtistName = ""
        self.choosedAlbum = ""

        self.playFirstTrackOfCollection = True
        self.playOtherTrack = False
        self.closeApp = False

        self.playbackDirection = playbackControlConstants.PLAY_NEXT_TRACK

        # настройка соединений сигналов со слотами:
        self.connectSignalWithSlot(
            self.buttonAddTracks.clicked,
            self.addTracksThread)

        self.connectSignalWithSlot(
            self.tableListContextMenuActionDeleteTrack.triggered,
            self.deleteTrack)

        self.connectSignalWithSlot(
            self.tableList.itemDoubleClicked,
            self.playTrackByDoubleClickOnTitle)

        self.connectSignalWithSlot(
            self.tracksOfAlbumList.itemDoubleClicked,
            self.playTrackByDoubleClickOnTitle)

        self.connectSignalWithSlot(
            self.buttonPlayPauseTrack.clicked,
            self.playTrack)

        self.connectSignalWithSlot(
            self.buttonPreviousTrack.clicked,
            self.playPreviousTrack)

        self.connectSignalWithSlot(
            self.buttonNextTrack.clicked,
            self.playNextTrack)

        self.connectSignalWithSlot(
            self.albumArtistsList.itemDoubleClicked,
            self.loadAlbumsOfArtist)

        self.connectSignalWithSlot(
            self.albumsOfArtistList.itemDoubleClicked,
            self.loadTracksOfAlbum)

        self.connectSignalWithSlot(
            self.timer.timeout,
            self.updateTimer)

        self.connectSignalWithSlot(
            self.messageDuplicateOfLQ.buttonClicked,
            self.closeMessageDuplicateOfLQ)

    @staticmethod
    def getConfiguredWidget(widget,
                            x, y, width, height,
                            text=None,
                            icon=None,
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
        :param icon: иконка (необязательный параметр).
        :param sortOrder: порядок сортировки элементов
        (объект класса-наследника класса QtCore.Qt.SortOrder)
        [необазятельный параметр, используется в вызове,
        когда элемент интерфейса обладает элементами).
        :return: настроенный элемент интерфейса
        (объект класса-наследника класса QWidget).
        """

        widget.setGeometry(x, y, width, height)

        if isinstance(text, QIcon):
            text, icon = icon, text
        elif isinstance(text, QtCore.Qt.SortOrder):
            text, sortOrder = sortOrder, text

            icon = None

        if text is not None:
            widget.setText(text)

        if icon is not None and \
                hasattr(widget, 'setIcon'):
            widget.setIcon(icon)

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
        :return: настроенное контекстное меню.
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
        :param trackInfoList: список с информацией
        о треке.
        """

        cell1 = QTableWidgetItem(
            trackInfoList[tableListConstants.TITLE_INDEX])
        cell1.setFont(self.fontForTableList)

        self.tableList.setItem(
            rowIndex,
            tableListConstants.TITLE_INDEX,
            cell1)

        cell2 = QTableWidgetItem(
            trackInfoList[tableListConstants.ARTIST_INDEX])
        cell2.setFont(self.fontForTableList)

        self.tableList.setItem(
            rowIndex,
            tableListConstants.ARTIST_INDEX,
            cell2)

    def loadTracksFromMusicTracksTableToTableList(self):
        """
        загружает в табличный UI-список плеера
        треки из таблицы музыкальных композиций,
        находящейся в базы данных приложения.
        """

        self.tableList.setRowCount(0)

        self.allTracksInDatabaseList = \
            db.getListOfAllRowsForTableList()

        self.tableList.setRowCount(len(self.allTracksInDatabaseList))

        currentRow = 0
        for track in self.allTracksInDatabaseList:
            self.setRowInTableList(currentRow, track)

            currentRow += 1

    def addItemToListWidget(self, listWidget, itemText):
        """
        добавляет элемент в UI-список.
        :param listWidget: UI-список, в который
        добавляется элемент;
        :param itemText: подпись добавляемого в
        UI-список элемента.
        """

        item = QListWidgetItem()
        item.setText(itemText)
        item.setFont(self.fontForTableList)

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

    def loadAlbumArtists(self):
        """
        загружает в UI-список исполнителей
        альбомов артистов из таблицы
        музыкальных композиций,
        находящейся в базе данных
        приложения.
        """

        self.albumArtistsList.clear()

        self.setItemsOfListWidget(self.albumArtistsList,
                                  db.getListOfAllAlbumArtists())

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

        self.tracksOfAlbumList.clear()

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

        fileToAddPath = easygui.fileopenbox(
            filetypes="*.mp3, *.flac", multiple=False)

        if fileToAddPath:
            cancelledTrackTitle = ""

            addTrackFlag = True

            trackFileExtension = tde.getTrackFileExtension(fileToAddPath)
            tagsDict = tp.getTagsDict(fileToAddPath)
            trackBitDepth = tde.getBitDepth(fileToAddPath)
            trackBitRate = tagsDict.info.bitrate
            trackDuration = int(tagsDict.info.length)
            trackBPM = tde.getBPM(fileToAddPath)

            listOfPotentialDuplicates = \
                db.getListOfTrackWithCertainDurationAndBPM(trackDuration,
                                                           trackBPM)

            print(listOfPotentialDuplicates)

            trackHQ = False

            if listOfPotentialDuplicates:
                i = 0
                areEqual = False

                while i < len(listOfPotentialDuplicates) and not areEqual:
                    areEqual = tc.areIdenticalTracks(
                        fileToAddPath,
                        listOfPotentialDuplicates[i][-3]) or \
                               len(listOfPotentialDuplicates) == 1

                    if areEqual:
                        if trackBitDepth > int(listOfPotentialDuplicates[i][-2]) or \
                                trackBitRate > int(listOfPotentialDuplicates[i][-1]):
                            tp.copyTags(
                                listOfPotentialDuplicates[i][-3],
                                fileToAddPath)

                            db.deleteTrack(
                                listOfPotentialDuplicates[i][0],
                                listOfPotentialDuplicates[i][1])

                            self.loadTracksFromMusicTracksTableToTableList()

                            if not trackHQ:
                                trackHQ = True
                        else:
                            cancelledTrackTitle = listOfPotentialDuplicates[i][0]

                            addTrackFlag = False

                    i += 1

            if addTrackFlag:
                db.addRow(fileToAddPath)

                self.loadTracksFromMusicTracksTableToTableList()

                self.allTracksInDatabaseList.append(
                    db.getTrackInfoListByPath(fileToAddPath))

                if trackHQ:
                    self.messageDuplicateOfLQ.move(self.pos())
                    self.messageDuplicateOfLQ.setText(
                        "Трек '" +
                        cancelledTrackTitle +
                        "' был заменен на вариант в более высоком качестве.\n")

                    self.messageDuplicateOfLQ.exec()

                self.loadAlbumArtists()
            else:
                self.messageDuplicateOfLQ.move(self.pos())
                self.messageDuplicateOfLQ.setText(
                    "Трек '" +
                    cancelledTrackTitle +
                    "' уже загружен в плеер в более высоком качестве.\n")

                self.messageDuplicateOfLQ.exec()

    def addTracksThread(self):
        """
        запускает добавление треков в отдельный
        поток.
        """

        addTracksTask = Thread(target=self.addTracks)

        addTracksTask.start()

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

        self.loadAlbumArtists()
        self.albumsOfArtistList.clear()
        self.tracksOfAlbumList.clear()

    def resetTimer(self):
        """
        сбрасывает таймер.
        """

        self.stopTimer()

        self.timerSecondsValue = 0
        self.timerMinutesValue = 0

    def runTimer(self):
        """
        запускает таймер.
        """

        self.timer.start(1000)

    def stopTimer(self):
        """
        останавливает таймер.
        """

        self.timer.stop()

    def playTrack(self):
        """
        загружает трек в средство проигрывания
        и запускает его воспрозведение.
        """

        if self.playOtherTrack or self.playFirstTrackOfCollection:
            self.resetTimer()

            self.currentTimeLabel.setText("00:00")

            if self.playOtherTrack:
                self.trackOnPlaybackIndex = self.choosedTrackIndex

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

            self.buttonPlayPauseTrack.setIcon(self.pauseIcon)

            if self.playOtherTrack:
                self.playOtherTrack = False

            if self.playFirstTrackOfCollection:
                self.playFirstTrackOfCollection = False

            self.runTimer()

            self.playbackToolEventFilter()
        elif self.player.isPlaybackPaused():
            self.player.resumePlayback()

            self.runTimer()

            self.buttonPlayPauseTrack.setIcon(self.pauseIcon)
        elif self.player.isBusy():
            self.player.pausePlayback()

            self.stopTimer()

            self.buttonPlayPauseTrack.setIcon(self.playIcon)

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
                    if not self.closeApp:
                        if (self.playbackDirection ==
                            playbackControlConstants.PLAY_PREVIOUS_TRACK and
                            self.trackOnPlaybackIndex != 0) or \
                                (self.playbackDirection ==
                                 playbackControlConstants.PLAY_NEXT_TRACK and
                                 len(self.playbackQueue) - self.trackOnPlaybackIndex > 1):
                            self.choosedTrackIndex = self.trackOnPlaybackIndex + \
                                                     self.playbackDirection

                            self.playOtherTrack = True

                            self.playTrack()
                        else:
                            isPlaybackRunning = False

                            time.sleep(1)

                            self.trackOnPlaybackTitleLabel.setText("")
                            self.trackOnPlaybackAlbumArtistLabel.setText("")

                            self.buttonPlayPauseTrack.setIcon(self.playIcon)

                            self.resetTimer()

                            self.currentTimeLabel.setText("")

                            self.playFirstTrackOfCollection = True

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
            self.trackOnPlaybackTitle = choosedTrackTitle
            self.choosedTrackIndex = itemRow

        self.playOtherTrack = True

        self.playTrack()

    def rewindTrack(self):
        """
        перематывает проигрываемый трек
        или трек, поставленный на паузу,
        на его начало.
        """

        self.player.rewindPlayback()

        if not self.player.isBusy():
            self.buttonPlayPauseTrack.setIcon(self.playIcon)

        self.resetTimer()

        self.currentTimeLabel.setText("00:00")

        self.runTimer()

    def stopTrack(self):
        """
        останавливает воспроизведение треков.
        """

        self.player.stopPlayback()

        self.playFirstTrackOfCollection = True

        self.buttonPlayPauseTrack.setIcon(self.playIcon)

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

        if self.trackOnPlaybackIndex == 0:
            self.rewindTrack()
        else:
            self.playbackDirection = playbackControlConstants.PLAY_PREVIOUS_TRACK
            self.stopTrack()

    def playNextTrack(self):
        """
        запускает проигрывание трека,
        идущего в очереди воспроизведения
        за проигрываемым (если он есть).
        """

        if len(self.playbackQueue) - self.trackOnPlaybackIndex > 1:
            self.playbackDirection = playbackControlConstants.PLAY_NEXT_TRACK
            self.stopTrack()

    @staticmethod
    def getFormattedStrOfTimeParameterValue(timeParameterValue):
        """
        возвращает форматированную строку с величиной
        измерения времени (количеством минут или
        количеством секунд) [старший байт строки принимает
        значение '0' в случае, когда значение величины
        измерения времени меньше 10].
        :parameter timeParameterValue: значение величина изм
        :return: форматированная строка с величиной
        измерения времени (количеством минут или
        количеством секунд)
        """

        timeParameterValueStr = str(timeParameterValue)

        if len(timeParameterValueStr) == 1:
            timeParameterValueStr = '0' + timeParameterValueStr

        return timeParameterValueStr

    def displayCurrentTime(self):
        """
        обновляет отображение текущего времени
        воспроизведения трека.
        """

        timerSecondsValueStr = self.getFormattedStrOfTimeParameterValue(
            self.timerSecondsValue)

        timerMinutesValueStr = self.getFormattedStrOfTimeParameterValue(
            self.timerMinutesValue)

        self.currentTimeLabel.setText(timerMinutesValueStr +
                                      ":" +
                                      timerSecondsValueStr)

    def updateTimer(self):
        """
        обновляет текущее время воспроизведения трека.
        """

        self.timerSecondsValue += 1

        if self.timerSecondsValue % 60 == 0:
            self.timerSecondsValue = 0
            self.timerMinutesValue += 1

        self.displayCurrentTime()

    def updateTimerThread(self):
        """
        запускает обновление таймера в отдельный
        поток.
        """

        task = Thread(target=self.updateTimer)

        task.start()

    def closeEvent(self, event):
        """
        обрабатывает закрытие приложения.
        """

        self.closeApp = True

        self.stopTrack()
        self.close()

    def closeMessageDuplicateOfLQ(self):
        self.messageDuplicateOfLQ.close()


def runApplication():
    """
    запускает приложение музыкального плеера.
    """

    musicPlayerApplication = QApplication(sys.argv)
    window = mainWindow()
    window.show()

    sys.exit(musicPlayerApplication.exec())