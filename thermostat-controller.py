import RPi.GPIO as GPIO
import Adafruit_DHT
import time

SENSOR_TYPE = Adafruit_DHT.DHT11
PIN_SENSOR = 4
PIN_HEATER = 21
targetTemp = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_HEATER, GPIO.OUT)

def sensor_read():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, PIN_SENSOR)
    return humidity, temperature

def heater(on):
    GPIO.output(PIN_HEATER, on)

while True:
    humidity, temperature = sensor_read()
    if temperature < targetTemp:
        heater(True)
        print(f"Temp={temperature}, Target={targetTemp}, HeaterOn=True")
    else:
        heater(False)
        print(f"Temp={temperature}, Target={targetTemp}, HeaterOn=False")
