#A modérer avec précaution !!

import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *

# Initialize PN532
pn532 = PN532_SPI(cs=4, reset=20, debug=False)

# Get firmware version
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

# Write default data (16 bytes of null) to block 4
default_data = b'\x00' * 16
try:
    pn532.mifare_classic_write_block(4, default_data)
    print('Bloc 4 réinitialisé avec succès.')
except Exception as e:
    print('Erreur lors de la réinitialisation du bloc 4 :', e)

# Clean up GPIO connection
GPIO.cleanup()
