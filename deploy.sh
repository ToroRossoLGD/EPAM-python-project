#!/bin/bash
set -e

cd ~/EPAM-python-project

git pull origin main
docker pull ghcr.io/tororossolgd/epam-python-project:latest
docker-compose up -d
