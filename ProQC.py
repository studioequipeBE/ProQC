#!/usr/bin/env python
#-*- coding: utf-8 -*

# Fichier: Main (+ les fonctions...)
# Version: 0.8

# == IMPORTS ==

import imageio
import subprocess as sp
import numpy as np
import TimecodeP as tc

#from TimecodeP import Timecodes
import ServeurDate as date

import ChoixFichier as cf # Programme qui choisi le fichier a analyser.
import ChoixRatio as cr
import ChoixFramerate as cfr
import ChoixTC as ctc # Programme qui choisi l'interval a analyser
import Rapport as r
import sys
from PIL import Image

# == VALEURS ==

# Si on peut utiliser le programme
licence= None

# Se connecte pour voir si on depasse la limite d'utilisation du programme:
if int(date.Aujourdhui()) <= 20181124:
    print "Licence OK"
    licence= True
else:
    print "Licence depassee/!\\"
    licence= False

# == Declaration variables: ==
ratio= None

start_y= None
end_y= None
start_x= None
start_y= None

x_p= None
y_p= None

x_g= None
y_g= None

start_y_p= None
end_y_p= None
start_x_p= None
end_x_p= None

start_y_g= None
end_y_g= None
start_x_g= None
end_x_g= None

# Matrice pour mediaofflin Premiere
MOLP25= None
MOLP100= None

# Matrice pour mediaoffline Resolve
MOLR25= None
MOLR100= None

# Matrice pour le drop Resolve
DR25= None
DR100= None

starttc= None
starttc_frame= 0
endtc_frame= None

framerate= None

# Liste des erreurs: tc in | tc out | erreur
list_tc_in= np.array([])
list_tc_out= np.array([])
list_erreur= np.array([])

# Fichier pour rapport:
file= None

# Les image ref:
reader_MOLP= imageio.get_reader("ImageRef/AppleProRes444/MEDIAOFFLINE_PREMIERE_PR444_1920x1080_2.mov", ffmpeg_params= ["-an"])
MOLP= reader_MOLP.get_data(0)
reader_MOLP.close()

reader_MOLR= imageio.get_reader("ImageRef/AppleProRes444/MEDIAOFFLINE_RESOLVE_PR444_1920x1080.mov", ffmpeg_params= ["-an"])
MOLR= reader_MOLR.get_data(0)
reader_MOLR.close()

# == FONCTIONS ==

# Donne le TC actuel à l'aide d'un nombre d'image et sur base d'un tc de depard:
def TcActuel(numImage, framerate= 24):
    tc1 = Timecode(framerate, starttc)
    if numImage > 0:
        # Comme le résultat est toujours une image en trop, j'enleve ce qu'il faut: :)
        tc2 = Timecode(framerate, tc.frames_to_timecode((numImage-1), framerate))
        tc3 = tc1 + tc2
        return tc3
    else:
        return tc1

# Met a jour la liste des erreurs pour ecrire dans le rapport:
def UpdateListeProbleme(numImage):
    global list_tc_in, list_tc_out, list_erreur
    
    # Parcoure la liste des problemes, si tc out discontinu, alors on ecrit dans le rapport.
    for i in range(0, np.size(list_tc_in)):
        if i < np.size(list_tc_in) and list_tc_out[i] != (numImage-1):
            # On ecrit dans le rapport l'erreur:

            # La notion de temps en timecode
            #r.setRapport(str(TcActuel(list_tc_in[i], framerate)) + " a " + str(TcActuel(list_tc_out[i], framerate)) + ": " + str(list_erreur[i]) + "\n")
            # La notion de temps en image
            #r.setRapport(str(int(list_tc_in[i])) + " a " + str(int(list_tc_out[i])) + ": " + str(list_erreur[i]) + "\n")
            r.addProbleme(str(int(list_tc_in[i])), str(int(list_tc_out[i])), str(list_erreur[i]))

            # On supprime de la liste l'erreur:
            list_tc_in= np.delete(list_tc_in, i)
            list_tc_out= np.delete(list_tc_out, i)
            list_erreur= np.delete(list_erreur, i)
            # On doit stagner dans les listes si on supprime un element.
            i-= 1

# Quand on doit reporter un probleme dans le rapport:
def Probleme(message, numImage):
    global list_tc_in, list_tc_out, list_erreur

    new= True
    
    # Si l'erreur est dans la liste:
    for i in range(0, np.size(list_tc_in, 0)):
        if list_erreur[i] == message:
            list_tc_out[i]= numImage # Met a jour le tc out
            new= False

    # Sinon, on ajoute le probleme a la liste:
    if new:
        list_tc_in= np.append(list_tc_in, numImage)
        list_tc_out= np.append(list_tc_out, numImage)
        list_erreur= np.append(list_erreur, message)

