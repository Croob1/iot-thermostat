import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime
import sys
import paho.mqtt.client
import json

SENSOR_TYPE = Adafruit_DHT.DHT11
PIN_SENSOR = 4
PIN_HEATER = 21
targetTemps = [0, 0, 0, 0, 0, 0, 0, 21, 21, 21, 0, 0, 0, 0, 0, 0, 0, 21, 21, 21, 0, 0, 0, 0]
targetTemp = 0
address, port, username, password = "127.0.0.1", 1883, "user", "pass"
READ_INTERVAL = 300

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

def load_config():
    global address, port, username, password

    try:
        file = open("config.json", "r") 
    except Exception as err:
        i = input("Error: cannot open config.json. If this is a first time execution press (y) to generate a default config file: ")
        if i == "y":
            save_config()
            print("Generated config.json, edit this file and try again.")
            sys.exit()
        else:
            print("Error code has been logged")
            log(err)
            sys.exit()

    try:
        with file:
            contents = json.load(file)
            targetTemps = contents["targets"]
            address, port, username, password = contents["address"], contents["port"], contents["username"], contents["password"]
    except Exception as err:
        print("Error: reading config.json contents failed, please ensure the file is correctly formatted and try again.")
        log(err)
        sys.exit()

def save_config():
    try:
        with open("config.json", "w") as file:
            contents = {"address": address, "port": port, "username": username, "password": password, "targets": targetTemps}
            json.dump(contents, file, indent=4)
    except Exception as e:
        print("Error: writing to config.json failed, please check process permissions and try again")
        log(err)
        sys.exit()

load_config()

try:
    client = paho.mqtt.client.Client(paho.mqtt.client.CallbackAPIVersion.VERSION2, client_id="pi", userdata=None, protocol=paho.mqtt.client.MQTTv5)
    client.username_pw_set(username, password)
    client.connect(address, port)

    client.loop_start()
except Exception as err:
    log(err)
    print("Error: connection to MQTT broker failed")
    sys.exit()


while True:
    humidity, temperature = sensor_read()

    now = time.localtime()
    hour = now.tm_hour
    targetTemp = targetTemps[hour - 1]

    if temperature < targetTemp:
        heater(True)
        print(f"Temp={temperature}, Target={targetTemp}, HeaterOn=True")
        client.publish("temperature", payload=temperature, qos=1)
    else:
        heater(False)
        print(f"Temp={temperature}, Target={targetTemp}, HeaterOn=False")
        client.publish("temperature", payload=temperature, qos=1)

    time.sleep(READ_INTERVAL)

client.loop_stop()
