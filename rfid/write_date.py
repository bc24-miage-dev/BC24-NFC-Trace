import RPi.GPIO as GPIO
import pn532.pn532 as nfc
import datetime
import utils

from pn532 import PN532_I2C

def write_to_tag(pn532, uid, data_date):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        # Assurer que les données font exactement 16 octets
        data_bytes_date = data_date.ljust(16, b'\0')[:16]

        print("Ecriture de la date de création...")
        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=14, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        # Lecture du bloc pour vérifier s'il est vide
        current_data = pn532.mifare_classic_read_block(14)

        if utils.is_block_empty(current_data):
            print("Le bloc 14 est vide, écriture de la date...")
            pn532.mifare_classic_write_block(14, data_bytes_date)
            
            if pn532.mifare_classic_read_block(14) == data_bytes_date:
                print('Côté écriture : Écriture réussie sur le bloc 14.')
                return True
            else:
                print('Côté écriture : Erreur lors de la lecture des données écrites dans le bloc 14.')
                return False
        
        print(" ")
        print("Mise à jour de la date de dernière modification...")
        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=16, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        print("Côté écriture : Écriture des données dans le bloc 16")
        pn532.mifare_classic_write_block(16, data_bytes_date)

        if pn532.mifare_classic_read_block(16) == data_bytes_date:
            print('Côté écriture : Écriture réussie sur le bloc 16.')
            return True
        else:
            print('Côté écriture : Erreur lors de la lecture des données écrites dans le bloc 16.')
            return False
    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=16, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')

        print("Côté lecture : Lecture des données du bloc...")
        data_read_date = pn532.mifare_classic_read_block(16)

        print('Côté lecture : Lecture réussie sur le bloc 16 : %r' % data_read_date)
        return data_read_date
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_date():
    write_date = datetime.datetime.now().strftime('%Y-%m-%d')
    print("Date : " + write_date)
    return write_date