#!/bin/bash
set -e



if ! sudo systemctl is-active --quiet docker; then
    sudo systemctl start docker
fi

cd ~/EPAM-python-project

docker pull ghcr.io/tororossolgd/epam-python-project:latest
docker-compose up -d
