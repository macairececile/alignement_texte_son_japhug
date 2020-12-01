import re
import shutil
import xml.etree.ElementTree as et
import string as s
import wave as wav
from os import listdir
from os.path import isfile, join
import librosa
import textgrids as tg
import os
import xml.dom.minidom
from pydub import AudioSegment
from lxml import etree
import hanzidentifier
import subprocess
import urllib.request

irrelevant_annotations = ['!)', '"', '"/???/', '(', '(!!!', '(...)', '(?)', '(??)', '(???)', '(agreement',
                          '(anticausative)', '(antipassif)', '(associated', '(au', '(autoben)', '(autoben+anticaus)',
                          '(autobenefactive)', '(benefactif)', '(calque', '(calque)', '(calque?)', '(cataphoric)',
                          '(causatif)', '(causation)', '(causative)', '(causative,', '(cleft)', '(comme)',
                          '(complementation', '(complementation)', '(conatif)', '(conative)', '(converb)', '(dative)',
                          '(diminutive)', '(en', '(erreur', '(faute)6:40', '(faux:', '(floating)', '(focalisation,',
                          '(focus)', '(generic)', '(hybrid?)', '(ideoph', '(ideoph)', '(ideoph.pause).', '(il', '(ils',
                          '(imp?', '(imperative', '(in', '(indefinite)', '(infinitive)', '(intensif', '(inverse',
                          '(inverse', '(inverse', '(inverse)', '(inverse+associated', '(inverse?', '(nominal', '(pas',
                          '(passive)', '(permansive)', '(pluriel)', '(possessive)', '(redp)', '(reduplication',
                          '(relation', '(relative)', '(revoir)', '(right', '(superlative)', '(trill)', ')', '*', ',',
                          '-', '..', '...', '...,', '....', '/', '/.../', '//', '//?//', '/?/', '/???/', '050)',
                          '0805)', '1015)', '200)', '2:00', '?', '?"', '??', '??', '???', '???,', '????', 'X', '\\b',
                          'adjectives)', 'causee)', 'ce', 'dans', '(050', 'de', 'de', 'deux', 'deux', 'deux', 'disloc)',
                          'emph)', 'entre', 'et', 'fact?', 'fur', 'hybrid)', 'inanimés).', 'inanimés).', 'inverse)',
                          "l'original,", 'la', 'lui', 'main)', 'mange', 'manner)(testimonial)', 'mesure)', 'mismatch)',
                          'modifiers,', 'motion)', 'motion,', 'n\'avaient', 'particulier)', 'parties', 'passif',
                          'preventive)', 'quasi-clivée)', 'qui', 'redp)', 'relative,', 'rien', 'permansif?)', 'sous',
                          'strategy)', 'that)', 'tombe', 'tout', 'traduction', 'à', 'ǀǀǀǀǀǀ', '(IMM)', 'khWjNga2',
                          '(faute)', 'ǀǀǀǀǀǀ\"', '(demonstrative,', 'pronouns,', 'present)', '(kɯ?', '730)',
                          'possessor)']


# ------------------------------------- #
# Functions on wav files :              #
# - retrieve sampling rate from wav     #
# - get all files from a directory      #
# - get the duration of a wav file      #
# - convert from stereo to mono wav     #
# ------------------------------------- #

def get_sampling_rate(file):
    """Get the sample rate of a wav file"""
    with wav.open(file, "rb") as wave_file:
        frame_rate = str(wave_file.getframerate())
    return frame_rate


def get_files_from_directory(path):
    """Get all wav files"""
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return files


def length_wav_file(path, file):
    """Get the duration in secondes of a wav file"""
    return librosa.get_duration(filename=path + file)


def convert_mono(path, path_export, file):
    """Convert wav stereo files into mono wav files"""
    sound = AudioSegment.from_wav(path + file)
    sound = sound.set_channels(1)
    sound.export(path_export + file, format="wav")


def mute_sound(path_wav, wav_file):
    # mute a part of a sound between seconds of audio file
    command = 'ffmpeg -i ' + path_wav + wav_file + ' -af \"volume=enable=\'between(t,23.31,29.64)\':volume=0" ' + path_wav + wav_file[
                                                                                                                             :-4] + '_cut.wav'
    subprocess.check_output(command, shell=True)


