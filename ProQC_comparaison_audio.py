#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main

# == IMPORTS ==
import numpy as np
import os

import ChoixFichierAudio as cf  # Programme qui choisi le fichier à analyser.
import ChoixFichierAudio as cf2  # Programme qui choisi le fichier à analyser.
import ChoixFramerateListe as cfr  # On doit définir le framerate pour avoir un TC.
import fonctions as fct
import Rapport as r


ffmpeg = fct.getFFmpeg()
os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg

# == VALEURS ==

# == Declaration variables: ==
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
            r.addProbleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]), str(liste_option[i]))

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            liste_option = np.delete(liste_option, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


def addProbleme(message: str, option: str, num_image: int) -> None:
    """
    Quand on doit reporter un problème dans le rapport.
    :param str message: Le message.
    :param str option:
    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_option

    # Si c'est une nouvelle erreur :
    new = True

    # Si l'erreur est dans la liste :
    for i in range(0, np.size(list_tc_in, 0)):
        if list_erreur[i] == message:
            list_tc_out[i] = num_image  # Met à jour le tc out
            new = False

    # Sinon, on ajoute le problème à la liste :
    if new:
        # Quand on ajoute, on spécifie le tableau à qui on ajoute une valeur.
        list_tc_in = np.append(list_tc_in, num_image)
        list_tc_out = np.append(list_tc_out, num_image)
        liste_option = np.append(liste_option, option)
        list_erreur = np.append(list_erreur, message)


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    # Fichier 1:
    cf.fenetre()
    fichier = cf.filename.get()
    print('fichier 1: ' + str(fichier))
    start_tc = fct.startTimeCodeFile(ffmpeg, fichier)
    print('- Start tc: ' + start_tc)

    duree = 100

    # Note: [-1] = dernier element de la liste.
    r.rapport(fichier.split('/')[-1], True, 'html')

    # r.setRapport("== Debut du rapport ==\n")

    framerate = int(cfr.getFramerate())

    print('- Framerate: ' + str(framerate))

    r.setInformations(duree, start_tc, framerate)

    # Fichier 2:
    cf2.fenetre()
    fichier2 = cf2.filename.get()
    print('fichier 2: ' + str(fichier2))
    print('- Start tc: ' + str(fct.startTimeCodeFile(ffmpeg, fichier2)))

    # Cloture l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
    # On récupère les dernières valeurs de la liste.
    updateListeProbleme(duree)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux.
    r.close()

# == END ==
