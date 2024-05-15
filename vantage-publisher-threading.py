from pyvantagepro import VantagePro2
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import threading
import os
'''
MQTT Publisher made for Davis VantagePro2 weather station.

v.1.1
'''

DEVICE_NAME = "it.uniparthenope.meteo." + os.getenv("HOSTNAME")


def readUsb(url):
    packet_data = {}
    try:
        device = VantagePro2.from_url(url, timeout=3)
        # Read data from USB device
        data = device.get_current_data()

        device.close()

        # Exclude parameters
        filt_data = {key: data[key] for key, value in parameters_data.items() if value}

        # Parse in JSON format
        for key, value in filt_data.items():
            packet_data[key] = value

        return packet_data

    except Exception as e:
        print(e)
        print("ERROR USB!")
        return packet_data


def on_publish(client, userdata, mid, reason_code, properties):
    print(f"{datetime.now()} - Device {DEVICE_NAME} : Data published.")


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()


# Load parameters
with open('parameters.json', 'r') as param_file:
    parameters_data = json.load(param_file)

with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)


# Creating MQTT connection
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(username=config_data['mqttUser'], password=config_data['mqttPass'])
mqttc.on_publish = on_publish
mqttc.connect(config_data['mqttBroker'], config_data['mqttPort'], config_data['timeout'])

# Connect to USB device
print(f"Connecting to device tcp:127.0.0.1:{config_data['usbPort']}")
#device = VantagePro2.from_serial(config_data['usb'], config_data['baud'])
#device = VantagePro2.from_url(f"tcp:127.0.0.1:{config_data['usbPort']}")
usbUrl = f"tcp:127.0.0.1:{config_data['usbPort']}"

mqttc.loop_start()

# Send packets
while True:
    usbData = [None]

    def getData():
        usbData[0] = readUsb(usbUrl)

    thread = threading.Thread(target=getData)
    thread.start()
    thread.join(timeout=10)

    if thread.is_alive():
        print("No response in 10 sec. Restarting...")
        thread.join()
    else:
        packet_data = usbData[0]
        packet_data['DatetimeWS'] = packet_data['Datetime']
        packet_data['Datetime'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        packet_data['latitude'] = config_data['deviceLat']
        packet_data['longitude'] = config_data['deviceLong']
        try:
            # Publish on MQTT
            ret = mqttc.publish(DEVICE_NAME, json.dumps(packet_data, default=datetime_serializer))

            # Wait a delay
            time.sleep(config_data['delay'])
        except Exception as e:
            print(e)
            print("ERROR MQTT!")

        except KeyboardInterrupt:
            # Gestisci l'interruzione da tastiera (CTRL+C) per uscire dal loop
            break

# Disconnect
mqttc.disconnect()
mqttc.loop_stop()
