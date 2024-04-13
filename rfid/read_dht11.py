import time
import board
import busio
import adafruit_bme680

class BME680:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(self.i2c)
        self.bme680.sea_level_pressure = 1013.25

    def read_bme680_data(self):
        if self.bme680.temperature is not None and self.bme680.humidity is not None:
            return 0, self.bme680.temperature, self.bme680.humidity
        else:
            return -999, -999, -999

def loop():
    bme = BME680()
    sumCnt = 0
    okCnt = 0
    while True:
        sumCnt += 1
        chk, temperature, humidity = bme.read_bme680_data()
        if chk == 0:
            okCnt += 1

        okRate = 100.0 * okCnt / sumCnt
        print("Attempt: %d, \t Success rate: %.2f%%" % (sumCnt, okRate))
        print("Status: %d, \t Temperature: %.2f, \t Humidity: %.2f" % (chk, temperature, humidity))
        time.sleep(3)

if __name__ == '__main__':
    print('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        pass
    exit()
