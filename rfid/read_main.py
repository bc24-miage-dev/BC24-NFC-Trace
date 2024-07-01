import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *
import json
import os
from flask import *
import sys, time, pathlib
from write_temperature import get_temperature
from write_gps import get_gps
import threading, time

class Reader(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = True

    def run(self):
        # Initial-iser PN532
        #pn532 = PN532_SPI(cs=4, reset=20, debug=False)
        pn532 = PN532_I2C(debug=False, reset=20, req=16)

        # Obtenir la version du firmware
        ic, ver, rev, support = pn532.get_firmware_version()
        print('PN532 trouvé avec la version du firmware : {0}.{1}'.format(ver, rev))

        # Configurer PN532 pour communiquer avec les cartes MiFare
        pn532.SAM_configuration()

        # Chemin du répertoire JSON
        JSON_DIRECTORY = "json/"

        # Créer le répertoire JSON s'il n'existe pas
        if not os.path.exists(JSON_DIRECTORY):
            os.makedirs(JSON_DIRECTORY)

        # Boucle principale
        try:
            counter = 0
            while self._stop_event and counter < 5:
                print("running...")

                # Vérifier si une carte est disponible à la lecture
                uid = pn532.read_passive_target(timeout=1.5)

                # Réessayer si aucune carte n'est disponible.
                if uid is None:
                    print("No NFC tag")   
                    time.sleep(5)
                    counter += 1
                    continue

                # Convertir UID en chaîne hexadécimale
                uid_hex = ':'.join('{:02X}'.format(x) for x in uid)

                # Lire les données des blocs spécifiques
                key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
                token_id = ""
                temperature = get_temperature()
                gps_data = get_gps() #"longitude : 2.3572, latitude : 48.82, altitude : 35"
                if (gps_data == None):
                    gps_data = {"longitude": "non trouve", "latitude": "non trouve", "altitude": "non trouve"}
                date = ""
                date_last_modified = ""

                # Numéros de bloc pour des données spécifiques
                block_numbers = {
                    "NFT_tokenID": 10,
                    "date_creation": 14,
                    "date_derniere_modification": 16
                }

                for block_name, block_number in block_numbers.items():
                    try:
                        pn532.mifare_classic_authenticate_block(
                            uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
                        data = pn532.mifare_classic_read_block(block_number)
                        if block_name == "NFT_tokenID":
                            token_id = data.decode('utf-8').strip('\x00')
                        elif block_name == "date_creation":
                            date = data.decode('utf-8').strip('\x00')
                        elif block_name == "date_derniere_modification":
                            date_last_modified = data.decode('utf-8').strip('\x00')
                    except nfc.PN532Error as e:
                        print(e.errmsg)
                        break

                print(date_last_modified)
                try:
                    # Ajouter les données du tag à la liste
                    tag_data = {'uid': uid_hex, 'NFT_tokenID': token_id, 'temperature': temperature, 'gps': gps_data, 'date_creation': date, 'date_derniere_modification': date_last_modified}
                    print(tag_data)
                    return tag_data

                    # Supprimer tous les fichiers présents dans le dossier /json
                    json_file = os.listdir(JSON_DIRECTORY)
                    for filename in json_file:
                        try:
                            file_path = pathlib.Path(JSON_DIRECTORY + "/" + filename)
                            print(file_path)
                            file_path.unlink()
                            print("Fichier supprimé")
                        except:
                            print("Répertoire /json vide")


                    # Écrire les données du tag dans un fichier JSON avec UID comme nom de fichier
                    filename = JSON_DIRECTORY + 'data_' + uid_hex.replace(':', '_') + '.json'
                    with open(filename, 'w') as f:
                        json.dump(tag_data, f, indent=4)
                        print("file created !")

                    # Attendre que l'utilisateur retire la carte
                    #while uid is not None:
                    #   uid = pn532.read_passive_target(timeout=0.5)
                except:
                    print("Erreur écriture des données.")

                time.sleep(5)
                counter += 1
            print("Reader à l'arrêt")
            return {"Message": "Reader à l'arrêt sans carte trouvée."}

        except KeyboardInterrupt:
            print("Programme interrompu...")
            GPIO.cleanup()
            sys.exit(0)

    def stop(self):
        if (self._stop_event):
            self._stop_event = False

def start():
    global thread
    thread = Reader()
    result = thread.run()
    return result
    time.sleep(3)

def stop():
    thread.stop()
    