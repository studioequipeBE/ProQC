#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le ratio à analyser.

# == IMPORTS ==
from tkinter import *

root = Tk()
entry = None

filename = None


# == FONCTIONS ==
def getRatio() -> str:
    """
    Retourne le ratio.
    """
    return filename


def quitter():
    """
    Quand on quitte la fenêtre.
    """
    global root, filename
    filename = str(entry.get())
    root.quit()
    root.destroy()


def fenetre():
    """
    Affiche la fenêtre.
    """
    global root, entry
    # Affiche le nom du fichier sélectionner (remplacer par un message : "Choisisez le fichier à analyser")
    entry = Entry(root, text='Ratio')
    entry.insert(0, '2.39')
    entry.focus_set()
    entry.pack()

    # Bouton pour choisir le fichier :
    button = Button(root, text='Valider le ratio', command=quitter)
    button.pack()

    # Écouteur sur la fenêtre :
    root.mainloop()
