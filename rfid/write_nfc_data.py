import pn532.pn532 as nfc
from pn532 import PN532_SPI
import json
import binascii

def write_to_tag(pn532, uid, data):
    try:
        print("Chargement d'écriture des données dans le tag NFC...")
        # Configuration pour communiquer avec les cartes MiFare
        pn532.SAM_configuration()

        # Définir le numéro de bloc à écrire
        block_number = 6

        # Convertir les données en chaîne de caractères hexadécimale
        print("Conversion des données en chaîne hexadécimale...")
        data_hex = binascii.hexlify(data.encode('utf-8')).decode('utf-8')

        # Ajouter des zéros à gauche de la chaîne hexadécimale jusqu'à ce qu'elle ait une longueur de 32 caractères
        data_hex = data_hex.zfill(32)

        # Convertir la chaîne hexadécimale en tableau d'octets
        data_bytes = binascii.unhexlify(data_hex)

        # Écrire les données dans le bloc
        print("Écriture des données dans le bloc...")
        pn532.mifare_classic_write_block(block_number, binascii.unhexlify(data_bytes))

        print("Données écrites avec succès dans le tag NFC.")
        return True
    except Exception as e:
        print("Erreur lors de l'écriture dans le tag NFC :", e)
        exit()

def get_data_from_user():
    # Demander à l'utilisateur d'entrer les données à écrire dans le tag NFC
    vache_id = input("Entrez l'ID de la vache : ")
    date_passage = input("Entrez la date de passage : ")
    etat_sante = input("Entrez l'état de santé : ")
    # etat_alimentation = input("Entrez l'état d'alimentation : ")
    # temperature = input("Entrez la température : ")
    # latitude = input("Entrez la latitude : ")
    # longitude = input("Entrez la longitude : ")
    
    # Ajout des informations de température et de GPS
    data = {
        "vache_id": vache_id,
        "date_passage": date_passage,
        "etat_sante": etat_sante,
        # "etat_alimentation": etat_alimentation,
        # "temperature": temperature,
        # "latitude": latitude,
        # "longitude": longitude
    }
    
    return json.dumps(data)

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
