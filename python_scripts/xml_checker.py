import os
import re
import xml.etree.ElementTree as ET

items_notes = ['X', '(superlative)', '(causatif)', '(ideoph)', '(passive)', '(au', 'fur', 'et', 'à', 'mesure)']

items_to_delete = ['/?/', '//?//', '????', '(?)', '(???)', '*', '...', '(...)', 'ǀǀǀǀǀǀ', '/.../', '...,',
                   '....', '-', '\"']


def extract_information(xml):
    """Extract information from xml dictionary with another configuration"""
    tree = ET.parse(xml)
    root = tree.getroot()  # lexical resources
    transcript = root.find('FORM').text  # get content from tag FORM
    lines = [e + '\n' for e in transcript.split('\n') if e]
    lines = [lines[i].split() for i, j in enumerate(lines)]
    return lines


def check_notes(text):
    notes = {}
    mistakes = {}
    chinese = {}
    length_text = [len(x) for x in text]
    length_text = sum(length_text)
    for i, j in enumerate(text):
        for k, l in enumerate(j):
            c = re.findall(r'[\u4e00-\u9fff]+', l)
            digits = re.findall(r'^\(\d+', l)
            for el in digits:
                notes.setdefault(el + '...)', [])
                notes[el+ '...)'].append(i)
            if '=' in l:
                notes.setdefault(l, [])
                notes[l].append(i)
            if 'xxx' in l:
                notes.setdefault(l, [])
                notes[l].append(i)
            for n in c:
                chinese[n] = i
            for m in items_notes:
                notes.setdefault(m, [])
                if m == l:
                    notes[m].append(i)
            for p in items_to_delete:
                mistakes.setdefault(p, [])
                if p == l:
                    mistakes[p].append(i)
    len_wrong = len(notes) + len(mistakes) + len(chinese)
    total_len_wrong = "%.2f" % round(len_wrong * 100 / length_text, 2)
    return total_len_wrong, notes, mistakes, chinese


def write_error_files(xml, percentage_errors, notes, mistakes, chinese):
    name_xml = os.path.splitext(xml)[0].split('/')[7]
    with open(name_xml + '_log.txt', 'w+') as f:
        f.write('Your file contains : ' + str(percentage_errors) + ' % of errors.\n\n')
        f.write('Items should be put in tag NOTE in xml :\n')
        notes = {k: v for k, v in notes.items() if len(v) != 0}
        mistakes = {k: v for k, v in mistakes.items() if len(v) != 0}
        if len(notes) != 0:
            for k, v in notes.items():
                f.write('- ' + k + ', line ' + str(v) + '\n')
        f.write('\n')
        f.write('Items that generate an error (wrong space, ...) :\n')
        if len(mistakes) != 0:
            for h, g in mistakes.items():
                f.write('- ' + h + ', line ' + str(g) + '\n')
        f.write('\n')
        f.write('Items which are chinese elements :\n')
        if len(chinese) != 0:
            for p, m in chinese.items():
                f.write('- ' + p + ', line ' + str(m) + '\n')


def ckech_errors(xml):
    data = extract_information(xml)
    perc, n, m, c = check_notes(data)
    write_error_files(xml, perc, n, m, c)


if __name__ == '__main__':
    xml_name = '/media/macaire/Ubuntu/Japhug/japhug_not_online/xml/hist160707_riquet2.xml'
    ckech_errors(xml_name)
