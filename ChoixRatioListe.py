#!/usr/bin/env python
# -*- coding: utf-8 -*

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
def getRatio():
    return str(filename)


# Fermer la fenêtre.
def quitter(text):
    global fen, filename
    filename = text
    fen.quit()
    fen.destroy()


filename = None

# Définit les couleurs.
couleurs = ('2.40', '2.39', '2.35', '2.00', '1.85',
            '1.77', '1.33')

fen = Pmw.initialise()
# bou= Button(fen, text= "Choisir", command= changeLabel)
# bou.grid(row= 1, column= 0, padx= 8, pady= 6)
# lab.grid(row= 1, column= 1, padx= 8)

combo = Pmw.ComboBox(fen, labelpos=NW,
                     label_text='Choisissez le ratio :',
                     scrolledlist_items=couleurs,
                     listheight=120,  # 15 par élément. + 15 de base
                     selectioncommand=quitter)
combo.grid(row=2, columnspan=2, padx=10, pady=10)

# Ecouteur sur la fenêtre:
fen.mainloop()
