# Alignement Texte-Son de documents de langue Japhug

Ce répertoire comprend l'ensemble des données et les scripts réalisés tout au long de mon stage au LACITO-CNRS. 

- **Dictionnaire** : comprend le dictionnaire + lexicon de la langue japhug.
- **Japhug** : données de la langue japhug séparées en deux dossiers : online et not online. Chaque dossier comprend les enregistrements .wav et leur transcription .xml.
- **python_scripts** : scripts python
- **correct_alignment_japhug** : dossier avec les données dont l'alignement entre audio et transcription est correct.


## Python_script : xml_info_japhug.py

Ce script permet l'ajout de balises temporelles dans le xml pour chaque ligne de transcription en IPA de la langue japhug. WebMaus va être utilisée pour générer un alignement temporel forcé entre transcription et audio. A noter que l'alignement produit est correct pour les audios de moins de 4 minutes.


### Prérequis
#### Librairies

- xml.etree.ElementTree (API pour parser et créer des données XML)
- wave (Lecture et écriture des fichiers WAV)
- librosa (Librairie python pour l'analyse des audios)
- textgrids (Manipulation TextGrid Praat en python)
- xml.dom.minidom 
- pydub (Audio processing tool)
- lxml
- hanzidentifier (Librairie Python qui identifie une chaîne de texte comme ayant des caractères simplifiés ou traditionnels Chinois)
- urllib.request (Librairie pour lire URL)


#### Structure des données

Le script nécessite la création de 6 dossiers:

**wav/** - fichiers .wav


**wav_mono/** - fichiers .wav mono


**xml/** - fichiers .xml (transcriptions)


**xml_new/** - fichiers .xml (transcriptions avec timecodes)


**par/** - fichiers .par générés pour MAUS


**textGrid/** - fichiers .TextGrid générés par MAUS après alignement.


#### Fichiers en entrée

Deux types de fichiers sont attendus; les fichiers .wav (dans dossier **wav**) avec leur transcription respective dans un fichier xml (dans dossier **xml**), dont la structure est comme suit:
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TEXT SYSTEM "https://cocoon.huma-num.fr/schemas/Archive.dtd">
<TEXT id="_id_" xml:lang="jya">
    <HEADER>
</HEADER>
    <FORM>*transcription en IPA*</FORM>
</TEXT>
```


### Procédure

L'ensemble des opérations sont regroupées dans `def process()`.


1. Conversion des fichiers .wav stéréo en mono avec `def convert_mono(path, path_export, file)`.


2. Création des fichiers .par (BAS Partitur Format : https://www.bas.uni-muenchen.de/forschung/Bas/BasFormatseng.html#Partitur) pour WebMAUS General (https://clarin.phonetik.uni-muenchen.de/BASWebServices/interface/WebMAUSGeneral) qui comprend la transcription de l'audio.

La fonction `def process_xml(path_wav, path_xml, path_par, wav_file, xml_file)` récupère la fréquence d'échantillonage de l'audio, son nom (fichiers .wav et .par doivent avoir le même nom), extrait la transcription du xml avec `def extract_information(xml_file)` et crée le .par avec `def create_par(text, file, frame_rate)`. 

La variable _items_to_delete_ regroupe l'ensemble des annotations qui ne correspondent pas à la transcription en IPA du japhug (commentaires, notes, etc.).


3. Lancement de WebMAUS General par requête HTTP et récupération du fichier de sortie TextGrid comprenant l'alignement de la transcription avec l'audio.

La fonction `run_Maus(path_wav, path_par, path_save, wav_file, par_file)` lance la requête HTTP par cette ligne de commande :
```bash
curl -v -X POST -H \'content-type: multipart/form-data\' -F SIGNAL=@' + path_wav + wav_file + ' -F LANGUAGE=sampa -F INSKANTEXTGRID=false -F MODUS=align -F RELAXMINDUR=false -F OUTFORMAT=TextGrid -F TARGETRATE=100000 -F ENDWORD=999999 -F STARTWORD=0 -F INSYMBOL=ipa -F PRESEG=false -F USETRN=false -F BPF=@' + path_par + par_file + ' -F MAUSSHIFT=10 -F INSPROB=0.0 -F INSORTTEXTGRID=false -F MINPAUSLEN=5 -F OUTSYMBOL=ipa -F WEIGHT=default -F NOINITIALFINALSILENCE=false -F ADDSEGPROB=false \'https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runMAUS\'
```

Le fichier .TextGrid généré est ensuite téléchargé et stocké dans le dossier **textGrid**.


4. Ajout des informations dans les fichiers .xml  (timecodes pour chaque ligne, balise Note) avec la fonction `def update_xml(path, path2, textGrid_file, wav_file, xml_file)`. 

On extrait les informations du TextGrid avec `def extract_info_textGrid(textgrid)`. Le dictionnaire en sortie regroupe pour chaque _id_ de ligne les informations temporelles de début et fin. 

`def add_xml_info(timecode, wav_file, xml_file)` ajoute les informations dans le xml. Un exemple de fichier xml, dans le dossier **xml_new** :
```xml
<?xml version="1.0" ?>
<!DOCTYPE TEXT SYSTEM "https://cocoon.huma-num.fr/schemas/Archive.dtd">
<TEXT id="id" xml:lang="jya">
	<HEADER>
		<TITLE>xml_with_timec</TITLE>
		<SOUNDFILE href="hist140426_jla_ra_nWrmi.wav"/>
	</HEADER>
	<S id="S001">
		<AUDIO start="0.65" end="3.3"/>
		<FORM kindOf="phono">﻿tɕe jla ra nɯ tɕe, nɯ-rmi li dɤn ma</FORM>
	</S>
	<NOTE message="=================" xmlns:lang="fr"/>
	<S id="S002">
		<AUDIO start="3.8" end="6.78"/>
		<FORM kindOf="phono">jla kɯ-ɤskɯ kɯ-fse nɯ chaŋskɯ tu-kɯ-ti ŋgrɤl. </FORM>
	</S>
</TEXT>
```
