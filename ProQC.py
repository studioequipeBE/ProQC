#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Main.
"""

# == IMPORTS ==
import imageio
import numpy as np
import os

from ChoixFichier import ChoixFichier  # Programme qui choisi le fichier à analyser.
from ChoixRatio import ChoixRatio
from ChoixTC import ChoixTC  # Programme qui choisi l'intervalle à analyser.
import fonctions as fct
from Rapport import Rapport
from outils.metadata import MetaData

ffmpeg = fct.get_ffmpeg()
os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg

# == VALEURS ==
ratio = None

start_y = None
end_y = None
start_x = None
end_x = None

x_p = None
y_p = None

x_g = None
y_g = None

start_y_p = None
end_y_p = None
start_x_p = None
end_x_p = None

start_y_g = None
end_y_g = None
start_x_g = None
end_x_g = None

# Matrice pour media offline Premiere.
MOLP25 = None
MOLP100 = None

# Matrice pour media offline Resolve.
MOLR25 = None
MOLR100 = None

# Matrice pour le drop Resolve.
DR25 = None
DR100 = None

starttc = None
starttc_frame = 0
endtc_frame = None

framerate = None

# Liste des erreurs : tc in | tc out | erreur
list_tc_in = np.array([])
list_tc_out = np.array([])
list_erreur = np.array([])

# Fichier pour rapport :
file = None

# Les images ref :
reader_MOLP = imageio.get_reader('ImageRef/AppleProRes444/MEDIAOFFLINE_PREMIERE_PR444_1920x1080_2.mov',
                                 ffmpeg_params=["-an"])
MOLP = reader_MOLP.get_data(0)
reader_MOLP.close()

reader_MOLR = imageio.get_reader('ImageRef/AppleProRes444/MEDIAOFFLINE_RESOLVE_PR444_1920x1080.mov',
                                 ffmpeg_params=["-an"])
MOLR = reader_MOLR.get_data(0)
reader_MOLR.close()


# == FONCTIONS ==
def update_liste_probleme(num_image) -> None:
    """
    Met à jour la liste des erreurs pour écrire dans le rapport.

    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur, rapport

    # Parcoure la liste des problèmes, si tc out discontinu, alors on écrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (num_image - 1):
            # On écrit dans le rapport l'erreur :

            # La notion de temps en timecode
            rapport.add_probleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]), '')

            # On supprime de la liste l'erreur :
            list_tc_in = np.delete(list_tc_in, i)
            list_tc_out = np.delete(list_tc_out, i)
            list_erreur = np.delete(list_erreur, i)
            # On doit stagner dans les listes si on supprime un élément.
            i -= 1


def add_probleme(message: str, num_image: int) -> None:
    """
    Quand on doit reporter un problème dans le rapport.

    :param str message: Le message.
    :param int num_image: Numéro d'image.
    """
    global list_tc_in, list_tc_out, list_erreur

    new = True

    # Si l'erreur est dans la liste :
    for i in range(0, np.size(list_tc_in, 0)):
        if list_erreur[i] == message:
            list_tc_out[i] = num_image  # Met à jour le tc out.
            new = False

    # Sinon, on ajoute le problème à la liste :
    if new:
        list_tc_in = np.append(list_tc_in, num_image)
        list_tc_out = np.append(list_tc_out, num_image)
        list_erreur = np.append(list_erreur, message)


