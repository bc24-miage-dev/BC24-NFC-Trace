import RPi.GPIO as GPIO
import pn532.pn532 as nfc
import bme680
import utils

from pn532 import PN532_SPI
from read_temperature import BME680Sensor

def write_to_tag(pn532, uid, data_temperature):
    try:
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        # Assurer que les données font exactement 16 octets
        data_bytes_temperature = data_temperature.ljust(16, b'\0')[:16]

        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=12, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        # Si aucune donnée n'est présente, alors écriture de la température
        current_data = pn532.mifare_classic_read_block(12)
        if (utils.is_block_empty(current_data)): 
            print("Côté écriture : Écriture des données dans le bloc...")
            pn532.mifare_classic_write_block(12, None)
            return True
            """
            if pn532.mifare_classic_read_block(12) == data_bytes_temperature:
                print('Côté écriture : Écriture réussie sur le bloc 12.')
                return True
            else:
                print('Côté écriture : Erreur lors de la lecture des données écrites.')
                return False
            """

    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=12, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')

        print("Côté lecture : Lecture des données du bloc...")
        data_read_temperature = pn532.mifare_classic_read_block(12)

        print('Côté lecture : Lecture réussie sur le bloc 12 : %.2f' % (data_read_temperature))
        return data_read_temperature
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_temperature():
    bme = BME680Sensor()
    temperature = bme.read_temperature()
    if temperature is not None:
        print("Temperature read")
        return "%.2f" % temperature
    else:
        print("No temperature read")
        return "N/A"