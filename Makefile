build:
	docker build -t vantage-publisher .

run:
	docker run -it --network=host -v ./config.json:/config/config.json -v ./parameters.json:/config/parameters.json vantage-publisher