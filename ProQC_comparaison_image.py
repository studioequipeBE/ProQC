#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main (+ les fonctions...)

# == IMPORTS ==
import imageio
import numpy as np
import os

from ChoixFichier import ChoixFichier
import fonctions as fct
import Rapport as r
import ServeurDate as date

ffmpeg = 'C:\\ffmpeg\\ffmpeg.exe'

os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg

# == VALEURS ==

# Si on peut utiliser le programme
licence = None

# Se connecte pour voir si on dépasse la limite d'utilisation du programme :
if int(date.aujourdhui()) <= 20230101:
    print('Licence OK')
    licence = True
else:
    print('Licence depassee/!\\')
    licence = False

# == Declaration variables: ==
ratio = None

starttc = None
starttc_frame = 0
endtc_frame = None

framerate = None

option_afficher = ''  # Valeur des paramètres.

# Liste des erreurs : tc in | tc out | erreur | option
list_tc_in = np.array([])
list_tc_out = np.array([])
list_erreur = np.array([])
liste_option = np.array([])

# Fichier pour rapport :
file = None

# Numéro d'erreur
num_erreur = 0


# == FONCTIONS ==
def updateListeProbleme(num_image: int) -> None:
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.

    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_option, num_erreur

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            num_erreur = num_erreur + 1
            print(str(num_erreur) + ' / ' + str(list_tc_in[i]) + " : update liste, on ajoute une erreur!")
            # On écrit dans le rapport l'erreur :

            # La notion de temps en timecode.
            # r.setRapport(str(TcActuel(list_tc_in[i], framerate)) + " a " + str(TcActuel(list_tc_out[i], framerate)) + ": " + str(list_erreur[i]) + "\n")
            # La notion de temps en image.
            # r.setRapport(str(int(list_tc_in[i])) + " a " + str(int(list_tc_out[i])) + ": " + str(list_erreur[i]) + "\n")
            r.addProbleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]), str(liste_option[i]))

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            liste_option = np.delete(liste_option, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


# :
def addProbleme(message, option, num_image) -> None:
    """
    Quand on doit reporter un problème dans le rapport.

    :param str message: Le message.
    :param str option: Les options.
    :param int num_image: Le numéro d'image.
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
        liste_option = np.append(liste_option, option)
        list_erreur = np.append(list_erreur, message)


delta = 0.01  # Delta qu'on tolère entre 2 images.
delta_min = 1 - delta  # Delta min
delta_max = 1 + delta  # Delta max


def setOption(i_sum, i2_sum, i_min, i2_min, i_mean, i2_mean, i_max, i2_max) -> None:
    """
    Affichage automatisé.
    """
    global option_afficher

    if i_sum != 0:
        calcule = (100.0 / i2_sum) * i_sum
    else:
        calcule = 0

    option_afficher = "(ratio: " + str(i_sum) + " [~" + str(i_mean) + ", -" + str(i_min) + ", +" + str(
        i_max) + "] / " + str(i2_sum) + " [~" + str(i2_mean) + ", -" + str(i2_min) + ", +" + str(i2_max) + "]): " + str(
        calcule) + "%"


def identique(image, image2) -> bool:
    """
    Vérifie que 2 images sont identiques.
    Méthode via la moyenne des images.

    :param image:
    :param image2:

    :return: True si les deux images sont les mêmes.
    """
    setOption(image.sum(), image2.sum(), image.min(), image2.min(), image.mean(), image2.mean(), image.max(),
              image2.max())

    if image.mean() == image2.mean():
        return True
    else:
        return False


"""
# Méthode via la différence entre les deux images.
def Identique(image, image2):

    setOption(image.sum(), image2.sum(), image.min(), image2.min(), image.mean(), image2.mean(), image.max(), image2.max())
    
    if (np.abs(image-image2)).sum() == 0:
        return True
    else:
        return False"""


def close() -> None:
    """
    Clôturer l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
    """
    # On récupère les dernières valeurs de la liste.
    updateListeProbleme(i)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux :
    reader.close()
    r.close()


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if licence:
    # Fichier 1:
    cf = ChoixFichier()
    cf.show()
    fichier = cf.getFilename()
    print('fichier 1: ' + fichier)

    start_tc = fct.startTimeCodeFile(ffmpeg, fichier)

    print('- Start tc: ' + start_tc)

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader = imageio.get_reader(fichier, ffmpeg_params=['-an'])

    framerate = int(reader.get_meta_data()['fps'])

    print('- Framerate: ' + str(framerate))

    duree_seconde = str(reader.get_meta_data()['duration']).split('.')

    duree = int(duree_seconde[0]) * framerate + int((int(duree_seconde[1]) / 100) * framerate)

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Note: [-1] = dernier element de la liste.
    r.rapport(fichier.split('/')[-1], True, 'bdd')

    r.setInformations(duree, start_tc, framerate)

    # Fichier 2:
    cf2 = ChoixFichier()
    cf2.show()
    fichier2 = cf2.getFilename()
    print('fichier 2: ' + fichier2)
    print('- Start tc: ' + fct.startTimeCodeFile(ffmpeg, fichier2))

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader2 = imageio.get_reader(fichier2, ffmpeg_params=['-an'])

    framerate2 = int(reader2.get_meta_data()['fps'])

    print('- Framerate: ' + str(framerate))

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Chaque iteration équivaut à une image :
    for i, image in enumerate(reader):

        image2 = reader2.get_data(i)  # Récupère l'image suivante de reader2 (image 2).

        # Met à jour la liste des erreurs (pour avoir un groupe de tc pour une erreur):
        updateListeProbleme(i)

        # Affiche l'avancement tous les 30 secondes :
        if (i % (framerate * 30)) == 0:
            print(str(i) + ' / ' + str(duree))

        if not identique(image, image2):
            addProbleme('Pas les mêmes image.', str(option_afficher), i)

close()
print('Fin analyse.')
# == END ==
