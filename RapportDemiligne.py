#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : il gère le rapport.
# Export aussi une version JSON pour faciliter les traitements.
# Backup dans une base de données SQLite le traitement en cours.

# == IMPORTS ==
import os
import sqlite3
from timecode import Timecode
from typing import NoReturn

import TimecodeP as tc

# == ATTRIBUTS ==

# Fichier pour rapport :
file_ = None

# Numéro d'erreur.
numero = 0

# Framerate du fichier:
framerate = None
tc_debut = None

# Type de rapport (HTML, txt):
type_ = None

chemin_rapport = "Rapports/"

# ID du projet dans la base de données :
id_projet = None

# Base de données avec le rapport en cours. (on va essayer de créer le rapport à la fin !)
db = None
cur = None  # curseur pour faire les opérations sur la base de données.

fichier_tmp = None

ratio_ = None
duree_image_ = None
timecodestart_ = None


# == FONCTIONS ==
# Création du rapport en .txt ou HTML, on pourrait faire un rapport en HTML, plus classe voir ajouter les valeurs dans la base de donnees de QC! :)
# Valeur de type_tmp= {txt, html}
def Rapport(fichier, type_tmp='txt') -> NoReturn:
    global type_, file_, chemin_rapport, db, cur, fichier_tmp

    fichier_tmp = fichier
    type_ = type_tmp

    # On crée dans la base de données, isolation_level en None = autocommit.
    db = sqlite3.connect('data.db', isolation_level=None)
    cur = db.cursor()

    # Si la table n'existe pas, on la créée :
    cur.execute('''CREATE TABLE IF NOT EXISTS projet (id INTEGER PRIMARY KEY AUTOINCREMENT, fichier TEXT, statut TEXT, image_analyse TEXT, resolution TEXT, framerate TEXT, ratio TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS remarque (id_projet TEXT, tc_in TEXT, tc_out TEXT, probleme TEXT, option TEXT)''')

    if not os.path.exists(chemin_rapport):  # Tu remplaces chemin par le chemin complet.
        os.mkdir(chemin_rapport)


# Indique si un projet est en cours.
def projet_en_cours() -> int:
    global cur
    cur.execute("SELECT count(*) FROM projet WHERE statut LIKE 'en cours'")

    return cur.fetchall()


# Quand on commence le rapport :
def Start(fichier: str, duree_image: int, timecodestart: str = "00:00:00:00", framerate_: int = 24, ratio: str = "2.39", resolution_: str = "1920x1080") -> NoReturn:
    global framerate, tc_debut, file_, id_projet, ratio_, duree_image_, timecodestart_, resolution

    ratio_ = ratio
    duree_image_ = duree_image
    timecodestart_ = timecodestart

    framerate = int(framerate_)
    resolution = resolution_

    tc_debut = int(Timecode(framerate, timecodestart_).frames - 1)

    # Ajoute le projet en base de données.
    cur.execute("INSERT INTO projet (fichier, statut, image_analyse, resolution, framerate, ratio)" +
                "VALUES ('" + fichier + "', 'en cours', '0', '" + resolution + "', '" + str(framerate) + "', '" + ratio + "')")

    # Récupère l'ID de la dernière entrée :
    id_projet = cur.lastrowid

    # Si on écrit un fichier texte :
    if type_ == "txt":
        file_.write("Fichier: " + fichier + "\n")
        file_.write("Durée: " + str(duree_image) + " image(s) (TC " + tc.frames_to_timecode(duree_image, framerate) + ")\n")

        # Parfois l'affichage du TC bug quand le fichier vient du réseau.
        try:
            file_.write("Timecode début: " + timecodestart + "\n")
        except:
            file_.write("Timecode début: inconnu\n")
        file_.write("Framerate: " + str(framerate) + " i/s\n")


def addProbleme(tc_in_image: int, tc_out_image: int, probleme: str, option: str) -> NoReturn:
    """
    Ajoute une erreur dans le rapport.
    """
    global numero, framerate, tc_debut, id_projet

    tc_in_tc = tc.frames_to_timecode(int(tc_in_image)+tc_debut, framerate)
    tc_out_tc = tc.frames_to_timecode(int(tc_out_image)+tc_debut, framerate)

    cur.execute("INSERT INTO remarque VALUES ('" + str(id_projet) + "', '" + tc_in_tc + "', '" + tc_out_tc + "', '" + probleme + "', '" + option + "')")


def savestate(num_image) -> NoReturn:
    """
    Indique jusqu'où on était dans le rapport s'il y a eu un crash.
    """
    global cur, id_projet
    cur.execute('UPDATE projet SET image_analyse = "' + str(num_image) + '" WHERE id LIKE "' + str(id_projet) + '"')


