# BC24 : Hardware material & API

## Presentation :
This project consists of two parts:
1. The python module for managing the hardware components, it allow us to trace all resources with NFC tag
2. The API to serve our [webapp](https://github.com/bc24-miage-dev/BC24-WEBAPP) and allow the communication with our material below

## Hardware components :
1. Raspberry Pi
2. [Touch screen](https://www.raspberrypi.com/products/raspberry-pi-touch-display/) to display and run our [webapp](https://github.com/bc24-miage-dev/BC24-WEBAPP)
2. [NFC tag](https://en.wikipedia.org/wiki/MIFARE) to store metadata
3. [NFC hat](https://www.waveshare.com/wiki/PN532_NFC_HAT) to read and write NFC tag
4. [GPS sensor](https://www.waveshare.com/wiki/L76K_GPS_Module) to read GPS position 
5. [Temperature Sensor](https://www.gotronic.fr/art-capteur-de-t-et-d-humidite-dht11-st052-26117.htm) to read temperature

## Local Deployment on Raspberry Pi
Follow these steps to launch the API locally:
1. Ensure you have at least Python 3 installed.
2. run `python3 restAPI.py`

### Common eror :
1. if error : ModuleNotFoundError: No module named 'bme680’ 
  `sudo pip3 install bme680`
2. if error : ModuleNotFoundError: No module named 'pa1010d’ 
  `sudo pip3 install pa1010d`

## Project management and Documentation :
The project was managed using Notion, bringing together all the different working groups and their contributions. It is free to consult it [here](https://www.notion.so/NFC-Trace-72dcf67da73045f8bcafedac6dd7224e).
