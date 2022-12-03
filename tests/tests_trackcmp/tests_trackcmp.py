import modules.trackcmp as tc

import os
from os import path


def test_01_isIdenticalTracks_identicalTracks_flacWAV():
    assert tc.areIdenticalTracks(
        path.abspath("tests/tests_trackcmp/dataset/mahler.flac"),
        path.abspath("tests/tests_trackcmp/dataset/mahler.wav"))

    print("test_01_isIdenticalTracks_identicalTracks_01: OK")


def test_02_isIdenticalTracks_identicalTracks_flacMP3():
    assert not tc.areIdenticalTracks(
        path.abspath("tests/tests_trackcmp/dataset/Calvin Harris - Intro.flac"),
        path.abspath("tests/tests_trackcmp/dataset/Calvin Harris - Intro.mp3"))

    print("test_02_isIdenticalTracks_identicalTracks_02: OK")


def test_03_isIdenticalTracks_nonIdenticalTracks():
    assert not tc.areIdenticalTracks(
        path.abspath("tests/tests_trackcmp/dataset/FIRMAA - Ozzy.mp3"),
        path.abspath("tests/tests_trackcmp/dataset/Archy Brown - Bounce.flac"))

    print("test_03_isIdenticalTracks_nonIdenticalTracks: OK")


def tests_isIdenticalTracks():
    test_01_isIdenticalTracks_identicalTracks_flacWAV()
    test_02_isIdenticalTracks_identicalTracks_flacMP3()
    test_03_isIdenticalTracks_nonIdenticalTracks()


def tests_trackcmp():
    tests_isIdenticalTracks()
