import RPi.GPIO as GPIO
import time

# Utiliser la numérotation des broches BCM
GPIO.setmode(GPIO.BCM)

# Définir la broche du capteur DHT11
DHT_PIN = 11

# Définir la fonction pour lire les données du capteur DHT11
def read_dht11():
    GPIO.setup(DHT_PIN, GPIO.OUT)
    GPIO.output(DHT_PIN, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(DHT_PIN, GPIO.HIGH)
    GPIO.setup(DHT_PIN, GPIO.IN)

    while GPIO.input(DHT_PIN) == GPIO.LOW:
        pass
    while GPIO.input(DHT_PIN) == GPIO.HIGH:
        pass

    data = [0, 0, 0, 0, 0]
    for i in range(40):
        while GPIO.input(DHT_PIN) == GPIO.LOW:
            pass
        while GPIO.input(DHT_PIN) == GPIO.HIGH:
            pass
        data[i // 8] <<= 1
        if GPIO.input(DHT_PIN) == GPIO.HIGH:
            data[i // 8] |= 1

    if data[0] + data[1] + data[2] + data[3] != data[4]:
        return None, None

    return data[0], data[2]

def main():
    while True:
        humidity, temperature = read_dht11()
        if humidity is not None and temperature is not None:
            print("Humidity: {:.1f}%  Temperature: {:.1f}°C".format(humidity, temperature))
        else:
            print("Failed to read data from DHT11 sensor")
        time.sleep(5)

if __name__ == '__main__':
	print ('Program is starting ... ')
	try:
		main()
	except KeyboardInterrupt:
		pass
		exit()
