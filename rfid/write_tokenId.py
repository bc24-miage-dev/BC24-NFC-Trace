import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

class WriteTokenID:
    @staticmethod
    def write_to_tag(pn532, uid):
        try:
            block_number = 10
            key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
            print("Chargement d'écriture des données dans le tag NFC...")

            # Demander à l'utilisateur d'entrer les données à écrire dans le tag NFC
            data_token = input("Entrez l'ID de token NFC à écrire dans le tag NFC (16 octets) : NFT_tokenID : ")

            # Assurer que les données font exactement 16 octets
            data_bytes_token = data_token.ljust(16, b'\0')[:16]

            print("Côté écriture : Authentification du bloc...")
            pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=PN532_SPI.MIFARE_CMD_AUTH_A, key=key_a)
            
            print("Côté écriture : Écriture des données dans le bloc...")
            pn532.mifare_classic_write_block(block_number, data_bytes_token)
            if pn532.mifare_classic_read_block(block_number) == data_bytes_token:
                print('Côté écriture : Écriture réussie sur le bloc %d.' % block_number)
                return True
            else:
                print('Côté écriture : Erreur lors de la lecture des données écrites.')
                return False
        except Exception as e:
            print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
            return False