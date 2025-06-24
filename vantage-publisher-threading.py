from pyvantagepro import VantagePro2
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import threading
import os
from airlink import airlinkData
import requests
import csv

'''
MQTT Publisher made for Davis VantagePro2 weather station.

NEW:
    Support for AirLink devices
v.1.2
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


def save_data_to_csv(config_data, packet_data):
    try:
        # Extract year and month from the 'Datetime' field
        timestamp = packet_data['Datetime']
        year = timestamp[:4]
        month = timestamp[5:7].zfill(2)
        day = timestamp[8:10].zfill(2)

        # Create year directory if it doesn't exist
        year_directory = os.path.join(config_data['pathStorage'], year)
        month_directory = os.path.join(year_directory, month)
        os.makedirs(month_directory, exist_ok=True)

        # Create or open the monthly CSV file
        csv_file_path = os.path.join(month_directory, f"{year}-{month}-{day}.csv")
        file_exists = os.path.isfile(csv_file_path)

        if file_exists:
            with open(csv_file_path, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_fieldnames = reader.fieldnames

                # Update the header if the new fieldnames have more fields
                if set(packet_data.keys()) != set(existing_fieldnames):
                    if len(packet_data.keys()) > len(existing_fieldnames):
                        temp_rows = list(reader)
                        with open(csv_file_path, mode='w', newline='') as csvfile_w:
                            writer = csv.DictWriter(csvfile_w, fieldnames=packet_data.keys())
                            writer.writeheader()
                            writer.writerows(temp_rows)

        # Write data to the CSV file
        with open(csv_file_path, mode='a', newline='') as csvfile:
            fieldnames = packet_data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header only if the file is new
            if not file_exists:
                writer.writeheader()

            # Write the data row
            writer.writerow(packet_data)

    except Exception as e:
        print(f"Error writing to CSV: {e}")


# Load parameters
with open('parameters.json', 'r') as param_file:
    parameters_data = json.load(param_file)

with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

# Ensure the root directory exists
os.makedirs(config_data['pathStorage'], exist_ok=True)

# Read AirLink ID
airlink_url = f"http://{config_data['mqttBroker']}:8088/get_airlink/{DEVICE_NAME}"
airlink_response = requests.get(airlink_url)
airlink_id = ""
if airlink_response.status_code == 200:
    airlink_json = airlink_response.json()
    airlink_id = airlink_json["airlinkID"]
elif airlink_response.status_code == 404:
    print("Error: Instrument not found")
else:
    print(f"Errore: {airlink_response.status_code}. {airlink_url}")

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

# Handle airlink data
last_airlink_data = None
last_airlink_time = 0
AIRLINK_INTERVAL = 300 


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
        if "Datetime" in packet_data:
            packet_data['DatetimeWS'] = packet_data['Datetime']
            
        packet_data['Datetime'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        #packet_data['latitude'] = config_data['deviceLat']
        #packet_data['longitude'] = config_data['deviceLong']
        packet_data['place'] = config_data['devicePlace']

        current_time = time.time()
        # Update airlink data only each AIRLINK_INTERVAL sec.
        if airlink_id != "" and (last_airlink_data is None or (current_time - last_airlink_time) > AIRLINK_INTERVAL):
            try:
                last_airlink_data = airlinkData(airlink_id)
                last_airlink_time = current_time
            except Exception as e:
                print(f"Errore nell'aggiornamento dati Airlink: {e}")
        if last_airlink_data:
            packet_data.update(last_airlink_data)
        
        save_data_to_csv(config_data, packet_data)

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
