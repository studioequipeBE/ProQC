#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier: Permet de choisir (graphiquement) le ratio a analyser.
# Version: 0.1

# == IMPORTS ==

# Essaie d'importer les fichiers necessaires au programme:
try:
    from Tkinter import *
    from tkFileDialog import askopenfilename

# Sinon, il essai d'importer les mêmes mais en Python 3.
except ImportError:
    from tkinter import *
    from tkinter.filedialog import askopenfilename


# == FONCTIONS ==

def getRatio():
    return str(filename)


def quitter():
    global root, filename
    filename = entry.get()
    root.quit()
    root.destroy()


root = Tk()

filename = None

# L1 = Label(root, text="Ratio")
# L1.pack(side= LEFT)

# Affiche le nom du fichier sélectionner (remplacer par un message: "Choisisez le fichier à analyser")
entry = Entry(root, text="Ratio")
entry.insert(0, "2.39")
entry.focus_set()
entry.pack()

# Bouton pour choisir le fichier:
button = Button(root, text='Valider le ratio', command=quitter)
button.pack()

# Ecouteur sur la fenêtre:
root.mainloop()
