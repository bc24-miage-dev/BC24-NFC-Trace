import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *
import pygame
import json
import os
import sys

# Initialiser Pygame
pygame.init()

# Configurer l'affichage
DISPLAY_WIDTH = 720
DISPLAY_HEIGHT = 500
display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Lecteur de Tags NFC')

# Configurer les polices
FONT_SIZE = 16
FONT = pygame.font.SysFont('Arial', FONT_SIZE)

# Initialiser PN532
pn532 = PN532_SPI(cs=4, reset=20, debug=False)

# Obtenir la version du firmware
ic, ver, rev, support = pn532.get_firmware_version()
print('PN532 trouvé avec la version du firmware : {0}.{1}'.format(ver, rev))

# Configurer PN532 pour communiquer avec les cartes MiFare
pn532.SAM_configuration()

# Chemin du répertoire JSON
JSON_DIRECTORY = "json/"

# Créer le répertoire JSON s'il n'existe pas
if not os.path.exists(JSON_DIRECTORY):
    os.makedirs(JSON_DIRECTORY)

# Boucle principale
try:
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Vérifier si une carte est disponible à la lecture
        uid = pn532.read_passive_target(timeout=0.5)

        # Réessayer si aucune carte n'est disponible.
        if uid is None:
            continue

        # Convertir UID en chaîne hexadécimale
        uid_hex = ':'.join('{:02X}'.format(x) for x in uid)

        # Lire les données des blocs spécifiques
        key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        token_id = ""
        temperature = ""
        gps_data = {"longitude": "", "latitude": "", "altitude": ""}
        default_gps_data = {"longitude": "non trouve", "latitude": "non trouve", "altitude": "non trouve"}
        date = ""

        # Numéros de bloc pour des données spécifiques
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

        # Ajouter les données du tag à la liste
        tag_data = {'uid': uid_hex, 'NFT_tokenID': token_id, 'temperature': temperature, 'gps': gps_data, 'date': date}

        # Afficher les données du tag à l'écran
        display.fill((255, 255, 255))
        label = FONT.render('Données du Tag (' + uid_hex + '):', True, (0, 0, 0))
        display.blit(label, (50, 50))

        # Dessiner l'en-tête du tableau
        header_font = pygame.font.SysFont('Arial', FONT_SIZE * 2)
        header_label = header_font.render('Bloc', True, (0, 0, 0))
        header_rect = header_label.get_rect()
        header_rect.topleft = (50, 100)
        display.blit(header_label, header_rect)

        # Dessiner les données du tableau
        row_height = FONT_SIZE + 5
        col_width = 450
        num_cols = 1
        for i, block_name in enumerate(["NFT_tokenID", "temperature", "gps", "date"]):
            if block_name == "gps":
                data_label = block_name + ": {"
                data_label += "longitude: " + gps_data["longitude"] + ", "
                data_label += "latitude: " + gps_data["latitude"] + ", "
                data_label += "altitude: " + gps_data["altitude"] + "}"
            else:
                data_label = block_name + ": " + tag_data[block_name]
            label = FONT.render(data_label, True, (0, 0, 0))
            label_rect = label.get_rect()
            row = i
            col = 0
            label_rect.topleft = (150 + col * col_width, 130 + row * row_height)
            display.blit(label, label_rect)

        pygame.display.update()

        # Écrire les données du tag dans un fichier JSON avec UID comme nom de fichier
        filename = JSON_DIRECTORY + 'data_' + uid_hex.replace(':', '_') + '.json'
        with open(filename, 'w') as f:
            json.dump(tag_data, f, indent=4)

        # Attendre que l'utilisateur retire la carte
        while uid is not None:
            uid = pn532.read_passive_target(timeout=0.5)

        # Effacer l'affichage
        display.fill((255, 255, 255))
        pygame.display.update()

except KeyboardInterrupt:
    print("Programme interrompu...")
    GPIO.cleanup()
    pygame.quit()
    sys.exit(0)
