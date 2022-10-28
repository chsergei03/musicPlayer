import os
import enum
import mutagen

import modules.tagsParsing as tagsParsing


class testsErrorMessages(enum.Enum):
    getKeysDict_errorMessage = "tags dictionary was not received"


def getTagsDict_test_01():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Calvin Harris - Lean On Me "
                               "(feat. Swae Lee).flac")

    tagsDict = tagsParsing.getTagsDict(filepath)

    assert isinstance(tagsDict, mutagen.flac.FLAC)


def getTagsDict_test_02():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Markul - 2 минуты.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)

    assert isinstance(tagsDict, mutagen.mp3.MP3)


def getTagsDict_test_03():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "half·alive - Hot Tea.flac")

    tagsDict = tagsParsing.getTagsDict(filepath)

    assert isinstance(tagsDict, mutagen.flac.FLAC)


def getTagsDict_test_04():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Куок - Миллион мегатонн.flac")

    tagsDict = tagsParsing.getTagsDict(filepath)

    assert isinstance(tagsDict, mutagen.flac.FLAC)


def getTagsDict_test_05():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Thrice - Scavengers.flac")

    tagsDict = tagsParsing.getTagsDict(filepath)

    assert isinstance(tagsDict, mutagen.flac.FLAC)


def getTagsDict_tests():
    getTagsDict_test_01()
    getTagsDict_test_02()
    getTagsDict_test_03()
    getTagsDict_test_04()
    getTagsDict_test_05()


def getInfoFromTagsDictByKey_test_title_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Markul, Тося Чайкина - Стрелы.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    title = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'title')

    assert title == "Стрелы"


def getInfoFromTagsDictByKey_test_title_flac():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Calvin Harris - Nothing More To Say (feat. 6LACK & Donae’O).flac")

    tagsDict = tagsParsing.getTagsDict(filepath)
    title = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'title')

    assert title == "Nothing More To Say (feat. 6LACK & Donae’O)"


def getInfoFromTagsDictByKey_test_album_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Idan - Комната. вход.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    album = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'album')

    assert album == "Зона комфорта"


def getInfoFromTagsDictByKey_test_album_flac():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Ed Sheeran - 2step.flac")

    tagsDict = tagsParsing.getTagsDict(filepath)
    album = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'album')

    assert album == "="


def getInfoFromTagsDictByKey_test_artist_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "LeTai - Миядзаки.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    artist = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'artist')

    assert artist == "LeTai"


def getInfoFromTagsDictByKey_test_artist_flac():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Mike Shinoda - Make It Up As I Go (feat. K.Flay).flac")

    tagsDict = tagsParsing.getTagsDict(filepath)
    artist = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'artist')

    assert artist == "Mike Shinoda"


def getInfoFromTagsDictByKey_test_albumArtist_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Jeembo - Следуй за мной.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    albumArtist = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'albumArtist')

    assert albumArtist == "Jeembo"


def getInfoFromTagsDictByKey_test_albumArtist_flac():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Markul - Карусель.flac")

    tagsDict = tagsParsing.getTagsDict(filepath)
    albumArtist = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'albumArtist')

    assert albumArtist == "Markul"


def getInfoFromTagsDictByKey_test_date_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Loqiemean - Солнечная Сторона.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    date = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'date')

    assert date == "2019"


def getInfoFromTagsDictByKey_test_genre_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Jimm - Очередной день.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    genre = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'genre')

    assert genre == "Хип-хоп/рэп"


def getInfoFromTagsDictByKey_test_genre_flac():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Machine Gun Kelly - 9 lives.flac")

    tagsDict = tagsParsing.getTagsDict(filepath)
    genre = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'genre')

    assert genre == "Альтернативная музыка/инди"


def getInfoFromTagsDictByKey_test_composer_mp3():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Скриптонит - Chapter II.mp3")

    tagsDict = tagsParsing.getTagsDict(filepath)
    composer = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'composer')

    assert composer == "Разные композиторы"


def getInfoFromTagsDictByKey_test_composer_flac():
    filepath = os.path.abspath("tests/tagsParsing_tests/dataset/"
                               "Calvin Harris - Stay With Me (feat. Justin Timberlake, Halsey & Pharrell).flac")

    tagsDict = tagsParsing.getTagsDict(filepath)
    composer = tagsParsing.getInfoFromTagsDictByKey(tagsDict, 'composer')

    assert composer == "Adam Richard Wiles"


def getInfoFromTagsDictByKey_tests():
    getInfoFromTagsDictByKey_test_title_mp3()
    getInfoFromTagsDictByKey_test_title_flac()
    getInfoFromTagsDictByKey_test_album_mp3()
    getInfoFromTagsDictByKey_test_album_flac()
    getInfoFromTagsDictByKey_test_artist_mp3()
    getInfoFromTagsDictByKey_test_artist_flac()
    getInfoFromTagsDictByKey_test_albumArtist_mp3()
    getInfoFromTagsDictByKey_test_albumArtist_flac()
    getInfoFromTagsDictByKey_test_date_mp3()
    getInfoFromTagsDictByKey_test_date_flac()
    getInfoFromTagsDictByKey_test_genre_mp3()
    getInfoFromTagsDictByKey_test_genre_flac()
    getInfoFromTagsDictByKey_test_composer_mp3()
    getInfoFromTagsDictByKey_test_composer_flac()


def tagsParsing_tests():
    getTagsDict_tests()
    getInfoFromTagsDictByKey_tests()