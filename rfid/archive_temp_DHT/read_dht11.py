#!/usr/bin/env python3

import bme680
import time

class BME680Sensor:
    def __init__(self):
        try:
            self.sensor = bme680.BME680(bme680.SPI_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.SPI_ADDR_SECONDARY)

        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)

    def read_data(self):
        if self.sensor.get_sensor_data():
            return self.sensor.data.temperature, self.sensor.data.humidity
        else:
            return None

def loop():
    bme = BME680Sensor()
    sumCnt = 0
    okCnt = 0
    while True:
        sumCnt += 1
        data = bme.read_data()
        if data is not None:
            okCnt += 1
        okRate = 100.0 * okCnt / sumCnt
        print("sumCnt : %d, \t okRate : %.2f%% " % (sumCnt, okRate))
        if data is not None:
            temperature, humidity = data
            print("Status: 0, \t Temperature: %.2f, \t Humidity: %.2f" % (temperature, humidity))
        else:
            print("Status: -1, \t Temperature: n/a, \t Humidity: n/a")
        time.sleep(3)

if __name__ == '__main__':
    print('Program is starting...')
    try:
        loop()
    except KeyboardInterrupt:
        pass
