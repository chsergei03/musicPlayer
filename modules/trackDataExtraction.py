import modules.tagsParsing as tp

import sys
import subprocess

import os
from os import path
from pathlib import Path

import enum
from strenum import StrEnum

import soundfile as sf
from scipy.io import wavfile as wav
from scipy.fftpack import rfft
import numpy as np

from pydub import AudioSegment
import librosa
import warnings

warnings.simplefilter("ignore", UserWarning)


class formatsConstants(StrEnum):
    MP3_FORMAT_FILE_EXTENSION = ".mp3"
    FLAC_FORMAT_FILE_EXTENSION = ".flac"
    WAV_FORMAT_FILE_EXTENSION = ".wav"
    ENCODING_FORMAT = "latin-1"


class getBitDepthConstants(enum.IntEnum):
    SEEK_WHENCE = 0

    N_BYTES_BEFORE_BIT_DEPTH_SECTION = 34

    BIT_DEPTH_SECTION_SIZE = 2


class pathConstants(StrEnum):
    CONVERTED_TRACK_REL_PATH = "data/convertedTrack"

    MP3_FILE_PATH = path.abspath(
        CONVERTED_TRACK_REL_PATH +
        formatsConstants.MP3_FORMAT_FILE_EXTENSION)

    WAV_FILE_PATH = path.abspath(
        CONVERTED_TRACK_REL_PATH +
        formatsConstants.WAV_FORMAT_FILE_EXTENSION)


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
    tempo, beat_frames = librosa.beat.beat_track(y=wave,
                                                 sr=sampleRate)

    return int(tempo)


def getDuration(filepath):
    """
    возвращает продолжительность трека в
    секундах.
    :param filepath: строка, содержащая путь
    к файлу трека.
    :return: продолжительность трека в
    секундах.
    """

    tagsDict = tp.getTagsDict(filepath)

    return int(tagsDict.info.length)


def getBitDepth(filepath):
    """
    возвращает глубину звучания трека.
    :param filepath: строка, содержащая
    путь к файлу трека.
    :return: глубина звучания трека.
    """

    convertToWAV(filepath, pathConstants.WAV_FILE_PATH)

    filepath = pathConstants.WAV_FILE_PATH

    f = open(filepath, encoding=formatsConstants.ENCODING_FORMAT)

    f.seek(getBitDepthConstants.N_BYTES_BEFORE_BIT_DEPTH_SECTION,
           getBitDepthConstants.SEEK_WHENCE)

    bitDepth = int.from_bytes(
        f.read(getBitDepthConstants.BIT_DEPTH_SECTION_SIZE).encode(
            formatsConstants.ENCODING_FORMAT
        ), "little")

    f.close()

    os.remove(filepath)

    return bitDepth


def convertToWAV(filepath, convertedFilepath):
    """
    конвертирует аудиофайл в формат WAV.
    :param filepath: строка, содержащая путь
    к файлу трека;
    :param convertedFilepath: строка, содержащая
    путь к конвертированному файлу трека.
    """

    fileFormat = getTrackFileExtension(filepath)[1:]

    sound = AudioSegment.from_file(filepath, fileFormat)
    sound.export(convertedFilepath,
                 format="wav")


def convertToMP3(filepath, convertedFilepath):
    """
    конвертирует аудиофайл в формат WAV.
    :param filepath: строка, содержащая путь
    к файлу трека;
    :param convertedFilepath: строка, содержащая
    путь к конвертированному файлу трека.
    """

    fileFormat = getTrackFileExtension(filepath)[1:]

    sound = AudioSegment.from_file(filepath, fileFormat)
    sound.export(convertedFilepath,
                 format="mp3", bitrate="320k")