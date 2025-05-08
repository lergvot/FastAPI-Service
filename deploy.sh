#!/bin/bash
cd /opt/fastapi-app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --no-cache-dir
sudo systemctl restart fastapi.service
