#!/usr/bin/python
# -*- coding: utf-8 -*-

# == IMPORTS ==
import socket
import struct
import time

import locale

locale.setlocale(locale.LC_TIME, '')


# == FONCTIONS ==

def Aujourdhui(sntp='ntp.univ-lyon1.fr'):
    try:
        """tempsntp(sntp='ntp.univ-lyon1.fr'): Donne la date et l'heure exacte par consultation d'un serveur ntp"""
        jsem = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        temps19701900 = 2208988800
        buffer = 1024
        # initialisation d'une connexion UDP
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # envoie de la requête UDP
        data = '\x1b' + 47 * '\0'
        client.sendto(data, (sntp, 123))
        # réception de la réponse UDP
        data, addresse = client.recvfrom(buffer)
        if data:
            tps = struct.unpack('!12I', data)[10]
            tps -= temps19701900
            t = time.localtime(tps)
            # Retourne la date structuré: JJ/MM/AAAA
            # ch=str(t[2]).zfill(2)+'/'+str(t[1]).zfill(2)+'/'+str(t[0]).zfill(4)
            # return ch

            # Retourne la date en: AAAAMMJJ ce qui fait un chiffre facilement analysable.
            return str(t[0]).zfill(4) + str(t[1]).zfill(2) + str(t[2]).zfill(2)
        else:
            return 20200000
    except:
        return 20200000
