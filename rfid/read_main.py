import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *
import pygame
import json
import os
import sys

# Initialize Pygame
pygame.init()

# Set up the display
DISPLAY_WIDTH = 1080
DISPLAY_HEIGHT = 850
display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('NFC Tag Reader')

# Set up fonts
FONT_SIZE = 16
FONT = pygame.font.SysFont('Arial', FONT_SIZE)

# Initialize PN532
pn532 = PN532_SPI(cs=4, reset=20, debug=False)

# Get firmware version
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

# Chemin du répertoire JSON
JSON_DIRECTORY = "json/"

# Créer le répertoire JSON s'il n'existe pas
if not os.path.exists(JSON_DIRECTORY):
    os.makedirs(JSON_DIRECTORY)

# Main loop
try:
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)

        # Try again if no card is available.
        if uid is None:
            continue

        # Convert UID to hex string
        uid_hex = ':'.join('{:02X}'.format(x) for x in uid)

        # Read data from specific blocks
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        token_id = ""
        temperature = ""
        gps_data = {"longitude": "", "latitude": "", "altitude": ""}
        default_gps_data = {"longitude": "not found", "latitude": "not found", "altitude": "not found"}
        date = ""

        # Block numbers for specific data
        block_numbers = {
            "NFT_tokenID": 10,
            "temperature": 12,
            "gps": 13,
            "date": 14
        }

        for block_name, block_number in block_numbers.items():
            try:
                pn532.mifare_classic_authenticate_block(
                    uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
                data = pn532.mifare_classic_read_block(block_number)
                if block_name == "NFT_tokenID":
                    token_id = data.decode('utf-8').strip('\x00')
                elif block_name == "temperature":
                    temperature = data.hex()
                elif block_name == "gps":
                    gps_data_list = data.decode('utf-8').strip('\x00').split(',')
                    if len(gps_data_list) == 3:
                        gps_data["longitude"] = gps_data_list[0]
                        gps_data["latitude"] = gps_data_list[1]
                        gps_data["altitude"] = gps_data_list[2]
                    else:
                        gps_data = default_gps_data
                elif block_name == "date":
                    date = data.decode('utf-8').strip('\x00')
            except nfc.PN532Error as e:
                print(e.errmsg)
                break

        # Add tag data to list
        tag_data = {'uid': uid_hex, 'NFT_tokenID': token_id, 'temperature': temperature, 'gps': gps_data, 'date': date}

        # Display tag data on screen
        display.fill((255, 255, 255))
        label = FONT.render('Tag Data (' + uid_hex + '):', True, (0, 0, 0))
        display.blit(label, (50, 50))

        # Draw table header
        header_font = pygame.font.SysFont('Arial', FONT_SIZE * 2)
        header_label = header_font.render('Block', True, (0, 0, 0))
        header_rect = header_label.get_rect()
        header_rect.topleft = (50, 100)
        display.blit(header_label, header_rect)

        # Draw table data
        row_height = FONT_SIZE + 5
        col_width = 450
        num_cols = 2
        for i, block_name in enumerate(["NFT_tokenID", "temperature", "gps", "date"]):
            if block_name == "gps":
                longitude_label = FONT.render("longitude: " + gps_data["longitude"], True, (0, 0, 0))
                latitude_label = FONT.render("latitude: " + gps_data["latitude"], True, (0, 0, 0))
                altitude_label = FONT.render("altitude: " + gps_data["altitude"], True, (0, 0, 0))

                longitude_rect = longitude_label.get_rect()
                latitude_rect = latitude_label.get_rect()
                altitude_rect = altitude_label.get_rect()

                longitude_rect.topleft = (150 + col * col_width, 130 + row * row_height)
                latitude_rect.topleft = (150 + col * col_width, 150 + row * row_height)
                altitude_rect.topleft = (150 + col * col_width, 170 + row * row_height)

                display.blit(longitude_label, longitude_rect)
                display.blit(latitude_label, latitude_rect)
                display.blit(altitude_label, altitude_rect)
            else:
                data_label = block_name + ": " + tag_data[block_name]
                label = FONT.render(data_label, True, (0, 0, 0))
                label_rect = label.get_rect()
                row = i // num_cols
                col = i % num_cols
                label_rect.topleft = (150 + col * col_width, 130 + row * row_height)
                display.blit(label, label_rect)

        pygame.display.update()

        # Write tag data to JSON file with UID as filename
        filename = JSON_DIRECTORY + 'data_' + uid_hex.replace(':', '_') + '.json'
        with open(filename, 'w') as f:
            json.dump(tag_data, f, indent=4)

        # Wait for user to remove card
        while uid is not None:
            uid = pn532.read_passive_target(timeout=0.5)

        # Clear the display
        display.fill((255, 255, 255))
        pygame.display.update()

except KeyboardInterrupt:
    print("Exiting program...")
    GPIO.cleanup()
    pygame.quit()
    sys.exit(0)
