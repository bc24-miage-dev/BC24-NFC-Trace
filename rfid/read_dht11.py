import Adafruit_DHT
import time
import RPi.GPIO as GPIO

class DHT(object):
    DHTLIB_OK = 0
    DHTLIB_ERROR_CHECKSUM = -1
    DHTLIB_ERROR_TIMEOUT = -2
    DHTLIB_INVALID_VALUE = -999

    DHTLIB_DHT11_WAKEUP = 0.020  # 18ms
    DHTLIB_TIMEOUT = 0.0001  # 100us

    humidity = 0
    temperature = 0

    def __init__(self, pin):
        self.pin = pin
        self.bits = [0, 0, 0, 0, 0]
        GPIO.setmode(GPIO.BCM)
        print("DHT object initialized on pin:", pin)

    def read_dht_sensor(self):
        print("Reading sensor data...")
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.pin)
        if humidity is not None and temperature is not None:
            print("Sensor data read successfully.")
            return self.DHTLIB_OK, humidity, temperature
        else:
            print("Warning: Failed to read sensor data.")
            return self.DHTLIB_INVALID_VALUE, self.DHTLIB_INVALID_VALUE, self.DHTLIB_INVALID_VALUE

def loop():
    dht = DHT(11)
    sumCnt = 0
    okCnt = 0
    while True:
        sumCnt += 1
        chk, humidity, temperature = dht.read_dht_sensor()
        if chk == 0:
            okCnt += 1

        okRate = 100.0 * okCnt / sumCnt
        print("Attempt: %d, \t Success rate: %.2f%%" % (sumCnt, okRate))
        print("Status: %d, \t Humidity: %.2f, \t Temperature: %.2f" % (chk, humidity, temperature))
        time.sleep(3)

if __name__ == '__main__':
    print('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    exit()
