#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le framerate.

# == IMPORTS ==
import Pmw
from tkinter import *

import bdd

fen = None
framerate = None
combo = None


# == FONCTIONS ==
def getFramerate() -> str:
    """
    Retourne le framerate.

    :returns: Le framerate.
    """
    return framerate


def quitter():
    """
    Quand on quitte la fenêtre.
    """
    global framerate, fen, combo
    framerate = combo.get()
    fen.quit()
    fen.destroy()


def fenetre():
    """
    Affiche la fenêtre.
    """
    global fen, combo
    bdd.connect()
    liste_framerate = (bdd.convertTab(bdd.select('liste_cadence', 'cadence')))  # Ce qu'il retourne n'est pas un vrai tableau.
    bdd.close()

    fen = Pmw.initialise()
    bou = Button(fen, text='Valider', command=quitter)
    bou.focus_set()
    bou.grid(row=1, column=0, padx=8, pady=6)

    combo = Pmw.ComboBox(fen, labelpos=NW,
                         label_text='Choisissez le framerate :',
                         scrolledlist_items=liste_framerate,
                         listheight=150)
    combo.grid(row=2, columnspan=2, padx=10, pady=10)

    fen.mainloop()
