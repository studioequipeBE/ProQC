#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier: Main (+ les fonctions...)
# Version: 0.9

# == IMPORTS ==
import timecode as Timecode
import imageio
import subprocess as sp
import numpy as np
import TimecodeP as tc

# from TimecodeP import Timecodes
import ServeurDate as date

import ChoixFichier as cf  # Programme qui choisi le fichier a analyser.
import ChoixFichier as cf2  # Programme qui choisi le fichier a analyser.
import ChoixFramerateListe as cfr
import ChoixTC as ctc  # Programme qui choisi l'interval a analyser
import Rapport as r
import sys
from PIL import Image

# == VALEURS ==

# Si on peut utiliser le programme
licence = None

# Se connecte pour voir si on depasse la limite d'utilisation du programme:
if int(date.Aujourdhui()) <= 20201025:
    print
    "Licence OK"
    licence = True
else:
    print
    "Licence depassee/!\\"
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

option_afficher = ""  # Valeur des paramètres.

# Liste des erreurs: tc in | tc out | erreur | option
list_tc_in = np.array([])
list_tc_out = np.array([])
list_erreur = np.array([])
liste_option = np.array([])

# Fichier pour rapport:
file = None

# Numéro d'erreur
num_erreur = 0


# == FONCTIONS ==

# Donne le TC actuel à l'aide d'un nombre d'image et sur base d'un tc de depard:
def TcActuel(numImage, framerate=24):
    tc1 = Timecode(framerate, starttc)
    if numImage > 0:
        # Comme le résultat est toujours une image en trop, j'enleve ce qu'il faut: :)
        tc2 = Timecode(framerate, tc.frames_to_timecode((numImage - 1), framerate))
        tc3 = tc1 + tc2
        return tc3
    else:
        return tc1


# Met a jour la liste des erreurs pour ecrire dans le rapport:
def UpdateListeProbleme(numImage):
    global list_tc_in, list_tc_out, list_erreur, liste_option, num_erreur

    # Parcoure la liste des problemes, si tc out discontinu, alors on ecrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (numImage - 1):
            num_erreur = num_erreur + 1
            print
            str(num_erreur) + " / " + str(list_tc_in[i]) + " : update liste, on ajoute une erreur!"
            # On ecrit dans le rapport l'erreur:

            # La notion de temps en timecode
            # r.setRapport(str(TcActuel(list_tc_in[i], framerate)) + " a " + str(TcActuel(list_tc_out[i], framerate)) + ": " + str(list_erreur[i]) + "\n")
            # La notion de temps en image
            # r.setRapport(str(int(list_tc_in[i])) + " a " + str(int(list_tc_out[i])) + ": " + str(list_erreur[i]) + "\n")
            r.addProbleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]), str(liste_option[i]))

            # On supprime de la liste l'erreur:
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            liste_option = np.delete(liste_option, i)
            # On doit stagner dans les listes si on supprime un element.
            i -= 1


# Quand on doit reporter un probleme dans le rapport:
def Probleme(message, option, numImage):
    global list_tc_in, list_tc_out, list_erreur, liste_option

    # Si c'est une nouvelle erreur:
    new = True

    # Si l'erreur est dans la liste:
    for i in range(0, np.size(list_tc_in, 0)):
        if list_erreur[i] == message:
            list_tc_out[i] = numImage  # Met a jour le tc out
            new = False

    # Sinon, on ajoute le probleme a la liste:
    if new:
        # Dans append, on spécifie le tableau à qui on ajoute une valeur.
        list_tc_in = np.append(list_tc_in, numImage)
        list_tc_out = np.append(list_tc_out, numImage)
        liste_option = np.append(liste_option, option)
        list_erreur = np.append(list_erreur, message)


# Timecode du fichier analyse:
def StartTimeCodeFile(fichier):
    global starttc
    command = ["ffmpeg.exe", '-i', fichier, '-']
    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
    pipe.stdout.readline()
    pipe.terminate()
    infos = pipe.stderr.read()
    tc = ""
    for i in range(18, 29):
        tc += infos[(infos.find("timecode") + i)]
    starttc = tc
    return tc


delta = 0.01  # Delta qu'on tolère entre 2 images.
delta_min = 1 - delta  # Delta min
delta_max = 1 + delta  # Delta max


# Affichage automatisé:
def setOption(i_sum, i2_sum, i_min, i2_min, i_mean, i2_mean, i_max, i2_max):
    global option_afficher

    if i_sum != 0:
        calcule = (100.0 / i2_sum) * i_sum
    else:
        calcule = 0

    option_afficher = "(ratio: " + str(i_sum) + " [~" + str(i_mean) + ", -" + str(i_min) + ", +" + str(
        i_max) + "] / " + str(i2_sum) + " [~" + str(i2_mean) + ", -" + str(i2_min) + ", +" + str(i2_max) + "]): " + str(
        calcule) + "%"


# Vérifie que 2 images sont identiques:

# Méthode via la moyenne des images:
def Identique(image, image2):
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


# Cloturer l'analyse d'une video (en cloturant son flux ainsi que celui du rapport):
def close():
    # On récupère les dernières valeurs de la liste.
    UpdateListeProbleme(i)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On cloture tous les flux:
    reader.close()
    r.close()


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if licence:
    # Fichier 1:
    cf.Fenetre()
    fichier = cf.filename.get()
    print("fichier 1: " + str(fichier))
    print("- Start tc: " + str(StartTimeCodeFile(fichier)))

    # Image quoi? RGB/NB??? En fait, cette information est importante...
    reader = imageio.get_reader(fichier, ffmpeg_params=["-an"])

    framerate = int(cfr.getFramerate())

    print("- Framerate: " + str(framerate))

    duree = reader.get_length()

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier:
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Note: [-1] = dernier element de la liste.
    r.Rapport(fichier.split('/')[-1], "html")

    # r.setRapport("== Debut du rapport ==\n")

    r.Start(fichier, str(duree), str(StartTimeCodeFile(fichier)), framerate)

    # Fichier 2:
    cf2.Fenetre()
    fichier2 = cf2.filename.get()
    print
    "fichier 2: " + str(fichier2)
    print
    "- Start tc: " + str(StartTimeCodeFile(fichier2))

    # Image quoi? RGB/NB??? En fait, cette information est importante...
    reader2 = imageio.get_reader(fichier2, ffmpeg_params=["-an"])

    framerate2 = int(cfr.getFramerate())

    print
    "- Framerate: " + str(framerate)

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier:
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Chaque iteration équivaut à une image:
    for i, image in enumerate(reader):

        image2 = reader2.get_data(i)  # Récupère l'image suivante de reader2 (image 2).

        # Met a jout la liste des erreurs (pour avoir un groupe de tc pour une erreur):
        UpdateListeProbleme(i)

        # Affiche l'avancement tous les 30 secondes:
        if (i % (framerate * 30)) == 0:
            print
            str(i) + " / " + str(duree)

        if not Identique(image, image2):
            Probleme("Demi ligne <strong>haut</strong>.", str(option_afficher), i)

close()

# == END ==
