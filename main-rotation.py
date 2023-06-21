#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Main.
"""

# == IMPORTS ==
import sys

import imageio
import numpy as np
from timecode import Timecode

from ChoixFichier import ChoixFichier  # Programme qui choisi le fichier à analyser.
from ChoixRatio import ChoixRatio
import fonctions as fct
from Rapports import Rapport
from outils.metadata import MetaData

# == VALEURS ==

# == Déclaration variables: ==
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

option_afficher = ""  # Valeur du ratio.

# Liste des erreurs : tc in | tc out | erreur | option
list_tc_in = np.array([])
list_tc_out = np.array([])
list_erreur = np.array([])
liste_option = np.array([])

# Coefficient appliqué à certains chiffres.
# Les calculs sont basé sur de la HD, donc souvent, x2 pour de l'UHD (calcule en ligne et non intégralité image).
coefficient_resolution = 1

# Fichier pour rapport :
file = None

# Numéro d'erreur
num_erreur = 0


# == FONCTIONS ==

def update_liste_probleme(num_image):
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_option, num_erreur

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            num_erreur = num_erreur + 1
            print(str(num_erreur) + " / " + str(int(list_tc_in[i])) + " : update liste, on ajoute une erreur!")
            # On écrit dans le rapport l'erreur :
            rapport.addProbleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]),
                                str(liste_option[i]))

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            liste_option = np.delete(liste_option, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


def add_probleme(message, option, num_image):
    """
    Quand on doit reporter un problème dans le rapport.
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


def set_ratio(ratio_tmp, resolution_tmp):
    """
    On définit le ratio et on prépare les matrices d'analyse de l'image.
    """
    global ratio, coefficient_resolution

    global y_debut_haut, y_debut_bas, x_debut_gauche, x_debut_droite

    ratio = ratio_tmp

    # Ligne utile en 2.00 1920x1080
    if ratio == '2.40':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 140
            y_debut_bas = 939

            x_debut_gauche = 0
            x_debut_droite = 1919
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 2.39 1920x1080
    elif ratio == '2.39':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 138
            y_debut_bas = 941

            x_debut_gauche = 0
            x_debut_droite = 1919
        # Pour l'instant, car UHD :
        else:
            y_debut_haut = 277
            y_debut_bas = 1883

            x_debut_gauche = 0
            x_debut_droite = 3839

            # l'UHD a un coefficient x2 :
            coefficient_resolution = 2

    # Ligne utile en 2.00 1920x1080
    elif ratio == '2.35':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 131
            y_debut_bas = 948

            x_debut_gauche = 0
            x_debut_droite = 1919
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 2.00 1920x1080
    elif ratio == '2.00':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 60
            y_debut_bas = 1019

            x_debut_gauche = 0
            x_debut_droite = 1919
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 1.85 1920x1080
    elif ratio == '1.85':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 21
            y_debut_bas = 1058

            x_debut_gauche = 0
            x_debut_droite = 1919
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    # Ligne utile en 1.77 1920x1080
    elif ratio == '1.77':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 0
            y_debut_bas = 1079

            x_debut_gauche = 0
            x_debut_droite = 1919
        # Pour l'instant, car UHD :
        else:
            y_debut_haut = 0
            y_debut_bas = 2159

            x_debut_gauche = 0
            x_debut_droite = 3839

            # l'UHD a un coefficient x2 :
            coefficient_resolution = 2

    # Ligne utile en 1.77 1920x1080
    elif ratio == '1.33':
        if resolution_tmp == '1920x1080':
            y_debut_haut = 0
            y_debut_bas = 1079

            x_debut_gauche = 240
            x_debut_droite = 1679
        else:
            sys.exit("Le ratio n'est pas disponible pour cette résolution.")

    else:
        sys.exit('Erreur: Ratio inconnu!!!')


def set_option_image(pixels, image):
    """
    Définit les options dans le rapport.
    """
    global option_afficher

    option_afficher = "max : " + str(pixels.max()) + ",<br>"
    option_afficher += "min : " + str(pixels.min()) + ",<br>"
    option_afficher += "mean : " + str(pixels.mean()) + ",<br>"
    option_afficher += "sum : " + str(pixels.sum()) + ",<br>"
    option_afficher += "total image max : " + str(image.max()) + ",<br>"
    option_afficher += "total image min : " + str(image.min()) + ",<br>"
    option_afficher += "total image mean : " + str(image.mean()) + ",<br>"
    option_afficher += "total image sum : " + str(image.sum()) + "<br>"


# Calcule s'il y a un défaut de rotation sur base d'une liste de pixel renseigné :
# On calcule sur base de la somme de la valeur des pixels.
# Si c'est (presque) noir, alors c'est considéré comme une erreur.
def calcule_rotation(pixels):
    sum = pixels.sum()
    # mean = pixels.mean()

    # S'il y a le défaut, on retourne True, sinon on retourne faux.
    if sum < 2:  # or mean < 8:
        set_option_image(pixels, image)
        return True
    else:
        return False


