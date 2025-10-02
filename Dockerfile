# === Giai đoạn 1: Build Environment ===
# Bắt đầu từ một image Python chính thức
FROM python:3.11.5-slim-bookworm AS builder

# Thiết lập các biến môi trường để tránh các câu hỏi tương tác khi cài đặt
ENV DEBIAN_FRONTEND=noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Cài đặt các gói cần thiết để tải Chrome và các phụ thuộc
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Tải và cài đặt Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# === Giai đoạn 2: Production Environment ===
# Bắt đầu từ một image Python nhỏ gọn hơn để chạy ứng dụng
FROM python:3.11.5-slim-bookworm

# Sao chép các gói Python đã cài đặt từ giai đoạn build
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Sao chép Google Chrome đã cài đặt từ giai đoạn build
COPY --from=builder /opt/google/chrome /opt/google/chrome
COPY --from=builder /usr/bin/google-chrome* /usr/bin/

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép code ứng dụng của bạn vào
COPY proxy_app.py .

# Thiết lập biến môi trường cho WebDriver Manager để nó biết Chrome ở đâu
ENV CHROME_DRIVER_PATH=/usr/bin/google-chrome
ENV CHROME_BINARY_PATH=/opt/google/chrome/google-chrome

# Mở cổng 10000 mà Render sử dụng
EXPOSE 10000

# Lệnh để chạy ứng dụng khi container khởi động
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "proxy_app:app"]