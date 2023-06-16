#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Permet de réaliser des connexions à une base de données : INSERT, DELETE, SELECT, ...
# Bien si on veut ajouter des infos de QC pour ProQC ! :)

# == IMPORTS ==
import datetime
import os
import sqlite3

# Pour SQLite :
fichier = 'data.db'
db = None
cur = None


# == FONCTIONS ==
def connect() -> None:
    """
    Connexion à la base de données.
    """
    global db, cur, fichier

    new = False

    if not os.path.exists(fichier):
        new = True

    db = sqlite3.connect(fichier, isolation_level=None)
    cur = db.cursor()

    # Si la DB n'existait pas, on crée les tables et les données de base :
    if new:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS liste_cadence(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cadence TEXT UNIQUE
        )
        ''')

        cur.execute('INSERT INTO liste_cadence' +
                    '(cadence)' +
                    'VALUES' +
                    '("24"),("25"),("23.976")')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS liste_codec(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codec TEXT UNIQUE
        )
        ''')

        # J'ai un doute pour les codecs :
        cur.execute('INSERT INTO liste_codec' +
                    '(codec)' +
                    'VALUES' +
                    '("H264"),("Apple Pro Res 422HQ"),("Apple Pro Res 444")')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS liste_ratio(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ratio TEXT UNIQUE
        )
        ''')

        cur.execute('INSERT INTO liste_ratio' +
                    '(ratio)' +
                    'VALUES' +
                    '("2.40"),("2.39"),("2.35"),("2.00"),("1.85"),("1.77"),("1.66"),("1.33")')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS liste_resolution(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resolution TEXT UNIQUE
        )
        ''')

        cur.execute('INSERT INTO liste_codec' +
                    '(codec)' +
                    'VALUES' +
                    '("1920x1080"),("3840x2160")')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS rapport_qc(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fichier TEXT,
            date_creation TEXT
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS rapport_comparaison(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fichier1_nom TEXT,
            fichier2_nom TEXT,
            date_creation TEXT,
            date_commencement TEXT,
            date_fin TEXT,
            fichier1_duree_image INTEGER,
            fichier2_duree_image INTEGER,
            fichier1_start_timecode TEXT,
            fichier2_start_timecode TEXT,
            fichier1_framerate TEXT,
            fichier2_framerate TEXT,
            fichier2_offset_image TEXT
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS rapport_comparaison_difference(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rapport_comparaison INTEGER,
            fichier2_timecode_in TEXT,
            fichier2_timecode_out TEXT
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS rapport_qc_informations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rapport_qc INTEGER,
            duree INTEGER,
            start_timecode TEXT,
            framerate TEXT,
            ratio TEXT
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS rapport_qc_remarque(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rapport_qc INTEGER,
            timecode_in INTEGER,
            timecode_out INTEGER,
            remarque TEXT,
            options TEXT,
            echelle INTEGER
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS rapport_qc_message(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rapport INTEGER,
            message TEXT
        )
        ''')


def insert(table: str, colonnes: str, valeurs: str) -> None:
    """
    Ajouter des données dans la base de données.

    :param str table: Nom de la table
    :param str colonnes: La liste des colonnes.
    :param str valeurs: La liste des valeurs.
    """
    global cur
    cur.execute('INSERT INTO ' + table + ' (' + colonnes + ') VALUES (' + valeurs + ')')


def addRapport(fichier: str) -> int:
    """
    Ajoute un rapport à la base de données.

    :param str fichier: Le fichier à analyser.
    :returns: ID du rapport créé.
    """
    global cur
    cur.execute('INSERT INTO rapport_qc (fichier, date_creation) VALUES ("' + fichier + '", "' + str(
        datetime.datetime.now()) + '")')
    cur.execute('SELECT id FROM rapport_qc WHERE fichier = "' + fichier + '" ORDER BY id DESC')
    return int(cur.fetchall()[0][0])


def addMessage(id_rapport: int, message: str) -> None:
    """
    Ajout un message à la base de données.
    """
    global cur
    cur.execute(
        'INSERT INTO rapport_qc_message (id_rapport, message) VALUES (' + str(id_rapport) + ', "' + message + '")')


def update(table: str, valeurs: str, condition: str = '*') -> None:
    """
    Mettre à jour des données.

    :param str table: Nom de la table.
    :param str valeurs: Colonne et valeur.
    :param str condition: Condition SQL (optionnel).
    """
    global cur
    cur.execute('UPDATE ' + table + ' SET ' + valeurs + ' WHERE ' + condition)


def select(table: str, selection: str = '*', condition: str = ''):
    """
    Sélectionne des données.

    :param str table: Nom de la table
    :param str selection:
    :param str condition:
    """
    global cur
    cur.execute('SELECT ' + selection + ' FROM ' + table + condition)
    return cur.fetchall()


def convertTab(fetch):
    """
    Convertir un résultat select en un beau tableau exploitable.

    :param fetch: Le contenu du fetch.
    :returns: Un tableau avec une colonne.
    """
    tab = []
    for row in fetch:
        tab.append(format(row[0]))
    return tab


def getID(table: str, condition: str) -> str:
    """
    Retourne l'ID d'une valeur.

    :param str table : Nom de la table.
    :param str condition : Condition sur la table.
    :return: ID.
    """
    global cur
    cur.execute('SELECT id FROM ' + table + " WHERE " + condition)
    for valeur in cur.fetchall():
        return format(valeur[0])


def close() -> None:
    """
    On se déconnecte de la basse de données.
    """
    global cur, db
    cur.close()
    db.close()
