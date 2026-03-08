#!/bin/bash

set -e

APP_DIR="/opt/qjoe"

echo "Updating system..."
apt update
apt install -y python3 python3-venv python3-pip git

echo "Creating app directory..."
mkdir -p $APP_DIR

echo "Cloning repo..."
git clone https://github.com/YOUR_REPO/qjoe-prompts.git $APP_DIR

cd $APP_DIR

echo "Creating virtualenv..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing playwright browsers..."
playwright install

echo "Copying systemd services..."
cp infra/systemd/qjoe-api.service /etc/systemd/system/
cp infra/systemd/qjoe-batch.service /etc/systemd/system/
cp infra/systemd/qjoe-batch.timer /etc/systemd/system/
cp infra/systemd/qjoe-spontaneous.service /etc/systemd/system/
cp infra/systemd/qjoe-spontaneous.timer /etc/systemd/system/

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling services..."
systemctl enable qjoe-api
systemctl enable qjoe-batch.timer
systemctl enable qjoe-spontaneous.timer

echo "Starting services..."
systemctl start qjoe-api
systemctl start qjoe-batch.timer
systemctl start qjoe-spontaneous.timer

echo "Bootstrap complete."
