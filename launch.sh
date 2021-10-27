#!/bin/bash

cd ~/Documents/Projects/Python/boomer

java -jar Lavalink.jar &

sleep 10

pipenv run python -m boomer