# Timecode du fichier analyse:
def StartTimeCodeFile(fichier):
    global starttc
    command= ["ffmpeg.exe", '-i', fichier, '-']
    pipe= sp.Popen(command, stdout= sp.PIPE, stderr= sp.PIPE)
    pipe.stdout.readline()
    pipe.terminate()
    infos= pipe.stderr.read()
    tc= ""
    for i in range(18, 29):
        tc+= infos[(infos.find("timecode")+i)]
    starttc= tc
    return tc

# On definit le ratio et on prepare les matrices d'analyse de l'image:
def setRatio(ratio_tmp):
    global ratio, start_x, end_x, start_y, end_y, x_p, y_p, x_g, y_g
    global start_y_p, end_y_p, start_x_p, end_x_p
    global start_y_g, end_y_g, start_x_g, end_x_g
    global MOLP25, MOLP100, MOLR25, MOLR100
    
    ratio= ratio_tmp
    # Ligne utile en 2.39 1920x1080
    if ratio == "2.39":
        start_y= 138
        end_y= 941
    # Ligne utile en 1.77 1920x1080
    else:
        start_y= 0
        end_y= 1079
    # Implementer, plus tard: 1.33 (dans 1920x1080), et surtout le 1.85.
    
    x_p= 1920/(7)
    y_p= (end_y-start_y)/(7)

    x_g= 1920/(12)
    y_g= (end_y-start_y)/(12)

    # Definit les valeurs de x (import quand on aura du 4/3)
    start_x= 0
    end_x= 1919

    # Definit l'image utile en haut/bas, gauche/droite pour la "petite analyse" (5x5) et la "grande analyse" (10x10):
    start_y_p= start_y+y_p
    end_y_p= start_y+(y_p*6)
    start_x_p= start_x+x_p
    end_x_p= start_x+(x_p*6)

    start_y_g= start_y+y_g
    end_y_g= start_y+(y_g*11)
    start_x_g= start_x+x_g
    end_x_g= start_x+(x_g*11)

    # Pour etre plus rapide, on fait les 2 sous-matrices qu'une fois! On a besoin du format d'image.
    MOLP25= MOLP[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]
    MOLP100= MOLP[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]

    MOLR25= MOLR[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]
    MOLR100= MOLR[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]

# Detecter les noirs:
# methodeAnalyse est la precision avec la quelle il faut verifier l'image.
def DetecteNoir(image):
    # Verifie 5*5 pixels: 3,3 MHz (pour un film de 90min en 24 i/s)
    if image[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p].max() < 15:
        # Verifie 10*10 pixeles: 13 MHz (pour un film de 90min en 24 i/s)
        if image[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g].max() < 15:
            # Verifie tous les pixels: 269 GHz (pour un film de 90min en 24 i/s)
            # Si le total de tous les pixels est inferieurs a 100, alors l'image est noire...
            if image.max() < 15:
                return False
    return True

# Note: si retourne 'False' c'est que ce n'est pas bon...

# Compare deux matrice, renvoi une liste avec des True et des False pour l'egalite de la valeur au meme coordonne.
def CompareTab(a, b):
    return str(a == b)

# Detecter "mediaoffline" Premiere:
def MediaOffLinePremiere(image):
    if CompareTab(MOLP25, image[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]).count('False') < 2: # Marge d'erreur de 2 sur 25
        if CompareTab(MOLP100, image[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]).count('False') < 10: # Marge d'erreur de 10 sur 100
            # Egalite des deux matrices + la soustraction des deux doit donner moins de 500:
            if CompareTab(MOLP, image).count('False') < 150: # Marge d'erreur de 150 sur 1920*1080
                return False
            else:
                return True
    return True

# Detecter "mediaoffline" Premiere:
def MediaOffLineResolve(image):
    if CompareTab(MOLR25, image[start_y_p:end_y_p:y_p, start_x_p:end_x_p:x_p]).count('False') < 2: # Marge d'erreur de 2 sur 25
        if CompareTab(MOLR100, image[start_y_g:end_y_g:y_g, start_x_g:end_x_g:x_g]).count('False') < 10: # Marge d'erreur de 10 sur 100
            # Egalite des deux matrices + la soustraction des deux doit donner moins de 500:
            if CompareTab(MOLR, image).count('False') < 150: # Marge d'erreur de 150 sur 1920*1080
                return False
            else:
                return True
    return True

