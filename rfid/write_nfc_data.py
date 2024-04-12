import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def write_to_tag(pn532, uid, block_number, data_bytes):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        # Assurez-vous que les données font exactement 16 octets
        data_bytes = data_bytes.ljust(16, b'\0')[:16]
        pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
        pn532.mifare_classic_write_block(block_number, data_bytes)
        if pn532.mifare_classic_read_block(block_number) == data_bytes:
            print(f'Écriture réussie sur le bloc {block_number}.')
            return True
        else:
            print(f'Erreur lors de la lecture des données écrites sur le bloc {block_number}.')
            return False
    except nfc.PN532Error as e:
        print('Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def get_block_number_for_key(key):
    # Fonction fictive qui renvoie le numéro de bloc approprié pour chaque clé
    if key == "NFT_tokenID":
        return 4
    elif key == "temperature":
        return 5
    elif key == "gps":
        return 6
    elif key == "date":
        return 7
    else:
        print(f"Clé non reconnue : {key}")
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

        # Demander à l'utilisateur d'entrer les informations pour chaque clé
        data = {}
        for key in ["NFT_tokenID", "temperature", "gps", "date"]:
            value = input(f"Entrez la valeur pour {key} : ")
            data[key] = value

        # Convertir les données en octets et écrire dans le tag NFC
        for key, value in data.items():
            data_bytes = value.encode('utf-8')  # Convertir en octets
            block_number = get_block_number_for_key(key)  # Déterminer le numéro de bloc pour chaque clé
            if block_number is not None:
                if write_to_tag(pn532, uid, block_number, data_bytes):
                    print(f"Écriture réussie sur le bloc {block_number} pour {key}.")
                else:
                    print(f"Échec de l'écriture sur le bloc {block_number} pour {key}.")
            else:
                print(f"Clé non reconnue : {key}")

    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
