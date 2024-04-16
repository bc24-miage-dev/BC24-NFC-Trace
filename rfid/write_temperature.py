import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI
import bme680
import time

class BME680Sensor:
    def __init__(self):
        try:
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)

    def read_temperature(self):
        if self.sensor.get_sensor_data():
            return self.sensor.data.temperature
        else:
            return None

def write_to_tag(pn532, uid, data):
    try:
        block_number = 10
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        print("Chargement d'écriture des données dans le tag NFC...")

        # Assurer que les données font exactement 16 octets
        data_bytes = data.ljust(16, b'\0')[:16]

        print("Côté écriture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=10, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)

        print("Côté écriture : Écriture des données dans le bloc...")
        pn532.mifare_classic_write_block(10, data_bytes)
        if pn532.mifare_classic_read_block(10) == data_bytes:
            print('Côté écriture : Écriture réussie sur le bloc %d.' % 10)
            return True
        else:
            print('Côté écriture : Erreur lors de la lecture des données écrites.')
            return False
    except Exception as e:
        print('Côté écriture : Erreur lors de l\'écriture dans le tag NFC :', e)
        return False

def read_from_tag(pn532, uid):
    try:
        print("Côté lecture : Authentification du bloc...")
        pn532.mifare_classic_authenticate_block(uid, block_number=10, key_number=nfc.MIFARE_CMD_AUTH_A, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')

        print("Côté lecture : Lecture des données du bloc...")
        data_read = pn532.mifare_classic_read_block(10)

        print('Côté lecture : Lecture réussie sur le bloc %d : %s' % (10, data_read))
        return data_read
    except Exception as e:
        print('Erreur lors de la lecture du tag NFC :', e)
        return None

def get_temperature():
    bme = BME680Sensor()
    temperature = bme.read_temperature()
    if temperature is not None:
        return "Temperature: %.2f" % temperature
    else:
        return "Temperature: n/a"

def write_temperature_to_tag(pn532, uid):
    temperature = get_temperature()
    if write_to_tag(pn532, uid, temperature):
        print("Température écrite dans le tag NFC avec succès")
    else:
        print("Erreur lors de l'écriture de la température dans le tag NFC")

def read_temperature_from_tag(pn532, uid):
    data_read = read_from_tag(pn532, uid)
    if data_read is not None:
        temperature = data_read.decode("utf-8").strip()
        print("Température lue depuis le tag NFC :", temperature)
        return temperature
    else:
        print("Erreur lors de la lecture de la température depuis le tag NFC")
        return None

if __name__ == '__main__':
    # Créer une instance de la classe PN532 pour communiquer avec le lecteur NFC
    pn532 = PN532_SPI(debug=False, reset=17, cs=0)

    # Vérifier la version du firmware du lecteur NFC
    ic, ver, rev, support = pn532.get_firmware_version()
    if not (ic == 0x14 and ver == 0x01 and rev == 0x16):
        print("Erreur : version du firmware incorrecte")
        exit()

    # Écrire la température dans le tag NFC
    uid = (0x4, 0xe, 0x10, 0x1) # Remplacez par l'UID de votre tag NFC
    write_temperature_to_tag(pn532, uid)

    # Lire la température depuis le tag NFC
    temperature = read_temperature_from_tag(pn532, uid)
    print("Température :", temperature)
