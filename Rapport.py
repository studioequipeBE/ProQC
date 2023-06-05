#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier: il gere le rapport généré. Le tout existe dans "Main.py". On pourait en faire un objet!
# Version: 0.1

# == IMPORTS ==
import bdd
import TimecodeP as tc
from timecode import Timecode
import os

# == ATTRIBUTS ==

# Fichier pour rapport:
file_ = None

# Numéro d'erreur.
numero = 0

# Framerate du fichier:
framerateG = None
tc_debut = None

# Type de rapport (HTML, txt, bdd):
type_ = None

chemin_rapport = "Rapports/"


# == FONCTIONS ==

# Creation du rapport en .txt, on pourrait faire un rapport en HTML, plus classe voir ajouter les valeurs dans la base de donnees de QC! :)
# Valeur de type_tmp= {txt, html, bdd}
def Rapport(fichier, type_tmp="txt"):
    global type_, file_, chemin_rapport
    type_ = type_tmp

    if not os.path.exists(chemin_rapport):  # Tu remplaces chemin par le chemin complet
        os.mkdir(chemin_rapport)

    if type_ == "txt":
        file_ = open(str(chemin_rapport) + "rapport_" + str(fichier) + ".txt", "w")
        file_.write("")
    elif type_ == "html":
        file_ = open(str(chemin_rapport) + "rapport_" + str(fichier) + ".html", "w")
        file_.write("<html>\n<head>\n<title>Rapport: " + str(fichier) + "</title>\n</head>\n<body>\n")
        file_.write(
            "<style type=\"text/css\">\n.bord{\nborder-width: 1px;\n border-style: solid;\n border-bottom-width: 1px;\n}\n</style>\n")
    else:
        bdd.Open()


# Quand on commence le rapport:
def Start(fichier, duree, timecodestart="00:00:00:00", framerate="24", ratio="2.39"):
    global framerateG, tc_debut
    framerateG = int(framerate)
    # Si on écrit un fichier texte:
    if type_ == "txt":
        file_.write("Fichier: " + fichier + "\n")
        file_.write("Duree: " + str(duree) + " image(s) (TC " + + ")\n")

        # Parfois l'affichage du TC bug quand le fichier vient du réseau.
        try:
            file_.write("Timecode debut: " + str(timecodestart) + "\n");
        except:
            file_.write("Timecode debut: inconnu\n");
        file_.write("Framerate : " + str(framerate) + " i/s\n")
        file_.write("Ratio : " + str(ratio) + "\n")
    # Si on écrit un fichier HTML:
    elif type_ == "html":
        file_.write("<p><strong>Fichier :</strong> " + fichier + "</p>\n")
        file_.write("<p><strong>Duree :</strong> " + str(duree) + " image(s) (TC " + tc.frames_to_timecode(int(duree),
                                                                                                           framerateG) + ")</p>\n")

        # Parfois l'affichage du TC bug quand le fichier vient du réseau.
        try:
            tc_debut = int(Timecode(framerate, timecodestart).frames - 1)
            # print "TC debut: " + str(tc_debut)
            file_.write(
                "<p><strong>Timecode debut :</strong> " + str(timecodestart) + " (" + str(tc_debut) + ")</p>\n");
        except:
            file_.write("<p><strong>Timecode debut :</strong> <i>inconnu</i></p>\n");

        file_.write("<p><strong>Framerate :</strong> " + str(framerate) + " i/s</p>\n")
        file_.write("<p><strong>Ratio :</strong> " + str(ratio) + "<p>\n")
        file_.write("<table class= \"bord\">\n")
        file_.write(
            "<tr><th class= \"bord\">n°</th><th class= \"bord\">TC IN</th><th class= \"bord\">TC OUT</th><th class= \"bord\">REMARK</th><th class= \"bord\">OPTION</th></tr>\n")

    # Si on ajoute les informations en base de données:
    else:
        bdd.Insert("rapport", "id_film, id_production, id_cadence, id_balayage, fichier, duree, id_ratio, id_format",
                   "1, 1, 1, 1, \"" + str(fichier) + "\", '" + str(duree) + "', 1, 1")


# Ecrire dans le rapport:
def setRapport(message):
    if type_ == "txt":
        file_.write(message)
    elif type_ == "html":
        file_.write("<tr><td class= \"bord\">" + message + "</td></tr>\n")
    # else:
    #    bdd.Insert(message)


# Ecrire dans le rapport:
def addProbleme(tc_in, tc_out, probleme, option):
    global numero, framerate, tc_debut

    if type_ == "txt":
        file_.write(probleme)
    elif type_ == "html":
        numero = numero + 1
        file_.write("<tr><td class= \"bord\">" + str(numero) + "</td><td class= \"bord\">" + tc.frames_to_timecode(
            int(tc_in) + tc_debut, framerateG) + "</td><td class= \"bord\">" + tc.frames_to_timecode(
            int(tc_out) + tc_debut,
            framerateG) + "</td><td class= \"bord\">" + probleme + "</td><td class= \"bord\">" + option + "</td></tr>\n")
    else:
        bdd.Insert("rapport_commentaire_video", "id_rapport, timecode_in, timecode_out, remarque, echelle",
                   "2, '" + tc_in + "', '" + tc_out + "', \"" + probleme + "\", 1")


# Cloturer le flux du fichier de rapport:
def close():
    if type_ == "txt":
        file_.write("== Fin du rapport ==")
        file_.close()
    elif type_ == "html":
        file_.write("</table>\n</body>\n</html>")
        file_.close()
    else:
        bdd.close()
