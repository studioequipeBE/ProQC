#!/usr/bin/env python
#-*- coding: utf-8 -*

# Fichier: Permet de choisir (graphiquement) le fichier à analyser.
# Version: 0.0

# == IMPORTS ==

# Essaie d'importer les fichiers nécessaires au programme:
try:
    from Tkinter import *
    from tkFileDialog import askopenfilename
    
# Sinon, il essai d'importer les mêmes mais en Python 3.
except ImportError:
    from tkinter import *
    from tkinter.filedialog import askopenfilename


# Propose d'abord Pro Res puis H264.
FILETYPES = [ ("Quicktime", "*.mov"), ("PAD MXF", "*.mxf"), ("H264", "*.mp4"), ("AVI", "*.avi") ]

root = Tk()
 
filename = StringVar(root)
 
def set_filename():
    filename.set(askopenfilename(filetypes=FILETYPES))
    global root
    root.quit()
    root.destroy()

# Bouton pour choisir le fichier:
button = Button(root, text= "Choisir le fichier a analyser", command=set_filename)
button.pack()

# Ecouteur sur la fenêtre:
root.mainloop()
