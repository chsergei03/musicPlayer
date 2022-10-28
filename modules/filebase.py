import enum
import sqlite3
import os.path

import modules.tagsParsing as tagsParsing

FILEBASE_PATH = os.path.abspath("data/filebase/filebase.db")


class executeQueryConstants(enum.IntEnum):
    NO_SELECT_QUERY = 0
    GET_ONE_ROW_BY_SELECT_QUERY = 1
    GET_ALL_ROWS_BY_SELECT_QUERY = 2


def initConnectionAndCursor(filebasePath):
    """
    создает объект соединения с базой данных
    и курсор для работы с её содержимым.
    :param filebasePath: путь к файлу базы
    данных.
    :return: объект соединения с базой данных
    connection, курсор для работы с её содержимым
    cursor.
    """

    connection = sqlite3.connect(filebasePath)
    cursor = connection.cursor()

    return connection, cursor


def closeConnectionAndCursor(connection,
                             cursor):
    """
    закрывает курсор для работы с содержимым
    базы данных и соединение с ней.
    :param connection: курсор для работы с
    содержимым базы данных;
    :param cursor: объект соединения с базой
    данных.
    """

    cursor.close()
    connection.close()


def sustainChanges(connection,
                   cursor):
    """
    закрепляет изменения в базе
    данных с закрытием курсора
    для работы с содержимым базы
    данных и соединения с ней.
    :param connection: курсор для
    работы с содержимым базы данных;
    :param cursor: объект соединения
    с базой данных.
    """

    connection.commit()
    closeConnectionAndCursor(connection, cursor)


def executeQuery(query,
                 queryType,
                 tupleWithInfo=None):
    """
    выполняет запрос к базе данных,
    закрепляет изменения в базе данных,
    если запрос относится к типу NO_SELECT_QUERY,
    в противном случае возвращает список строк,
    удовлетворяющих запросу.
    :param query: запрос к базе данных;
    :param queryType: тип запроса к базе
    данных (целочисленная константа из
    перечисления executeQueryConstants);
    :param tupleWithInfo: кортеж, хранящий
    в себе информацию о содержимом таблицы,
    необходимую информацию для запроса к
    базе данных (кортеж, является необязательным
    параметром).
    :return: список 'строк' rowsList, удовлетворяющих
    запросу; возвращается, если запрос
    относится к типу GET_ONE_ROW_BY_SELECT_QUERY
    или GET_ALL_ROWS_BY_SELECT_QUERY ('строка'
    представляет из себя список с данными из
    контректной строки таблицы).
    """

    connection, cursor = initConnectionAndCursor(FILEBASE_PATH)

    if tupleWithInfo is None:
        cursor.execute(query)
    else:
        cursor.execute(query, tupleWithInfo)

    if queryType == executeQueryConstants.NO_SELECT_QUERY:
        sustainChanges(connection, cursor)
    else:
        if queryType == executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY:
            rowsDatas = cursor.fetchone()
        elif queryType == executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY:
            rowsDatas = cursor.fetchall()

        closeConnectionAndCursor(connection, cursor)

        if rowsDatas is not None:
            if isinstance(rowsDatas, tuple):
                return rowsDatas[0] if len(rowsDatas) == 1 else list(rowsDatas)
            else:
                return [list(rowData) if isinstance(rowData, tuple) \
                                         and len(rowData) > 1 else rowData[0] \
                        for rowData in rowsDatas]
        else:
            return rowsDatas


def musicTracksTableInit():
    """
    создает таблицу с музыкальными
    композициями в базе данных приложения.
    """

    executeQuery(
        """CREATE TABLE musicTracks(
        id INTEGER PRIMARY KEY NOT NULL,
        filepath TEXT NOT NULL,
        title TEXT NOT NULL,
        album TEXT NOT NULL,
        artist TEXT NOT NULL,
        albumArtist TEXT NOT NULL,
        yearRelease INT NOT NULL,
        genre TEXT NOT NULL,
        numberInTracklist INTEGER NOT NULL,
        composer TEXT NOT NULL,
        nListenings INTEGER NOT NULL);""",
        executeQueryConstants.NO_SELECT_QUERY)


