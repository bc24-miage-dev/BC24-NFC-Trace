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
#pn532 = PN532_I2C(debug=False, reset=20, req=16)

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

        # Read data from all blocks
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        token_id = ""
        temperature = ""
        gps = ""
        date = ""

        for i, block_name in enumerate(["NFT_tokenID", "temperature", "gps", "date"]):
            try:
                pn532.mifare_classic_authenticate_block(
                    uid, block_number=10+i, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
                data = pn532.mifare_classic_read_block(10+i)
                if i == 0:
                    token_id = data.hex()
                elif i == 1:
                    temperature = data.hex()
                elif i == 2:
                    gps = data.hex()
                elif i == 3:
                    date = data.hex()
            except nfc.PN532Error as e:
                print(e.errmsg)
                break

        # Add tag data to list
        tag_data = {'uid': uid_hex, 'NFT_tokenID': token_id, 'temperature': temperature, 'gps': gps, 'date': date}

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
