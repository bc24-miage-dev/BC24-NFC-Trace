import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def write_to_tag(pn532, uid, data):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        nft_token, temperature, gps, date = data

         # Assurer que les données font exactement 16 caractères unicode
        nft_token_unicode = nft_token.ljust(16, ' ')
        temperature_unicode = temperature.ljust(16, ' ')
        gps_unicode = gps.ljust(16, ' ')
        # date_unicode = date.ljust(16, ' ')

        # Convertir les données en bytes
        nft_token_bytes = nft_token_unicode.encode('utf-8')
        temperature_bytes = temperature_unicode.encode('utf-8')
        gps_bytes = gps_unicode.encode('utf-8')
        # date_bytes = date_unicode.encode('utf-8')

        for block_number, data_bytes in zip(range(4, 7), [nft_token_bytes, temperature_bytes, gps_bytes, 
        # date_bytes
        ]):
            print("Côté écriture : Authentification du bloc {}...".format(block_number))
            pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

            print("Côté écriture : Écriture des données dans le bloc {}...".format(block_number))
            pn532.mifare_classic_write_block(block_number, data_bytes)
            if pn532.mifare_classic_read_block(block_number) == data_bytes:
                print('Côté écriture : Écriture réussie sur le bloc {}.'.format(block_number))
            else:
                print('Côté écriture : Erreur lors de la lecture des données écrites sur le bloc {}.'.format(block_number))
                return False

        return True
    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'

        for block_number in range(4, 7):
            print("Côté lecture : Authentification du bloc {}...".format(block_number))
            pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

            print("Côté lecture : Lecture des données du bloc {}...".format(block_number))
            data_read = pn532.mifare_classic_read_block(block_number)

            print('Côté lecture : Lecture réussie sur le bloc {} : {}'.format(block_number, data_read))
            print("Données lues depuis la carte RFID/NFC (bloc {}): {}".format(block_number, data_read.decode().rstrip('\x00')))

    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_data_from_user():
    nft_token = input("NFT_tokenID : ")
    temperature = input("Température : ")
    gps = input("GPS : ")
    # date = input("Date : ")
    return nft_token, temperature, gps
     
    #, date

if __name__ == '__main__':
    try:
        # Initialisation du module NFC PN532
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = pn532.get_firmware_version()
        print('Module NFC PN532 trouvé avec la version de firmware : {0}.{1}'.format(ver, rev))
        
        while True:
            # Configuration pour communiquer avec les cartes MiFare
            pn532.SAM_configuration()

            print('En attente de la carte RFID/NFC à écrire...')
            # Vérifier si une carte est disponible à la lecture
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Réessayer si aucune carte n'est disponible.
            if uid is not None:    
                print("Tag NFC détecté avec l'UID suivant : ", [hex(i) for i in uid])
                print("Permission d'écriture autorisée ...")

                # Demander à l'utilisateur d'entrer les données à écrire dans la carte RFID/NFC
                data_to_write = get_data_from_user()

                # Écrire sur la carte RFID/NFC
                if write_to_tag(pn532, uid, data_to_write):
                    print("Écriture réussie sur la carte RFID/NFC.")

                    # Lire à nouveau les données écrites pour vérification
                    read_from_tag(pn532, uid)  # Appeler la fonction read_from_tag ici
                    break
                else:
                    print("Échec de l'écriture sur la carte RFID/NFC.")
            else:
                print("Aucun tag NFC détecté après 15 secondes.")
                while True:
                    choix = input("Voulez-vous réessayer ? (yes/no) : ")
                    if choix.lower() == "yes":
                        print("Réessayer la détection du tag NFC...")
                        break
                    elif choix.lower() == "no":
                        print("Arrêt du programme.")
                        exit()
                    else:
                        print("Choix invalide. Veuillez répondre par 'yes' ou 'no'.")
            
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
