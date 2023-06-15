#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Main (+ les fonctions...)

# == IMPORTS ==
import hashlib
import imageio
import numpy as np
import os
import xml.etree.ElementTree as xmlparser

import fonctions as fct
import RapportComparaison as r

ffmpeg = 'C:\\ffmpeg\\ffmpeg.exe'

os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg

# == VALEURS ==

# == Declaration variables: ==
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

# Numéro d'erreur
num_erreur = 0


# == FONCTIONS ==
def updateListeProbleme(rapport, num_image: int) -> None:
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.

    :param rapport:
    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, num_erreur

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            num_erreur = num_erreur + 1
            print(str(num_erreur) + ' / ' + str(list_tc_in[i]) + " : update liste, on ajoute une erreur!")
            # On écrit dans le rapport l'erreur :

            # La notion de temps en image.
            rapport.addDifference(str(int(list_tc_in[i])), str(int(list_tc_out[i])))

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


def addProbleme(message, option, num_image) -> None:
    """
    Quand on doit reporter un problème dans le rapport.

    :param str message: Le message.
    :param str option: Les options.
    :param int num_image: Le numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur

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


delta = 0.01  # Delta qu'on tolère entre 2 images.
delta_min = 1 - delta  # Delta min
delta_max = 1 + delta  # Delta max


def identique(image1, image2, methode: int) -> bool:
    """
    Vérifie que 2 images sont identiques.
    Méthode via la moyenne des images.

    :param image1:
    :param image2:
    :param int methode: Méthode de comparaison.
        0 = pixel par pixel,
        1 = moyenne,
        2 = somme,
        3 = MD5 : ne pas utiliser.

    :return: True si les deux images sont les mêmes.
    """

    # Comparaison pixel par pixel :
    if methode == 0:
        compare = np.array(image1) == np.array(image2)
        compare2 = (image1 == image2).all()
        if compare2:
            print('Identique.')
            return True
        else:
            print('Dif.')
            return False
    # Comparaison par moyenne :
    elif methode == 1:
        if image1.mean() == image2.mean():
            return True
        else:
            return False
    # Comparaison par différence :
    elif methode == 2:
        diff = np.abs(image1.astype(np.intc) - image2.astype(np.intc))
        # sum = diff.sum()
        max = diff.max()

        print('max (intc) = ' + str(max))
        # print('sum (intc) = ' + str(sum))

        # Si la différence est infime, alors on dit que c'est la même chose.
        if max <= 1:  # sum <= 1000 and # La sum tient compte de s'il y a beaucoup de différence entre les deux images.
            return True
        else:
            return False
    # Comparaison par MD5 :
    elif methode == 3:
        image1_md5 = hashlib.md5(image1)
        image2_md5 = hashlib.md5(image2)

        if image1_md5.hexdigest() == image2_md5.hexdigest():
            return True
        else:
            return False


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    # TODO : Import XML de comparaison (généré par App Java):
    xml = xmlparser.parse('C:\\Users\\win10dev\\Desktop\\comparaison.xml')
    options = xml.getroot().find('options')
    fichier_ref = xml.getroot().find('fichier_ref')
    chemin_fichier_ref = fichier_ref.find('chemin').text
    fichiers = xml.getroot().find('fichiers')

    start_tc = fct.startTimeCodeFile(ffmpeg, chemin_fichier_ref)
    print('- Start tc: ' + start_tc)

    # Construit une DB avec le résultat.
    rapport = r.RapportComparaison(os.path.basename(chemin_fichier_ref))

    # Image quoi ? RGB/NB??? En fait, cette information est importante...
    reader = imageio.get_reader(chemin_fichier_ref, ffmpeg_params=['-an'])

    framerate = int(reader.get_meta_data()['fps'])

    print('- Framerate: ' + str(framerate))

    duree_seconde = str(reader.get_meta_data()['duration']).split('.')

    duree = int(duree_seconde[0]) * framerate + int((int(duree_seconde[1]) / 100) * framerate)

    rapport.rapport(duree, start_tc, framerate, False)

    endtc_frame = duree - 1

    # On vérifie l'intégralité du fichier :
    starttc_frame = starttc_frame
    endtc_frame = endtc_frame

    # Fichier 2:
    for fichier in fichiers:
        # Chemin du 2ième fichier
        fichier2 = fichier.find('chemin').text
        print('fichier 2: ' + fichier2)
        start_tc_f2 = fct.startTimeCodeFile(ffmpeg, fichier2)
        print('- Start tc: ' + start_tc_f2)

        # Image quoi ? RGB/NB??? En fait, cette information est importante...
        reader2 = imageio.get_reader(fichier2, ffmpeg_params=['-an'])

        framerate2 = int(reader2.get_meta_data()['fps'])

        print('- Framerate: ' + str(framerate))

        endtc_frame = duree - 1

        # On vérifie l'intégralité du fichier :
        starttc_frame = starttc_frame
        endtc_frame = endtc_frame

        rapport.addFichier(os.path.basename(fichier2), start_tc_f2)

        # Chaque iteration équivaut à une image :
        for i, image in enumerate(reader, 0):
            image2 = reader2.get_data(i)  # Récupère l'image suivante de reader2 (image 2).

            # Met à jour la liste des erreurs (pour avoir un groupe de tc pour une erreur).
            updateListeProbleme(rapport, i)

            # Affiche l'avancement tous les 30 secondes :
            if (i % (framerate * 30)) == 0:
                print(str(i) + ' / ' + str(duree))

            if not identique(image, image2, 2):
                addProbleme('Pas les mêmes image.', str(option_afficher), i)

        # Ferme le flux du fichier à comparer.
        reader2.close()

        # Clôturer l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
        # On récupère les dernières valeurs de la liste.
        updateListeProbleme(rapport, duree)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

    # On clôture tous les flux :
    reader.close()
    rapport.close()

print('Fin analyse.')
