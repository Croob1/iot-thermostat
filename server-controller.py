import time
import datetime
import sys
import paho.mqtt.client
import json
import boto3

address, port, username, password = "127.0.0.1", 1883, "user", "pass"

def log(text):
    try:
        with open ("./output/log.txt", "a") as file:
            now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S:%f')
            file.write(now + ": " + str(text) + "\n")
    except Exception as e:
        print(f"Error: writing to log failed. Printing error to terminal:\n{e}")

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
            address, port, username, password = contents["address"], contents["port"], contents["username"], contents["password"]
    except Exception as err:
        print("Error: reading config.json contents failed, please ensure the file is correctly formatted and try again.")
        log(err)
        sys.exit()

def save_config():
    try:
        with open("config.json", "w") as file:
            contents = {"address": address, "port": port, "username": username, "password": password}
            json.dump(contents, file, indent=4)
    except Exception as e:
        print("Error: writing to config.json failed, please check process permissions and try again")
        log(err)
        sys.exit()

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("temperature")

def on_message(client, userdata, msg):
    temperature = msg.payload.decode("utf-8")
    dynamodb.put_item(
        TableName="temperatures",
        Item={
            'device-id': {'S': '1'},
            'date-time': {'S': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            'temperature': {'N': temperature},
        }
    )

load_config()

dynamodb = boto3.client("dynamodb", region_name="us-east-1")

try:
    client = paho.mqtt.client.Client(paho.mqtt.client.CallbackAPIVersion.VERSION2, client_id="server", userdata=None, protocol=paho.mqtt.client.MQTTv5)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(address, port)
except Exception as err:
    log(err)
    print("Error: connection to MQTT broker failed")
    sys.exit()

client.loop_forever()
