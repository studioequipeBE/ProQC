#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : il gçre le rapport généré. Le tout existe dans "Main.py". On pourrait en faire un objet !

# == IMPORTS ==
import os
from timecode import Timecode

import bdd
import TimecodeP as tc

# == ATTRIBUTS ==

# Fichier pour rapport :
file_ = None

# Numéro d'erreur.
numero = 0

# Framerate du fichier:
framerateG = None
tc_debut = None

# Type de rapport (HTML, txt, bdd):
type_ = None

chemin_rapport = 'Rapports/'

# ID du rapport QC dans la DB à utiliser.
id_rapport = 0


# == FONCTIONS ==
def rapport(fichier: str, nouveau_rapport: bool, type_tmp: str = 'html'):
    """
    Création du rapport en .txt, on pourrait faire un rapport en HTML, plus classe voir ajouter les valeurs dans la base de données de QC ! :)

    :param str fichier : Le fichier.
    :param bool nouveau_rapport: Si on doit faire un nouveau rapport ou partir sur le précédent (fct que pour db).
    :param str type_tmp : Valeur de type_tmp={html, bdd}
    """
    global type_, file_, chemin_rapport, id_rapport
    type_ = type_tmp

    if not os.path.exists(chemin_rapport):  # Tu remplaces chemin par le chemin complet.
        os.mkdir(chemin_rapport)

    if type_ == 'html':
        file_ = open(str(chemin_rapport) + 'rapport_' + str(fichier) + '.html', 'w')
        file_.write('<html>\n<head>\n<title>Rapport: ' + str(fichier) + "</title>\n</head>\n<body>\n")
        file_.write(
            "<style type=\"text/css\">\n.bord{\nborder-width: 1px;\n border-style: solid;\n border-bottom-width: 1px;\n}\n</style>\n")
    else:
        bdd.connect()
        if nouveau_rapport:
            id_rapport = bdd.addRapport(fichier)


def setInformations(duree: int, timecodestart: str = '00:00:00:00', framerate: int = 24, ratio: str = None) -> None:
    """
    Quand on commence le rapport.

    :param int duree: La durée du fichier en image.
    :param str timecodestart:
    :param int framerate:
    :param str ratio: Le ratio du fichier
    """
    global framerateG, tc_debut, id_rapport, type_
    framerateG = framerate
    # Si on écrit un fichier texte :
    if type_ == 'html':
        file_.write("<p><strong>Durée :</strong> " + str(duree) + " image(s) (TC " + tc.frames_to_timecode(duree,
                                                                                                           framerateG) + ")</p>\n")

        # Parfois l'affichage du TC bug quand le fichier vient du réseau.
        try:
            tc_debut = int(Timecode(framerate, timecodestart).frames - 1)
            # print "TC debut: " + str(tc_debut)
            file_.write(
                "<p><strong>Timecode debut :</strong> " + timecodestart + " (" + str(tc_debut) + ")</p>\n")
        except:
            file_.write("<p><strong>Timecode debut :</strong> <i>inconnu</i></p>\n")

        file_.write('<p><strong>Framerate :</strong> ' + str(framerate) + " i/s</p>\n")
        file_.write('<p><strong>Ratio :</strong> ' + ratio + "<p>\n")
        file_.write("<table class= \"bord\">\n")
        file_.write(
            "<tr><th class= \"bord\">n°</th><th class= \"bord\">TC IN</th><th class= \"bord\">TC OUT</th><th class= \"bord\">REMARK</th><th class= \"bord\">OPTION</th></tr>\n")

    # Si on ajoute les informations en base de données :
    else:
        bdd.insert(
            'rapport_qc_informations',
            'id_rapport_qc, duree, start_timecode, framerate',
            str(id_rapport) + ', ' + str(duree) + ', "' + timecodestart + '", ' + str(framerate)
        )


def setRapport(message: str) -> None:
    """
    Écrire dans le rapport.

    :param str message: Le message.
    """
    global id_rapport
    if type_ == 'html':
        file_.write("<tr><td class= \"bord\">" + message + "</td></tr>\n")
    else:
        bdd.addMessage(id_rapport, message)


def addProbleme(tc_in: str, tc_out: str, remarque: str, option: str) -> None:
    """
    Écrire dans le rapport.

    :param str tc_in: Timecode in.
    :param str tc_out: Timecode out.
    :param str remarque: Le problème.
    :param str option: Les options.
    """
    global numero, framerate, tc_debut, id_rapport

    if type_ == 'html':
        numero = numero + 1
        file_.write("<tr><td class= \"bord\">" + str(numero) + "</td><td class= \"bord\">" + tc.frames_to_timecode(
            int(tc_in) + tc_debut, framerateG) + "</td><td class= \"bord\">" + tc.frames_to_timecode(
            int(tc_out) + tc_debut,
            framerateG) + "</td><td class= \"bord\">" + remarque + "</td><td class= \"bord\">" + option + "</td></tr>\n")
    else:
        bdd.insert('rapport_qc_remarque',
                   'id_rapport_qc, timecode_in, timecode_out, remarque, echelle',
                   str(id_rapport) + ', "' + tc_in + '", "' + tc_out + '", "' + remarque + '", 1')


def close() -> None:
    """
    Clôture le flux du fichier de rapport.
    """
    if type_ == 'html':
        file_.write("</table>\n</body>\n</html>")
        file_.close()
    else:
        bdd.close()
