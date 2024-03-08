build:
	docker build -t vantage-publisher .

run:
	docker run --rm -it -v ./config.json:/config/config.json -v ./parameters.json:/config/parameters.json --device=/dev/ttyUSB0 vantage-publisher