def set_ratio(ratio_tmp: str) -> None:
    """
    On définit le ratio et on prépare les matrices d'analyse de l'image.

    :param str ratio_tmp: Nouvelle valeur ratio.
    """
    global ratio, start_x, end_x, start_y, end_y, x_p, y_p, x_g, y_g
    global start_y_p, end_y_p, start_x_p, end_x_p
    global start_y_g, end_y_g, start_x_g, end_x_g
    global MOLP25, MOLP100, MOLR25, MOLR100

    ratio = ratio_tmp
    # Ligne utile en 2.39 1920x1080
    if ratio == '2.39':
        start_y = 138
        end_y = 941
    # Ligne utile en 1.77 1920x1080
    else:
        start_y = 0
        end_y = 1079
    # Implementer, plus tard: 1.33 (dans 1920x1080), et surtout le 1.85.

    x_p = 1920 / 7
    y_p = (end_y - start_y) / 7

    x_g = 1920 / 12
    y_g = (end_y - start_y) / 12

    # Définit les valeurs de x (import quand on aura du 4/3).
    start_x = 0
    end_x = 1919

    # Définit l'image utile en haut/bas, gauche/droite pour la "petite analyse" (5x5) et la "grande analyse" (10x10) :
    start_y_p = start_y + y_p
    end_y_p = start_y + (y_p * 6)
    start_x_p = start_x + x_p
    end_x_p = start_x + (x_p * 6)

    start_y_g = start_y + y_g
    end_y_g = start_y + (y_g * 11)
    start_x_g = start_x + x_g
    end_x_g = start_x + (x_g * 11)

    # Pour être plus rapide, on fait les 2 sous-matrices qu'une fois ! On a besoin du format d'image.
    MOLP25 = MOLP[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]
    MOLP100 = MOLP[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]

    MOLR25 = MOLR[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]
    MOLR100 = MOLR[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]


def detecte_noir(image) -> bool:
    """
    Détecter les noirs.
    methodeAnalyse est la precision avec laquelle il faut vérifier l'image.

    :param image:
    """

    # Vérifie 5*5 pixels: 3,3 MHz (pour un film de 90min en 24 i/s)
    if image[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p].max() < 15:
        # Vérifie 10*10 pixels : 13 MHz (pour un film de 90min en 24 i/s)
        if image[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g].max() < 15:
            # Vérifie tous les pixels : 269 GHz (pour un film de 90min en 24 i/s)
            # Si le total de tous les pixels est inférieurs à 100, alors l'image est noire...
            if image.max() < 15:
                return False
    return True


# Note : si retourne 'False' c'est que ce n'est pas bon...


def compare_tab(a, b):
    """
    Compare deux matrices, renvoi une liste avec des True et des False pour l'égalité de la valeur aux mêmes coordonnées.

    :param a:
    :param b:
    """
    return str(a == b)


def media_offline_premiere(image) -> bool:
    """
    Détecter "mediaoffline" Premiere.

    :param image:
    """
    if compare_tab(MOLP25, image[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]).count(
            'False') < 2:  # Marge d'erreur de 2 sur 25
        if compare_tab(MOLP100, image[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]).count(
                'False') < 10:  # Marge d'erreur de 10 sur 100
            # Egalite des deux matrices + la soustraction des deux doit donner moins de 500 :
            if compare_tab(MOLP, image).count('False') < 150:  # Marge d'erreur de 150 sur 1920*1080
                return False
            else:
                return True
    return True


def media_offline_resolve(image) -> bool:
    """
    Détecter "mediaoffline" Premiere.

    :param image:
    """
    if compare_tab(MOLR25, image[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]).count(
            'False') < 2:  # Marge d'erreur de 2 sur 25.
        if compare_tab(MOLR100, image[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]).count(
                'False') < 10:  # Marge d'erreur de 10 sur 100.
            # Égalité des deux matrices + la soustraction des deux doit donner moins de 500 :
            if compare_tab(MOLR, image).count('False') < 150:  # Marge d'erreur de 150 sur 1920*1080
                return False
            else:
                return True
    return True


def ligne_haut_image(image) -> bool:
    """
    Détecter quand les blankings ne sont pas justes :
    ratio est le ratio à verifier pour les blankings.
    Prévu pour 2.39.

    :param image:
    """
    tab = image[start_y:(start_y + 1):1, 0:1920:1]
    if tab.sum() < 1000 and tab.max() < 3:
        return False
    else:
        return True


def ligne_bas_image(image) -> bool:
    """
    Vérifie si les blanking du bas sont correctes.
    Prévu pour 2.39.

    :param image:
    """
    tab = image[end_y:(end_y + 1):1, 0:1920:1]
    if tab.sum() < 1000 and tab.max() < 3:
        return False
    else:
        return True


def colonne_gauche_image(image) -> bool:
    """
    Vérifie les blankings gauches.

    :param image:
    """
    tab = image[start_y:(end_y + 1):1, 0:1:1]
    if tab.sum() < 1000 and tab.max() < 5:
        return False
    else:
        return True


