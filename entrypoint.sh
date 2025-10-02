#!/bin/bash

# Start Selenium Server in background
java -jar /opt/selenium/selenium-server.jar standalone --port 4444 &

# Wait for Selenium to be ready
echo "Waiting for Selenium Server to start..."
until curl -s http://localhost:4444/wd/hub/status > /dev/null 2>&1; do
    sleep 1
done
echo "Selenium Server is ready!"

# Start Flask app
exec gunicorn --bind 0.0.0.0:10000 --timeout 120 --workers 1 proxy_app:app