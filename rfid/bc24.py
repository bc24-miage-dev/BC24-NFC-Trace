#!/usr/bin/python
import RPi.GPIO as GPIO
from functools import reduce
import time
import Freenove_DHT as DHT
import pn532.pn532 as nfc
from pn532 import *
from math import floor

DHTPin = 17
ledPin = 27    # define ledPin
buttonPins = [12,16,20]    # define buttonPin


def setup():
    
    GPIO.setmode(GPIO.BCM)      # use PHYSICAL GPIO Numbering
    GPIO.setup(ledPin, GPIO.OUT)   # set ledPin to OUTPUT mode
    for i in buttonPins:
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # set buttonPin to PULL UP INPUT mode
def handle_button_pressed(dht):
    
    chk = dht.readDHT11()
    if (chk is dht.DHTLIB_OK):
        print("Humidity : %.2f, \t Temperature : %.2f \n"%(dht.humidity,dht.temperature))


        #pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        pn532 = PN532_I2C(debug=False, reset=20, req=16)
        #pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card to write to!')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Try again if no card is available.
            if uid is not None:
                break
        print('Found card with UID:', [hex(i) for i in uid])

        """
        Warning: DO NOT write the blocks of 4N+3 (3, 7, 11, ..., 63)
        or else you will change the password for blocks 4N ~ 4N+2.

        Note: 
        1.  The first 6 bytes (KEY A) of the 4N+3 blocks are always shown as 0x00,
        since 'KEY A' is unreadable. In contrast, the last 6 bytes (KEY B) of the 
        4N+3 blocks are readable.
        2.  Block 0 is unwritable. 
        """
        # Write block #6
        block_number = 6
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        data = bytes([floor(dht.temperature), 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        try:
            pn532.mifare_classic_authenticate_block(
                uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
            pn532.mifare_classic_write_block(block_number, data)
            if pn532.mifare_classic_read_block(block_number) == data:
                print('write block %d successfully' % block_number)
        except nfc.PN532Error as e:
            print(e.errmsg)
        

    else:
        print(chk)

def loop():
    dht = DHT.DHT(DHTPin)
    button_pressed=False
    while True:
        if reduce(lambda x,y: x or y,map(lambda x:GPIO.input(x)==GPIO.LOW,buttonPins)): # if button is pressed
            GPIO.output(ledPin,GPIO.HIGH)   # turn on led
            if not button_pressed:
                print("button pressed!")
                button_pressed=True
                handle_button_pressed(dht)

            
        else : # if button is relessed
            GPIO.output(ledPin,GPIO.LOW) # turn off led 
            button_pressed=False
            

def destroy():
    GPIO.output(ledPin, GPIO.LOW)     # turn off led 
    GPIO.cleanup()                    # Release GPIO resource

if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()
