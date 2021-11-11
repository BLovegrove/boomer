#!/bin/bash

cd ~/Documents/Projects/Python/boomer/scripts/

DATE=$(date +'%d-%m-%Y')

mkdir -p ../logs/$DATE

java -jar ../Lavalink.jar >> ../logs/$DATE/lavalink.log 2>&1 &

cd ~/Documents/Projects/Python/boomer/

sleep 30

pipenv run python -m bot >> logs/$DATE/boomer.log 2>&1 &