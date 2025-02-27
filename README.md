# Vantage Publisher

Vantage Publisher is an application designed to collect and publish data from a Davis VantagePro2 weather station and the AirLink device via MQTT. The project supports data collection from both the weather station console and AirLink, allowing real-time transmission to an MQTT broker for further processing or storage.

## Main Features
- Data collection from Davis VantagePro2
- Integration with AirLink for air quality data
- Data publishing to an MQTT broker
- Threading support for efficient process management
- Configurable settings via a configuration file
- Dockerization for easy and scalable deployment

## Installation
### Requirements
- Python 3.7+
- MQTT broker (e.g., Mosquitto)
- Required Python libraries listed in `requirements.txt`

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/gennaromellone/vantage-publisher.git
   cd vantage-publisher
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure parameters in `config.yaml` if necessary.

## Usage


### Running `vantage-publisher-threading.py`
This script collects weather data from the VantagePro2 console using a threading-based model to handle communication and data transmission to MQTT in parallel.

#### Run the script:
```sh
python vantage-publisher-threading.py
```

#### How it works:
- Starts multiple threads to read sensor data in parallel.
- Converts data into a standard JSON format.
- Publishes data to the MQTT broker.
- Handles automatic reconnection in case of communication errors.
- Logs main activities and errors for debugging.

#### Example JSON output published to MQTT:
```json
{
    "timestamp": "2025-02-27T12:00:00Z",
    "temperature": 21.8,
    "humidity": 58.4,
    "wind_speed": 15.2,
    "wind_direction": 220,
    "rain_rate": 0.0,
    "pressure": 1012.3
}
```

## Configuration
The MQTT broker settings and sensor reading configurations can be modified in the `config.yaml` file.
Example configuration:
```yaml
mqtt:
  broker: "mqtt.example.com"
  port: 1883
  topic_airlink: "weather/airlink"
  topic_vantage: "weather/vantage"

sensor:
  airlink_ip: "192.168.1.100"
  vantage_serial_port: "/dev/ttyUSB0"
```

## Running with Docker
To start the service with Docker:
```sh
docker build -t vantage-publisher .
docker run -d --name vantage -e MQTT_BROKER=mqtt.example.com vantage-publisher
```

## Logging and Debugging
Logs are saved in the `logs/` directory and can be used for debugging.
```sh
tail -f logs/vantage.log
```

## Contributions
If you wish to contribute, open a pull request or report any issues via the repository's issue tracker.

## License
This project is released under the Apache-2.0 license.

