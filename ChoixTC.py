#!/usr/bin/env python
# -*- coding: utf-8 -*

# Fichier : Permet de choisir (graphiquement) le tc de debut et de fin a analyser dans le fichier.

# == IMPORTS ==
from tkinter import *
from tkinter.filedialog import askopenfilename

tc_in = None
tc_out = None

entry = None
entry2 = None
root = None


# == FONCTIONS ==
def quitter() -> None:
    """
    Quand on quitte la fenêtre.
    """
    global root, entry, entry2, tc_in, tc_out
    tc_in = entry.get()
    tc_out = entry2.get()
    root.quit()
    root.destroy()


def getTimecodeIn() -> str:
    """
    Retourne le timecode in.

    :return: Timecode in.
    """
    return tc_in


def getTimecodeOut() -> str:
    """
    Retourne le timecode out.

    :return: Timecode out.
    """
    return tc_out


def setTimecodeIn(tc_in_tmp: str) -> None:
    """
    Définit le timecode in.

    :param str tc_in_tmp:
    """
    global tc_in
    tc_in = tc_in_tmp


def setTimecodeOut(tc_out_tmp: str) -> None:
    """
    Définit le timecode out.

    :param str tc_out_tmp:
    """
    global tc_out
    tc_out = tc_out_tmp


def fenetre() -> None:
    """
    Affiche la fenêtre.
    """
    global root, tc_in, tc_out, entry, entry2
    root = Tk()

    l1 = Label(root, text='TC IN')
    l1.pack(side=LEFT)

    entry = Entry(root)
    entry.insert(0, str(tc_in))
    entry.pack(side=LEFT)

    # Bouton pour choisir le fichier :
    button = Button(root, text='Fini', command=quitter)
    button.pack(side=RIGHT)

    entry2 = Entry(root)
    entry2.insert(0, str(tc_out))
    entry2.pack(side=RIGHT)

    l1 = Label(root, text='TC OUT')
    l1.pack(side=RIGHT)

    # Écouteur sur la fenêtre :
    root.mainloop()
