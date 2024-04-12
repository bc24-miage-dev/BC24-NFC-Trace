import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def write_to_tag(pn532, uid, data):
    try:
        block_number = 6
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        # Assurer que les données font exactement 16 octets
        data_bytes = data.ljust(16, b'\0')[:16]
        pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
        pn532.mifare_classic_write_block(block_number, data_bytes)
        if pn532.mifare_classic_read_block(block_number) == data_bytes:
            print('Écriture réussie sur le bloc %d.' % block_number)
            return True
        else:
            print('Erreur lors de la lecture des données écrites.')
            return False
    except Exception as e:
        print('Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid, block_number):
    try:
        pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
        data_read = pn532.mifare_classic_read_block(block_number)
        print('Lecture réussie sur le bloc %d : %s' % (block_number, data_read))
        return data_read
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

if __name__ == '__main__':
    try:
        # Initialisation du module NFC PN532
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = pn532.get_firmware_version()
        print('Module NFC PN532 trouvé avec la version de firmware : {0}.{1}'.format(ver, rev))
        # Configuration pour communiquer avec les cartes MiFare
        pn532.SAM_configuration()

        print('En attente de la carte RFID/NFC à écrire...')
        while True:
            # Vérifier si une carte est disponible à la lecture
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Réessayer si aucune carte n'est disponible.
            if uid is not None:
                break
        print('Carte trouvée avec UID :', [hex(i) for i in uid])

        # Demander à l'utilisateur d'entrer les données à écrire dans la carte RFID/NFC
        data_to_write = input("Entrez les données à écrire sur la carte RFID/NFC : ")

        # Écrire sur la carte RFID/NFC
        if write_to_tag(pn532, uid, data_to_write.encode()):
            print("Écriture réussie sur la carte RFID/NFC.")

            # Lire à nouveau les données écrites pour vérification
            read_data = read_from_tag(pn532, uid, block_number=6)
            if read_data is not None:
                print("Données lues depuis la carte RFID/NFC :", read_data.decode())
            else:
                print("Échec de la lecture des données depuis la carte RFID/NFC.")
        else:
            print("Échec de l'écriture sur la carte RFID/NFC.")
            
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
