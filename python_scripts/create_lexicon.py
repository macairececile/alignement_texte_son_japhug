import xml.etree.ElementTree as ET


def extract_information(xml):
    """Extract information from xml dictionary"""
    tree = ET.parse(xml)
    root = tree.getroot()  # lexical resources
    info = dict()
    for child in root:
        for el in child.findall('LexicalEntry'):
            lexical_entry = el.get('id')
            lemma = el.find('Lemma').find('feat').get('val')
            info[lemma] = lexical_entry
            for i in el.findall('RelatedForm'):
                if i.find('a') is None:
                    continue
                related_form_1 = i.find('a').text
                related_form_2 = i.find('a').get('href')
                info[related_form_1] = related_form_2
    return info


def save_information(file, info):
    with open(file, 'w+') as f:
        for k, v in info.items():
            f.write(k + ' ' + v + '\n')


if __name__ == '__main__':
    path = '/home/macaire/Bureau/Stage_2020/'
    # extract_info = extract_information(path + 'japhug_dictionary.xml')
    # segment_phonemes(extract_info)
    # save_information('/home/macaire/Bureau/Stage_2020/lexicon_japhug.txt', extract_info)
