#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le framerate à analyser.

# == IMPORTS ==

# Essaie d'importer les fichiers nécessaires au programme :
try:
    from Tkinter import *
    from tkFileDialog import askopenfilename

# Sinon, il essaie d'importer les mêmes, mais en Python 3.
except ImportError:
    from tkinter import *
    from tkinter.filedialog import askopenfilename

root = Tk()
entry = Entry(root)
framerate = None


# == FONCTIONS ==
def getFramerate() -> str:
    """
    Retourne le framerate.

    :returns: Le framerate.
    """
    return framerate


def quitter() -> None:
    """
    Quand on ferme la fenêtre.
    """
    global root, framerate
    framerate = str(entry.get())
    root.quit()
    root.destroy()


def fenetre() -> None:
    """
    Affiche la fenêtre.
    """
    global root, entry
    # Affiche le nom du fichier sélectionner (remplacer par un message : "Choisissez le fichier à analyser").
    entry.insert(0, '24')
    entry.focus_set()
    entry.pack()

    # Bouton pour choisir le fichier :
    button = Button(root, text='Valider le framerate', command=quitter)
    button.pack()

    # Écouteur sur la fenêtre :
    root.mainloop()