# ------------------------------------- #
# Extract information from xml file and #
#      generate PAR file for MAUS       #
# ------------------------------------- #
def extract_information(xml_file):
    """Extract the transcription from xml file"""
    tree = et.parse(xml_file)
    root = tree.getroot()  # lexical resources
    transcript = root.find('FORM').text  # get content from tag FORM
    return transcript


def create_par(text, file, frame_rate):
    """Create PAR file from the transcription previously extracted from xml file"""
    words_tr2 = [e + '\n' for e in text.split('\n') if e]  # split text by lines
    words_tr2 = [i.replace('\ufeff', '') for i in words_tr2]  # remove space at the beginning
    words_tr2 = [i.replace('>', '') for i in words_tr2]  # remove '>'
    digits = [re.findall(r'\(\d+.*\)', l) for l in words_tr2]  # find all the digits of the form '(201)'
    for k, p in enumerate(words_tr2):
        if len(digits[k]) != 0:
            words_tr2[k] = words_tr2[k].replace(digits[k][0], '')  # and delete them 
    words_tr2 = [words_tr2[i].split() for i, j in enumerate(words_tr2)]  # split sentences into words
    words_tr2 = [[i for i in nested if (
            i not in irrelevant_annotations and not hanzidentifier.has_chinese(
        i) and 'xxxx' not in i and '---' not in i and '\\c' not in i and 'FICHIER' not in i and '=' not in i)] for
                 nested in
                 words_tr2]  # delete characters for MAUS
    words_tr2 = list(filter(None, words_tr2))  # remove blank lines
    words = [x for z in words_tr2 for x in z if x]  # extract all the words from sublist
    replace_characters = {'-': '', 'g': 'ɡ', 'ʁ': 'ʀ', 'ɯ́': 'ɯ', 'ɤ́': 'ɤ', 'ó': 'o', 'ú': 'u', 'ɢ': 'ɣ', '2': 'ø',
                          '4': 'ɾ', 'M': 'ɯ', 'T': 't', 'ü': 'y', 'û': 'u', 'é': 'e', 'B': 'b', 'à': 'a', 'á': 'a',
                          '，': '', 'A': 'a', 'U': 'u', 'h́': 'h', '@': '', '（': '(', '）': ')', '6': 'ɐ', '9': 'œ',
                          '7': 'ɤ', '0': '', 'Z': 'z', 'ù́': 'u', 'í': 'i', '1': 'ɨ', '3': ''}
    for k, v in replace_characters.items():
        words = [w.replace(k, v) for w in words]
    words = [w.translate(str.maketrans('', '', s.punctuation)) for w in words]  # delete punctuation
    phonemes = [i for i in words]  # separate each 'letter' of each word
    if len(words) != 0:
        with open(file, 'w+') as f1:  # create the par file
            f1.write('LHD: Partitur 1.3.1' + '\n' + 'SAM: ' + frame_rate + '\n' + 'LBD:' + '\n')
            for i, j in enumerate(words):
                char = ''
                for el in phonemes[i]:
                    char += el + ' '
                f1.write('KAN: ' + str(i) + ' ' + char + '\n')  # add KAN level
            for i, j in enumerate(words):
                f1.write('ORT: ' + str(i) + ' ' + j + '\n')  # add ORT level
            compt = 0
            for i, j in enumerate(words_tr2):  # add TR2 level with '\n' for end of sentence
                for k, m in enumerate(words_tr2[i]):
                    if k == len(words_tr2[i]) - 1:
                        m = m + "\\n"
                        f1.write('TR2: ' + str(compt) + ' ' + m + '\n')
                        compt += 1
                    else:
                        f1.write('TR2: ' + str(compt) + ' ' + m + '\n')
                        compt += 1
        return True
    else:
        return False


def process_xml(path_wav, path_xml, path_par, wav_file, xml_file):
    """Extract info from xml and create par"""
    frame_rate = get_sampling_rate(path_wav + wav_file)
    wav_file_name = os.path.splitext(path_wav + wav_file)[0].split('/')[7]  # get filename from wav file
    extract_info = extract_information(path_xml + xml_file)
    create_par(extract_info, path_par + wav_file_name + '.par', frame_rate)  # create the par file with the same
    # name as wav file


# ------------------------------------- #
# Extract and add information from      #
# textGrid generated by MAUS in xml     #
# files                                 #
# ------------------------------------- #

