#!/usr/bin/env python
#-*- coding: utf-8 -*

# == IMPORTS ==
from cx_Freeze import setup, Executable


# == MAIN ==
target= Executable(
    script= "ProQC.py",
    #base= "Win32GUI",
    #compress= False,
    #copyDependentFiles= True,
    #appendScriptToExe= True,
    #appendScriptToLibrary= False,
    icon= "_Projet/logo_ProQC.ico"
    )

setup(
        name= "Pro QC",
        version= "0.8",
        description= "Logiciel de QC image",
        author= "Edouard Jeanjean",
        executables= [target]
        #executables = [Executable("ProQC.py")]
)
