#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier: Permet de choisir (graphiquement) le ration a analyser.
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

def getFramerate():
    return str(framerate)


def quitter():
    global root, framerate
    framerate = entry.get()
    root.quit()
    root.destroy()


root = Tk()

framerate = None

# L1 = Label(root, text="Ratio")
# L1.pack(side= LEFT)

# Affiche le nom du fichier sélectionner (remplacer par un message: "Choisisez le fichier à analyser")
entry = Entry(root)
entry.insert(0, "24")
entry.focus_set()
entry.pack()

# Bouton pour choisir le fichier:
button = Button(root, text='Valider le framerate', command=quitter)
button.pack()

# Ecouteur sur la fenêtre:
root.mainloop()
