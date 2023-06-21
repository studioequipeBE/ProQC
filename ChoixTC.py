#!/usr/bin/env python
# -*- coding: utf-8 -*

from tkinter import *


class ChoixTC:
    """
    Permet de choisir (graphiquement) le tc de debut et de fin à analyser dans le fichier.
    """

    def __init__(self):
        self.tc_in = None
        self.tc_out = None

        self.entry = None
        self.entry2 = None
        self.root = None

    def __quitter(self) -> None:
        """
        Quand on quitte la fenêtre.
        """
        self.tc_in = self.entry.get()
        self.tc_out = self.entry2.get()
        self.root.quit()
        self.root.destroy()

    def get_timecode_in(self) -> str:
        """
        Retourne le timecode in.

        :return: Timecode in.
        """
        return self.tc_in

    def get_timecode_out(self) -> str:
        """
        Retourne le timecode out.

        :return: Timecode out.
        """
        return self.tc_out

    def set_timecode_in(self, tc_in: str) -> None:
        """
        Définit le timecode in.

        :param str tc_in:
        """
        self.tc_in = tc_in

    def set_timecode_out(self, tc_out: str) -> None:
        """
        Définit le timecode out.

        :param str tc_out:
        """
        self.tc_out = tc_out

    def show(self) -> None:
        """
        Affiche la fenêtre.
        """
        self.root = Tk()

        l1 = Label(self.root, text='TC IN')
        l1.pack(side=LEFT)

        self.entry = Entry(self.root)
        self.entry.insert(0, str(self.tc_in))
        self.entry.pack(side=LEFT)

        # Bouton pour choisir le fichier :
        button = Button(self.root, text='Fini', command=self.__quitter)
        button.pack(side=RIGHT)

        self.entry2 = Entry(self.root)
        self.entry2.insert(0, str(self.tc_out))
        self.entry2.pack(side=RIGHT)

        l1 = Label(self.root, text='TC OUT')
        l1.pack(side=RIGHT)

        # Écouteur sur la fenêtre :
        self.root.mainloop()