# Detecter quand les blankings ne sont pas justes:
# ratio est le ratio a verifier pour les blankings.
# Prevu pour 2.39
def LigneHautImage(image):
    tab= image[start_y:(start_y+1):1, 0:1920:1]
    if tab.sum() < 1000 and tab.max() < 3:
        return False
    else:
        return True

# Prevu pour 2.39
def LigneBasImage(image):
    tab= image[end_y:(end_y+1):1, 0:1920:1]
    if tab.sum() < 1000 and tab.max() < 3:
        return False
    else:
        return True

def ColonneGaucheImage(image):
    tab= image[start_y:(end_y+1):1, 0:1:1]
    if tab.sum() < 1000 and tab.max() < 5:
        return False
    else:
        return True

def ColonneDroiteImage(image):
    tab= image[start_y:(end_y+1):1, 1919:1920:1]
    if tab.sum() < 1000 and tab.max() < 5:
        return False
    else:
        return True

# Prevu pour 2.39
def BlankingHaut(image): 
    if image[0:start_y:1, 0:1920:1].max() > 4:
        return False
    else:
        return True

# Prevu pour 2.39
def BlankingBas(image):
    if image[(end_y+1):1080:1, 0:1920:1].max() > 4:
        return False
    else:
        return True

# Cloturer l'analyse d'une video (en cloturant son flux ainsi que celui du rapport):
def close():
    # On récupère les dernières valeurs de la liste.
    UpdateListeProbleme(i+1)

    # On cloture tous les flux:
    reader.close()
    r.close()

# == MAIN ==
# On ne lance le programme que si la licence est OK.
if licence:
    # Note: Normalement décode du Pro Res 422HQ! :)
    fichier= cf.filename.get()
    print "fichier: " + str(fichier)
    print "Start tc: " + str(StartTimeCodeFile(fichier))
    reader = imageio.get_reader(fichier, ffmpeg_params= ["-an"])

    framerate= int(cfr.getFramerate())

    # Note: [-1] = dernier element de la liste.
    r.Rapport(fichier.split('/')[-1], "html")

    r.setRapport("== Debut du rapport ==\n")

    ratio= cr.getRatio()

    # Choix du ratio:
    setRatio(ratio)
    duree= reader.get_length()
    endtc_frame= duree-1
    print "Ratio: " + str(ratio)

    ctc.setTimecodeIn(starttc_frame)
    ctc.setTimecodeOut(endtc_frame)

    # Choix du timecode (debut et fin) a verifier:
    ctc.Fenetre()

    starttc_frame= ctc.getTimecodeIn()
    endtc_frame= ctc.getTimecodeOut()

    r.Start(fichier, str(duree), "0", framerate, str(ratio))

    # Choix des vérifications: noirs, drop, mediaoffline...
    #try:
    # Chaque iteration équivaut à une image:
    for i, image in enumerate(reader):
        
        # Met a jout la liste des erreurs (pour avoir un group de tc pour une erreur):
        UpdateListeProbleme(i)

        # Affiche l'avancement tous les 24 images:
        if (i%(framerate*3)) == 0:
            print str(i) + " / " + str(duree)

        # On regarde si l'image est noir:
        if not DetecteNoir(image):
            Probleme("L'image est noire", i)
        # Si l'image n'est pas noir:
        # MediaOffLine Premiere?
        elif not MediaOffLinePremiere(image):
            Probleme("Media offline Premiere", i)
        # Media Offline Resolve?
        elif not MediaOffLineResolve(image):
            Probleme("Media offline Resolve", i)
        # Drop de Resolve?
        #elif not DropResolve(image):
        #    Probleme("Drop Resolve", i)
        # Si l'image n'est pas un média offline ou drop sur toutes l'image, alors on peut s'interesser au blanking et/ou lignes utiles de l'image.
        else:
            if not LigneHautImage(image):
                Probleme("Ligne noir en haut de l'image", i)

            if not LigneBasImage(image):
                Probleme("Ligne noire en bas de l'image", i)

            if not ColonneGaucheImage(image):
                Probleme("Colonne noire à gauche de l'image", i)

            if not ColonneDroiteImage(image):
                Probleme("Colonne noire à droite de l'image", i)

            # On ne vérifie les bandes noires que si on est pas du 1.77 et que l'image n'est pas noir:
            if ratio != "1.77":
                if not BlankingHaut(image):
                    Probleme("Les blankings du haut ne sont pas noirs", i)
                if not BlankingBas(image):
                    Probleme("Les blankings du bas ne sont pas noirs", i)

    #except:
    #    print "Une erreur est survenue lors de l'analyse du fichier video: ", sys.exc_info()[0]

close()

# == END ==
