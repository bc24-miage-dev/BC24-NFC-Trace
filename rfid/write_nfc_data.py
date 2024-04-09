from pn532 import PN532_SPI
import json

def write_to_tag(pn532, data):
    try:
        print("Écriture des données dans le tag NFC...")
        # Configuration pour détecter le tag NFC
        pn532.SAM_configuration()

        # Détection du tag NFC
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is None:
            print("Aucun tag NFC détecté.")
            return
        
        # Lecture du numéro de bloc à écrire
        block_number = 4  # Modifier le numéro de bloc si nécessaire

        # Écriture des données dans le tag NFC
        pn532.mifare_classic_write_block(block_number, data)

        print("Données écrites avec succès dans le tag NFC.")
    except Exception as e:
        print("Erreur lors de l'écriture dans le tag NFC :", e)

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

        # Demander à l'utilisateur d'entrer les données à écrire dans le tag NFC
        data_to_write = get_data_from_user()

        # Appeler la fonction pour écrire dans le tag
        write_to_tag(pn532, data_to_write)
                
    except Exception as e:
        print(e)
