#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) la résolution à analyser.

# == IMPORTS ==
import Pmw
from tkinter import *

import bdd

fen = None
resolution = None


# == FONCTIONS ==
def getResolution() -> str:
    """
    Valeur choisie.

    :return: La résolution.
    """
    return resolution


def quitter(text: str) -> None:
    """
    Fermer la fenêtre.

    :param str text : La résolution.
    """
    global fen, resolution
    resolution = text
    fen.quit()
    fen.destroy()


def fenetre() -> None:
    """
    Affiche la fenêtre.
    """
    global fen
    # Définit les résolutions.
    bdd.connect()
    liste_resolution = (bdd.convertTab(bdd.select('liste_resolution', 'resolution')))
    bdd.close()

    fen = Pmw.initialise()
    # bou= Button(fen, text= "Choisir", command= changeLabel)
    # bou.grid(row= 1, column= 0, padx= 8, pady= 6)
    # lab.grid(row= 1, column= 1, padx= 8)

    combo = Pmw.ComboBox(fen, labelpos=NW,
                         label_text='Choisissez la resolution :',
                         scrolledlist_items=liste_resolution,
                         listheight=120,  # 15 par élément. + 15 de base
                         selectioncommand=quitter)
    combo.grid(row=2, columnspan=2, padx=10, pady=10)

    # Écouteur sur la fenêtre :
    fen.mainloop()
