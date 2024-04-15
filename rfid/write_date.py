import datetime
from pn532 import PN532_SPI

class WriteDate:
    @staticmethod
    def write_to_tag(pn532, uid):
        try:
            key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
            print("Chargement d'écriture des données dans le tag NFC...")

            # Obtenir la date actuelle
            data_date = datetime.datetime.now().strftime('%Y-%m-%d')
            # Assurer que les données font exactement 16 octets
            data_bytes_date = data_date.ljust(16, b'\0')[:16]

            print("Côté écriture : Authentification du bloc...")
            pn532.mifare_classic_authenticate_block(uid, block_number=13, key_number=PN532_SPI.MIFARE_CMD_AUTH_A, key=key_a)

            print("Côté écriture : Écriture des données dans le bloc 13")
            pn532.mifare_classic_write_block(13, data_bytes_date)

            if pn532.mifare_classic_read_block(13) == data_bytes_date:
                print('Côté écriture : Écriture réussie sur le bloc 13.')
                return True
            else:
                print('Côté écriture : Erreur lors de la lecture des données écrites dans le bloc 13.')
                return False
        except Exception as e:
            print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
            return False