def extract_info_textGrid(textgrid):
    """"Extract information from textGrid generate by MAUS"""
    data = {}
    grid = tg.TextGrid(textgrid)  # extract TextGrid
    time = []
    compt = 0
    for item in grid['TR2-MAU']:  # extract timecodes
        if item.text != "" and '\\n' in item.text and len(time) == 0:
            time.append(item.xmin)
            time.append(item.xmax)
        else:
            if item.text != "" and '\\n' not in item.text and len(time) == 0:
                time.append(item.xmin)
            elif '\\n' in item.text and '.' in item.text:
                time.append(round(item.xmax, 2))
            elif '\\n' in item.text:
                time.append(item.xmax)
        if len(time) == 2:
            data[compt] = time
            time = []
            compt += 1
    return data


def add_xml_info(timecode, wav_file, xml_file):
    """Add information for each transcription lines in xml file"""
    tree = etree.parse(xml_file)
    root = tree.getroot()  # lexical resources
    header = root.find('HEADER')
    time_begin = 0
    if header.find("TITLE") is None:  # add information into HEADER
        title = etree.SubElement(header, 'TITLE')
        title.text = xml_file.split('/')[7][:-4]
        sound_file = etree.SubElement(header, 'SOUNDFILE', href=wav_file)
    identifiant = 0
    has_s = False
    sentences = []
    if root.find('FORM') is not None:  # extract transcription from FORM
        transcript = root.find('FORM')
        trans = list(filter(None, transcript.text.split('\n')))
        identifiant = 0
    else:
        has_s = True
        trans = []
        sentences = root.findall('S')
        for i, j in enumerate(sentences):
            if j.find('FORM') is not None:
                identifiant = int(j.attrib['id'][1:])
                time_begin = float(j.find('AUDIO').attrib['end'])
            else:
                trans.append(j.text)
        sentences = [el for el in sentences if el.find('FORM') is None]
    for key, value in timecode.items():
        value[0] += time_begin
        value[1] += time_begin
    num = 0
    for i, j in enumerate(trans):  # for each line
        if '==' in j or 'xxxx' in j or '---' in j or '\\c' in j or '\\b' in j or (
                j.startswith('(') and j.isdigit() and j.endswith(')')) or 'khWjNga2' in j:
            nsmap = {"lang": "fr"}
            tag = etree.SubElement(root, "NOTE", nsmap=nsmap, message=j)  # add NOTE element for specific characters
        elif num < len(timecode):  # add timecode until the end
            if 0 <= identifiant < 9:
                if has_s:
                    tag = sentences[i]
                    tag.set('id', 'S00' + str(identifiant + 1))
                    tag.text = None
                else:
                    tag = etree.SubElement(root, "S", id='S00' + str(identifiant + 1))
            elif 9 <= identifiant < 99:
                if has_s:
                    tag = sentences[i]
                    tag.set('id', 'S0' + str(identifiant + 1))
                    tag.text = None
                else:
                    tag = etree.SubElement(root, "S", id='S0' + str(identifiant + 1))
            elif 99 <= identifiant < 999:
                if has_s:
                    tag = sentences[i]
                    tag.set('id', 'S' + str(identifiant + 1))
                    tag.text = None
                else:
                    tag = etree.SubElement(root, "S", id='S' + str(identifiant + 1))
            time = etree.SubElement(tag, 'AUDIO', start=str(round(timecode[num][0], 2)),
                                    end=str(round(timecode[num][1], 2)))
            form = etree.SubElement(tag, 'FORM', kindOf="phono")
            form.text = j
            num += 1
            identifiant += 1
        else:
            if not has_s:
                tag = etree.SubElement(root, "S")
                tag.text = j
    form = root.find('FORM')
    if form is not None:
        root.remove(form)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)  # create xml file with the new annotations
    dom = xml.dom.minidom.parse(xml_file)  # or xml.dom.minidom.parseString(xml_string) 
    pretty_xml_as_string = dom.toprettyxml()  # correctly print xml file
    pretty_xml_as_string = '\n'.join([line for line in pretty_xml_as_string.split('\n') if line.strip()])
    lines = pretty_xml_as_string.split('\n')
    del lines[1:3]
    lines.insert(1, '<!DOCTYPE TEXT SYSTEM "https://cocoon.huma-num.fr/schemas/Archive.dtd">')
    for k, m in enumerate(lines):
        if '<AUDIO' in m:
            a = m.split(' ')
            if 'end' in a[1]:
                a[1:3] = a[1:3][::-1]
                a[1] = a[1][:-2]
                a[2] = a[2] + '/>'
                lines[k] = ' '.join(a)
    pretty_xml_as_string = '\n'.join(lines)
    pretty_xml_as_string = pretty_xml_as_string.replace("&quot;", "\"")
    with open(xml_file, "wb") as f:
        f.write(pretty_xml_as_string.encode('utf-8'))


