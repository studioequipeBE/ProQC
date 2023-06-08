#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le fichier à analyser.

# == IMPORTS ==

# Essaie d'importer les fichiers nécessaires au programme :
try:
    from Tkinter import *
    from tkFileDialog import askopenfilename

# Sinon, il essaie d'importer les mêmes, mais en Python 3.
except ImportError:
    from tkinter import *
    from tkinter.filedialog import askopenfilename

# Propose que du wave
FILETYPES = [('WAV', '*.wav')]

root = Tk()

filename = StringVar(root)


def setFilename() -> None:
    """
    Définit le fichier.
    """
    global root, filename
    filename.set(askopenfilename(filetypes=FILETYPES))
    root.quit()
    root.destroy()


def fenetre() -> None:
    """
    Affiche la fenêtre.
    """
    global root
    # Bouton pour choisir le fichier :
    button = Button(root, text='Choisir le fichier a analyser', command=setFilename)
    button.pack()

    # Écouteur sur la fenêtre :
    root.mainloop()
