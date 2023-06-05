#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Permet de realiser des connexions à une base de données: INSERT, DELETE, SELECT, ...
# Bien si on veut ajouter des infos de QC pour ProQC! :)

# == IMPORTS ==
import mysql.connector

cursor = None
conn = None


# == FONCTIONS ==

# Connexion à la base de donnees:
def Open():
    global cursor, conn
    conn = mysql.connector.connect(host="localhost", user="root", password="naruto", database="rapport_qc")
    cursor = conn.cursor()
    # cursor.execute("SELECT codec FROM liste_codec")
    # rows = cursor.fetchall()
    # for row in rows:
    #    print format(row[0])


# Ajouter des donnees dans la base de donnees:
def Insert(table, colonnes, valeurs):
    # ...
    global cursor
    cursor.execute("INSERT INTO " + str(table) + " (" + str(colonnes) + ") VALUES (" + str(valeurs) + ")")
    conn.commit()


# Mettre a jour des donnees:
def Update(table, valeurs, condition="*"):
    # ...
    global cursor
    cursor.execute("UPDATE " + str(table) + " SET " + str(valeurs) + " WHERE " + str(condition))


# Selectionner des donnees:
def Select(table, selection="*", condition=""):
    global cursor
    cursor.execute("SELECT " + str(selection) + " FROM " + str(table) + str(condition))
    return cursor.fetchall()


# Convertir un resultat select en un beau tableau exploitable:
def ConvertTab(fetch):
    tab = []
    for row in fetch:
        tab.append(format(row[0]))
    return tab


# Recuperer l'ID d'une valeur:
def getID(table, condition):
    global cursor
    cursor.execute("SELECT id FROM " + str(table) + " WHERE " + str(condition))
    for valeur in cursor.fetchall():
        return format(valeur[0])


# Dernier id?
# emp_no = cursor.lastrowid

# On se deconnnecte de la basse de donnees:
def close():
    conn.close()
    cursor.close()
