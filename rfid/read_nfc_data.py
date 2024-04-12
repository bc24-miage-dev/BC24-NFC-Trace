import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *
import pygame
import json
import os

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

# Load tag data from JSON file
tag_data = []
if os.path.isfile('data.json') and os.stat('data.json').st_size > 0:
    with open('data.json', 'r') as f:
        tag_data = json.load(f)

# Main loop
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

    # Read data from the first 7 blocks
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    block_data = []
    for i in range(7):  # Seulement les 7 premiers blocs
        try:
            pn532.mifare_classic_authenticate_block(
                uid, block_number=i, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
            data = pn532.mifare_classic_read_block(i)
            block_data.append(data.hex())  # Convert data to hex string
        except nfc.PN532Error as e:
            print(e.errmsg)
            break

    # Add tag data to list
    tag_data.append({'uid': uid_hex, 'data': block_data})

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
    for i, data in enumerate(block_data):
        row = i // num_cols
        col = i % num_cols
        data_label = ' '.join(data[j:j+2] for j in range(0, len(data), 2))
        label = FONT.render(data_label, True, (0, 0, 0))
        label_rect = label.get_rect()
        label_rect.topleft = (150 + col * col_width, 130 + row * row_height)
        display.blit(label, label_rect)

    pygame.display.update()

    # Serialize tag data to JSON file
    with open('data.json', 'w') as f:
        json.dump(tag_data, f, indent=4)  # Indent JSON output
        f.write('\n')  # Add a newline after each tag data

    # Wait for user to remove card
    while uid is not None:
        uid = pn532.read_passive_target(timeout=0.5)

    # Clear the display
    display.fill((255, 255, 255))
    pygame.display.update()

# Clean up
GPIO.cleanup()
pygame.quit()
