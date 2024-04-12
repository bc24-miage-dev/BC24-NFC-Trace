#!/usr/bin/python
import pygame
import RPi.GPIO as GPIO
import json
from pn532 import *

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# Définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Définition de la taille de la fenêtre
WINDOW_SIZE = (800, 600)

# Configuration de l'écran
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Lecteur de tag NFC")

# Chargement de la police
font = pygame.font.SysFont('Arial', 30)

def display_message(message):
    screen.fill(WHITE)
    text_surface = font.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def read_nfc_tag():
    # Lecture du bloc de données sur le tag NFC Mifare
    block_number = 6  # Choisir le numéro de bloc approprié pour votre application
    try:
        data = pn532.mifare_classic_read_block(block_number)
        if data is not None:
            print("Contenu du bloc {} : {}".format(block_number, data))
            return data
        else:
            print("Impossible de lire le contenu du tag NFC Mifare.")
            return None
    except PN532_SPI as e:  # Utiliser PN532_SPI ici
        print("Erreur lors de la lecture du tag NFC Mifare :", e)
        return None

if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = pn532.get_firmware_version()
        print('Module NFC PN532 NFC HAT trouvé : {0}.{1}'.format(ver, rev))
        pn532.SAM_configuration()

        print("En attente d'un tag nfc...")
        display_message("En attente d'un tag nfc...")
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            if uid is not None:
                print("Tag NFC trouvé avec l'UID suivant : ", [hex(i) for i in uid])
                display_message("Tag NFC trouvé avec l'UID suivant : " + ', '.join([hex(i) for i in uid]))
                
                # Lecture du contenu du tag NFC Mifare
                tag_data = read_nfc_tag()
                if tag_data:
                    # Traitement ou affichage des données lues
                    # Exemple : Affichage du contenu du tag sur l'écran
                    display_message("Contenu du tag NFC Mifare : " + ', '.join([str(byte) for byte in tag_data]))
                
                # Sérialisation des données
                data = {'UID': [hex(i) for i in uid]}
                serialized_data = json.dumps(data)
                print('Sérialisation des données:', serialized_data)
                
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()