def colonne_droite_image(image) -> bool:
    """
    Vérifie les blankings droits.

    :param image:
    """
    tab = image[start_y:(end_y + 1):1, 1919:1920:1]
    if tab.sum() < 1000 and tab.max() < 5:
        return False
    else:
        return True


def blanking_haut(image) -> bool:
    """
    Vérifie les blankings hauts.
    Prévu pour 2.39.

    :param image:
    """
    if image[0:start_y:1, 0:1920:1].max() > 4:
        return False
    else:
        return True


def blanking_bas(image) -> bool:
    """
    Vérifie les blanking bas.
    Prévu pour 2.39.

    :param image:
    """
    if image[(end_y + 1):1080:1, 0:1920:1].max() > 4:
        return False
    else:
        return True


def close() -> None:
    """
    Clôturer l'analyse d'une video (en clôturant son flux ainsi que celui du rapport).
    """
    global rapport
    # On récupère les dernières valeurs de la liste.
    update_liste_probleme(i + 1)

    # On clôture tous les flux :
    reader.close()
    rapport.close()


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    # Note : Normalement décode du Pro Res 422HQ ! :)
    cf = ChoixFichier(ChoixFichier.liste_fichier_video())
    cf.show()
    fichier = cf.get_filename()
    print('fichier: ' + fichier)
    print('Start tc: ' + fct.start_timecode_file(ffmpeg, fichier))
    reader = imageio.get_reader(fichier, ffmpeg_params=['-an'])

    # Récupère les informations concernant le fichier.
    metadonnees = MetaData(fichier)
    framerate = metadonnees.framerate()

    # Note: [-1] = dernier element de la liste.
    rapport = Rapport(fichier.split('/')[-1], True, 'html')

    cr = ChoixRatio()
    cr.show()
    ratio = cr.get_ratio()

    # Choix du ratio :
    set_ratio(ratio)
    duree = reader.get_length()
    endtc_frame = duree - 1
    print('Ratio: ' + ratio)

    ctc = ChoixTC()
    ctc.set_timecode_in(str(starttc_frame))
    ctc.set_timecode_out(str(endtc_frame))

    # Choix du timecode (debut et fin) à vérifier :
    ctc.show()

    starttc_frame = ctc.get_timecode_in()
    endtc_frame = ctc.get_timecode_out()

    rapport.set_informations(duree, '00:00:00:00', framerate, ratio)

    # Choix des vérifications : noirs, drop, mediaoffline...
    # Chaque iteration équivaut à une image :
    for i, image in enumerate(reader, start=0):

        # Met à jour la liste des erreurs (pour avoir un group de tc pour une erreur) :
        update_liste_probleme(i)

        # Affiche l'avancement tous les 24 images :
        if (i % (framerate * 3)) == 0:
            print(str(i) + ' / ' + str(duree))

        # On regarde si l'image est noir :
        if not detecte_noir(image):
            add_probleme("L'image est noire", i)
        # Si l'image n'est pas noir :
        # MediaOffLine Premiere ?
        elif not media_offline_premiere(image):
            add_probleme('Media offline Premiere', i)
        # Media Offline Resolve?
        elif not media_offline_resolve(image):
            add_probleme('Media offline Resolve', i)
        # Drop de Resolve ?
        # elif not DropResolve(image):
        #    Probleme("Drop Resolve", i)
        # Si l'image n'est pas un média offline ou drop sur toute l'image, alors on peut s'intéresser au blanking et/ou lignes utiles de l'image.
        else:
            if not ligne_haut_image(image):
                add_probleme('Ligne noir en haut de l\'image', i)

            if not ligne_bas_image(image):
                add_probleme('Ligne noire en bas de l\'image', i)

            if not colonne_gauche_image(image):
                add_probleme('Colonne noire à gauche de l\'image', i)

            if not colonne_droite_image(image):
                add_probleme('Colonne noire à droite de l\'image', i)

            # On ne vérifie les bandes noires que si on n'est pas du 1.77 et que l'image n'est pas noir :
            if ratio != '1.77':
                if not blanking_haut(image):
                    add_probleme('Les blankings du haut ne sont pas noirs', i)
                if not blanking_bas(image):
                    add_probleme('Les blankings du bas ne sont pas noirs', i)

close()

# == END ==