def noir_haut_gauche(image):
    """
    Vérifie que la ligne de l'image utile du haut est bien codée (cas 2.39).
    """
    global option_afficher, y_debut_haut, x_debut_gauche

    # pixels = image[y_debut_haut, x_debut_gauche]
    # Coin, coin-bas, coin-droite.
    pixels = np.array([
        image[y_debut_haut, x_debut_gauche],
        image[y_debut_haut + 1, x_debut_gauche],
        image[y_debut_haut, x_debut_gauche + 1]
    ], dtype=np.uint8)

    return calcule_rotation(pixels)


def noir_haut_droite(image):
    """
    Vérifie que la ligne de l'image utile du bas est bien codée (cas 2.39).
    """
    global option_afficher, y_debut_haut, x_debut_droite

    # pixels = image[y_debut_haut, x_debut_droite]
    # Coin, coin-bas, coin-gauche.
    pixels = np.array([
        image[y_debut_haut, x_debut_droite],
        image[y_debut_haut + 1, x_debut_droite],
        image[y_debut_haut, x_debut_droite - 1]
    ], dtype=np.uint8)

    return calcule_rotation(pixels)


def noir_bas_gauche(image):
    """
    Vérifie que la colonne de gauche de l'image utile est bien codée (cas 2.39).
    """
    global option_afficher, y_debut_bas, x_debut_gauche

    # pixels = image[y_debut_bas, x_debut_gauche]
    # Coin, coin-haut, coin-droite.
    pixels = np.array([
        image[y_debut_bas, x_debut_gauche],
        image[y_debut_bas - 1, x_debut_gauche],
        image[y_debut_bas, x_debut_gauche + 1]
    ], dtype=np.uint8)

    return calcule_rotation(pixels)


def noir_bas_droite(image):
    """
    Vérifie que la colonne de droite de l'image utile est bien codée (cas 2.39).
    """
    global option_afficher, y_debut_bas, x_debut_droite

    # pixels = image[y_debut_bas, x_debut_droite]
    # Coin, coin-haut, coin-gauche.
    pixels = np.array([
        image[y_debut_bas, x_debut_droite],
        image[y_debut_bas - 1, x_debut_droite],
        image[y_debut_bas, x_debut_droite - 1]
    ], dtype=np.uint8)

    return calcule_rotation(pixels)


# Clôturer l'analyse d'une video (en clôturant son flux ainsi que celui du rapport) :
def close():
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
    print("fichier : " + str(fichier))

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader = imageio.get_reader(fichier, ffmpeg_params=["-an"])

    # Récupère les informations concernant le fichier.
    metadonnees = MetaData(fichier)

    # == Informations techniques sur le fichier : ==
    start_tc = metadonnees.start()  # "01:00:00:00"

    framerate = metadonnees.framerate()  # int(24)

    # Choix du ratio :
    cr = ChoixRatio()
    cr.show()
    ratio = cr.get_ratio()  # '2.39'

    resolution = metadonnees.resolution()  # '3840x2160'

    set_ratio(ratio, resolution)

    duree_to_tc = int(Timecode(framerate, metadonnees.duree_to_tc()).frames - 1)
    duree_image = duree_to_tc  # metadonnees.duree_to_tc()  # 172800

    # == Fin information sur technique sur le fichier. ==

    print("Start tc: " + start_tc)
    print("Framerate: " + str(framerate))

    # Note: [-1] = dernier element de la liste.
    rapport = Rapport(fichier.split('/')[-1], True, 'html')

    print('Projet en cours :')
    print(rapport.getProjetEnCours())

    endtc_frame = duree_image - 1
    print("Ratio: " + str(ratio))

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    rapport.setInformations(duree_image, start_tc, framerate, resolution, str(ratio))

    # Chaque iteration équivaut à une image :
    # On reprend où on s'est arrêté.
    for i, image in enumerate(reader, start=0):

        i_global = i

        # Met à jour la liste des erreurs (pour avoir un groupe de tc pour une erreur) :
        update_liste_probleme(i)

        # Affiche l'avancement tous les 30 secondes :
        if (i % (framerate * 30)) == 0:
            print(str(i) + " / " + str(duree_image))
            rapport.savestate(i)

        # On saute le noir.
        if image.max() > 0:
            if noir_haut_gauche(image):
                add_probleme("Défaut rotation en <strong>haut/gauche</strong>.", str(option_afficher), i)

            if noir_haut_droite(image):
                add_probleme("Défaut rotation en <strong>haut/droite</strong>.", str(option_afficher), i)

            if noir_bas_gauche(image):
                add_probleme("Défaut rotation en <strong>bas/gauche</strong>.", str(option_afficher), i)

            if noir_bas_droite(image):
                add_probleme("Défaut rotation en <strong>bas/droite</strong>.", str(option_afficher), i)

    # On récupère les dernières valeurs de la liste.
    update_liste_probleme(i_global)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux :
    reader.close()
    rapport.close()

# == END ==
