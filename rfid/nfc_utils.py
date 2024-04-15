import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import PN532_SPI

def authenticate_block(pn532, uid, block_number, key):
    pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key)

def write_block(pn532, block_number, data_bytes):
    pn532.mifare_classic_write_block(block_number, data_bytes)

def read_block(pn532, block_number):
    return pn532.mifare_classic_read_block(block_number)

def init_pn532():
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Module NFC PN532 trouvé avec la version de firmware : {0}.{1}'.format(ver, rev))
    return pn532