import datetime
import RPi.GPIO as GPIO

import write_date
import write_tokenId
import write_temperature
import write_gps
from read_temperature import BME680Sensor
from read_gps import GPS
from pn532 import *

def write_main(pn532, uid, NFT_tokenID):
    try:
        print("Tag NFC détecté avec l'UID suivant : ", [hex(i) for i in uid])
        print("Permission d'écriture autorisée ...")

        # Données à écrire dans la carte RFID/NFC

        data_date = write_date.get_date()
        print(uid)
        print(NFT_tokenID)
            
        # Écrire l'ID de token NFC sur la carte RFID/NFC
        print("------------------------------------------------------")
        print("Ecriture de l'ID de token NFC sur la carte RFID/NFC...")
        try:
            write_tokenId.write_to_tag(pn532, uid, NFT_tokenID.encode())
            print("Écriture de l'ID de token NFC réussie sur la carte RFID/NFC.")
        except:
            print("Échec de l'écriture de l'ID de token NFC sur la carte RFID/NFC.")
            return False

        # Écrire la date sur la carte RFID/NFC
        print("--------------------------------------------")
        print("Ecriture de la date sur la carte RFID/NFC...")
        try:
            write_date.write_to_tag(pn532, uid, data_date.encode())
            print("Écriture de la date réussie sur la carte RFID/NFC.")
        except:
            print("Échec de l'écriture de la date sur la carte RFID/NFC.")
            return False
        
        return True
    except Exception as e:
        print("Exception : " + e)
        return False
    finally:
        GPIO.cleanup()

