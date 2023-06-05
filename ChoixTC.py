#!/usr/bin/env python
#-*- coding: utf-8 -*

# Fichier: Permet de choisir (graphiquement) le tc de debut et de fin a analyser dans le fichier.
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


tc_in= None
tc_out= None

entry= None
entry2= None
root= None

# == FONCTIONS ==

def quitter():
    global root, entry, entry2, tc_in, tc_out
    tc_in= entry.get()
    tc_out= entry2.get()
    root.quit()
    root.destroy()

def getTimecodeIn():
    return tc_in

def getTimecodeOut():
    return tc_out

def setTimecodeIn(tc_in_tmp):
    global tc_in
    tc_in= tc_in_tmp

def setTimecodeOut(tc_out_tmp):
    global tc_out
    tc_out= tc_out_tmp

def Fenetre():
    global root, tc_in, tc_out, entry, entry2
    root = Tk()

    l1= Label(root, text= "TC IN")
    l1.pack(side= LEFT)

    entry = Entry(root)
    entry.insert(0, str(tc_in))
    entry.pack(side= LEFT)

    # Bouton pour choisir le fichier:
    button = Button(root, text= "Fini", command=quitter)
    button.pack(side= RIGHT)

    entry2 = Entry(root)
    entry2.insert(0, str(tc_out))
    entry2.pack(side= RIGHT)

    l1= Label(root, text= "TC OUT")
    l1.pack(side= RIGHT)

    # Ecouteur sur la fenêtre:
    root.mainloop()