def update_xml(path, path2, textGrid_file, wav_file, xml_file):
    """Extract info from textgrid and add information in xml file"""
    time = extract_info_textGrid(path + textGrid_file)
    add_xml_info(time, wav_file, path2 + xml_file)


def get_name_files(path, string):
    """Get names from string"""
    name_wav = os.path.splitext(path + string)[0].split('/')[7]
    name_par = name_wav + '.par'
    name_xml = 'crdo-JYA_' + str.upper(name_wav) + '.xml'
    name_textGrid = os.path.splitext(path + string)[0].split('/')[7] + '.TextGrid'
    return name_wav, name_xml, name_par, name_textGrid


def get_name_files_bis(path, string):
    name_wav = os.path.splitext(path + string)[0].split('/')[7]
    name_par = name_wav + '.par'
    name_xml = name_wav + '.xml'
    name_textGrid = name_wav + '.TextGrid'
    return name_wav, name_xml, name_par, name_textGrid


# ----------------------------------- #
#               Run MAUS              #
# ----------------------------------- #
def run_Maus(path_wav, path_par, path_save, wav_file, par_file):
    """Run maus with command line and download the textGrid file in the corresponding folder"""
    command = 'curl -v -X POST -H \'content-type: multipart/form-data\' -F SIGNAL=@' \
              + path_wav + wav_file + ' -F LANGUAGE=sampa -F INSKANTEXTGRID=false -F ' \
                                      'MODUS=align -F RELAXMINDUR=false -F OUTFORMAT=TextGrid -F ' \
                                      'TARGETRATE=100000 -F ENDWORD=999999 -F STARTWORD=0 -F INSYMBOL=ipa -F ' \
                                      'PRESEG=false -F USETRN=false -F BPF=@' + path_par + par_file + \
              ' -F MAUSSHIFT=10 -F INSPROB=0.0 -F INSORTTEXTGRID=false -F MINPAUSLEN=5 -F ' \
              'OUTSYMBOL=ipa -F WEIGHT=default -F NOINITIALFINALSILENCE=false -F ' \
              'ADDSEGPROB=false ' \
              '\'https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runMAUS\''
    result = subprocess.check_output(command, shell=True)  # run the MAUS command
    # retrieve the dowload link textGrid file
    url = (''.join(str(result).split('<downloadLink>')[1])).split('</downloadLink>')[0]
    name_file = str(url.split('/')[-1])
    urllib.request.urlretrieve(url, path_save + name_file)  # save textGrid file into specific folder


def process():
    """Main process -> run the steps to add information in xml file from textGrid"""
    path_1 = '/media/macaire/Ubuntu/Japhug/japhug_online/wav/'
    path_2 = '/media/macaire/Ubuntu/Japhug/japhug_online/xml/'
    path_3 = '/media/macaire/Ubuntu/Japhug/japhug_online/par/'
    path_4 = '/media/macaire/Ubuntu/Japhug/japhug_online/wav_mono/'
    path_5 = '/media/macaire/Ubuntu/Japhug/japhug_online/textGrid/'
    path_6 = '/media/macaire/Ubuntu/Japhug/japhug_online/xml_with_timecodes/'
    files = get_files_from_directory(path_1)
    for i in files:
        convert_mono(path_1, path_4, i)
        name_wav, name_xml, name_par, name_textGrid = get_name_files(path_1, i)
        try:
            process_xml(path_1, path_2, path_3, i, name_xml)
            run_Maus(path_4, path_3, path_5, i, name_par)
            update_xml(path_5, path_6, name_textGrid, i, name_xml)
        except:
            print(name_xml)


if __name__ == '__main__':
    process()
