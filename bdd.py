#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Permet de réaliser des connexions à une base de données : INSERT, DELETE, SELECT, ...
# Bien si on veut ajouter des infos de QC pour ProQC ! :)

# == IMPORTS ==
import mysql.connector

cursor = None
conn = None


# == FONCTIONS ==
def connect() -> None:
    """
    Connexion à la base de données.
    """
    global cursor, conn
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='rapport_qc')
    cursor = conn.cursor()


def insert(table: str, colonnes: str, valeurs: str) -> None:
    """
    Ajouter des donnees dans la base de données.

    :param str table: Nom de la table
    :param str colonnes: La liste des colonnes.
    :param str valeurs: La liste des valeurs.
    """
    global cursor
    cursor.execute('INSERT INTO ' + table + ' (' + colonnes + ') VALUES (' + valeurs + ')')
    conn.commit()


def addRapport(fichier: str) -> int:
    """
    Ajoute un rapport à la base de données.

    :param str fichier: Le fichier à analyser.
    """
    global cursor
    cursor.execute('INSERT INTO rapport_qc (fichier, date_creation) VALUES ("' + fichier + '", NOW())')
    conn.commit()
    cursor.execute('SELECT id FROM rapport_qc WHERE fichier = "' + fichier + '" ORDER BY id DESC')
    # print(cursor.fetchall()[0])
    return int(cursor.fetchall()[0][0])


def addMessage(id_rapport: int, message: str) -> None:
    global cursor
    cursor.execute(
        'INSERT INTO rapport_qc_message (id_rapport, message) VALUES (' + str(id_rapport) + ', "' + message + '")')
    conn.commit()


def update(table: str, valeurs: str, condition: str = '*') -> None:
    """
    Mettre à jour des données.

    :param str table: Nom de la table.
    :param str valeurs: Colonne et valeur.
    :param str condition: Condition SQL (optionnel).
    """
    global cursor
    cursor.execute('UPDATE ' + table + ' SET ' + valeurs + ' WHERE ' + condition)


def select(table: str, selection: str = '*', condition: str = ''):
    """
    Sélectionne des données.

    :param str table: Nom de la table
    :param str selection:
    :param str condition:
    """
    global cursor
    cursor.execute('SELECT ' + selection + ' FROM ' + table + condition)
    return cursor.fetchall()


def convertTab(fetch):
    """
    Convertir un résultat select en un beau tableau exploitable.

    :param fetch:
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
    global cursor
    cursor.execute('SELECT id FROM ' + table + " WHERE " + condition)
    for valeur in cursor.fetchall():
        return format(valeur[0])

    # Dernier id?
    # emp_no = cursor.lastrowid


def close() -> None:
    """
    On se déconnecte de la basse de données.
    """
    conn.close()
    cursor.close()
