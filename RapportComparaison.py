#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : il gère le rapport généré.

# == IMPORTS ==
import datetime
import os
import sqlite3


class RapportComparaison:
    """
    Rapport pour les comparaisons de plusieurs images.
    """
    # == ATTRIBUTS ==

    # Numéro d'erreur.
    numero = 0

    # Framerate du fichier:
    framerate = None
    tc_debut = None

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

        self.con = sqlite3.connect(
            'C:\\Users\\win10dev\\Desktop\\comparaison_' + fichier_ref + '.db')
        self.cur = self.con.cursor()

        # Table contenant les informations sur le fichier.
        self.cur.execute('''
         CREATE TABLE IF NOT EXISTS fichier_ref
         (
             id INTEGER NOT NULL,
             nom TEXT NOT NULL UNIQUE,
             duree_image INTEGER NOT NULL,
             start_timecode TEXT NOT NULL,
             framerate TEXT NOT NULL,
             debut_analyse TEXT NOT NULL,
             fin_analyse TEXT,
             PRIMARY KEY("id" AUTOINCREMENT)
         )
         ''')

        self.cur.execute('''
         CREATE TABLE IF NOT EXISTS fichier
         (
             id INTEGER NOT NULL,
             nom TEXT NOT NULL UNIQUE,
             start_timecode TEXT NOT NULL,
             PRIMARY KEY("id" AUTOINCREMENT)
         )
         ''')

        self.cur.execute('''
         CREATE TABLE IF NOT EXISTS difference
         (
             id INTEGER NOT NULL,
             id_fichier_ref TEXT NOT NULL,
             id_fichier_compare TEXT NOT NULL,
             tc_in TEXT NULL,
             tc_out TEXT NULL,
             PRIMARY KEY("id" AUTOINCREMENT)
         )
         ''')

    def setInformation(self, duree: int = 0, timecodestart: str = '00:00:00:00', framerate_: int = 24) -> None:
        """
        On définit des informations sur le fichier de référence.

        :param int duree: La durée du fichier en image.
        :param str timecodestart: Timecode début du fichier.
        :param int framerate_: Framerate du fichier.
        """
        self.framerate = framerate_

        # Info du fichier analysé :
        self.cur.execute(
            'INSERT INTO fichier_ref(nom, duree_image, start_timecode, framerate, debut_analyse) VALUES("'
            + self.fichier_ref + '", ' + str(duree) + ', "' + timecodestart + '", "'
            + str(self.framerate) + '", "' + str(datetime.datetime.now()) + '")')
        self.con.commit()

        res = self.cur.execute(
            'SELECT id FROM fichier_ref WHERE nom= "' + self.fichier_ref + '" ORDER BY id DESC LIMIT 1')
        self.id_fichier_ref = res.fetchall()[0][0]

    def addFichier(self, nom_fichier: str, timecodestart: str):
        """
        Ajoute un fichier à comparer et le définit comme celui courant.
        """
        self.cur.execute(
            'INSERT INTO fichier(nom, start_timecode) VALUES("'
            + nom_fichier + '", "' + timecodestart + '")')
        self.con.commit()

        res = self.cur.execute(
            'SELECT id FROM fichier WHERE nom= "' + nom_fichier + '" ORDER BY id DESC LIMIT 1')
        self.id_fichier_compare = res.fetchall()[0][0]

    def addDifference(self, tc_in: str, tc_out: str) -> None:
        """
        Écrire dans le rapport.

        :param str tc_in: Timecode in.
        :param str tc_out: Timecode out.
        """
        self.cur.execute(
            'INSERT INTO difference(id_fichier_ref, id_fichier_compare, tc_in, tc_out)'
            'VALUES'
            '(' + str(self.id_fichier_ref) + ', ' + str(self.id_fichier_compare)
            + ', "' + tc_in + '", "' + tc_out + '")')
        self.con.commit()

    def close(self) -> None:
        """
        Clôture les flux sur la base de données.
        """
        self.con.close()
        self.cur.close()
