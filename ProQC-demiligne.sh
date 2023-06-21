#!/bin/bash
BASEDIR=$(dirname $0)
echo "Lancement du script depuis : ${BASEDIR}"
cd $BASEDIR
venv/bin/python main-demiligne.py