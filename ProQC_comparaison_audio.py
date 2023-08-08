#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Main.
"""

# == IMPORTS ==
import numpy as np
import os

from ChoixFichier import ChoixFichier  # Programme qui choisi le fichier à analyser.
from ChoixFramerate import ChoixFramerate  # On doit définir le framerate pour avoir un TC.
import fonctions as fct
from Rapport import Rapport

ffmpeg = fct.get_ffmpeg()
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
def update_liste_probleme(num_image: int) -> None:
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.

    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_option, num_erreur, rapport

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            num_erreur = num_erreur + 1
            print(str(num_erreur) + ' / ' + str(list_tc_in[i]) + ' : update liste, on ajoute une erreur !')
            # On écrit dans le rapport l'erreur :
            rapport.add_probleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]),
                                 str(liste_option[i]))

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
    # cf = ChoixFichier(ChoixFichier.liste_fichier_audio())
    # cf.show()
    fichier = 'C:/Users/win10dev/Desktop/braqueurs_s01_e101_v03_PM_Nearfield_2ch_48k_24b_24.L.wav'  # cf.get_filename()
    print('Fichier 1: ' + str(fichier))
    start_tc = fct.start_sample_rate_file(ffmpeg, fichier)
    print('- Start tc: ' + str(start_tc))

    duree = 100

    # Note: [-1] = dernier element de la liste.
    rapport = Rapport(fichier.split('/')[-1], True)

    # cfr = ChoixFramerate()
    # cfr.show()

    framerate = 24  # int(cfr.get_framerate())

    print('- Framerate: ' + str(framerate))

    rapport.set_informations(duree, start_tc, framerate, '', '')

    # Fichier 2:
    # cf = ChoixFichier(ChoixFichier.liste_fichier_audio())
    # cf.show()
    fichier2 = 'C:/Users/win10dev/Desktop/braqueurs_s01_e101_v04_PM_Nearfield_2ch_48k_24b_24.L.wav'  # cf.get_filename()
    print('Fichier 2: ' + str(fichier2))
    print('- Start tc: ' + str(fct.start_sample_rate_file(ffmpeg, fichier2)))

    # Cloture l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
    # On récupère les dernières valeurs de la liste.
    update_liste_probleme(duree)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    import soundfile as sf

    a = '0'

    signal, samplerate = sf.read(fichier)
    signal2, samplerate2 = sf.read(fichier2)

    print('- Signal: ' + str(signal))
    print('- size: ' + str(signal.size))
    print('- Samplerate: ' + str(samplerate))
    print('- Duree : ' + str(signal.size / samplerate))

    print('- Signal2: ' + str(signal2))
    print('- size2: ' + str(signal2.size))
    print('- Samplerate2: ' + str(samplerate2))

    if signal2.size > signal.size:
        print('OUI : ' + str(signal2.size - signal.size))
        signal = np.append(signal, np.zeros(signal2.size - signal.size))
    elif signal2.size < signal.size:
        print('OUI : ' + str(signal.size - signal2.size))
        signal2 = np.append(signal2, np.zeros(signal.size - signal2.size))

    print('- size: ' + str(signal.size))
    print('- size2: ' + str(signal2.size))
    signal3 = signal - signal2
    print('- signal3: ' + str(signal3))

    difference = np.count_nonzero(signal3 != 0)
    liste_diff = np.transpose((signal3 != 0).nonzero())

    liste_diff = liste_diff + start_tc
    liste_diff = liste_diff // (samplerate/framerate)

    print('- difference: ' + str(difference))
    print('- liste_diff: ' + str(liste_diff))

    f = open('C:/Users/win10dev/Desktop/rapport.txt', 'w+')

    last_tc = ''

    tc_courant = ''

    for i in range(0, len(liste_diff)):
        tc_courant = fct.tc_actuel(liste_diff[i][0], '00:00:00:00', framerate)
        if tc_courant != last_tc:
            f.write(tc_courant + '\n')
            last_tc = tc_courant
    f.close()

    # On clôture tous les flux.
    rapport.close()

# == END ==
