from pyvantagepro import VantagePro2
import time
import json
from datetime import datetime
import csv

with open('parameters.json', 'r') as param_file:
    parameters_data = json.load(param_file)

url = "tcp:127.0.0.1:22222"
device = VantagePro2.from_url(url, timeout=3)
time_offset = datetime.now() - device.gettime()
start = time.time()
datas = device.get_archives(start_date=datetime(2009, 1, 1, 1, 1, 1))
print("Time", time.time()-start)

device.close()
packet_data = []
for data in datas:
	d = {}
	# Exclude parameters
	#filt_data = {key: data[key] for key, value in parameters_data.items() if value}
	filt_data = data
	for key, value in filt_data.items():
		if key == 'Datetime':
			d[key] = value + time_offset
		else:
			d[key] = value
	packet_data.append(d)

print(packet_data)
filename = 'weather_data.csv'

with open(filename, mode='w', newline='') as file:
  
    fieldnames = packet_data[0].keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for row in packet_data:
        row['Datetime'] = row['Datetime'].strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow(row)
