#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : il gère le rapport généré. On pourrait en faire un objet !

# == IMPORTS ==
import os
from timecode import Timecode

import bdd
import TimecodeP as tc


class Rapport:
    def __init__(self, fichier: str, nouveau_rapport: bool, type: str = 'html'):
        """
        Création du rapport en HTML ou dans une base de données de QC.

        :param str fichier : Le fichier.
        :param bool nouveau_rapport: Si on doit faire un nouveau rapport ou partir sur le précédent (fct que pour db).
        :param str type : Valeurs possible : html, bdd
        """
        # Fichier pour rapport :
        self.file_ = None

        # Numéro d'erreur.
        self.numero = 0

        # Framerate du fichier:
        self.framerate = None
        self.tc_debut = None

        # Type de rapport (HTML, txt, bdd):
        self.type = type

        self.chemin_rapport = 'Rapports/'

        # ID du rapport QC dans la DB à utiliser.
        self.id_rapport = 0

        # ID du projet dans la base de données :
        self.id_projet = None

        if not os.path.exists(self.chemin_rapport):  # Tu remplaces chemin par le chemin complet.
            os.mkdir(self.chemin_rapport)

        if self.type == 'html':
            self.file_ = open(self.chemin_rapport + 'rapport_' + fichier + '.html', 'w', encoding='utf-8')
            self.file_.write('<html>\n<head>\n<title>Rapport: ' + fichier + "</title>\n</head>\n<body>\n")
            self.file_.write(
                "<style type=\"text/css\">\n.bord{\nborder-width: 1px;\n border-style: solid;\n border-bottom-width: 1px;\n}\n</style>\n")
        else:
            bdd.connect()
            if nouveau_rapport:
                self.id_rapport = bdd.addRapport(fichier)

    def set_informations(self, duree: int, timecodestart: str = '00:00:00:00', framerate: float = 24,
                         resolution: str = '1920x1080', ratio: str = None) -> None:
        """
        Quand on commence le rapport.

        :param int duree: La durée du fichier en image.
        :param str timecodestart: Le timecode début.
        :param int framerate: Le framerate.
        :param str resolution: La résolution.
        :param str ratio: Le ratio du fichier
        """
        self.framerate = framerate
        # Si on écrit un fichier texte :
        if self.type == 'html':
            self.file_.write("<p><strong>Durée :</strong> " + str(duree) + " image(s) (TC " +
                             tc.frames_to_timecode(duree, self.framerate) + ")</p>\n")

            # Parfois l'affichage du TC bug quand le fichier vient du réseau.
            try:
                self.tc_debut = int(Timecode(self.framerate, timecodestart).frames - 1)
                # print "TC debut: " + str(tc_debut)
                self.file_.write(
                    "<p><strong>Timecode debut :</strong> " + timecodestart + " (" + str(self.tc_debut) + ")</p>\n")
            except:
                self.file_.write("<p><strong>Timecode debut :</strong> <i>inconnu</i></p>\n")

            self.file_.write('<p><strong>Framerate :</strong> ' + str(self.framerate) + " i/s</p>\n")
            self.file_.write('<p><strong>Ratio :</strong> ' + ratio + "<p>\n")
            self.file_.write("<table class= \"bord\">\n")
            self.file_.write(
                "<tr><th class= \"bord\">n°</th><th class= \"bord\">TC IN</th><th class= \"bord\">TC OUT</th><th class= \"bord\">REMARK</th><th class= \"bord\">OPTION</th></tr>\n")

        # Si on ajoute les informations en base de données :
        else:
            bdd.insert(
                'rapport_qc_informations',
                'id_rapport_qc, duree, start_timecode, framerate',
                str(self.id_rapport) + ', ' + str(duree) + ', "' + timecodestart + '", ' + str(framerate)
            )

    def get_projet_en_cours(self) -> int:
        """
        Indique si un projet est en cours.
        """
        bdd.cur.execute("SELECT count(*) FROM projet WHERE statut LIKE 'en cours'")

        return bdd.cur.fetchall()

    def set_rapport(self, message: str) -> None:
        """
        Écrire dans le rapport.

        :param str message: Le message.
        """
        if self.type == 'html':
            self.file_.write("<tr><td class= \"bord\">" + message + "</td></tr>\n")
        else:
            bdd.addMessage(self.id_rapport, message)

    def add_probleme(self, tc_in: str, tc_out: str, remarque: str, option: str = '') -> None:
        """
        Ajoute une remarque dans le rapport.

        :param str tc_in: Timecode in.
        :param str tc_out: Timecode out.
        :param str remarque: Le problème.
        :param str option: Les options.
        """

        if self.type == 'html':
            self.numero += 1
            self.file_.write("<tr><td class= \"bord\">" + str(self.numero) + "</td><td class= \"bord\">" +
                             tc.frames_to_timecode(int(tc_in) + self.tc_debut,
                                                   self.framerate) + "</td><td class= \"bord\">" +
                             tc.frames_to_timecode(int(tc_out) + self.tc_debut, self.framerate) +
                             "</td><td class= \"bord\">" + remarque + "</td><td class= \"bord\">" + option + "</td></tr>\n")
        else:
            bdd.insert('rapport_qc_remarque',
                       'id_rapport_qc, timecode_in, timecode_out, remarque, echelle',
                       str(self.id_rapport) + ', "' + tc_in + '", "' + tc_out + '", "' + remarque + '", 1')

    def savestate(self, num_image) -> None:
        """
        Indique jusqu'où on était dans le rapport s'il y a eu un crash.
        """
        bdd.cur.execute(
            'UPDATE projet SET image_analyse = "' + str(num_image) + '" WHERE id LIKE "' + str(self.id_projet) + '"')

    def close(self) -> None:
        """
        Clôture le flux du fichier de rapport.
        """
        if self.type == 'html':
            self.file_.write("</table>\n</body>\n</html>")
            self.file_.close()
        else:
            bdd.close()
