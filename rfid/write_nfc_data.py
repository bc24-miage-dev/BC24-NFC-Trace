import pn532.pn532 as nfc
from pn532 import PN532_SPI
import json
import binascii

def write_to_tag(pn532, uid, data):
    try:
        print("Chargement d'écriture des données dans le tag NFC...")
        # Configuration pour communiquer avec les cartes MiFare
        pn532.SAM_configuration()

        # Convertir les données en chaîne de caractères hexadécimale
        print("Conversion des données en chaîne hexadécimale...")
        data_hex = binascii.hexlify(json.dumps(data).encode('utf-8')).decode('utf-8')
        print("Valeur de data_hex :", data_hex)

        # Vérifier que chaque caractère de la chaîne hexadécimale est un caractère hexadécimal valide
        if all(c.isalnum() for c in data_hex):

            # Ajouter des zéros à droite de la chaîne hexadécimale jusqu'à ce qu'elle ait une longueur de 32 caractères
            data_hex = data_hex.rjust(32, '0')

            # Limiter la longueur de la chaîne hexadécimale à 32 caractères (16 octets)
            data_hex = data_hex[:32]
            print("Valeur de data_hex après ajout de zéros :", data_hex)

            # Convertir la chaîne hexadécimale en tableau d'octets
            data_bytes = [int(data_hex[i:i+2], 16) for i in range(0, len(data_hex), 2)]
            print("Valeur de data_bytes :", data_bytes)

            # Ajouter des octets nuls à la fin du tableau d'octets si nécessaire
            if len(data_bytes) < 16:
                data_bytes += [0] * (16 - len(data_bytes))

            # Écrire les données dans le bloc
            print("Écriture des données dans le bloc...")
            pn532.mifare_classic_write_block(6, data_bytes)

            print("Données écrites avec succès dans le tag NFC.")
            return True
        else:
            print("Erreur : la chaîne hexadécimale contient des caractères non hexadécimaux.")
            return False
    except Exception as e:
        print("Erreur lors de l'écriture dans le tag NFC :", e)
        exit()


def get_data_from_user():
    # Demander à l'utilisateur d'entrer les données à écrire dans le tag NFC
    NFT_tokenID = input("Entrez le NFT_tokenID : ")
    temperature = input("Entrez la température : ")
    gps = input("Entrez le GPS : ")
    date = input("Entrez la date : ")

    # Créer un dictionnaire avec les données entrées par l'utilisateur
    data = {
        "NFT_tokenID": NFT_tokenID,
        "temperature": temperature,
        "gps": gps,
        "date": date
    }

    return data

if __name__ == '__main__':
    try:
        # Initialisation du module NFC PN532
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)

        print('Module NFC PN532 NFC HAT trouvé.')

        while True:
            print("Attente de la détection du tag NFC...")
            # Configuration pour détecter le tag NFC
            pn532.SAM_configuration()

            # Détection du tag NFC
            uid = pn532.read_passive_target(timeout=15)
            if uid is None:
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
            else:
                print("Tag NFC détecté avec l'UID suivant : ", [hex(i) for i in uid])
                print("Permission d'écriture autorisée ...")
                # Demander à l'utilisateur d'entrer les données à écrire dans le tag NFC
                data_to_write = get_data_from_user()

                # Écrire dans le tag NFC
                if write_to_tag(pn532, uid, data_to_write):
                    break

    except Exception as e:
        print(e)
