#!/bin/bash
set -e  # Прерывать выполнение при любой ошибке

cd /opt/fastapi-app

git reset --hard HEAD
git pull origin main --force

source venv/bin/activate
pip install -r requirements.txt --no-cache-dir
sudo systemctl restart fastapi.service

echo "Deployment completed"