#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le codec.

# == IMPORTS ==
import Pmw
from tkinter import *

import bdd

fen = None
codec = None
combo = None


# == FONCTIONS ==
def quitter() -> None:
    """
    Quand on quitte la fenêtre.
    """
    global codec, fen
    codec = combo.get()
    fen.quit()
    fen.destroy()


def fenetre() -> None:
    """
    Définit la fenêtre.
    """
    global fen, combo
    bdd.connect()
    liste_codec = (bdd.convertTab(bdd.select('liste_codec', 'codec')))  # Ce qu'il retourne n'est pas un vrai tableau.
    bdd.close()

    fen = Pmw.initialise()
    bou = Button(fen, text='Valider', command=quitter)
    bou.focus_set()
    bou.grid(row=1, column=0, padx=8, pady=6)

    combo = Pmw.ComboBox(fen, labelpos=NW,
                         label_text='Choisissez le codec :',
                         scrolledlist_items=liste_codec,
                         listheight=150)
    combo.grid(row=2, columnspan=2, padx=10, pady=10)

    fen.mainloop()
