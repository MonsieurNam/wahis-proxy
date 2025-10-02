from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests # Chúng ta sẽ dùng lại requests, nhưng với cookie từ Selenium
import json
import time

# === PHẦN 1: KHỞI TẠO VÀ CẤU HÌNH ===
app = Flask(__name__)
WAHIS_API_URL = "https://wahis.woah.org/pi/getReportList"

def get_cloudflare_cookies():
    """
    Sử dụng Selenium để khởi động một trình duyệt ảo, truy cập WAHIS,
    và lấy về các cookie hợp lệ sau khi vượt qua thử thách của Cloudflare.
    """
    print("LOG: Bắt đầu quá trình lấy cookie Cloudflare với Selenium...")
    chrome_options = Options()
    # Chạy ở chế độ headless (không có giao diện người dùng)
    chrome_options.add_argument("--headless")
    # Các tùy chọn cần thiết để chạy trên môi trường server Linux (như Render)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Tự động cài đặt và quản lý ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Truy cập một trang bất kỳ trên WAHIS để kích hoạt Cloudflare
        driver.get("https://wahis.woah.org/#/home")
        
        # Đợi một chút để Cloudflare thực hiện các kiểm tra JavaScript
        # Có thể cần tăng thời gian này nếu mạng chậm
        time.sleep(10) 
        
        # Lấy tất cả cookie mà trình duyệt đã nhận được
        selenium_cookies = driver.get_cookies()
        
        # Chuyển đổi cookie sang định dạng mà thư viện 'requests' có thể hiểu
        requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        print("LOG: Đã lấy cookie thành công!")
        return requests_cookies
    finally:
        # Luôn đóng trình duyệt sau khi hoàn tất
        driver.quit()

# === PHẦN 2: ĐỊNH NGHĨA API ENDPOINT ===
@app.route('/get-wahis-reports', methods=['POST'])
def get_wahis_reports():
    print("LOG: Nhận được yêu cầu từ Voiceflow...")
    filters_from_voiceflow = request.get_json()

    payload_to_wahis = {
        # ... (Phần payload giữ nguyên như cũ) ...
        "pageNumber": filters_from_voiceflow.get("pageNumber", 1) if filters_from_voiceflow else 1,
        "pageSize": filters_from_voiceflow.get("pageSize", 5) if filters_from_voiceflow else 5,
        "reportFilters": {
            "country": filters_from_voiceflow.get("country", []) if filters_from_voiceflow else [],
            # ... thêm các bộ lọc khác nếu cần ...
        }
    }

    try:
        # BƯỚC QUAN TRỌNG: Lấy cookie mới cho mỗi lần yêu cầu
        cookies = get_cloudflare_cookies()
        
        # Headers bây giờ sẽ không cần nhiều thứ như trước
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Gửi yêu cầu POST bằng thư viện 'requests' thông thường,
        # nhưng lần này chúng ta gửi kèm theo cookie đã lấy được
        response_from_wahis = requests.post(WAHIS_API_URL, json=payload_to_wahis, headers=headers, cookies=cookies)
        
        print(f"LOG: WAHIS API trả về mã trạng thái: {response_from_wahis.status_code}")

        if response_from_wahis.status_code == 200:
            return jsonify(response_from_wahis.json())
        else:
            return jsonify({
                "error": "Failed to fetch data from WAHIS, even with Selenium", 
                "status_code": response_from_wahis.status_code,
                "response_text": response_from_wahis.text
            }), 500

    except Exception as e:
        print(f"LOG: Lỗi nghiêm trọng xảy ra: {e}")
        return jsonify({"error": str(e)}), 500

# === PHẦN 3: KHỞI CHẠY SERVER ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)