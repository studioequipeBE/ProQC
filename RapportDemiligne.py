#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import sqlite3
from timecode import Timecode
from typing import NoReturn

import TimecodeP as tc


class RapportDemiligne:
    """
    Rapport QC pour les remarques de demiligne.
    Il gère le rapport.
    Export aussi une version JSON pour faciliter les traitements.
    Backup dans une base de données SQLite le traitement en cours.
    """

    def __init__(self, fichier):
        """
        Création du rapport en .txt ou HTML, on pourrait faire un rapport en HTML, plus classe voir ajouter les valeurs dans la base de donnees de QC.
        """
        # Numéro d'erreur.
        self.numero = 0

        # Framerate du fichier:
        self.framerate = None
        self.tc_debut = None
        self.resolution = None

        # Type de rapport (HTML, txt):
        self.chemin_rapport = "Rapports/"

        # ID du projet dans la base de données :
        self.id_projet = None

        # Base de données avec le rapport en cours. (on va essayer de créer le rapport à la fin !)
        self.db = None
        self.cur = None  # curseur pour faire les opérations sur la base de données.

        self.fichier = fichier

        self.ratio = None
        self.duree_image = None
        self.timecodestart = None

        # On crée dans la base de données, isolation_level en None = autocommit.
        self.db = sqlite3.connect('data.db', isolation_level=None)
        self.cur = self.db.cursor()

        # Si la table n'existe pas, on la créée :
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS projet (id INTEGER PRIMARY KEY AUTOINCREMENT, fichier TEXT, statut TEXT, image_analyse TEXT, resolution TEXT, framerate TEXT, ratio TEXT)''')
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS remarque (id_projet TEXT, tc_in TEXT, tc_out TEXT, probleme TEXT, option TEXT)''')

        if not os.path.exists(self.chemin_rapport):  # Tu remplaces chemin par le chemin complet.
            os.mkdir(self.chemin_rapport)

    def projet_en_cours(self) -> int:
        """
        Indique si un projet est en cours.
        """
        self.cur.execute("SELECT count(*) FROM projet WHERE statut LIKE 'en cours'")

        return self.cur.fetchall()[0]

    def start(self, duree_image: int, timecodestart: str = '00:00:00:00', framerate: int = 24, ratio: str = '2.39',
              resolution: str = '1920x1080') -> NoReturn:
        """
        Quand on commence le rapport.
        """
        self.ratio = ratio
        self.duree_image = duree_image
        self.timecodestart = timecodestart

        self.framerate = int(framerate)
        self.resolution = resolution

        self.tc_debut = int(Timecode(framerate, timecodestart).frames - 1)

        # Ajoute le projet en base de données.
        self.cur.execute("INSERT INTO projet (fichier, statut, image_analyse, resolution, framerate, ratio)" +
                         "VALUES ('" + self.fichier + "', 'en cours', '0', '" + self.resolution + "', '" + str(
            self.framerate) + "', '" + self.ratio + "')")

        # Récupère l'ID de la dernière entrée :
        self.id_projet = self.cur.lastrowid

    def add_probleme(self, tc_in_image: int, tc_out_image: int, probleme: str, option: str) -> NoReturn:
        """
        Ajoute une erreur dans le rapport.
        """

        tc_in_tc = tc.frames_to_timecode(int(tc_in_image) + self.tc_debut, self.framerate)
        tc_out_tc = tc.frames_to_timecode(int(tc_out_image) + self.tc_debut, self.framerate)

        self.cur.execute("INSERT INTO remarque VALUES ('" + str(
            self.id_projet) + "', '" + tc_in_tc + "', '" + tc_out_tc + "', '" + probleme + "', '" + option + "')")

    def savestate(self, num_image: int) -> NoReturn:
        """
        Indique jusqu'où on était dans le rapport s'il y a eu un crash.
        """
        self.cur.execute(
            'UPDATE projet SET image_analyse = "' + str(num_image) + '" WHERE id LIKE "' + str(self.id_projet) + '"')

    def close(self) -> NoReturn:
        """
        Clôturer le flux du fichier de rapport.
        """

        # On indique que le fichier a fini d'être analysé.
        self.cur.execute('UPDATE projet SET statut = "fini" WHERE id LIKE "' + str(self.id_projet) + '"')

        # Écrit le fichier JSON depuis la base de données.
        json = open(self.chemin_rapport + '/JSON/rapport-demiligne_' + self.fichier + '.json', 'w', encoding='utf-8')
        json.write('{\n')
        json.write('\t"fichier" : "' + self.fichier + '",\n')
        json.write('\t"type_erreur" : "demiligne",\n')
        json.write('\t"start_timecode" : "' + self.timecodestart + '",\n')
        json.write('\t"duree" : "' + tc.frames_to_timecode(self.duree_image, self.framerate) + '",\n')
        json.write('\t"resolution" : "' + self.resolution + '",\n')
        json.write('\t"framerate" : "' + str(self.framerate) + '",\n')
        json.write('\t"remarque" :\n')
        json.write('\t\t[\n')

        i = 0

        for row in self.cur.execute(
                'SELECT * FROM remarque WHERE id_projet LIKE "' + str(self.id_projet) + '" ORDER BY tc_in, tc_out ASC'):
            print(row)
            if i != 0:
                json.write(',\n')
            json.write('\t\t\t{\n')
            json.write('\t\t\t\t"tc_in" : "' + row[1] + '",\n')
            json.write('\t\t\t\t"tc_out" : "' + row[2] + '",\n')

            row_3 = row[3]
            match row[3]:
                case 'Demi ligne <strong>droite</strong>.':
                    row_3 = 'Right half-line.'
                case 'Demi ligne <strong>gauche</strong>.':
                    row_3 = 'Left half-line.'
                case 'Demi ligne <strong>haut</strong>.':
                    row_3 = 'Top half-line.'
                case 'Demi ligne <strong>bas</strong>.':
                    row_3 = 'Bottom half-line.'

            json.write('\t\t\t\t"remarque" : "' + row_3 + '"\n')
            # json.write('\t\t\t\t"option" : "' + row[4] + '"\n')
            json.write('\t\t\t}')
            i = i + 1
        json.write('\n')

        json.write('\t\t]\n')
        json.write('}\n')
        json.close()

        # Écrit le fichier HTML :
        file = open(self.chemin_rapport + 'rapport_' + self.fichier + '.html', 'w', encoding='utf-8')
        file.write("<html>\n")
        file.write("\t<head>\n")
        file.write("\t\t<title>Rapport : " + self.fichier + "</title>\n")

        file.write("\t\t<style type= \"text/css\">\n")
        file.write("\t\t.bord{\n")
        file.write("\t\t\tborder-width: 1px;\n")
        file.write("\t\t\tborder-style: solid;\n")
        file.write("\t\t\tborder-bottom-width: 1px;\n")
        file.write("\t\t\t}\n")
        file.write("\t\t</style>\n")

        file.write("\t</head>\n")
        file.write("\t<body>\n")
        file.write("\t\t<p>Rapport demi-ligne</p>\n")
        file.write("\t\t<p><strong>Fichier :</strong> " + self.fichier + "</p>\n")
        file.write("\t\t<p><strong>Ratio :</strong> " + self.ratio + "</p>\n")
        print('Framerate : ' + str(self.framerate))
        print('Durée (image) : ' + str(self.duree_image))
        print('Durée : ' + str(tc.frames_to_timecode(self.duree_image, self.framerate)))

        file.write(
            "\t\t<p><strong>Durée :</strong> " + str(self.duree_image) + " image(s) (TC " + tc.frames_to_timecode(
                self.duree_image, self.framerate) + ")</p>\n")

        # Parfois l'affichage du TC bug quand le fichier vient du réseau.
        try:
            tc_debut = int(Timecode(self.framerate, self.timecodestart).frames - 1)
            file.write(
                "\t\t<p><strong>Timecode début :</strong> " + self.timecodestart + " (" + str(tc_debut) + ")</p>\n")
        except:
            file.write("\t\t<p><strong>Timecode début :</strong> <i>inconnu</i></p>\n")

        file.write("\t\t<p><strong>Framerate :</strong> " + str(self.framerate) + " i/s</p>\n")
        file.write("\t\t<table class= \"bord\">\n")
        file.write("\t\t\t<tr>\n")
        file.write("\t\t\t\t<th class= \"bord\">n°</th>\n")
        file.write("\t\t\t\t<th class= \"bord\">TC IN</th>\n")
        file.write("\t\t\t\t<th class= \"bord\">TC OUT</th>\n")
        file.write("\t\t\t\t<th class= \"bord\">REMARK</th>\n")
        file.write("\t\t\t\t<th class= \"bord\">OPTION</th>\n")
        file.write("\t\t\t</tr>\n")

        self.numero = 0

        for row in self.cur.execute(
                'SELECT * FROM remarque WHERE id_projet LIKE "' + str(self.id_projet) + '" ORDER BY tc_in, tc_out ASC'):
            self.numero += 1
            file.write("\t\t\t<tr>\n")
            file.write("\t\t\t\t<td class= \"bord\">" + str(self.numero) + "</td>\n")
            file.write("\t\t\t\t<td class= \"bord\">" + row[1] + "</td>\n")
            file.write("\t\t\t\t<td class= \"bord\">" + row[2] + "</td>\n")
            file.write("\t\t\t\t<td class= \"bord\">" + row[3] + "</td>\n")
            file.write("\t\t\t\t<td class= \"bord\">" + row[4] + "</td>\n")
            file.write("\t\t\t</tr>\n")

        file.write("\t\t</table>\n")
        file.write("\t</body>\n")
        file.write('</html>')
        file.close()
