import sqlite3
import os.path

import modules.tagsParsing as tagsParsing

FILEBASE_PATH = os.path.abspath("data/filebase/filebase.db")

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

def executeQuery(query, queryType, varWithInfo=None):
    """
    выполняет запрос к базе данных, закрепляет изменения в базе
    данных, если запрос относится к типу "noSelectQuery", в противном
    случае возвращает список строк, удовлетворяющих запросу.
    :param query: запрос к базе данных;
    :param queryType: тип запроса к базе данных (строка);
    :param varWithInfo: переменная, хранящая дополнительную
    информацию для запроса к базе данных (кортеж, является
    необязательным параметром).
    :return: список 'строк', удовлетворяющих запросу; возвращается.
    если запрос относится к типу "getAllRowsBySelectQuery" или
    "getOneRowBySelectQuery" ('строка' представляет из себя кортеж
    с данными из контректной строки таблицы).
    """

    connection, cursor = initConnectionAndCursor(FILEBASE_PATH)

    if isinstance(varWithInfo, type(None)):
        cursor.execute(query)
    else:
        cursor.execute(query, varWithInfo)

    if queryType == "noSelectQuery":
        sustainChanges(connection, cursor)
    else:
        if queryType == "getOneRowBySelectQuery":
            rowsList = cursor.fetchone()
        elif queryType == "getAllRowsBySelectQuery":
            rowsList = cursor.fetchall()

        closeConnectionAndCursor(connection, cursor)

        return rowsList

def musicTracksTableInit():
    """
    создает таблицу с музыкальными композициями
    в базе данных приложения.
    """

    executeQuery("""CREATE TABLE musicTracks(
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
        "noSelectQuery")

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

    rows = executeQuery(
        """SELECT filepath FROM musicTracks WHERE filepath = ?""",
        "getAllRowsBySelectQuery",
        (fileToAddPath,))

    if len(rows) == 0:
        infoList = [fileToAddPath]
        tagsParsing.complementTrackInfoList(tagsParsing.getTagsDict(fileToAddPath),
                                            infoList)
        nListenings = 0
        infoList.append(nListenings)

        executeQuery("""INSERT INTO musicTracks 
            (filepath, title, album, artist, albumArtist, 
            yearRelease, genre, composer, nListenings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            "noSelectQuery",
            tuple(infoList))

def getListOfAllRowsOfMusicTracksTable():
    """
    возвращает список всех строк таблицы музыкальных композиций,
    находящейся в базе данных приложения (строка представляет из
    себя кортеж данных).
    :return: список всех 'строк' таблицы музыкальных композиций
    listOfAllRowsOfMusicTracksTable ('строка' представляет
    из себя кортеж с данными из контректной строки таблицы).
    """

    listOfAllRowsOfMusicTracksTable = executeQuery(
        """SELECT * FROM musicTracks""",
        "getAllRowsBySelectQuery")

    return listOfAllRowsOfMusicTracksTable

def getLastRowOfMusicTracksTableAndItsIndex():
    """
    # возвращает последнюю строку таблицы музыкальных композиций,
    находящейся в базе данных приложения (строка представляет из
    себя кортеж данных), а также индекс этой строки.
    :return: последняя 'строка' таблицы музыкальных композиций
    lastRowOfMusicTracksTable ('строка' представляет из себя кортеж
    с данными из контректной строки таблицы).
    """

    lastRowOfMusicTracksTable = executeQuery(
        """SELECT * FROM musicTracks ORDER BY id DESC""",
        "getOneRowBySelectQuery")

    return lastRowOfMusicTracksTable, lastRowOfMusicTracksTable[0] - 1

def initFilebaseIfNotExists():
    """
    инициализирует базу данных приложения, создавая в ней
    таблицу музыкальных композиций, если файл базы данных
    не существует.
    """

    if not os.path.exists(FILEBASE_PATH):
        musicTracksTableInit()