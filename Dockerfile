# Bắt đầu từ một image Docker chính thức của Selenium
# Image này đã có sẵn: Python, Google Chrome, và ChromeDriver được cấu hình hoàn chỉnh.
FROM selenium/standalone-chrome:latest

# Chuyển sang người dùng root để cài đặt các thư viện Python
USER root

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file requirements.txt vào
COPY requirements.txt .

# Cài đặt các thư viện Python cần thiết (Flask, gunicorn, cloudscraper)
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép file code ứng dụng của bạn vào
COPY proxy_app.py .

# Mở cổng mà Gunicorn sẽ chạy
EXPOSE 10000

# Lệnh để chạy ứng dụng khi container khởi động
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "proxy_app:app"]