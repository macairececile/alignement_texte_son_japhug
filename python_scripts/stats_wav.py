import librosa
from os import listdir
from os.path import isfile, join


def get_wav_files(path):
    """get all wav files"""
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return files


def length_wav_files(path, files):
    info_wav = dict()
    for el in files:
        info_wav[el] = librosa.get_duration(filename=path + el) / 60
    return info_wav


def stats_wav(wav_info):
    wav_onemin = {}
    wav_onetwomin = {}
    wav_threemin = {}
    wav_fivemin = {}
    wav_dixmin = {}
    wav_more = {}
    for k, v in wav_info.items():
        if v <= 1:
            wav_onemin[k] = v
            wav_onemin = {k: v for k, v in sorted(wav_onemin.items(), key=lambda item: item[1])}
        elif 1 < v <= 2:
            wav_onetwomin[k] = v
            wav_onetwomin = {k: v for k, v in sorted(wav_onetwomin.items(), key=lambda item: item[1])}
        elif 2 < v <= 3:
            wav_threemin[k] = v
            wav_threemin = {k: v for k, v in sorted(wav_threemin.items(), key=lambda item: item[1])}
        elif 3 < v <= 5:
            wav_fivemin[k] = v
            wav_fivemin = {k: v for k, v in sorted(wav_fivemin.items(), key=lambda item: item[1])}
        elif 5 < v <= 10:
            wav_dixmin[k] = v
            wav_dixmin = {k: v for k, v in sorted(wav_dixmin.items(), key=lambda item: item[1])}
        else:
            wav_more[k] = v
            wav_more = {k: v for k, v in sorted(wav_more.items(), key=lambda item: item[1])}
    print('Wav files of 1 minutes', wav_onemin)
    print('Wav files of 1 to 2 minutes', wav_onetwomin)
    print('Wav files of 2 to 3 minutes', wav_threemin)
    print('Wav files of 3 to 5 minutes', wav_fivemin)
    print('Wav files of 5 to 10 minutes', wav_dixmin)
    print('Wav files of more than 10 minutes', wav_more)
    print('\nCount of files:')
    print('Wav files of 1 minutes : ', len(wav_onemin))
    print('Wav files of 1 to 2 minutes : ', len(wav_onetwomin))
    print('Wav files of 2 to 3 minutes : ', len(wav_threemin))
    print('Wav files of 3 to 5 minutes : ', len(wav_fivemin))
    print('Wav files of 5 to 10 minutes : ', len(wav_dixmin))
    print('Wav files of more than 10 minutes : ', len(wav_more))
    wav_files = list(wav_onemin.keys()) + list(wav_onetwomin.keys()) + list(wav_threemin.keys()) + list(
        wav_fivemin.keys()) + list(wav_dixmin.keys()) + list(wav_more.keys())
    return wav_files


def stats(path1, path2):
    wav_f = get_wav_files(path1)
    wav_f_2 = get_wav_files(path2)
    wav_f_info = length_wav_files(path1, wav_f)
    wav_f_2_info = length_wav_files(path2, wav_f_2)
    print('Stats of wav files from japhug online directory : ')
    stats_wav(wav_f_info)
    print('Stats of wav files from japhug not online directory : ')
    stats_wav(wav_f_2_info)
    # return stats_wav(wav_f_info)
