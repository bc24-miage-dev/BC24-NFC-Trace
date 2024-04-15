import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def write_to_tag(pn532, uid, temperature):
    try:
        block_number = 11
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données de température dans le tag NFC...")

        # Convertir la température en chaîne de caractères et ajouter des espaces pour obtenir 16 octets
        temperature_str = str(temperature)
        temperature_bytes = temperature_str.ljust(16, b'\0')[:16]

        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        print("Côté écriture : Écriture des données de température dans le bloc...")
        pn532.mifare_classic_write_block(block_number, temperature_bytes)
        if pn532.mifare_classic_read_block(block_number) == temperature_bytes:
            print('Côté écriture : Écriture réussie sur le bloc %d.' % block_number)
            return True
        else:
            print('Côté écriture : Erreur lors de la lecture des données écrites.')
            return False
    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture de la température dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=11, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')

        print("Côté lecture : Lecture des données du bloc...")
        data_read = pn532.mifare_classic_read_block(11)

        print('Côté lecture : Lecture réussie sur le bloc %d : %s' % (11, data_read))
        temperature_str = data_read.decode('utf-8').strip('\x00')
        return float(temperature_str) if temperature_str else None
    except Exception as e:
        print('Erreur lors de la lecture de la température du tag NFC :', e)
        return None

def get_temperature(bme_sensor):
    if bme_sensor.get_sensor_data():
        return bme_sensor.data.temperature
    else:
        return None
