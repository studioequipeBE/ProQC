#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier: Permet de choisir (graphiquement) le codec.
# Version: 0.1

# == IMPORTS ==
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import Pmw
import bdd

bdd.Open()

codec = None


# == FONCTIONS ==
def Quitter():
    global codec, fen
    codec = combo.get()
    fen.quit()
    fen.destroy()


liste_codec = (bdd.ConvertTab(bdd.Select("liste_codec", "codec")))  # Ce qu'il retourne n'est pas un vrai tableau

fen = Pmw.initialise()
bou = Button(fen, text="Valider", command=Quitter)
bou.focus_set()
bou.grid(row=1, column=0, padx=8, pady=6)

combo = Pmw.ComboBox(fen, labelpos=NW,
                     label_text='Choisissez le codec :',
                     scrolledlist_items=liste_codec,
                     listheight=150)
combo.grid(row=2, columnspan=2, padx=10, pady=10)

fen.mainloop()

bdd.close()
