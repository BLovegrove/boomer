#!/bin/bash

DIR=$(pwd)

cd ~/Documents/Projects/Python/boomer

DATE=$(date +'%d-%m-%Y')

mkdir -p logs/$DATE

pipenv run python -m bot >> logs/$DATE/bot.log 2>&1 &

cd $DIR