def close() -> NoReturn:
    """
    Clôturer le flux du fichier de rapport.
    """
    global id_projet, file_, cur, fichier_tmp, type_, fichier_tmp, ratio_, duree_image_, timecodestart_, framerate, resolution

    # On indique que le fichier a fini d'être analysé.
    cur.execute('UPDATE projet SET statut = "fini" WHERE id LIKE "' + str(id_projet) + '"')

    # Écrit le fichier JSON depuis la base de données.
    json = open(str(chemin_rapport) + "/JSON/rapport_" + str(fichier_tmp) + ".json", "w")
    json.write('{\n')
    json.write('\t"fichier" : "' + str(fichier_tmp) + '",\n')
    json.write('\t"resolution" : "' + resolution + '",\n')
    json.write('\t"framerate" : "' + str(framerate) + '",\n')
    json.write('\t"ratio" : "' + ratio_ + '",\n')
    json.write('\t"remarque" :\n')
    json.write('\t\t[\n')

    i = 0

    for row in cur.execute('SELECT * FROM remarque WHERE id_projet LIKE "' + str(id_projet) + '" ORDER BY tc_in, tc_out ASC'):
        print(row)
        if i != 0:
            json.write(',\n')
        json.write('\t\t\t{\n')
        json.write('\t\t\t\t"tc_in" : "' + row[1]+'",\n')
        json.write('\t\t\t\t"tc_out" : "' + row[2] + '",\n')
        json.write('\t\t\t\t"remarque" : "' + row[3] + '",\n')
        json.write('\t\t\t\t"option" : "' + row[4] + '"\n')
        json.write('\t\t\t}')
        i = i + 1
    json.write('\n')

    json.write('\t\t]\n')
    json.write('}\n')
    json.close()

    # Si demande un fichier texte, on l'écrit ici.
    if type_ == 'txt':
        file_ = open(str(chemin_rapport) + 'rapport_' + str(fichier_tmp) + '.txt', 'w')
        file_.write('')

        # file_.write(message)

        file_.write('== Fin du rapport ==')
        file_.close()

    # Si demande un fichier HTML, on l'écrit ici.
    elif type_ == "html":
        file_ = open(str(chemin_rapport) + 'rapport_' + str(fichier_tmp) + '.html', 'w')
        file_.write("<html>\n")
        file_.write("\t<head>\n")
        file_.write("\t\t<title>Rapport : " + str(fichier_tmp) + "</title>\n")

        file_.write("\t\t<style type= \"text/css\">\n")
        file_.write("\t\t.bord{\n")
        file_.write("\t\t\tborder-width: 1px;\n")
        file_.write("\t\t\tborder-style: solid;\n")
        file_.write("\t\t\tborder-bottom-width: 1px;\n")
        file_.write("\t\t\t}\n")
        file_.write("\t\t</style>\n")

        file_.write("\t</head>\n")
        file_.write("\t<body>\n")
        file_.write("\t\t<p>Rapport demi-ligne</p>\n")
        file_.write("\t\t<p><strong>Fichier :</strong> " + fichier_tmp + "</p>\n")
        file_.write("\t\t<p><strong>Ratio :</strong> " + ratio_ + "</p>\n")
        print('Framerate : ' + str(framerate))
        print('Durée (image) : ' + str(duree_image_))
        print('Durée : ' + str(tc.frames_to_timecode(duree_image_, framerate)))

        file_.write("\t\t<p><strong>Durée :</strong> " + str(duree_image_) + " image(s) (TC " + tc.frames_to_timecode(duree_image_, framerate) + ")</p>\n")

        # Parfois l'affichage du TC bug quand le fichier vient du réseau.
        try:
            tc_debut = int(Timecode(framerate, timecodestart_).frames - 1)
            file_.write("\t\t<p><strong>Timecode début :</strong> " + timecodestart_ + " (" + str(tc_debut) + ")</p>\n")
        except:
            file_.write("\t\t<p><strong>Timecode début :</strong> <i>inconnu</i></p>\n")

        file_.write("\t\t<p><strong>Framerate :</strong> " + str(framerate) + " i/s</p>\n")
        file_.write("\t\t<table class= \"bord\">\n")
        file_.write("\t\t\t<tr>\n")
        file_.write("\t\t\t\t<th class= \"bord\">n°</th>\n")
        file_.write("\t\t\t\t<th class= \"bord\">TC IN</th>\n")
        file_.write("\t\t\t\t<th class= \"bord\">TC OUT</th>\n")
        file_.write("\t\t\t\t<th class= \"bord\">REMARK</th>\n")
        file_.write("\t\t\t\t<th class= \"bord\">OPTION</th>\n")
        file_.write("\t\t\t</tr>\n")

        numero = 0

        for row in cur.execute('SELECT * FROM remarque WHERE id_projet LIKE "' + str(id_projet) + '" ORDER BY tc_in, tc_out ASC'):
            numero = numero + 1
            file_.write("\t\t\t<tr>\n")
            file_.write("\t\t\t\t<td class= \"bord\">" + str(numero) + "</td>\n")
            file_.write("\t\t\t\t<td class= \"bord\">" + row[1] + "</td>\n")
            file_.write("\t\t\t\t<td class= \"bord\">" + row[2] + "</td>\n")
            file_.write("\t\t\t\t<td class= \"bord\">" + row[3] + "</td>\n")
            file_.write("\t\t\t\t<td class= \"bord\">" + row[4] + "</td>\n")
            file_.write("\t\t\t</tr>\n")

        file_.write("\t\t</table>\n")
        file_.write("\t</body>\n")
        file_.write('</html>')
        file_.close()
