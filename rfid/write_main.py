import datetime
import RPi.GPIO as GPIO
import write_date  # Importer le fichier contenant les fonctions pour écrire la date
import write_tokenId    # Importer le fichier contenant les fonctions pour écrire l'ID de token NFC

from pn532 import PN532_SPI

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

                # Données à écrire dans la carte RFID/NFC
                data_date = write_date.get_date()
                data_token = write_tokenId.get_tokenId()

                # Écrire la date sur la carte RFID/NFC
                if write_date.write_to_tag(pn532, uid, data_date.encode()):
                    print("Écriture de la date réussie sur la carte RFID/NFC.")
                else:
                    print("Échec de l'écriture de la date sur la carte RFID/NFC.")

                # Écrire l'ID de token NFC sur la carte RFID/NFC
                if write_tokenId.write_to_tag(pn532, uid, data_token.encode()):
                    print("Écriture de l'ID de token NFC réussie sur la carte RFID/NFC.")
                else:
                    print("Échec de l'écriture de l'ID de token NFC sur la carte RFID/NFC.")

                # Lire à nouveau les données écrites pour vérification
                read_date = write_date.read_from_tag(pn532, uid)
                read_id = write_tokenId.read_from_tag(pn532, uid)

                if read_date is not None:
                    print("Date lue depuis la carte RFID/NFC :", read_date.decode())
                else:
                    print("Échec de la lecture de la date depuis la carte RFID/NFC.")

                if read_id is not None:
                    print("ID de token NFC lu depuis la carte RFID/NFC :", read_id.decode())
                else:
                    print("Échec de la lecture de l'ID de token NFC depuis la carte RFID/NFC.")

                break

            else:
                print("Aucun tag NFC détecté après quelques secondes.")
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
