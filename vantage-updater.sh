#!/bin/bash

cd /home/weather/Desktop/vantage-publisher
docker-compose down
git pull
make build
docker-compose up -d
