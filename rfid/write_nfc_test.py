import RPi.GPIO as GPIO
import time
import pn532.pn532 as nfc
from pn532 import *

pn532 = PN532_SPI(debug=False, reset=20, cs=4)

# Définir la fonction pour écrire dans la carte
def write_to_card(uid, block_number, data):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    try:
        # Authentifier le bloc avec la clé A
        pn532.mifare_classic_authenticate_block(
            uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
        # Écrire les données dans le bloc
        pn532.mifare_classic_write_block(block_number, data)
        # Lire les données du bloc pour vérifier qu'elles ont été écrites correctement
        if pn532.mifare_classic_read_block(block_number) == data:
            print('Écriture du bloc %d réussie' % block_number)
    except nfc.PN532Error as e:
        print(e.errmsg)

if __name__ == '__main__':
    # Exemple d'UID de carte
    uid = [0x4, 0x9a, 0x2b, 0x4]
    # Exemple de numéro de bloc
    block_number = 6
    # Exemple de données à écrire
    data = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10])

    # Appeler la fonction d'écriture
    write_to_card(uid, block_number, data)

    # Lire les données du bloc pour vérifier qu'elles ont été écrites correctement
    block_data = pn532.mifare_classic_read_block(block_number)
    print('Données lues du bloc %d : %s' % (block_number, block_data))
