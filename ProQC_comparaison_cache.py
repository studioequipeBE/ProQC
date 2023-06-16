#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main

# == IMPORTS ==
import sqlite3

import fonctions as fct

# Liste de fichier à faire une cache.
liste_fichier = []

# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():

    # Construit une DB :
    con = sqlite3.connect('C:\\Users\\win10dev\\Desktop\\LesInvisibles_S02E01_4444_UHD-21_25p_MOS_TXL_220725.mov.db')
    cur = con.cursor()

    con2 = sqlite3.connect('C:\\Users\\win10dev\\Desktop\\LesInvisibles_S02E01_4444_UHD-21_25p_MOS_TXL_220729.mov.db')
    cur2 = con2.cursor()

    cur.execute('SELECT duree_image FROM fichier ORDER BY id DESC LIMIT 1')

    nombre_image = cur.fetchall()[0][0]

    print('nombre_image : ' + str(nombre_image))

    cur.execute('SELECT hash FROM md5 ORDER BY id ASC')
    liste_md5_f1 = cur.fetchall()

    cur2.execute('SELECT hash FROM md5 ORDER BY id ASC')
    liste_md5_f2 = cur2.fetchall()

    num_image_premiere_different = -1
    num_image_dernier_different = -1

    list_tc_in = -1
    list_tc_out = -1
    numero_erreur = 0

    # Parcoure chaque image :
    for i in range(0, int(nombre_image)):

        if list_tc_out != i - 1 and list_tc_out != -1:
            print(str(list_tc_in)+' - ' + str(list_tc_out) + ' : Different')
            list_tc_in = -1
            list_tc_out = -1

        # Vérifie si c'est identique ou différent.
        if liste_md5_f1[i][0] != liste_md5_f2[i][0]:
            if list_tc_in == -1:
                list_tc_in = i
            list_tc_out = i

    if list_tc_out != nombre_image - 1 and list_tc_out != -1:
        print(str(list_tc_in) + ' - ' + str(list_tc_out) + ' : Different')

    # Ferme flux DB.
    cur.close()
    con.close()

    cur2.close()
    con2.close()
