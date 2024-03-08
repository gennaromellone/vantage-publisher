from pyvantagepro import VantagePro2
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
'''
MQTT Publisher made for Davis VantagePro2 weather station.

v.1.0
'''

# Load parameters
with open('/config/parameters.json', 'r') as param_file:
    parameters_data = json.load(param_file)

with open('/config/config.json', 'r') as config_file:
    config_data = json.load(config_file)

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"Device {config_data['deviceName']} : Data published.")
    pass

def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

# Creating MQTT connection
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(username=config_data['mqttUser'], password=config_data['mqttPass'])
mqttc.on_publish = on_publish
mqttc.connect(config_data['mqttBroker'], config_data['mqttPort'], config_data['timeout'])

# Connect to USB device
print(f"Connecting to device {config_data['usb']}. Baudrate: {config_data['baud']}")
device = VantagePro2.from_serial(config_data['usb'], config_data['baud'])

# Send packets
while True:
    try:
        # Read data from USB device
        data = device.get_current_data()

        # Exclude parameters
        filt_data = {key: data[key] for key, value in parameters_data.items() if value}

        # Parse in JSON format
        packet_data = {}
        for key, value in filt_data.items():
            packet_data[key] = value

        # Publish on MQTT
        ret= mqttc.publish(config_data['deviceName'], json.dumps(packet_data, default=datetime_serializer))

        # Wait a delay
        time.sleep(config_data['delay'])

    except KeyboardInterrupt:
            # Gestisci l'interruzione da tastiera (CTRL+C) per uscire dal loop
            break

# Disconnect
mqttc.disconnect()
mqttc.loop_stop()
