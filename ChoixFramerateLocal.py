#!/usr/bin/env python
# -*- coding: utf-8 -*

import Pmw
from tkinter import *


class ChoixFramerate:
    """
    Fenêtre pour choisir un framerate.
    """

    def __init__(self):
        """
        Initialise la fenêtre.
        """
        self.fen = Pmw.initialise()
        self.combo = None
        self.framerate = StringVar(self.fen)

    def get_framerate(self) -> str:
        """
        Retourne le framerate.

        :returns: Le framerate. En `str` pour l'instant pour gérer le 23.976
        """
        return self.framerate.get()

    def __quitter(self) -> None:
        """
        Quand on quitte la fenêtre.
        """
        self.framerate.set(self.combo.get())
        self.fen.quit()
        self.fen.destroy()

    def show(self) -> None:
        """
        Affiche la fenêtre.
        """
        liste_framerate = (23.976, 24, 25)

        bou = Button(self.fen, text='Valider', command=self.__quitter)
        bou.focus_set()
        bou.grid(row=1, column=0, padx=8, pady=6)

        self.combo = Pmw.ComboBox(self.fen, labelpos=NW,
                                  label_text='Choisissez le framerate :',
                                  scrolledlist_items=liste_framerate,
                                  listheight=150)
        self.combo.grid(row=2, columnspan=2, padx=10, pady=10)

        self.fen.mainloop()
