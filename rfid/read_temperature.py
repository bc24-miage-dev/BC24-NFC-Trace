import bme680
import time
import json
from write_temperature import write_to_tag, read_from_tag, get_temperature

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

def loop(pn532, uid):
    bme = BME680Sensor()
    sumCnt = 0
    okCnt = 0
    while True:
        sumCnt += 1
        temperature = get_temperature(bme.sensor)
        if temperature is not None:
            okCnt += 1
        okRate = 100.0 * okCnt / sumCnt
        print("sumCnt : %d, \t okRate : %.2f%% " % (sumCnt, okRate))
        if temperature is not None:
            print("Status: 0, \t Temperature: %.2f" % temperature)

            # Écrire la température dans le tag NFC
            if write_to_tag(pn532, uid, temperature):
                print("Température écrite avec succès dans le tag NFC.")
            else:
                print("Échec de l'écriture de la température dans le tag NFC.")

        else:
            print("Status: -1, \t Temperature: n/a")
        time.sleep(3)