def addRow(fileToAddPath):
    """
    добавляет в таблицу музыкальных
    композиций, находяющуюся в базу
    данных приложения, новую строку,
    если такого трека ещё нет в таблице
    (на основании пути к файлу трека
    производит проверку на нахождение
    его в таблице, если трека в таблице
    нет, производит парсинг  данных о нём;
    данные заносятся в список, который
    затем будет преобразован в кортеж для
    вставки новой строки в таблицу).
    :param fileToAddPath: путь к файлу
    добавляемого трека.
    """

    rowWithFileToAddPath = executeQuery(
        """SELECT * 
        FROM musicTracks 
        WHERE filepath = ?""",
        executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY,
        (fileToAddPath,))

    if rowWithFileToAddPath is None:
        executeQuery(
            """INSERT INTO musicTracks 
            (filepath, title, album, artist, albumArtist, 
            yearRelease, genre,  
            numberInTracklist, composer, nListenings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            executeQueryConstants.NO_SELECT_QUERY,
            tuple([fileToAddPath,
                   *(tagsParsing.getTagsList(
                       tagsParsing.getTagsDict(fileToAddPath))),
                   0]))


def getListOfAllRowsForTableList():
    """
    возвращает список всех строк таблицы
    музыкальных композиций, находящейся
    в базе данных приложения, для формирования
    табличного списка музыкальных композиций.
    :return: список всех 'строк' таблицы
    музыкальных композиций
    listOfAllRowsOfMusicTracksTable
    ('строка' представляет из себя список
    с названием трека и именем его исполнителя).
    """

    listOfAllRowsOfMusicTracksTable = executeQuery(
        """SELECT title, artist 
        FROM musicTracks""",
        executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY)

    return listOfAllRowsOfMusicTracksTable


def getListOfAllAlbumArtists():
    """
    возвращает список всех исполнителей
    альбомов из таблицы музыкальных
    композиций, находящейся в базе
    данных приложения, без повторений.
    :return: список всех исполнителей
    альбомов без повторений listOfAllAlbumArtists.
    """

    listOfAllAlbumArtists = executeQuery(
        """SELECT DISTINCT albumArtist 
        FROM musicTracks""",
        executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY)

    return listOfAllAlbumArtists


def getListOfAlbumsOfArtist(artistName):
    """
    возвращает список всех альбомов
    исполнителя из таблицы музыкальных
    композиций, находящейся в базе
    данных приложения, без повторений.
    :param artistName: строка с именем
    исполнителя.
    :return: список названий всех альбомов
    исполнителя без повторений
    listOfAllAlbumsOfArtist.
    """

    listOfAlbumsOfArtist = executeQuery(
        """SELECT DISTINCT album 
        FROM musicTracks
        WHERE albumArtist = ?""",
        executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY,
        (artistName,))

    return listOfAlbumsOfArtist


def getListsWithInfoAboutTracksOfAlbum(albumArtistName,
                                       albumName):
    """
    возвращает списки названий треков альбома
    конкретного исполнителя и список путей до
    их файлов из таблицы музыкальных композиций,
    находящейся в базе данных приложения.
    :param albumArtistName: строка с именем
    исполнителя;
    :param albumName: строка с названием
    альбома.
    :return: списки названий треков альбома
    конкретного исполнителя и список путей до
    их файлов.
    """

    listWithInfoAboutTracksOfAlbum = executeQuery(
        """SELECT DISTINCT title, filepath
        FROM musicTracks
        WHERE albumArtist = ? AND album = ?
        ORDER BY numberInTracklist ASC""",
        executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY,
        (albumArtistName, albumName,))

    trackTitlesList = [x[0] for x in listWithInfoAboutTracksOfAlbum]
    trackFilepathsList = [x[1] for x in listWithInfoAboutTracksOfAlbum]

    return [trackTitlesList, trackFilepathsList]


def getLastRow():
    """
    возвращает последнюю строку таблицы
    музыкальных композиций, находящейся в
    базе данных приложения.
    :return: последняя 'строка' таблицы
    музыкальных композиций lastRowOfMusicTracksTable
    ('строка' представляет из себя список
    с названием трека, добавленного последним
    в таблицу, и его исполнителем).
    """

    lastRowOfMusicTracksTable = executeQuery(
        """SELECT title, albumArtist 
        FROM musicTracks 
        ORDER BY id DESC""",
        executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY)

    return lastRowOfMusicTracksTable


def deleteTrack(trackTitle, artistName):
    """
    удаляет трек из таблицы музыкальных
    композиций, находящейся в базе данных
    приложения.
    :param trackTitle: строка с названием
    трека;
    :param artistName: строка с исполнителем
    трека.
    """

    executeQuery(
        """DELETE 
        FROM musicTracks 
        WHERE title = ? and artist = ?""",
        executeQueryConstants.NO_SELECT_QUERY,
        (trackTitle, artistName,))


def getTrackPath(trackTitle, artistName):
    """
    возвращает путь к файлу музыкальной
    композиции из таблицы треков по
    названию песни и имени исполнителя.
    :param trackTitle: строка с
    названием трека;
    :param artistName: строка с именем
    исполнителя трека;
    :return: строка trackPath, в которой
    содержится путь к файлу трека.
    """

    trackPath = executeQuery(
        """SELECT filepath 
        FROM musicTracks
        WHERE title = ? and albumArtist = ?""",
        executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY,
        (trackTitle, artistName,))

    return trackPath


def initFilebaseIfNotExists():
    """
    инициализирует базу данных
    приложения, создавая в ней
    таблицу музыкальных композиций,
    если файл базы данных не существует.
    """

    if not os.path.exists(FILEBASE_PATH):
        musicTracksTableInit()