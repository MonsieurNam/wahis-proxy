# Bắt đầu từ image Docker chính thức của Selenium
FROM selenium/standalone-chrome:latest

# Chuyển sang người dùng root
USER root

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép các file requirements và entrypoint
COPY requirements.txt .
COPY entrypoint.sh .

# Cấp quyền thực thi cho file entrypoint.sh
RUN chmod +x entrypoint.sh

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép file code ứng dụng
COPY proxy_app.py .

# Mở cổng 10000
EXPOSE 10000

# Lệnh cuối cùng: Chạy file entrypoint.sh khi container khởi động
CMD ["./entrypoint.sh"]