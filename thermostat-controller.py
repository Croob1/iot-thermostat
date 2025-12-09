import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime
import sys

SENSOR_TYPE = Adafruit_DHT.DHT11
PIN_SENSOR = 4
PIN_HEATER = 21
targetTemps = [0, 0, 0, 0, 0, 0, 0, 21, 21, 21, 0, 0, 0, 0, 0, 0, 0, 21, 21, 21, 0, 0, 0, 0]
targetTemp = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_HEATER, GPIO.OUT)

def log(text):
    try:
        with open ("./output/log.txt", "a") as file:
            now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S:%f')
            file.write(now + ": " + str(text) + "\n")
    except Exception as e:
        print(f"Error: writing to log failed. Printing error to terminal:\n{e}")

def sensor_read():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, PIN_SENSOR)
    return humidity, temperature

def heater(on):
    GPIO.output(PIN_HEATER, on)

def load_targets():
    try:
        with open("config.txt", "r") as file:
            for i in range(23):
                try:
                    targetTemps[i] = int(file.readline())
                except Exception:
                    print("Error: reading config.txt contents failed, please ensure the file is correctly formatted and try again.")
                    log(e)
                    sys.exit()
    except Exception as e:
        print("Error: config.txt not found. Generating file with default parameters")
        log(e)
        save_targets()

def save_targets():
    try:
        with open("config.txt", "w") as file:
            for i in range(23):
                file.write(str(targetTemps[i]) + "\n")
    except Exception as e:
        print("Error: writing to config.txt failed, please check process permissions and try again")
        log(e)
        sys.exit()

load_targets()

while True:
    humidity, temperature = sensor_read()

    now = time.localtime()
    hour = now.tm_hour
    targetTemp = targetTemps[hour - 1]

    if temperature < targetTemp:
        heater(True)
        print(f"Temp={temperature}, Target={targetTemp}, HeaterOn=True")
    else:
        heater(False)
        print(f"Temp={temperature}, Target={targetTemp}, HeaterOn=False")

    time.sleep(5)
