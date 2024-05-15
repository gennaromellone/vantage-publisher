#!/bin/bash

cd /home/weather/vantage-publisher
docker-compose down
sudo git pull
sudo make build
sudo docker compose up -d
