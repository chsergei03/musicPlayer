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
    создает объект соединения с базой данных и курсор
    для работы с её содержимым.
    :param filebasePath: путь к файлу базы данных.
    :return: объект соединения с базой данных connection,
    курсор для работы с её содержимым cursor.
    """

    connection = sqlite3.connect(filebasePath)
    cursor = connection.cursor()

    return connection, cursor

def closeConnectionAndCursor(connection, cursor):
    """
    закрывает курсор для работы с содержимым базы данных
    и соединение с ней.
    :param connection: курсор для работы с содержимым базы данных;
    :param cursor: объект соединения с базой данных.
    """

    cursor.close()
    connection.close()

def sustainChanges(connection, cursor):
    """
    закрепляет изменения в базе данных с закрытием курсора
    для работы с содержимым базы данных и соединения
    с ней.
    :param connection: курсор для работы с содержимым базы данных;
    :param cursor: объект соединения с базой данных.
    """

    connection.commit()
    closeConnectionAndCursor(connection, cursor)

def executeQuery(query, queryType, tupleWithInfo=None):
    """
    выполняет запрос к базе данных, закрепляет изменения
    в базе данных, если запрос относится к типу NO_SELECT_QUERY,
    в противном случае возвращает список строк, удовлетворяющих
    запросу.
    :param query: запрос к базе данных;
    :param queryType: тип запроса к базе данных (целочисленная
    константа из перечисления executeQueryConstants);
    :param tupleWithInfo: кортеж, хранящий в себе информацию о
    содержимом таблицы, необходимую информацию для запроса к
    базе данных (кортеж, является необязательным параметром).
    :return: список 'строк' rowsList, удовлетворяющих запросу;
    возвращается, если запрос относится к типу GET_ONE_ROW_BY_SELECT_QUERY
    или GET_ALL_ROWS_BY_SELECT_QUERY ('строка' представляет
    из себя кортеж с данными из контректной строки таблицы).
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
            rowsList = cursor.fetchone()
        elif queryType == executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY:
            rowsList = cursor.fetchall()

        closeConnectionAndCursor(connection, cursor)

        return rowsList

def musicTracksTableInit():
    """
    создает таблицу с музыкальными композициями
    в базе данных приложения.
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
        composer TEXT NOT NULL,
        nListenings INTEGER NOT NULL);""",
        executeQueryConstants.NO_SELECT_QUERY)

def addRowToMusicTracksTable(fileToAddPath):
    """
    добавляет в таблицу музыкальных композиций, находяющуюся
    в базу данных приложения, новую строку, если такого трека
    ещё нет в таблице (на основании пути к файлу трека производит
    проверку на нахождение его в таблице, если трека в таблице нет,
    производит парсинг  данных о нём; данные заносятся в список,
    который затем будет преобразован в кортеж для вставки новой
    строки в таблицу).
    :param fileToAddPath: путь к файлу добавляемого трека.
    """

    rowWithFileToAddPath = executeQuery(
        """SELECT * 
        FROM musicTracks 
        WHERE filepath = ?""",
        executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY,
        (fileToAddPath,))

    if rowWithFileToAddPath is None:
        infoList = [fileToAddPath]
        tagsParsing.complementTrackInfoList(tagsParsing.getTagsDict(fileToAddPath),
                                            infoList)
        nListenings = 0
        infoList.append(nListenings)

        executeQuery(
            """INSERT INTO musicTracks 
            (filepath, title, album, artist, albumArtist, 
            yearRelease, genre, composer, nListenings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            executeQueryConstants.NO_SELECT_QUERY,
            tuple(infoList))

def getListOfAllRowsOfMusicTracksTableForTableList():
    """
    возвращает список всех строк таблицы музыкальных композиций,
    находящейся в базе данных приложения (строка представляет из
    себя кортеж данных), для формирования табличного списка
    музыкальных композиций.
    :return: список всех 'строк' таблицы музыкальных композиций
    listOfAllRowsOfMusicTracksTable ('строка' представляет
    из себя кортеж с данными из контректной строки таблицы).
    """

    listOfAllRowsOfMusicTracksTable = executeQuery(
        """SELECT title, artist 
        FROM musicTracks""",
        executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY)

    return listOfAllRowsOfMusicTracksTable

def getListOfAllAlbumArtistsFromMusicTracksTable():
    """
    возвращает список всех исполнителей альбомов из
    таблицы музыкальных композиций, находящейся в
    базе данных приложения, без повторений.
    :return: список всех исполнителей альбомов из
    таблицы музыкальных композиций, находящейся в
    базе данных приложения, listOfAllAlbumArtists.
    """

    listOfAllAlbumArtists = executeQuery(
        """SELECT DISTINCT albumArtist 
        FROM musicTracks""",
        executeQueryConstants.GET_ALL_ROWS_BY_SELECT_QUERY)

    return listOfAllAlbumArtists

def getLastRowOfMusicTracksTable():
    """
    # возвращает последнюю строку таблицы музыкальных
    композиций, находящейся в базе данных приложения
    (строка представляет из себя кортеж данных).
    :return: последняя 'строка' таблицы музыкальных
    композиций lastRowOfMusicTracksTable ('строка'
    представляет из себя кортеж с названием трека,
    добавленного последним в таблицу, и его исполнителем).
    """

    lastRowOfMusicTracksTable = executeQuery(
        """SELECT title, artist 
        FROM musicTracks 
        ORDER BY id DESC""",
        executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY)

    return lastRowOfMusicTracksTable

def deleteRowFromMusicTracksTable(trackInfoTuple):
    """
    удаляет трек из таблицы музыкальных композиций,
    находящейся в базе данных приложения.
    :param trackInfoTuple: кортеж с названием трека
    и его исполнителем.
    """

    executeQuery(
        """DELETE 
        FROM musicTracks 
        WHERE title = ? and artist = ?""",
        executeQueryConstants.NO_SELECT_QUERY,
        trackInfoTuple)

def getTrackPathFromMusicTracksTable(trackInfoTuple):
    """
    возвращает путь к файлу музыкальной композиции из
    таблицы треков, находящейся в базе данных приложения,
    по кортежу, в котором содержится название песни и
    имя исполнителя.
    :param trackInfoTuple: кортеж с названием трека и
    его исполнителем.
    :return: строка trackPath, в которой содержится путь
    к файлу трека.
    """

    trackPath = executeQuery(
        """SELECT filepath 
        FROM musicTracks
        WHERE title = ? and artist = ?""",
        executeQueryConstants.GET_ONE_ROW_BY_SELECT_QUERY,
        trackInfoTuple)[0]

    return trackPath

def initFilebaseIfNotExists():
    """
    инициализирует базу данных приложения, создавая в ней
    таблицу музыкальных композиций, если файл базы данных
    не существует.
    """

    if not os.path.exists(FILEBASE_PATH):
        musicTracksTableInit()