#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main (+ les fonctions...)

# == IMPORTS ==
import numpy as np
import subprocess as sp
import timecode as Timecode

import ChoixFichierAudio as cf  # Programme qui choisi le fichier à analyser.
import ChoixFichierAudio as cf2  # Programme qui choisi le fichier à analyser.
import ChoixFramerateListe as cfr  # On doit définir le framerate pour avoir un TC.
import Rapport as r
import ServeurDate as date
import TimecodeP as tc

# == VALEURS ==

# Si on peut utiliser le programme
licence = None

# Se connecte pour voir si on dépasse la limite d'utilisation du programme :
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
    Donne le TC actuel à l'aide d'un nombre d'images et sur base d'un tc de depart.

    :param int num_image: Numéro d'image.
    :param int framerate: Framerate.
    """
    tc1 = Timecode(framerate, starttc)
    if num_image > 0:
        # Comme le résultat est toujours une image en trop, j'enleve ce qu'il faut: :)
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


def close() -> None:
    """
    Cloture l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
    """
    # On récupère les dernières valeurs de la liste.
    updateListeProbleme()  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux :
    r.close()


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if licence:
    # Fichier 1:
    cf.fenetre()
    fichier = cf.filename.get()
    print('fichier 1: ' + str(fichier))
    print('- Start tc: ' + str(startTimeCodeFile(fichier)))

    duree = 100

    # Note: [-1] = dernier element de la liste.
    r.rapport(fichier.split('/')[-1], 'html')

    # r.setRapport("== Debut du rapport ==\n")

    framerate = int(cfr.getFramerate())

    print('- Framerate: ' + str(framerate))

    r.start(fichier, str(duree), str(startTimeCodeFile(fichier)), framerate)

    # Fichier 2:
    cf2.fenetre()
    fichier2 = cf2.filename.get()
    print('fichier 2: ' + str(fichier2))
    print('- Start tc: ' + str(startTimeCodeFile(fichier2)))

close()

# == END ==
