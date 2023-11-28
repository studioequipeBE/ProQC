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

# == Declaration variables: ==
framerate = None


# == MAIN ==
# On ne lance le programme que si la licence est OK.
if fct.licence():
    # Fichier 1:
    cf = ChoixFichier(ChoixFichier.liste_fichier_audio())
    cf.show()
    fichier = cf.get_filename()  # 'C:/Users/win10dev/Desktop/braqueurs_s01_e101_v03_PM_Nearfield_2ch_48k_24b_24.L.wav'
    print('Fichier 1: ' + str(fichier))
    start_tc = fct.start_sample_rate_file(ffmpeg, fichier)
    print('- Start tc: ' + str(start_tc))

    duree = 100

    # Note: [-1] = dernier element de la liste.
    rapport = Rapport(fichier.split('/')[-1], True)

    cfr = ChoixFramerate()
    cfr.show()

    framerate = float(cfr.get_framerate())  # 23.976

    print('- Framerate: ' + str(framerate))

    rapport.set_informations(duree, str(start_tc), framerate, '', '')

    # Fichier 2:
    cf = ChoixFichier(ChoixFichier.liste_fichier_audio())
    cf.show()
    fichier2 = cf.get_filename()  # 'C:/Users/win10dev/Desktop/braqueurs_s01_e101_v04_PM_Nearfield_2ch_48k_24b_24.L.wav'
    print('Fichier 2: ' + str(fichier2))
    print('- Start tc: ' + str(fct.start_sample_rate_file(ffmpeg, fichier2)))

    import soundfile as sf

    signal, samplerate = sf.read(fichier, dtype='int32')

    signal2, samplerate2 = sf.read(fichier2, dtype='int32')

    nb_canaux = 0
    nb_canaux2 = 0

    print('- Signal: ' + str(signal))
    print('- size: ' + str(signal.size))
    print('- Samplerate: ' + str(samplerate))
    print('- Duree : ' + str(signal.size / samplerate))

    # Si 1 = 1 canal dans le fichier, si 2 = multi canal.
    # On travaille qu'en multi canal pour simplifier le processus.
    if signal.ndim == 1:
        nb_canaux = 1
    else:
        nb_canaux = signal[0].size

    print('- Nombre de canaux : ' + str(nb_canaux))

    print()

    print('- Signal2 : ' + str(signal2))
    print('- size2 : ' + str(signal2.size))
    print('- Samplerate2 : ' + str(samplerate2))

    # Si 1 = 1 canal dans le fichier, si 2 = multi canal.
    # On travaille qu'en multi canal pour simplifier le processus.
    if signal2.ndim == 1:
        nb_canaux2 = 1
    else:
        nb_canaux2 = signal[0].size

    print('- Nombre de canaux2 : ' + str(nb_canaux2))

    if nb_canaux != nb_canaux2:
        print('/!\\ Vous comparé des fichiers contenant pas le même nombre de canaux.')

    if samplerate != samplerate2:
        print('/!\\ Vous comparé des fichiers avec des fréquences d\'échantillonnage différents.')

    # Traitement si c'est des audios discrets :
    if nb_canaux == 1:
        if signal2.size > signal.size:
            print('OUI : ' + str(signal2.size - signal.size))
            signal = np.append(signal, np.zeros(signal2.size - signal.size))
        elif signal2.size < signal.size:
            print('OUI : ' + str(signal.size - signal2.size))
            signal2 = np.append(signal2, np.zeros(signal.size - signal2.size))

        if signal.size != signal2.size:
            raise Exception('Les deux fichiers ont une durée différente et le programme n\'a pas réussi à compenser.')

        signal3 = signal - signal2

        total = signal3.size

        if signal.size != total:
            raise Exception('La comparaison n\'a pas la bonne durée.')

        del signal
        del signal2

        print('- signal3 : ' + str(signal3))

        liste_diff = np.argwhere(signal3 != 0)

        del signal3

        difference = liste_diff.shape[0]
        liste_diff = liste_diff + start_tc
        liste_diff = liste_diff // (samplerate/framerate)

        print('Divisé par une absurdé (mais cohérante pour pour le TC) :')
        print(liste_diff)

        # On ne garde qu'en image :
        liste_diff = np.unique(liste_diff, axis=0)

        print('- difference : ' + str(difference) + ' echantillon(s)')
        print('- difference : ' + str(difference / total * 100) + ' %')
        print('- liste_diff : ' + str(liste_diff))

        f = open('C:/Users/win10dev/Desktop/rapport.txt', 'w+', encoding='utf-8')
        f.write('Fichier comparé :\n')
        f.write(' - F1 : ' + fichier + '\n')
        f.write(' - F2 : ' + fichier2 + '\n')

        last_tc = ''
        last_tc_num = -1

        tc_courant = ''
        tc_courant_num = -1

        duree = 0

        f.write(' - Différence :\n')
        for i in range(0, len(liste_diff)):
            tc_courant = fct.tc_actuel(liste_diff[i][0], '00:00:00:00', framerate)
            tc_courant_num = liste_diff[i][0]

            duree = duree + 1

            if tc_courant_num != last_tc_num + duree:
                if duree != 1:
                    f.write('-')
                    f.write(fct.tc_actuel(last_tc_num + (duree - 1), '00:00:00:00', framerate) + '\n')
                else:
                    f.write('\n')

                f.write(tc_courant)
                last_tc = tc_courant
                last_tc_num = tc_courant_num
                duree = 0

        if duree != 0:
            f.write('à')
            f.write(tc_courant + '\n')

        f.close()

        # On clôture tous les flux.
        rapport.close()
    # Traitement si ce sont des audios multi canal :
    else:
        if signal2.size > signal.size:
            print('OUI : ' + str(signal2.size - signal.size))
            signal = np.append(signal, np.zeros((signal2.size - signal.size, nb_canaux)))
        elif signal2.size < signal.size:
            print('OUI : ' + str(signal.size - signal2.size))
            signal2 = np.append(signal2, np.zeros((signal.size - signal2.size, nb_canaux)))

        if signal.size != signal2.size:
            raise Exception('Les deux fichiers ont une durée différente et le programme n\'a pas réussi à compenser.')

        signal3 = np.absolute(signal - signal2)

        total = signal3.size

        if signal.size != total:
            raise Exception('La comparaison n\'a pas la bonne durée.')

        del signal
        del signal2

        print('- signal3 : ')
        # print(signal3)

        print('Pas zéro :')
        liste_diff = np.argwhere(signal3 > 0)

        # liste_diff = np.where(signal3 > 0, 10 * np.log(signal3 / (2147483392)), -144)

        # index = np.where(liste_diff > -30)

        # np.savetxt('C:/Users/win10dev/Desktop/db.txt', signal3[liste_diff][0], fmt="%.4f")

        del signal3

        print('Taille : ' + str(liste_diff.shape[0]))

        difference = liste_diff.shape[0]

        print('Ajout le start TC (en sample) au tableau...')
        liste_diff = liste_diff + [start_tc, 0]
        """
        liste_diff2 = np.zeros((difference, 3), dtype='int32')
        liste_diff2[:, :-1] = liste_diff + [start_tc, 0]
        liste_diff2[:, 2] = 10 * np.log(signal3[liste_diff[:, 0], liste_diff[:, 1]] / 2147483392)
        print(liste_diff2)
        """

        liste_diff = np.divide(liste_diff, [samplerate / framerate, 1]).astype('int32')

        # del liste_diff2

        print('Transforme le tableau en = (Nombre d\'image, index canal)...')
        # print(liste_diff)

        # On ne garde qu'en image :
        print('Rend unique les valeurs du résultat...')
        print('- liste_diff (size) : ' + str(liste_diff.shape[0]))
        liste_diff = np.unique(liste_diff, axis=0)
        # print(liste_diff)

        print('- difference : ' + str(difference) + ' echantillon(s)')
        print('- difference : ' + str(difference / total * 100) + ' %')
        # print('- liste_diff : ' + str(liste_diff))
        print('- liste_diff (size) : ' + str(liste_diff.shape[0]))

        f = open('C:/Users/win10dev/Desktop/rapport.txt', 'w+', encoding='utf-8')
        f.write('Fichier comparé :\n')
        f.write(' - F1 : ' + fichier + '\n')
        f.write(' - F2 : ' + fichier2 + '\n')

        last_tc = ''
        last_tc_num = -1

        tc_courant = ''
        tc_courant_num = -1

        canal = []

        duree = 0

        # print('min : ' + str(np.min(liste_diff[:, 2])))

        f.write('\n')
        f.write(' - Différence :')
        # j = 0
        for i in range(0, len(liste_diff)):
            tc_courant_num = int(liste_diff[i][0])
            # db_diff = int(liste_diff[i][2])
            tc_courant = fct.tc_actuel(tc_courant_num, '00:00:00:00', framerate)

            duree = duree + 1

            # print('Durée  ' + str(duree))
            """
            if db_diff >= -96:
                # print('Db : ' + str(db_diff))
                j = j + 1
            """

            if tc_courant_num == last_tc_num + duree-1:
                # print('Même TC donc canal diff.')
                if liste_diff[i][1]+1 not in canal:
                    canal.append(liste_diff[i][1]+1)
                duree = duree - 1
                # print('m-Durée  ' + str(duree))

            if tc_courant_num != last_tc_num + duree:
                # print('TC différent, donc add ('+str(tc_courant_num)+'!='+str(last_tc_num)+'+'+str(duree)+').')
                if duree != 1:
                    f.write('-')
                    f.write(fct.tc_actuel(last_tc_num + (duree - 1), '00:00:00:00', framerate))
                    f.write(' ' + str(canal) + '\n')
                    canal = []
                else:
                    f.write('\n')
                    canal = []

                f.write(tc_courant)
                canal.append(liste_diff[i][1]+1)
                last_tc = tc_courant
                last_tc_num = tc_courant_num
                duree = 0

            # print()

        if duree != 0:
            f.write('-')
            f.write(tc_courant)
            f.write(' ' + str(canal) + '\n')

        # print('j : ' + str(j))

        f.close()

        # On clôture tous les flux.
        rapport.close()

# == END ==
