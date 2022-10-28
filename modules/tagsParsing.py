import mutagen

from mutagen import id3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC


def getTagsDict(filepath):
    """
    возвращает словарь тегов, присвоенных
    музыкальной композиции, файл которой
    расположен по пути filepath.
    :param filepath: путь к файлу трека.
    :return: словарь тегов, присвоенных
    музыкальной композиции.
    """

    trackFormat = filepath[-4:]

    if trackFormat == ".mp3":
        return MP3(filepath)
    elif trackFormat == "flac":
        return FLAC(filepath)


def getKeysDict(tagsDict):
    """
    возвращает словарь ключей словаря тегов
    музыкальной композиции.
    :param tagsDict: словарь тегов, присвоенных
    музыкальной композиции.
    :return: словарь ключей словаря тегов трека
    keysDict.
    """

    if isinstance(tagsDict, mutagen.flac.FLAC):
        titleKey = 'TITLE'
        albumKey = 'ALBUM'
        artistKey = 'ARTIST'
        albumArtistKey = 'ALBUMARTIST'
        dateKey = 'DATE'
        genreKey = 'GENRE'
        numberInTracklistKey = 'TRACKNUMBER'
        composerKey = 'COMPOSER'
    elif isinstance(tagsDict, mutagen.mp3.MP3):
        titleKey = 'TIT2'
        albumKey = 'TALB'
        artistKey = 'TPE1'
        albumArtistKey = 'TPE2'
        dateKey = 'TDRC'
        genreKey = 'TCON'
        numberInTracklistKey = 'TRCK'
        composerKey = 'TCOM'

    keysDict = {
        'title': titleKey,
        'album': albumKey,
        'artist': artistKey,
        'albumArtist': albumArtistKey,
        'date': dateKey,
        'genre': genreKey,
        'numberInTracklist': numberInTracklistKey,
        'composer': composerKey
    }

    return keysDict


def getInfoFromTagsDictByKey(tagsDict, key):
    """
    возвращает информацию о музыкальной композиции
    по ключу словаря ключей словаря тегов.
    :param tagsDict: словарь тегов, присвоенных
    музыкальной композиции;
    :param key: ключ словаря ключей словаря тегов.
    :return: строка с информацией о треке.
    """

    keysDict = getKeysDict(tagsDict)

    info = str(tagsDict[keysDict[key]][0])

    if key == "trackNumber" and isinstance(tagsDict, mutagen.mp3.MP3):
        slashPos = info.find('/')
        info = info[:slashPos]

    return info


def getTagsList(tagsDict):
    """
    возвращает список тегов, присвоенных
    музыкальной композиции, по их словарю.
    :param tagsDict: словарь тегов, присвоенных
    музыкальной композиции;
    :return: список тегов, присвоенных
    музыкальной композиции, tagsList.
    """

    tagsList = []

    for key in getKeysDict(tagsDict):
        tagsList.append(getInfoFromTagsDictByKey(tagsDict,
                                                 key))

    return tagsList