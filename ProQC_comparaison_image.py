#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Main.
"""

# == IMPORTS ==
import hashlib

import imageio
import numpy as np
import os
import xml.etree.ElementTree as xmlparser

import fonctions as fct
from ListePoint import ListePoint
from Point import Point
from outils.metadata import MetaData
from RapportComparaison import RapportComparaison

ffmpeg = fct.get_ffmpeg()
os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg


# == FONCTIONS ==
def update_liste_probleme(num_image: int) -> None:
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.

    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_pourcentage, liste_pixel, liste_nombre_canal, num_erreur

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            num_erreur = num_erreur + 1
            print(str(num_erreur) + ' / ' + str(list_tc_in[i]) + ' : update liste, on ajoute une erreur !')
            # On écrit dans le rapport l'erreur :

            # La notion de temps en image.
            rapport.add_difference(str(int(list_tc_in[i])), str(int(list_tc_out[i])), liste_pourcentage[i], liste_pixel[i])

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            liste_pourcentage = np.delete(liste_pourcentage, i)
            liste_pixel.pop(i)
            liste_nombre_canal = np.delete(liste_nombre_canal, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


def add_probleme(message: str, pourcentage: float, pixels: ListePoint, nombre_canal: int, num_image: int) -> None:
    """
    Quand on doit reporter un problème dans le rapport.

    :param str message: Le message.
    :param float pourcentage : Le pourcentage de différence.
    :param int num_image: Le numéro d'image.
    :param ListePoint pixels: Ensemble de pixel.
    :param int nombre_canal: Nombre de canaux modifiés.
    """
    global list_tc_in, list_tc_out, list_erreur, liste_pourcentage, liste_pixel, liste_nombre_canal

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
        liste_pourcentage = np.append(liste_pourcentage, pourcentage)
        liste_pixel.append(pixels)
        liste_nombre_canal = np.append(liste_nombre_canal, nombre_canal)


def pixel_loin(liste_pixel_ajoute: ListePoint, pixel: tuple[int, int, int]) -> bool:
    """
    Vérifie un pixel s'il est proche de ceux qui sont déjà dans la liste.
    """
    if liste_pixel_ajoute.size():
        for pixel_ajoute in liste_pixel_ajoute.get_liste():
            # Si le pixel qui nous intéresse est déjà trop près d'un autre, on le refuse.
            if abs(pixel_ajoute.x - pixel[0]) < 20 and abs(pixel_ajoute.y - pixel[1]) < 20:
                return False
    return True


def identique(image1, image2, methode: int) -> tuple[bool, float, ListePoint, int]:
    """
    Vérifie que 2 images sont identiques.
    Méthode via la moyenne des images.

    :param image1:
    :param image2:
    :param int methode: Méthode de comparaison.
        0 = pixel par pixel,
        1 = moyenne,
        2 = différence,
        3 = MD5 : ne pas utiliser (car il est possible que les deux fichiers n'ont pas été codé de la même manière).

    :return: True si les deux images sont les mêmes.
    """
    global nombre_pixel
    # Comparaison pixel par pixel :
    if methode == 0:
        compare2 = (image1 == image2).all()
        if compare2:
            return True, 0, ListePoint(), 0
        else:
            return False, 100, ListePoint(), -1
    # Comparaison par moyenne :
    elif methode == 1:
        if image1.mean() == image2.mean():
            return True, 0, ListePoint(), 0
        else:
            return False, 100, ListePoint(), -1
    # Comparaison par différence :
    elif methode == 2:
        diff = np.abs(image1.astype(np.intc) - image2.astype(np.intc))
        # sum = diff.sum()
        max = diff.max()

        print('max (intc) = ' + str(max))
        # print('sum (intc) = ' + str(sum))

        # Si la différence est infime, alors on dit que c'est la même chose.
        if max <= 1:  # sum <= 1000 and # La sum tient compte de s'il y a beaucoup de différence entre les deux images.
            return True, 0, ListePoint(), 0
        else:
            # Ici, on indique le pourcentage.
            nombre_different = np.count_nonzero(diff > 1)
            print('nombre_different : ' + str(nombre_different))
            pourcentage = round((float(nombre_different) / nombre_pixel) * float(100.0), 6)
            print('Différent à : ' + format(pourcentage, '.6f') + '%')

            # Ici, on récupère quelques pixels qui posent soucis.
            if pourcentage < 2:
                liste_pixel_image = ListePoint()

                for delta in reversed(range(1, max)):
                    liste_pixel_delta = np.transpose((diff == delta).nonzero())
                    for pixel in liste_pixel_delta:
                        # On ajoute jusqu'à 10 pixels max.
                        if liste_pixel_image.size() < 10:
                            # Les pixels en plus doivent être loin :
                            if pixel_loin(liste_pixel_image, pixel):
                                print('pixel add : ' + str(pixel[0]) + ', ' + str(pixel[1]))
                                liste_pixel_image.add_point(Point(pixel[0], pixel[1]))
                        else:
                            break

                    if liste_pixel_image.size() >= 10:
                        break
            else:
                liste_pixel_image = ListePoint()

            return False, pourcentage, liste_pixel_image, nombre_different
    # Comparaison par MD5 :
    elif methode == 3:
        image1_md5 = hashlib.md5(image1)
        image2_md5 = hashlib.md5(image2)

        if image1_md5.hexdigest() == image2_md5.hexdigest():
            return True, 0, ListePoint(), 0
        else:
            return False, 100, ListePoint(), -1


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    # TODO : Import XML de comparaison (généré par App Java):
    xml = xmlparser.parse(fct.get_desktop() + os.sep + 'comparaison.xml')

    # S'il y a plusieurs comparaisons à faire :
    for comparaison in xml.getroot().findall('comparaison'):

        # == Déclaration variables: ==
        starttc = None
        starttc_frame = 0
        endtc_frame = None

        framerate = None
        nombre_pixel = None

        # Liste des erreurs : tc in | tc out | erreur | option | pourcentage
        list_tc_in = np.array([])
        list_tc_out = np.array([])
        list_erreur = np.array([])
        liste_option = np.array([])
        liste_pourcentage = np.array([])
        liste_pixel = []
        liste_nombre_canal = np.array([])

        # Numéro d'erreur
        num_erreur = 0

        options = comparaison.find('options')
        fichier_ref = comparaison.find('fichier_ref')
        chemin_fichier_ref = fichier_ref.find('chemin').text
        fichiers = comparaison.find('fichiers')

        print('Ref : ' + chemin_fichier_ref)

        start_tc = fct.start_timecode_file(ffmpeg, chemin_fichier_ref)
        print('- Start tc: ' + start_tc)

        # Construit une DB avec le résultat.
        rapport = RapportComparaison(os.path.basename(chemin_fichier_ref), True)

        # Image quoi ? RGB/NB??? En fait, cette information est importante...
        reader = imageio.get_reader(chemin_fichier_ref, ffmpeg_params=['-an'])

        framerate = int(reader.get_meta_data()['fps'])

        print('- Framerate: ' + str(framerate))

        duree_seconde = str(reader.get_meta_data()['duration']).split('.')

        duree_image = int(duree_seconde[0]) * framerate + int((int(duree_seconde[1]) / 100) * framerate)

        # Récupère les informations concernant le fichier.
        metadonnees = MetaData(chemin_fichier_ref)
        resolution = metadonnees.resolution()  # '3840x2160'

        nombre_pixel = int(resolution.split('x')[0]) * int(resolution.split('x')[0]) * 3

        rapport.set_information(duree_image, start_tc, framerate, resolution)

        # On vérifie l'intégralité du fichier :
        starttc_frame = starttc_frame
        endtc_frame = duree_image - 1

        # Fichier 2:
        for fichier in fichiers:
            # Chemin du 2ième fichier
            fichier2 = fichier.find('chemin').text
            print('fichier 2: ' + fichier2)
            start_tc_f2 = fct.start_timecode_file(ffmpeg, fichier2)
            print('- Start tc: ' + start_tc_f2)

            # Image quoi ? RGB/NB??? En fait, cette information est importante...
            reader2 = imageio.get_reader(fichier2, ffmpeg_params=['-an'])

            framerate2 = int(reader2.get_meta_data()['fps'])

            print('- Framerate: ' + str(framerate))

            endtc_frame = duree_image - 1

            # On vérifie l'intégralité du fichier :
            starttc_frame = starttc_frame
            endtc_frame = endtc_frame

            duree_seconde = str(reader2.get_meta_data()['duration']).split('.')

            duree_image = int(duree_seconde[0]) * framerate + int((int(duree_seconde[1]) / 100) * framerate)

            rapport.add_fichier(os.path.basename(fichier2), start_tc_f2, duree_image)

            # Chaque iteration équivaut à une image :
            for i, image in enumerate(reader, 0):
                image2 = reader2.get_data(i)  # Récupère l'image suivante de reader2 (image 2).

                # Met à jour la liste des erreurs (pour avoir un groupe de tc pour une erreur).
                update_liste_probleme(i)

                # Affiche l'avancement tous les 30 secondes :
                if (i % (framerate * 30)) == 0:
                    print(str(i) + ' / ' + str(duree_image))

                valeurs_identique = identique(image, image2, 2)

                if not valeurs_identique[0]:
                    add_probleme('Pas les mêmes image.', valeurs_identique[1], valeurs_identique[2], valeurs_identique[3], i)

            # Ferme le flux du fichier à comparer.
            reader2.close()

            # Clôturer l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
            # On récupère les dernières valeurs de la liste.
            update_liste_probleme(duree_image)  # De prime à bord, il ne faut pas incrémenter la valeur, elle l'est déjà.

        # On clôture tous les flux :
        reader.close()
        rapport.close()

    print('Fin analyse.')

print('Fin des analyses.')
