import mutagen

from mutagen import id3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

# возвращает словарь тегов, присвоенных музыкальной композиции,
# файл которой расположен по пути filepath.
def getTagsDict(filepath):
    trackFormat = filepath[-4:]

    if trackFormat == ".mp3":
        return MP3(filepath)
    elif trackFormat == "flac":
        return FLAC(filepath)

# возвращает словарь ключей словаря тегов музыкальной композиции.
def getKeysDict(tagsDict):
    if isinstance(tagsDict, mutagen.flac.FLAC):
        titleKey = 'TITLE'
        albumKey = 'ALBUM'
        artistKey = 'ARTIST'
        albumArtistKey = 'ALBUMARTIST'
        dateKey = 'DATE'
        genreKey = 'GENRE'
        composerKey = 'COMPOSER'
    elif isinstance(tagsDict, mutagen.mp3.MP3):
        titleKey = 'TIT2'
        albumKey = 'TALB'
        artistKey = 'TPE1'
        albumArtistKey = 'TPE2'
        dateKey = 'TDRC'
        genreKey = 'TCON'
        composerKey = 'TCOM'

    keysDict = {
        'title': titleKey,
        'album': albumKey,
        'artist': artistKey,
        'albumArtist': albumArtistKey,
        'date': dateKey,
        'genre': genreKey,
        'composer': composerKey
    }

    return keysDict

# возвращает информацию о музыкальной композиции по ключу из словаря
# тегов в формате строки.
def getInfoFromTagsDictByKey(tagsDict, key):
    keysDict = getKeysDict(tagsDict)

    return str(tagsDict[keysDict[key]][0])

# дополняет список информации о музыкальной композиции данными из тегов.
def complementTrackInfoList(tagsDict, infoList):
    for key in getKeysDict(tagsDict):
        infoList.append(getInfoFromTagsDictByKey(tagsDict, key))
