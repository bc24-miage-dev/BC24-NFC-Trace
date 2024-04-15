import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def write_to_tag(pn532, uid, data_token, data_date):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        # Assurer que les données font exactement 16 octets
        data_bytes_token = data_token.ljust(16, b'\0')[:16]
        data_bytes_date = data_date.ljust(16, b'\0')[:16]

        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=10, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
        pn532.mifare_classic_authenticate_block(uid, block_number=13, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        print("Côté écriture : Écriture des données dans le bloc 10")
        pn532.mifare_classic_write_block(10, data_bytes_token)

        if pn532.mifare_classic_read_block(10) == data_bytes_token:
            print('Côté écriture : Écriture réussie sur le bloc 10.')
            return True
        else:
            print('Côté écriture : Erreur lors de la lecture des données écrites dans le bloc 10.')
            return False

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

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=10, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
        pn532.mifare_classic_authenticate_block(uid, block_number=13, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')

        print("Côté lecture : Lecture des données du bloc...")
        data_read_token = pn532.mifare_classic_read_block(10)
        data_read_date = pn532.mifare_classic_read_block(13)

        print('Côté lecture : Lecture réussie sur le bloc 10 : %s' % data_read_token)
        print('Côté lecture : Lecture réussie sur le bloc 13 : %r' % data_read_date)
        return data_read_token, data_read_date
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_data_from_user():
    print("Entrez les données à écrire dans le tag NFC (16 octets) :", end=" ")
    data_write_token = input("NFT_tokenID : ")
    return data_write_token

def get_date():
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')
    return date_now

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
                data_write_token = get_data_from_user()
                data_write_date = get_date()

                # Écrire sur la carte RFID/NFC
                if write_to_tag(pn532, uid, data_write_token.encode(), data_write_date.encode()):
                    print("Écriture réussie sur la carte RFID/NFC.")

                    # Lire à nouveau les données écrites pour vérification
                    read_data = read_from_tag(pn532, uid)
                    if read_data is not None:
                        print("Données lues depuis la carte RFID/NFC :", read_data[0].decode(), read_data[1].decode())
                        break
                    else:
                        print("Échec de la lecture des données depuis la carte RFID/NFC.")
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
