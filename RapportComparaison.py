#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : il gère le rapport généré.

# == IMPORTS ==
import datetime
import os
import sqlite3
from timecode import Timecode

import fonctions as fct
import TimecodeP as tc
from ListePoint import ListePoint
from Point import Point


class RapportComparaison:
    """
    Rapport pour les comparaisons de plusieurs images.
    """
    # == ATTRIBUTS ==

    # Numéro d'erreur.
    numero = 0

    # Framerate du fichier:
    framerate = None
    timecodestart = None
    duree_image = None
    resolution = None

    chemin_rapport = 'Rapports/'

    # ID du rapport QC dans la DB à utiliser.
    id_fichier_ref = 0

    # Le fichier qu'on compare à la ref.
    id_fichier_compare = 0

    def __init__(self, fichier_ref: str, nouveau_rapport: bool = True):
        """
        Création du rapport dans une base de données SQLite.

        :param str fichier_ref : Le fichier de référence.
        :param bool nouveau_rapport: Si on doit faire un nouveau rapport ou partir sur le précédent (fct que pour db).
        """
        self.fichier_ref = fichier_ref

        if not os.path.exists(self.chemin_rapport):  # Tu remplaces chemin par le chemin complet.
            os.mkdir(self.chemin_rapport)

        self.con = sqlite3.connect(fct.get_desktop() + os.sep + 'comparaison_' + fichier_ref + '.db')
        self.cur = self.con.cursor()

        # Si c'est un nouveau rapport, on créé les tables.
        if nouveau_rapport:
            # Table contenant les informations sur le fichier de référence.
            self.cur.execute('''
             CREATE TABLE IF NOT EXISTS fichier_ref
             (
                 id INTEGER NOT NULL,
                 nom TEXT NOT NULL UNIQUE,
                 duree_image INTEGER NOT NULL,
                 start_timecode TEXT NOT NULL,
                 framerate TEXT NOT NULL,
                 resolution TEXT NOT NULL,
                 debut_analyse TEXT NOT NULL,
                 fin_analyse TEXT,
                 PRIMARY KEY("id" AUTOINCREMENT)
             )
             ''')

            # Les fichiers utilisés pour la comparaison.
            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS fichier
            (
                id INTEGER NOT NULL,
                nom TEXT NOT NULL UNIQUE,
                start_timecode TEXT NOT NULL,
                duree_image TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
            ''')

            # Table avec les différences :
            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS difference
            (
                id INTEGER NOT NULL,
                id_fichier_ref TEXT NOT NULL,
                id_fichier_compare TEXT NOT NULL,
                tc_in INTEGER NULL,
                tc_out INTEGER NULL,
                pourcentage REAL NULL,
                nombre_canal INTEGER NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
            ''')

            # Pixel à mettre en évidence :
            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS pixel
            (
                id INTEGER NOT NULL,
                id_difference INTEGER NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
            ''')

    def set_information(self, duree: int = 0, timecodestart: str = '00:00:00:00', framerate: int = 24, resolution: str= '1920x1080') -> None:
        """
        On définit des informations du fichier de référence.

        :param int duree: La durée du fichier en image.
        :param str timecodestart: Timecode début du fichier.
        :param int framerate: Framerate du fichier.
        """
        self.framerate = framerate
        self.timecodestart = timecodestart
        self.duree_image = duree
        self.resolution = resolution

        # Info du fichier analysé :
        self.cur.execute(
            'INSERT INTO fichier_ref(nom, duree_image, start_timecode, framerate, resolution, debut_analyse) VALUES("'
            + self.fichier_ref + '", ' + str(duree) + ', "' + timecodestart + '", "'
            + str(self.framerate) + '", "' + self.resolution + '", "' + str(datetime.datetime.now()) + '")')
        self.con.commit()

        res = self.cur.execute(
            'SELECT id FROM fichier_ref WHERE nom= "' + self.fichier_ref + '" ORDER BY id DESC LIMIT 1')
        self.id_fichier_ref = res.fetchall()[0][0]

    def add_fichier(self, nom_fichier: str, timecodestart: str, duree_image: int):
        """
        Ajoute un fichier à comparer et le définit comme celui courant.
        """
        self.cur.execute(
            'INSERT INTO fichier(nom, start_timecode, duree_image) VALUES("'
            + nom_fichier + '", "' + timecodestart + '", ' + str(duree_image) + ')')
        self.con.commit()

        res = self.cur.execute(
            'SELECT id FROM fichier WHERE nom= "' + nom_fichier + '" ORDER BY id DESC LIMIT 1')

        # Définit le fichier courant qu'on QC.
        self.id_fichier_compare = res.fetchall()[0][0]

    def add_difference(self, tc_in: str, tc_out: str, pourcentage: float, nombre_canal: int, pixels: ListePoint) -> None:
        """
        Écrire dans le rapport.

        :param str tc_in: Timecode in.
        :param str tc_out: Timecode out.
        :param float pourcentage: Pourcentage de différence.
        :param list[int, int] pixels: Liste des pixels de différence.
        """
        self.cur.execute(
            'INSERT INTO difference(id_fichier_ref, id_fichier_compare, tc_in, tc_out, pourcentage, nombre_canal)'
            'VALUES'
            '(' + str(self.id_fichier_ref) + ', ' + str(self.id_fichier_compare)
            + ', "' + tc_in + '", "' + tc_out + '", ' + format(pourcentage, '.6f') + ', ' + str(nombre_canal) + ')'
        )

        id_diff = str(self.cur.lastrowid)

        if pixels.size() > 0:
            for pixel in pixels.get_liste():
                self.cur.execute(
                    'INSERT INTO pixel(id_difference, x, y)'
                    'VALUES'
                    '(' + id_diff + ', ' + str(pixel.x) + ', ' + str(pixel.y) + ')')
        self.con.commit()

    def close(self) -> None:
        """
        Clôture les flux sur la base de données.
        """
        # On indique que le fichier a fini d'être analysé.
        print('Fin analyse : ' + str(datetime.datetime.now()))
        self.cur.execute('UPDATE fichier_ref SET fin_analyse = "' + str(datetime.datetime.now()) + '"')
        self.con.commit()

        # Récupère les informations de l'image ref
        self.cur.execute('SELECT nom, start_timecode, duree_image, resolution, framerate FROM fichier_ref')
        info = self.cur.fetchall()[0]

        framerate = int(info[4])

        # Écrit le fichier JSON depuis la base de données.
        json = open(self.chemin_rapport + '/JSON/rapport-difference_' + info[0] + '.json', 'w', encoding='utf-8')
        json.write('{\n')
        json.write('\t"fichier" : "' + info[0] + '",\n')
        json.write('\t"type_erreur" : "difference",\n')
        json.write('\t"start_timecode" : "' + info[1] + '",\n')
        json.write('\t"duree" : "' + tc.frames_to_timecode(int(info[2]), framerate) + '",\n')
        json.write('\t"resolution" : "' + info[3] + '",\n')
        json.write('\t"framerate" : "' + str(framerate) + '",\n')

        json.write('\t"compare" :\n')
        json.write('\t[\n')

        i = 0

        self.cur.execute('SELECT nom, start_timecode, duree_image FROM fichier ORDER BY start_timecode ASC')
        for row in self.cur.fetchall():
            print(row)
            if i != 0:
                json.write(',\n')

            json.write('\t\t{\n')
            json.write('\t\t\t"fichier" : "' + row[0] + '",\n')
            json.write('\t\t\t"start_timecode" : "' + row[1] + '",\n')
            json.write('\t\t\t"duree" : "' + tc.frames_to_timecode(int(row[2]), framerate) + '"\n')
            json.write('\t\t}\n')
            i += 1

        json.write('\t],\n')

        json.write('\t"remarque" :\n')
        json.write('\t[\n')

        i = 0

        start_frame = Timecode(framerate, info[1]).frames - 1

        self.cur.execute('SELECT tc_in, tc_out, pourcentage, nombre_canal, id FROM difference ORDER BY tc_in, tc_out ASC')
        for row in self.cur.fetchall():
            print(row)
            if i != 0:
                json.write(',\n')

            json.write('\t\t{\n')
            json.write('\t\t\t"tc_in" : "' + tc.frames_to_timecode(int(row[0]) + start_frame, framerate) + '",\n')
            json.write('\t\t\t"tc_out" : "' + tc.frames_to_timecode(int(row[1]) + start_frame, framerate) + '",\n')
            json.write('\t\t\t"pourcentage" : ' + format(row[2], '.6f') + ',\n')
            json.write('\t\t\t"nombre_canal" : ' + str(row[3] if row[3] is not None else 0) + ',\n')

            json.write('\t\t\t"pixels" : [\n')

            # On va rechercher tous les pixels intéressants à mettre en évidence :
            j = 0
            self.cur.execute('SELECT x, y FROM pixel WHERE id_difference = ' + str(row[4]))
            for pixel in self.cur.fetchall():
                if j != 0:
                    json.write(',\n')

                json.write('\t\t\t\t{\n')
                json.write('\t\t\t\t\t"x" : ' + str(pixel[0]) + ',\n')
                json.write('\t\t\t\t\t"y" : ' + str(pixel[1]) + '\n')
                json.write('\t\t\t\t}')

                j += 1

            json.write('\n')

            json.write('\t\t\t],\n')

            json.write('\t\t\t"remarque" : "Différence."\n')
            json.write('\t\t}')
            i += 1

        json.write('\n')

        json.write('\t]\n')
        json.write('}\n')
        json.close()

        self.cur.close()
        self.con.close()
