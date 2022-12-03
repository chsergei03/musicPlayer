import modules.trackDataExtraction as tde

import os
from os import path

import subprocess

import hashlib


def getFFMPEGPath():
    """
    возвращает путь к FFMPEG.
    """
    return os.environ.get('FFMPEG_BIN', 'ffmpeg')


def computeSHA256(f):
    """
    возвращает хеш-сумму последовательности
    байтов f.
    :param f: находящаяся в состоянии чтения
    последовательность байт.
    :return: хеш-сумму последовательности
    байтов f.
    """

    hashFunction = hashlib.sha256()

    isEmpty = True
    while True:
        data = f.read(hashFunction.block_size * 256)

        if not data:
            break

        isEmpty = False

        hashFunction.update(data)

    if isEmpty:
        return None

    return hashFunction.hexdigest()


def getChecksumSHA256(filepath, ffmpegBinPath=None):
    """
    возвращает хеш-сумму аудиофайла.
    :param filepath: строка, содержащая
    путь к аудиофайлу
    :param ffmpegBinPath: путь к FFMPEG
    :return: хеш-сумма аудиофайла.
    """

    if ffmpegBinPath is None:
        ffmpegBinPath = getFFMPEGPath()
    subprocessArgs = [
        ffmpegBinPath,
        '-i',
        filepath,
        '-vn',
        '-f',
        's24le',
        '-',
    ]

    with open(filepath,
              encoding=tde.formatsConstants.ENCODING_FORMAT) as f:
        f.read(1)

    with open(os.devnull, 'wb') as fnull:
        process = subprocess.Popen(subprocessArgs,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        sha256Sum = computeSHA256(process.stdout)

        process.wait()
        try:
            if sha256Sum is None:
                raise ExternalLibraryError(process.stderr.read())

            return sha256Sum
        finally:
            process.stdout.close()
            process.stderr.close()


def areIdenticalTracks(track1Filepath, track2Filepath):
    """
    возвращает значение 'истина', если два
    трека идентичны по содержанию, иначе - 'ложь'.
    :param track1Filepath: путь к файлу первого трека;
    :param track2Filepath: путь к файлу второго трека.
    """

    return getChecksumSHA256(track1Filepath) == \
        getChecksumSHA256(track2Filepath)