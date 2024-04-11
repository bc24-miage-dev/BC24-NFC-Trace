import pn532.pn532 as nfc
from pn532 import *

# Initialiser le lecteur NFC
pn532 = PN532_SPI(debug=False, reset=20, cs=4)
#pn532 = PN532_I2C(debug=False, reset=20, req=16)
#pn532 = PN532_UART(debug=False, reset=20)

# Configuration pour communiquer avec les cartes MiFare
pn532.SAM_configuration()

# Attendre que le tag soit présent
print('Attente de la détection du tag NFC...')
while not pn532.in_listen_mode():
    pass

# Lire l'UID du tag
uid = pn532.read_passive_target(timeout=0.5)
print('Tag NFC détecté avec l\'UID suivant :', [hex(i) for i in uid])

# Lire les données du bloc 6
block_number = 6
key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
data = pn532.mifare_classic_read_block(block_number, key_a)
print('Données lues du bloc 6 :', data)
