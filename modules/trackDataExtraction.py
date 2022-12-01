import modules.tagsParsing as tp

import sys
import subprocess

import os
from os import path
from pathlib import Path

import enum
from strenum import StrEnum

from mutagen.wave import WAVE
from pydub import AudioSegment

import librosa
import warnings

warnings.simplefilter("ignore", UserWarning)


class formatsConstants(StrEnum):
    MP3_FORMAT_FILE_EXTENSION = ".mp3"
    FLAC_FORMAT_FILE_EXTENSION = ".flac"
    WAV_FORMAT_FILE_EXTENSION = ".wav"


def getTrackFileExtension(filepath):
    """
    возвращает строку с расширением
    файла музыкальной композиции.
    :param filepath: строка, содержащая
    путь к файлу трека.
    :return: строка с расширением
    файла музыкальной композиции.
    """

    fileName, extension = path.splitext(filepath)

    return extension


def getBPM(filepath):
    """
    возвращает BPM трека (количество ударов в
    минуту).
    :param filepath: строка, содержащая путь
    к файлу трека.
    :return: BPM трека (количество ударов в минуту).
    """

    wave, sampleRate = librosa.load(filepath)
    tempo, beat_frames = librosa.beat.beat_track(y=wave, sr=sampleRate)

    return int(tempo)