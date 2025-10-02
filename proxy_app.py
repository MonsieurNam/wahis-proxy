from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import time
import traceback

app = Flask(__name__)
WAHIS_API_URL = "https://wahis.woah.org/pi/getReportList"

def get_cloudflare_cookies():
    print("LOG: Bắt đầu quá trình lấy cookie Cloudflare với Selenium...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # === THAY ĐỔI CUỐI CÙNG NẰM Ở ĐÂY ===
    # Quay trở lại sử dụng webdriver.Remote.
    # Bây giờ nó sẽ hoạt động vì entrypoint.sh đã khởi động Selenium Server.
    print("LOG: Đang kết nối đến Selenium Server tại localhost:4444...")
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=chrome_options
    )
    print("LOG: Kết nối đến Selenium Server thành công.")

    try:
        print("LOG: Đang truy cập trang WAHIS...")
        driver.get("https://wahis.woah.org/#/home")
        print("LOG: Đang chờ Cloudflare...")
        time.sleep(10) 
        
        selenium_cookies = driver.get_cookies()
        requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        print("LOG: Đã lấy cookie thành công!")
        return requests_cookies
    finally:
        print("LOG: Đang đóng trình duyệt...")
        driver.quit()
        print("LOG: Đã đóng trình duyệt.")

# === PHẦN CÒN LẠI GIỮ NGUYÊN ===
@app.route('/get-wahis-reports', methods=['POST'])
def get_wahis_reports():
    print("LOG: Nhận được yêu cầu từ Voiceflow...")
    try:
        filters_from_voiceflow = request.get_json()
        payload_to_wahis = {
            "pageNumber": filters_from_voiceflow.get("pageNumber", 1) if filters_from_voiceflow else 1,
            "pageSize": filters_from_voiceflow.get("pageSize", 5) if filters_from_voiceflow else 5,
            "reportFilters": {
                "country": filters_from_voiceflow.get("country", []) if filters_from_voiceflow else [],
            }
        }
        
        cookies = get_cloudflare_cookies()
        
        headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }
        
        print("LOG: Đang gửi yêu cầu POST đến API WAHIS...")
        response_from_wahis = requests.post(
            WAHIS_API_URL, 
            json=payload_to_wahis, 
            headers=headers, 
            cookies=cookies,
            timeout=30
        )
        
        print(f"LOG: WAHIS API trả về mã trạng thái: {response_from_wahis.status_code}")
        if response_from_wahis.status_code == 200:
            return jsonify(response_from_wahis.json())
        else:
            return jsonify({
                "error": "Failed after getting cookies", 
                "status_code": response_from_wahis.status_code,
                "response_text": response_from_wahis.text
            }), 500
            
    except Exception as e:
        print(f"LOG: Lỗi nghiêm trọng xảy ra: {e}")
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)