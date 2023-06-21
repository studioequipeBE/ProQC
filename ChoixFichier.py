#!/usr/bin/env python
# -*- coding: utf-8 -*

from tkinter import *
from tkinter.filedialog import askopenfilename


class ChoixFichier:
    """
    Permet de choisir (graphiquement) le fichier à analyser.
    """

    def __init__(self, liste_fichier):
        """
        Définit les fichiers à filtrer.

        :param liste_fichier: Les fichiers à filtrer : [('Nom', '*.extension')]
        """
        # Propose d'abord Pro Res puis H264.
        self.FILETYPES = liste_fichier
        self.root = Tk()
        self.filename = StringVar(self.root)

    def get_filename(self) -> str:
        return self.filename.get()

    def __quitter(self) -> None:
        """
        Définit le nom du fichier.
        """
        self.filename.set(askopenfilename(filetypes=self.FILETYPES))
        self.root.quit()
        self.root.destroy()

    def show(self) -> None:
        """
        Affiche la fenêtre.
        """
        # Bouton pour choisir le fichier :
        button = Button(self.root, text='Choisir le fichier à analyser', command=self.__quitter)
        button.pack()

        # Écouteur sur la fenêtre :
        self.root.mainloop()

    @staticmethod
    def liste_fichier_audio():
        """
        Liste de filtre fichier audio.
        """
        return [('WAV', '*.wav')]

    @staticmethod
    def liste_fichier_video():
        """
        Liste de filtre fichier vidéo.
        """
        return [('Quicktime', '*.mov'), ('PAD MXF', '*.mxf'), ('H264', '*.mp4'), ('AVI', '*.avi')]
