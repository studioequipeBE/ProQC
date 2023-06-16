#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main

# == IMPORTS ==
import hashlib
import imageio
import os
import sqlite3
import xml.etree.ElementTree as xmlparser

import fonctions as fct


ffmpeg = fct.getFFmpeg()
os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg


# Liste de fichier à faire une cache.
liste_fichier = []

# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    xml = xmlparser.parse('C:\\Users\\win10dev\\Desktop\\cache.xml')
    fichiers = xml.getroot().find('fichiers')

    # Récupère tous les fichiers :
    for fichier in fichiers.findall('fichier'):
        liste_fichier.append(fichier.find('chemin').text)
        print('Fichier : ' + fichier.find('chemin').text)
        print('Fichier existe : ' + str(os.path.isfile(fichier.find('chemin').text)))
        print('')

    # On fait la cache de tous les fichiers :
    for fichier in liste_fichier:
        # Image quoi ? RGB/NB??? En fait, cette information est importante...
        reader = imageio.get_reader(fichier, ffmpeg_params=['-an'])

        # Construit une DB :
        con = sqlite3.connect('C:\\Users\\win10dev\\Desktop\\' + os.path.basename(fichier) + '.db')
        cur = con.cursor()

        # Table contenant les informations sur le fichier.
        cur.execute('''
        CREATE TABLE IF NOT EXISTS fichier
        (
            id INTEGER NOT NULL,
            nom TEXT NOT NULL UNIQUE,
            duree_image INTEGER NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        )
        ''')

        # Table contenant les MD5 :
        cur.execute('''
        CREATE TABLE IF NOT EXISTS md5
        (
            id INTEGER NOT NULL,
            numero_image INTEGER NOT NULL,
            hash TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        )
        ''')

        framerate = int(reader.get_meta_data()['fps'])

        print('- Framerate : ' + str(framerate))

        duree_seconde = str(reader.get_meta_data()['duration']).split('.')

        duree = int(duree_seconde[0]) * framerate + int((int(duree_seconde[1]) / 100) * framerate)

        # Info du fichier analysé :
        cur.execute(
            'INSERT INTO fichier(nom, duree_image) VALUES("' + os.path.basename(fichier) + '", ' + str(duree) + ')')
        con.commit()

        # Chaque iteration équivaut à une image :
        for i, image in enumerate(reader, 0):

            # Affiche l'avancement tous les 30 secondes :
            if (i % (framerate * 30)) == 0:
                print(str(i) + ' / ' + str(duree))

            hash = hashlib.md5(image).hexdigest()

            cur.execute(
                'INSERT INTO md5(numero_image, hash) VALUES(' + str(i) + ', "' + hash + '")')
            con.commit()

        # On clôture tous les flux :
        reader.close()

        # Ferme flux DB.
        cur.close()
        con.close()

print('Fin création cache.')
