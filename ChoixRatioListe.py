#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le ratio à analyser.

# == IMPORTS ==
import Pmw

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import bdd

fen = None
ratio = None


# == FONCTIONS ==
def getRatio() -> str:
    """
    Retourne la valeur choisie.
    """
    return ratio


def quitter(text):
    """
    Fermer la fenêtre.
    """
    global fen, ratio
    ratio = text
    fen.quit()
    fen.destroy()


def fenetre():
    """
    Affiche la fenêtre.
    """
    # Définit les ratios.
    bdd.connect()
    liste_ratio = (bdd.convertTab(bdd.select('liste_ratio', 'ratio')))
    bdd.close()

    fen = Pmw.initialise()
    combo = Pmw.ComboBox(fen, labelpos=NW,
                         label_text='Choisissez le ratio :',
                         scrolledlist_items=liste_ratio,
                         listheight=120,  # 15 par élément. + 15 de base
                         selectioncommand=quitter)
    combo.grid(row=2, columnspan=2, padx=10, pady=10)

    # Écouteur sur la fenêtre :
    fen.mainloop()
