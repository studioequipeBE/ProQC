#!/usr/bin/env python
#-*- coding: utf-8 -*

# Fichier: Permet de choisir (graphiquement) le ratio a analyser.
# Version: 0.1

# == IMPORTS ==
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import Pmw          

# == FONCTIONS ==

# Valeur choisie.
def getFramerate():
    return str(framerate)

# Fermer la fenêtre.
def quitter(text):
    global fen, framerate
    framerate= text
    fen.quit()
    fen.destroy()

framerate= None

# Définit les couleurs.
couleurs= ('24', '25', '23,978')

# On créé la fenêtre:
fen= Pmw.initialise()

# L'objet de liste:
combo= Pmw.ComboBox(fen, labelpos= NW,
                     label_text= 'Choisissez le framerate :',
                     scrolledlist_items= couleurs,
                     listheight= 60, #15 par élément. + 15 de base
                     selectioncommand= quitter)
combo.grid(row= 2, columnspan= 2, padx= 10, pady= 10)

# Ecouteur sur la fenêtre:
fen.mainloop()
