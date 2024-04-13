import Adafruit_DHT
import time
import RPi.GPIO as GPIO

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 12

def read_dht_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return humidity, temperature
    else:
        return -999, -999

def loop():
    while True:
        humidity, temperature = read_dht_sensor()
        print("Humidity: {:.2f}%, \t Temperature: {:.2f}°C".format(humidity, temperature))
        time.sleep(3)

if __name__ == '__main__':
    print("Program is starting...")
    try:
        loop()
    except KeyboardInterrupt:
        pass