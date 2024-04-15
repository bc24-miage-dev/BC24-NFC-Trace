import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def write_to_tag(pn532, uid, data):
    try:
        block_number = 10
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        # Assurer que les données font exactement 16 octets
        data_bytes = data.ljust(16, b'\0')[:16]

        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=10, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
        
        print("Côté écriture : Écriture des données dans le bloc...")
        pn532.mifare_classic_write_block(10, data_bytes)
        if pn532.mifare_classic_read_block(10) == data_bytes:
            print('Côté écriture : Écriture réussie sur le bloc %d.' % 10)
            return True
        else:
            print('Côté écriture : Erreur lors de la lecture des données écrites.')
            return False
    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=10, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
        
        print("Côté lecture : Lecture des données du bloc...")
        data_read = pn532.mifare_classic_read_block(10)
        
        print('Côté lecture : Lecture réussie sur le bloc %d : %s' % (10, data_read))
        return data_read
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_tokenId():
    write_token = input("Entrez les données à écrire dans le tag NFC (16 octets) : NFT_tokenID : ")
    return write_token