import requests

def airlinkData(uuid):
	url = f"https://api.weatherlink.com/v2/current/{uuid}?api-key=b3xchodamrmfri3qd2zguel7nifkndh9"

	headers = {
  		'X-Api-Secret': 'zl4kshrwl7t0xl8z2u07ewptbmjfcdg9'
		}


	response = requests.request("GET", url, headers=headers)
	res = response.json()
	data = {}
	try:
		#print(len(res["sensors"]))
		for sensor in res["sensors"]:
			#print(sensor)
			if "hum" in sensor["data"][0]:
				data = sensor["data"][0]

				data['hum'] = float(data['hum'])
				data['pm_10_3_hour'] = float(data['pm_10_3_hour'])
				data['pm_10_24_hour'] = float(data['pm_10_24_hour'])
				data['pm_2p5_1_hour'] = float(data['pm_2p5_1_hour'])
				data['aqi_nowcast_val'] = float(data['aqi_nowcast_val'])
				data['heat_index'] = float(data['heat_index'])
				data['pm_2p5_nowcast'] = float(data['pm_2p5_nowcast'])
				data['pm_2p5_24_hour'] = float(data['pm_2p5_24_hour'])
				data['pm_1'] = float(data['pm_1'])
				data['aqi_val'] = float(data['aqi_val'])
				data['temp'] = float(data['temp'])
				data['pm_2p5_3_hour'] = float(data['pm_2p5_3_hour'])
				data['aqi_1_hour_val'] = float(data['aqi_1_hour_val'])
				data['pm_10_nowcast'] = float(data['pm_10_nowcast'])
				data['pm_10_1_hour'] = float(data['pm_10_1_hour'])
				data['dew_point'] = float(data['dew_point'])
				data['pm_10'] = float(data['pm_10'])
				data['pm_2p5'] = float(data['pm_2p5'])
	except Exception as e:
		print(e)

	return data
