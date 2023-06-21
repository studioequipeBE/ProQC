#!/usr/bin/env python
# -*- coding: utf-8 -*

import Pmw
from tkinter import *

import bdd


class ChoixRatio:
    """
    Fenêtre pour choisir un ratio.
    """

    def __init__(self):
        """
        Initialise la fenêtre.
        """
        self.fen = None
        self.ratio = None

    def get_ratio(self) -> str:
        """
        Retourne la valeur choisie.
        """
        return self.ratio

    def __quitter(self, text) -> None:
        """
        Fermer la fenêtre et définit le ratio.
        """
        self.ratio = text
        self.fen.quit()
        self.fen.destroy()

    def show(self) -> None:
        """
        Affiche la fenêtre.
        """
        # Définit les ratios.
        bdd.connect()
        liste_ratio = (bdd.convertTab(bdd.select('liste_ratio', 'ratio')))
        bdd.close()

        self.fen = Pmw.initialise()
        self.combo = Pmw.ComboBox(self.fen, labelpos=NW,
                                  label_text='Choisissez le ratio :',
                                  scrolledlist_items=liste_ratio,
                                  listheight=120,  # 15 par élément. + 15 de base
                                  selectioncommand=self.__quitter)
        self.combo.grid(row=2, columnspan=2, padx=10, pady=10)

        # Écouteur sur la fenêtre :
        self.fen.mainloop()
