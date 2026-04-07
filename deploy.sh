#!/bin/bash
set -e

cd ~/EPAM-python-project

git pull origin main

docker build -t epam-app .
docker-compose up -d
