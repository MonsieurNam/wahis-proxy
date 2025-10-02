#!/usr/bin/env bash
# exit on error
set -o errexit

# Cài đặt các gói hệ thống cần thiết cho Google Chrome
apt-get update
apt-get install -y procps libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 google-chrome-stable

# Cài đặt các thư viện Python
pip install -r requirements.txt