import modules.trackDataExtraction as tde
import modules.database as db

import enum
from strenum import StrEnum

from pathlib import Path

import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import ID3


class tagsDefaultStrConstants(StrEnum):
    DEFAULT_STR_TAG = "Неизвестно"
    DEFAULT_INT_TAG = "1"


def getKeysDict(tagsDict):
    """
    возвращает словарь ключей
    словаря тегов музыкальной
    композиции.
    :param tagsDict: словарь
    тегов, присвоенных музыкальной
    композиции.
    :return: словарь ключей
    словаря тегов трека keysDict.
    """

    if isinstance(tagsDict, mutagen.flac.FLAC):
        titleKey = 'TITLE'
        albumKey = 'ALBUM'
        artistKey = 'ARTIST'
        albumArtistKey = 'ALBUMARTIST'
        dateKey = 'DATE'
        genreKey = 'GENRE'
        numberInTracklistKey = 'TRACKNUMBER'
    elif isinstance(tagsDict, mutagen.mp3.MP3):
        titleKey = 'TIT2'
        albumKey = 'TALB'
        artistKey = 'TPE1'
        albumArtistKey = 'TPE2'
        dateKey = 'TDRC'
        genreKey = 'TCON'
        numberInTracklistKey = 'TRCK'

    keysDict = {
        'title': titleKey,
        'album': albumKey,
        'artist': artistKey,
        'albumArtist': albumArtistKey,
        'date': dateKey,
        'genre': genreKey,
        'numberInTracklist': numberInTracklistKey
    }

    return keysDict


def prescribeTagsOfUnknownTrack(filepath, tagsDict):
    """
    заполняет теги трека, не имеющего метаданных.
    :param filepath: путь к файлу трека;
    :param tagsDict: словарь тегов трека.
    """

    keysDict = getKeysDict(tagsDict)

    for key in keysDict:
        if key == 'title':
            infoText = Path(filepath).stem
        elif key == 'trackNumber':
            infoText = str(db.getNTracksWithTagsOfUnknownTrack() + 1)
        else:
            infoText = tagsDefaultStrConstants.DEFAULT_STR_TAG

        if isinstance(tagsDict, mutagen.mp3.MP3):
            tagsDict[keysDict[key]] = mutagen.id3.TextFrame(encoding=3,
                                                            text=[infoText])
        else:
            tagsDict[keysDict[key]] = infoText

    return tagsDict


def getTagsDict(filepath):
    """
    возвращает словарь тегов,
    присвоенных музыкальной
    композиции, файл которой
    расположен по пути filepath.
    :param filepath: путь к
    файлу трека.
    :return: словарь тегов,
    присвоенных музыкальной
    композиции.
    """

    trackFileExtension = \
        tde.getTrackFileExtension(filepath)

    if trackFileExtension == \
            tde.formatsConstants.MP3_FORMAT_FILE_EXTENSION:
        tagsDict = MP3(filepath)
    elif trackFileExtension == \
            tde.formatsConstants.FLAC_FORMAT_FILE_EXTENSION:
        tagsDict = FLAC(filepath)

    if len(tagsDict) == 0:
        prescribeTagsOfUnknownTrack(filepath,
                                    tagsDict)

    return tagsDict


def getInfoFromTagsDictByKey(tagsDict,
                             key):
    """
    возвращает информацию о музыкальной
    композиции по ключу словаря ключей
    словаря тегов.
    :param tagsDict: словарь тегов,
    присвоенных музыкальной композиции;
    :param key: ключ словаря ключей словаря
    тегов.
    :return: строка с информацией о треке.
    """

    keysDict = getKeysDict(tagsDict)

    info = tagsDict.get(keysDict[key])

    if info is not None:
        infoStr = str(info[0])

        if key == 'trackNumber' and isinstance(tagsDict, mutagen.mp3.MP3):
            slashPos = info.find('/')
            infoStr = infoStr[:slashPos]
    elif key == 'trackNumber':
        infoStr = tagsDefaultStrConstants.DEFAULT_STR_TAG
    else:
        infoStr = tagsDefaultStrConstants.DEFAULT_INT_TAG

    return infoStr


def getTagsList(tagsDict):
    """
    возвращает список тегов,
    присвоенных музыкальной
    композиции, по их словарю.
    :param tagsDict: словарь
    тегов, присвоенных музыкальной
    композиции;
    :return: список тегов,
    присвоенных музыкальной
    композиции, tagsList.
    """

    tagsList = []

    for key in getKeysDict(tagsDict):
        tagsList.append(getInfoFromTagsDictByKey(tagsDict,
                                                 key))

    return tagsList