#!/usr/bin/env python
# -*- coding: utf-8 -*

# == IMPORTS ==
from tkinter import *
from tkinter.filedialog import askopenfilename


class ChoixFichierVideo:
    """
    Permet de choisir (graphiquement) le fichier à analyser.
    """

    def __init__(self):
        # Propose d'abord Pro Res puis H264.
        self.FILETYPES = [('Quicktime', '*.mov'), ('PAD MXF', '*.mxf'), ('H264', '*.mp4'), ('AVI', '*.avi')]
        self.root = Tk()
        self.filename = StringVar(self.root)

    def getFilename(self) -> str:
        return self.filename.get()

    def setFilename(self) -> None:
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
        button = Button(self.root, text='Choisir le fichier a analyser', command=self.setFilename)
        button.pack()

        # Écouteur sur la fenêtre :
        self.root.mainloop()
