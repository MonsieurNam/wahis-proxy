#!/bin/bash

# Khởi động Selenium Server ở chế độ nền (background)
/opt/bin/entry_point.sh &

# Đợi một vài giây để Selenium Server khởi động hoàn toàn
sleep 5

# Khởi động ứng dụng Gunicorn/Flask ở chế độ chính (foreground)
exec gunicorn --bind 0.0.0.0:10000 proxy_app:app