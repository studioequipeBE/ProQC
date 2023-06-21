#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Main.
"""

# == IMPORTS ==
import imageio
import numpy as np
import os
import sys
from timecode import Timecode

from ChoixFichier import ChoixFichier  # Programme qui choisi le fichier à analyser.
from ChoixRatio import ChoixRatio
import fonctions as fct
from RapportDemiligne import RapportDemiligne
from outils.metadata import MetaData

ffmpeg = fct.get_ffmpeg()
os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg

# == VALEURS ==
ratio = None

starttc = None
starttc_frame = 0
endtc_frame = None

# Définit à quelle ligne commence l'image utile (en fonction de son ratio).
y_debut_haut = None  # 1ère ligne utile vers le haut.
y_debut_bas = None  # 1ère ligne utile vers le bas.

# Définit à quelle colonne commence l'image utile (en fonction de son ratio).
x_debut_gauche = None
x_debut_droite = None

framerate = None

option_afficher = ''  # Valeur du ratio.

# Liste des erreurs : tc in | tc out | erreur | option
list_tc_in = np.array([])
list_tc_out = np.array([])
list_erreur = np.array([])
liste_option = np.array([])

# Coefficient appliqué à certains chiffres.
# Les calculs sont basé sur de la HD, donc souvent, x2 pour de l'UHD (calcule en ligne et non intégralité image).
coefficient_resolution = 1

# Numéro d'erreur
num_erreur = 0

delta = 0.21  # Delta qu'on tolère pour la moyenne.
delta_min = 1 - delta  # Delta min
delta_max = 1 + delta  # Delta max


# == FONCTIONS ==
def update_liste_probleme(num_image: int) -> None:
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.

    :param int num_image: Numéro d'image.
    """
    global num_erreur, list_tc_in, list_tc_out, list_erreur, liste_option

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            num_erreur = num_erreur + 1
            print(str(num_erreur) + ' / ' + str(list_tc_in[i]) + " : update liste, on ajoute une erreur!")
            # On écrit dans le rapport l'erreur :
            # La notion de temps en image.
            rapport.add_probleme(int(list_tc_in[i]), int(list_tc_out[i]), str(list_erreur[i]), str(liste_option[i]))

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            liste_option = np.delete(liste_option, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


def add_probleme(message: str, option: str, num_image: int) -> None:
    """
    Quand on doit reporter un problème dans le rapport.

    :param str message: Le message.
    :param str option:
    :param int num_image : Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_option

    # Si c'est une nouvelle erreur :
    new = True

    # Si l'erreur est dans la liste :
    for i in range(0, np.size(list_tc_in, 0)):
        if list_erreur[i] == message:
            list_tc_out[i] = num_image  # Met à jour le tc out.
            new = False

    # Sinon, on ajoute le problème à la liste :
    if new:
        # Quand on ajoute, on spécifie le tableau à qui on ajoute une valeur.
        list_tc_in = np.append(list_tc_in, num_image)
        list_tc_out = np.append(list_tc_out, num_image)
        list_erreur = np.append(list_erreur, message)
        liste_option = np.append(liste_option, option)


def set_ratio(ratio_tmp: str, resolution_tmp) -> None:
    """
    On définit le ratio et on prépare les matrices d'analyse de l'image.

    :param str ratio_tmp:
    :param resolution_tmp:
    """
    global ratio, coefficient_resolution, y_debut_haut, y_debut_bas, x_debut_gauche, x_debut_droite

    ratio = ratio_tmp

    debut_HD_x = 0
    fin_HD_x = 1919
    debut_HD_y = 0
    fin_HD_y = 1079

    debut_UHD_x = 0
    fin_UHD_x = 3839
    debut_UHD_y = 0
    fin_UHD_y = 2139

    if resolution_tmp == '3840x2160':
        # L'UHD a un coefficient x2 :
        coefficient_resolution = 2

    # Ligne utile en 2.00 1920x1080
    if ratio == '2.40':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 140  # (1080 - (1920/2.4)) = 240 / 2 = 140
            y_debut_bas = 939  # (1080 - 140) = 940 - 1

            x_debut_gauche = debut_HD_x
            x_debut_droite = fin_HD_x
        elif resolution_tmp == '3840x2160':
            y_debut_haut = 280
            y_debut_bas = 1879

            x_debut_gauche = debut_UHD_x
            x_debut_droite = fin_UHD_x
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 2.39 1920x1080
    elif ratio == '2.39':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 138  # (1080 - (1920/2.39)) = 276 / 2 = 138
            y_debut_bas = 941  # (1080 - 138) = 942 - 1

            x_debut_gauche = debut_HD_x
            x_debut_droite = fin_HD_x
        elif resolution_tmp == '3840x2160':
            y_debut_haut = 277
            y_debut_bas = 1882  # (2160 - 277) = 1883 - 1

            x_debut_gauche = debut_UHD_x
            x_debut_droite = fin_UHD_x
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 2.00 1920x1080
    elif ratio == '2.35':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 131  # (1080 - (1920/2.35)) = 262 / 2 = 131
            y_debut_bas = 948  # (1080 - 131) = 949 - 1

            x_debut_gauche = debut_HD_x
            x_debut_droite = fin_HD_x
        elif resolution_tmp == '3840x2160':
            y_debut_haut = 263
            y_debut_bas = 1923  # (2160 - 263) = 1924 - 1

            x_debut_gauche = debut_UHD_x
            x_debut_droite = fin_UHD_x
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 2.00 1920x1080
    elif ratio == '2.00':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 60  # (1080 - (1920/2.00)) = 120 / 2 = 60
            y_debut_bas = 1019  # (1080 - 60) = 1020 - 1

            x_debut_gauche = debut_HD_x
            x_debut_droite = fin_HD_x
        elif resolution_tmp == '3840x2160':
            y_debut_haut = 120
            y_debut_bas = 2039  # (2160 - 120) = 2040 - 1

            x_debut_gauche = debut_UHD_x
            x_debut_droite = fin_UHD_x
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 1.85 1920x1080
    elif ratio == '1.85':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 21  # (1080 - (1920/1.85)) = 42 / 2 = 21
            y_debut_bas = 1058  # (1080 - 21) = 1059 - 1

            x_debut_gauche = debut_HD_x
            x_debut_droite = fin_HD_x
        elif resolution_tmp == '3840x2160':
            y_debut_haut = 42
            y_debut_bas = 2117  # (2160 - 42) = 2118 - 1

            x_debut_gauche = debut_UHD_x
            x_debut_droite = fin_UHD_x
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 1.77 1920x1080
    elif ratio == '1.77':
        if resolution_tmp == '1920x1080':
            y_debut_haut = debut_HD_y  # Fullframe.
            y_debut_bas = fin_HD_y  # Fullframe.

            x_debut_gauche = debut_HD_x  # Fullframe.
            x_debut_droite = fin_HD_x  # Fullframe.
        elif resolution_tmp == '3840x2160':
            y_debut_haut = debut_UHD_y  # Fullframe.
            y_debut_bas = debut_UHD_y  # Fullframe.

            x_debut_gauche = debut_UHD_x  # Fullframe.
            x_debut_droite = fin_UHD_x  # Fullframe.
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    elif ratio == '1.66':
        if resolution_tmp == '1920x1080':
            y_debut_haut = debut_HD_y
            y_debut_bas = fin_HD_y

            x_debut_gauche = 64  # (1920 - (1080 * 1.66)) = 128 / 2 = 64
            x_debut_droite = 1855  # (1920 - 64) = 1856 - 1
        elif resolution_tmp == '3840x2160':
            y_debut_haut = debut_UHD_y
            y_debut_bas = fin_UHD_y

            x_debut_gauche = 127
            x_debut_droite = 3712  # (3840 - 127) = 3713 - 1
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 1.77 1920x1080
    elif ratio == '1.33':
        if resolution_tmp == '1920x1080':
            y_debut_haut = debut_HD_y
            y_debut_bas = fin_HD_y

            x_debut_gauche = 240  # (1920 - (1080 * 1.33333)) = 480 / 2 = 240
            x_debut_droite = 1679  # (1920 - 240) = 1680 - 1
        elif resolution_tmp == '3840x2160':
            y_debut_haut = debut_UHD_y
            y_debut_bas = fin_UHD_y

            x_debut_gauche = 480
            x_debut_droite = 3359  # (2160 - 480) = 3360 - 1
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    else:
        sys.exit('Erreur : Ratio inconnu!!!')


def set_option(ligne_utile_sum, ligne_avant_sum, ligne_utile_min, ligne_avant_min, ligne_utile_mean, ligne_avant_mean,
               ligne_utile_max, ligne_avant_max) -> None:
    """
    Affichage automatisé.
    """
    global option_afficher

    if ligne_utile_sum != 0:
        calcule = (100.0 / ligne_avant_sum) * ligne_utile_sum
    else:
        calcule = 0

    option_afficher = "(ratio: " + str(ligne_utile_sum) + " [~" + str(ligne_utile_mean) + ", -" + str(
        ligne_utile_min) + ", +" + str(ligne_utile_max) + "] / " + str(ligne_avant_sum) + " [~" + str(
        ligne_avant_mean) + ", -" + str(ligne_avant_min) + ", +" + str(ligne_avant_max) + "]): " + str(calcule) + "%"


def demi_ligne(ligne_utile, ligne_avant) -> bool:
    """
    Commun entre les différents défauts.

    :param ligne_utile: Ligne dans l'image.
    :param ligne_avant: Ligne "avant" la dernière ligne utile.
    """
    global delta_min, delta_max, coefficient_resolution
    # Les sommes :
    ligne_utile_sum = ligne_utile.sum()
    ligne_avant_sum = ligne_avant.sum()

    # Les max :
    ligne_utile_max = ligne_utile.max()
    ligne_avant_max = ligne_avant.max()

    # La ligne limite (des blankinkgs) ne doit pas avoir un delta plus grand que 19% pour la moyenne.
    # La ligne limite avec les blankings ne doit pas avoir un delta plus grand que 18% pour les valeurs maximales.
    if (ligne_avant_max * delta_max > ligne_utile_max > ligne_avant_max * delta_min) or (
            ligne_avant_sum * delta_max > ligne_utile_sum > ligne_avant_sum * delta_min):
        return True

    # Le "else" permet de faire les préparations pour les autres calculs :
    else:
        # Les moyennes :
        ligne_utile_mean = ligne_utile.mean()
        ligne_avant_mean = ligne_avant.mean()

        # Si les deux vallent zéro, on ne compte pas d'erreur (cela serait possiblement un défaut de blanking mais pas de demi-ligne).
        # Si les valeurs (2 lignes) sont vraiment faible (100 = FHD, dû à la compression), on ne compte pas comme un défaut. C'est noir...
        # Si les deux lignes ont pour valeurs maximales 1 (= image noire avec défaut de compression), alors c'est bon, il n'y a pas de souci.
        # Si inférieur à 100 et que la moyenne est égale à moins d'un 1% près (0,95%), alors c'est bon!
        if (ligne_utile_sum < 100 * coefficient_resolution and ligne_avant_sum < 100 * coefficient_resolution) and (
                (ligne_utile_max <= 1 and ligne_avant_max <= 1) or (
                ligne_avant_mean - 0.0095 <= ligne_utile_mean <= ligne_avant_mean + 0.0095)):
            return True

        # Le "else" permet de faire les préparations pour les autres calculs :
        else:
            # Les min :
            ligne_utile_min = ligne_utile.min()
            ligne_avant_min = ligne_avant.min()

            # Cas où les lignes sont dans le noir et la compression est mal faite (cas : "Le Milieu De L'Horizon") :
            if (ligne_utile_sum < ligne_utile.size and ligne_avant_sum < ligne_utile.size) and (
                    ligne_utile_min == 0 and ligne_avant_min == 0) and (
                    ligne_utile_mean < 0.35 and ligne_avant_mean < 0.35) and (
                    ligne_utile_max < 20 and ligne_avant_max < 20) and (ligne_avant_max / ligne_utile_max < 1.5):
                return True

            # Si après toutes ces vérifications ce n'est toujours pas bon, alors la ligne est considéré avec le défaut.
            else:
                return False


def demi_ligne_haut(image) -> bool:
    """
    Vérifie que la ligne de l'image utile du haut est bien codée (cas 2.39).

    :param image:
    """
    ligne_utile = image[y_debut_haut:(y_debut_haut + 1):1, y_debut_haut:y_debut_bas:1]  # Ligne limite.
    ligne_avant = image[(y_debut_haut + 1):(y_debut_haut + 2):1, y_debut_haut:y_debut_bas:1]

    return demi_ligne(ligne_utile, ligne_avant)


def demi_ligne_bas(image) -> bool:
    """
    Vérifie que la ligne de l'image utile du bas est bien codée (cas 2.39).

    :param image:
    """
    ligne_utile = image[y_debut_bas:(y_debut_bas + 1):1, y_debut_haut:y_debut_bas:1]  # Ligne limite.
    ligne_avant = image[(y_debut_bas - 1):y_debut_bas:1, y_debut_haut:y_debut_bas:1]

    return demi_ligne(ligne_utile, ligne_avant)


def demi_ligne_gauche(image) -> bool:
    """
    Vérifie que la colonne de gauche de l'image utile est bien codée (cas 2.39).

    :param image:
    """
    ligne_utile = image[y_debut_haut:y_debut_bas:1, x_debut_gauche:(x_debut_gauche + 1):1]  # Ligne limite.
    ligne_avant = image[y_debut_haut:y_debut_bas:1, (x_debut_gauche + 1):(x_debut_gauche + 2):1]

    return demi_ligne(ligne_utile, ligne_avant)


def demi_ligne_droite(image) -> bool:
    """
    Vérifie que la colonne de droite de l'image utile est bien codée (cas 2.39).

    :param image:
    """
    ligne_utile = image[y_debut_haut:y_debut_bas:1, x_debut_droite:(x_debut_droite + 1):1]  # Ligne limite.
    ligne_avant = image[y_debut_haut:y_debut_bas:1, (x_debut_droite - 1):x_debut_droite:1]

    return demi_ligne(ligne_utile, ligne_avant)


def close() -> None:
    """
    Clôturer l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
    """
    global i_global, reader
    # On récupère les dernières valeurs de la liste.
    update_liste_probleme(i_global)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux :
    reader.close()
    rapport.close()


i_global = 0

# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    cf = ChoixFichier(ChoixFichier.liste_fichier_video())
    cf.show()
    fichier = cf.get_filename()
    print('fichier : ' + str(fichier))

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader = imageio.get_reader(fichier, ffmpeg_params=['-an'])

    # Choix du ratio :
    cr = ChoixRatio()
    cr.show()
    ratio = cr.get_ratio()

    # Récupère les informations concernant le fichier.
    metadonnees = MetaData(fichier)

    # == Informations techniques sur le fichier : ==
    start_tc = metadonnees.start()  # "01:00:00:00"
    # start_tc = fct.startTimeCodeFile(ffmpeg, fichier)

    framerate = metadonnees.framerate()  # int(24)

    resolution = metadonnees.resolution()  # '3840x2160'

    set_ratio(ratio, resolution)

    duree_to_tc = int(Timecode(framerate, metadonnees.duree_to_tc()).frames - 1)
    duree_image = duree_to_tc  # metadonnees.duree_to_tc()  # 172800

    # == Fin information sur technique sur le fichier. ==

    print("Start tc : " + start_tc)
    print("Framerate : " + str(framerate))

    # Note: [-1] = dernier element de la liste.
    rapport = RapportDemiligne(fichier.split('/')[-1])

    print('Projet en cours :')
    print(rapport.projet_en_cours())

    endtc_frame = duree_image - 1
    print('Ratio : ' + ratio)

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    rapport.start(duree_image, start_tc, framerate, ratio, resolution)

    # Chaque iteration équivaut à une image :
    # On reprend où on s'est arrêté.
    for i, image in enumerate(reader, start=0):

        i_global = i

        # Met à jour la liste des erreurs (pour avoir un groupe de tc pour une erreur) :
        update_liste_probleme(i)

        # Affiche l'avancement tous les 30 secondes :
        if (i % (framerate * 30)) == 0:
            print(str(i) + ' / ' + str(duree_image))
            rapport.savestate(i)

        if not demi_ligne_haut(image):
            add_probleme('Demi ligne <strong>haut</strong>.', str(option_afficher), i)

        if not demi_ligne_bas(image):
            add_probleme('Demi ligne <strong>bas</strong>.', str(option_afficher), i)

        if not demi_ligne_gauche(image):
            add_probleme('Demi ligne <strong>gauche</strong>.', str(option_afficher), i)

        if not demi_ligne_droite(image):
            add_probleme('Demi ligne <strong>droite</strong>.', str(option_afficher), i)

    # On récupère les dernières valeurs de la liste.
    update_liste_probleme(i_global)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux :
    reader.close()
    rapport.close()

# == END ==
