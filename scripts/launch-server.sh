#!/bin/bash

DIR=$(pwd)

cd ~/Documents/Projects/Python/boomer

DATE=$(date +'%d-%m-%Y')

mkdir -p logs/$DATE

java -jar Lavalink.jar >> logs/$DATE/lavalink.log 2>&1 &

cd $DIR