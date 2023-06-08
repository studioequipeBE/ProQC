#!/usr/bin/python
# -*- coding: utf-8 -*-

# == IMPORTS ==
import locale
import socket
import struct
import time

locale.setlocale(locale.LC_TIME, '')


# == FONCTIONS ==
def aujourdhui(sntp='ntp.univ-lyon1.fr') -> int:
    """"
    Retourne la date d'aujourd'hui.

    :param str sntp: Le serveur où regarder.
    :returns: Date d'aujourd'hui en nombre.
    """
    try:
        """tempsntp(sntp='ntp.univ-lyon1.fr'): Donne la date et l'heure exacte par consultation d'un serveur ntp"""
        temps19701900 = 2208988800
        buffer = 1024
        # Initialisation d'une connexion UDP.
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Envoie de la requête UDP.
        data = '\x1b' + 47 * '\0'
        client.sendto(data, (sntp, 123))
        # réception de la réponse UDP
        data, addresse = client.recvfrom(buffer)
        if data:
            tps = struct.unpack('!12I', data)[10]
            tps -= temps19701900
            t = time.localtime(tps)

            # Retourne la date en : AAAAMMJJ ce qui fait un chiffre facilement analysable.
            return int(str(t[0]).zfill(4) + str(t[1]).zfill(2) + str(t[2]).zfill(2))
        else:
            print('Erreur : Aucune données récupérées du serveur.')
            return 20230101
    except:
        print('Erreur lors de l\'accès au serveur.')
        return 20230101
