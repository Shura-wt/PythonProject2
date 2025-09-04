#! /usr/bin/env python3

import paho.mqtt.client as mqtt
from datetime import datetime
import requests
import json, traceback

tls_ca_cert = "/etc/mosquitto/ca_certificates/rootCA.pem"
tls_certfile = "/etc/mosquitto/ca_certificates/mosquitto.crt"
tls_keyfile = "/etc/mosquitto/ca_certificates/mosquitto.key"

MOSQUITTO_USER = "gps_tracker"
MOSQUITTO_PWD = "p8$9z5Gn&x"

BAESAPI_SERVER = "localhost"
BAESAPI_USER = "superadmin"
BAESAPI_PWD = "superadmin_password"

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe("baes/data")


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode('utf-8')
        json_data = json.loads(payload)

        # Get the error code from the JSON data
        erreur_raw = json_data.get("baes_state", json_data.get("erreur", 6))
        erreur = int(erreur_raw) if isinstance(erreur_raw, (int, float)) or (
                    isinstance(erreur_raw, str) and erreur_raw.isdigit()) else 6

        # Get the baes_id from the JSON data
        baes_id_raw = json_data.get("baes_id")

        # Remove colons and convert hex string to integer
        baes_id = int(baes_id_raw.replace(":", ""), 16)

        # Ensure it's within 64-bit unsigned range
        baes_id &= 0xFFFFFFFFFFFFFFFF
            
        # Get temperature and vibration from the JSON data if they exist
        temperature = json_data.get("temperature")
        vibration = json_data.get("vibration")

        data = {
            "baes_id": baes_id,
            "erreur": int(erreur)
        }
        
        # Add temperature and vibration to the data if they exist
        if (temperature is not None) and (temperature != "nan"):
            data["temperature"] = float(temperature)
        if vibration is not None:
            data["vibration"] = vibration

        print("Sending data to BAES API:", data)
        result = requests.post(f"http://{BAESAPI_SERVER}:5000/erreurs/", json=data, verify=False, timeout=5.0)
        print(result.text)
    except Exception as e:
        print("Error while decoding and inserting data:", str(e))
        traceback.print_exc()


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
#client.tls_set(ca_certs=tls_ca_cert,
#               certfile=tls_certfile,
#               keyfile=tls_keyfile,
#               tls_version=mqtt.ssl.PROTOCOL_TLS)
#client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(MOSQUITTO_USER, MOSQUITTO_PWD)

client.connect("20.82.99.234", 1883, 60) #8883
client.loop_forever()
