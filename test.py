from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# webdriver-manager không còn cần thiết nữa vì chúng ta đã có Chrome trong Docker
# from webdriver_manager.chrome import ChromeDriverManager 
import requests
import json
import time
import os # Import thư viện os

# === PHẦN 1: KHỞI TẠO VÀ CẤU HÌNH ===
app = Flask(__name__)
WAHIS_API_URL = "https://wahis.woah.org/pi/getReportList"

def get_cloudflare_cookies():
    print("LOG: Bắt đầu quá trình lấy cookie Cloudflare với Selenium...")
    chrome_options = Options()
    
    # === THAY ĐỔI QUAN TRỌNG NẰM Ở ĐÂY ===
    # Chỉ định rõ ràng đường dẫn đến file thực thi của Chrome
    # Đây là đường dẫn chuẩn sau khi cài đặt google-chrome-stable trên Debian/Ubuntu
    chrome_options.binary_location = "/usr/bin/google-chrome-stable" 
    
    # Các tùy chọn cần thiết để chạy trên môi trường server
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # Chúng ta không cần ChromeDriverManager nữa vì Chrome đã được cài sẵn trong Docker
    # service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://wahis.woah.org/#/home")
        time.sleep(10) 
        
        selenium_cookies = driver.get_cookies()
        requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        print("LOG: Đã lấy cookie thành công!")
        return requests_cookies
    finally:
        driver.quit()

# === PHẦN 2: ĐỊNH NGHĨA API ENDPOINT (Giữ nguyên) ===
@app.route('/get-wahis-reports', methods=['POST'])
def get_wahis_reports():
    # ... (Toàn bộ logic của hàm này giữ nguyên, không cần thay đổi) ...
    print("LOG: Nhận được yêu cầu từ Voiceflow...")
    filters_from_voiceflow = request.get_json()

    payload_to_wahis = {
        "pageNumber": filters_from_voiceflow.get("pageNumber", 1) if filters_from_voiceflow else 1,
        "pageSize": filters_from_voiceflow.get("pageSize", 5) if filters_from_voiceflow else 5,
        "reportFilters": {
            "country": filters_from_voiceflow.get("country", []) if filters_from_voiceflow else [],
        }
    }

    try:
        cookies = get_cloudflare_cookies()
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }
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
        # Trả về lỗi chi tiết hơn để dễ gỡ lỗi
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# === PHẦN 3: KHỞI CHẠY SERVER (Giữ nguyên) ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)