#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main (+ les fonctions...)

# == IMPORTS ==
import imageio
import numpy as np
import subprocess as sp
import timecode as Timecode

import ChoixFichier as cf  # Programme qui choisi le fichier a analyser.
import ChoixFichier as cf2  # Programme qui choisi le fichier a analyser.
import ChoixFramerateListe as cfr
import Rapport as r
import ServeurDate as date
import TimecodeP as tc

# == VALEURS ==

# Si on peut utiliser le programme
licence = None

# Se connecte pour voir si on depasse la limite d'utilisation du programme:
if int(date.aujourdhui()) <= 20201025:
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

# Définit à quelle ligne commence l'image utile (en fonction de son ratio).
y_debut_haut = None  # 1ère ligne utile vers le haut.
y_debut_bas = None  # 1ère ligne utile vers le bas.

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
def tcActuel(num_image: int, framerate: int = 24) -> str:
    """
    Donne le TC actuel à l'aide d'un nombre d'images et sur base d'un tc de départ.

    :param int num_image: Numéro d'image.
    :param int framerate: Framerate.
    """
    tc1 = Timecode(framerate, starttc)
    if num_image > 0:
        # Comme le résultat est toujours une image en trop, j'enlève ce qu'il faut : :)
        tc2 = Timecode(framerate, tc.frames_to_timecode((num_image - 1), framerate))
        tc3 = tc1 + tc2
        return tc3
    else:
        return tc1


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

            # La notion de temps en timecode
            # r.setRapport(str(TcActuel(list_tc_in[i], framerate)) + " a " + str(TcActuel(list_tc_out[i], framerate)) + ": " + str(list_erreur[i]) + "\n")
            # La notion de temps en image
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


def startTimeCodeFile(fichier: str) -> str:
    """
    Timecode du fichier analyse.

    :param str fichier: Le fichier.
    """
    global starttc
    command = ['ffmpeg.exe', '-i', fichier, '-']
    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
    pipe.stdout.readline()
    pipe.terminate()
    infos = pipe.stderr.read()
    tc = ''
    for i in range(18, 29):
        tc += infos[(infos.find('timecode') + i)]
    starttc = tc
    return tc


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
    cf.fenetre()
    fichier = cf.filename.get()
    print('fichier 1: ' + fichier)
    print('- Start tc: ' + startTimeCodeFile(fichier))

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader = imageio.get_reader(fichier, ffmpeg_params=['-an'])

    framerate = int(cfr.getFramerate())

    print('- Framerate: ' + str(framerate))

    duree = reader.get_length()

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Note: [-1] = dernier element de la liste.
    r.rapport(fichier.split('/')[-1], 'html')

    # r.setRapport("== Debut du rapport ==\n")

    r.start(fichier, str(duree), str(startTimeCodeFile(fichier)), str(framerate))

    # Fichier 2:
    cf2.fenetre()
    fichier2 = cf2.filename.get()
    print('fichier 2: ' + fichier2)
    print('- Start tc: ' + startTimeCodeFile(fichier2))

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader2 = imageio.get_reader(fichier2, ffmpeg_params=['-an'])

    framerate2 = int(cfr.getFramerate())

    print('- Framerate: ' + str(framerate))

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Chaque iteration équivaut à une image :
    for i, image in enumerate(reader):

        image2 = reader2.get_data(i)  # Récupère l'image suivante de reader2 (image 2).

        # Met a jout la liste des erreurs (pour avoir un groupe de tc pour une erreur):
        updateListeProbleme(i)

        # Affiche l'avancement tous les 30 secondes :
        if (i % (framerate * 30)) == 0:
            print(str(i) + ' / ' + str(duree))

        if not identique(image, image2):
            addProbleme('Pas les mêmes image..', str(option_afficher), i)

close()

# == END ==
