import RPi.GPIO as GPIO
import pn532.pn532 as nfc
import bme680
import utils

from pn532 import PN532_SPI
from read_gps import GPS

def write_to_tag(pn532, uid, data_gps):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        # Assurer que les données font exactement 16 octets
        #data_bytes_gps = data_gps.ljust(16, b'\0')[:16]
        data_bytes_gps = bytes(data_gps, 'utf-8')
        print(data_bytes_gps)

        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=13, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        # Si aucune donnée n'est présente alors écriture des coordonnées GPS...
        current_data = pn532.mifare_classic_read_block(13)
        if utils.is_block_empty(current_data):
            print("Côté écriture : Écriture des données dans le bloc...")
            pn532.mifare_classic_write_block(13, None)
            return True
            """
            if pn532.mifare_classic_read_block(13) == data_bytes_gps:
                print('Côté écriture : Écriture réussie sur le bloc 13.')
                return True
            else:
                print('Côté écriture : Erreur lors de la lecture des données écrites.')
                return False
            """
        return True
            
    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=13, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')

        print("Côté lecture : Lecture des données du bloc...")
        data_read_gps = pn532.mifare_classic_read_block(13)

        # Convertir les données GPS en dictionnaire
        data_dict_gps = eval(data_read_gps.decode('utf-8'))

        print('Côté lecture : Lecture réussie sur le bloc 13 : %.2f' % (data_read_gps))
        return data_read_gps
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_gps():
    gps = GPS()
    data = gps.read_data()
    if data is not None:
        print("GPS read")
        print(str(data))
        return str(data)
    else:
        print("GPS not read")
        return "N/A"