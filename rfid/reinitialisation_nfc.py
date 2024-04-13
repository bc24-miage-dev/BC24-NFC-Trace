#A modérer avec précaution !!

import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *
import json
import os

# Initialize PN532
pn532 = PN532_SPI(cs=4, reset=20, debug=False)

# Get firmware version
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

# Définition des données de bloc par défaut
default_block_data = b'\x00' * 16  # 16 octets de données nuls

# Réinitialisation des blocs 4 à 11 avec les valeurs par défaut
for i in range(4, 12):
    try:
        pn532.mifare_classic_write_block(i, default_block_data)
        print('Bloc %d réinitialisé avec succès.' % i)
    except Exception as e:
        print('Erreur lors de la réinitialisation du bloc %d :' % i, e)
        break

# Fermeture propre de la connexion GPIO
GPIO.cleanup()
