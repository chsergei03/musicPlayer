import sqlite3
import os.path

import modules.tagsParsing as tagsParsing

FILEBASE_PATH = os.path.abspath("data/filebase/filebase.db")

# возвращает объект соединения с базой данных приложения
# и курсор для работы с её содержимым.
def initConnectionAndCursor(filebasePath):
    connection = sqlite3.connect(filebasePath)
    cursor = connection.cursor()

    return connection, cursor

# закрывает курсор для работы с содержимым базы данных
# приложения и соединение с ней.
def closeConnectionAndCursor(connection, cursor):
    cursor.close()
    connection.close()

# закрепляет изменения в базе данных и закрывает соединение
# c ней.
def sustainChanges(connection, cursor):
    connection.commit()
    closeConnectionAndCursor(connection, cursor)

# инициализирует базу данных приложения.
def filebaseInit():
    initConnection, initCursor = initConnectionAndCursor(FILEBASE_PATH)

    initCursor.execute("""CREATE TABLE musicTracks(
        filepath TEXT NOT NULL,
        title TEXT NOT NULL,
        album TEXT NOT NULL,
        artist TEXT NOT NULL,
        albumArtist TEXT NOT NULL,
        yearRelease INT NOT NULL,
        genre TEXT NOT NULL,
        composer TEXT NOT NULL,
        nListenings INT NOT NULL);""")

    sustainChanges(initConnection, initCursor)

# добавляет в базу данных приложения новую строку.
def addRowToFilebase(fileToAddPath):
    connection, cursor = initConnectionAndCursor(FILEBASE_PATH)

    searchQuery = """SELECT filepath FROM musicTracks WHERE filepath = ?"""
    cursor.execute(searchQuery, (fileToAddPath,))
    rows = cursor.fetchall()

    if len(rows) == 0:
        infoList = [fileToAddPath]
        tagsParsing.complementTrackInfoList(tagsParsing.getTagsDict(fileToAddPath),
                                            infoList)

        nListenings = 0
        infoList.append(nListenings)

        insertQuery = """INSERT INTO musicTracks 
            (filepath, title, album, artist, albumArtist, 
            yearRelease, genre, composer, nListenings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        cursor.execute(insertQuery, tuple(infoList))
        sustainChanges(connection, cursor)

# возвращает список из строк базы данных приложения
# (строка представлена в виде кортежа).
def getAllRowsOfFilebaseList():
    connection, cursor = initConnectionAndCursor(FILEBASE_PATH)

    selectAllQuery = """SELECT * FROM musicTracks"""
    cursor.execute(selectAllQuery)
    allRowsOfFilebaseList = cursor.fetchall()

    closeConnectionAndCursor(connection, cursor)

    return allRowsOfFilebaseList

if not os.path.exists(FILEBASE_PATH):
    filebaseInit()
