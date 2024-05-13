#!/bin/bash

cd $HOME/vantage-publisher
docker-compose down
git pull
make build
docker-compose up -d
