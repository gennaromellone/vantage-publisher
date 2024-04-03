build:
	docker build -t vantage-publisher .

run:
	docker run --network=host -v ./config.json:/config/config.json -v ./parameters.json:/config/parameters.json -d vantage-publisher 