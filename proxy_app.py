from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import traceback
from datetime import datetime

app = Flask(__name__)
WAHIS_API_URL = "https://wahis.woah.org/pi/getReportList"

# --- HÀM HELPER ĐỂ ĐỊNH DẠNG DỮ LIỆU ---
def format_events_to_markdown(events_json):
    if not events_json or 'homePageDto' not in events_json or not events_json['homePageDto']:
        return "No new events found at this time. What are you looking for?"

    event_list = events_json['homePageDto']
    output_text = "Here are the latest updates from WAHIS:\n\n"
    max_events = min(len(event_list), 3)

    for i in range(max_events):
        event = event_list[i]
        
        disease = event.get('disease', 'N/A')
        country = event.get('country', 'N/A')
        reason = event.get('reason', 'N/A')
        
        # Định dạng ngày tháng
        report_date_str = 'N/A'
        if event.get('reportDate'):
            try:
                # Chuyển chuỗi ISO 8601 sang đối tượng datetime, rồi định dạng lại
                dt_object = datetime.fromisoformat(event['reportDate'].replace('Z', '+00:00'))
                report_date_str = dt_object.strftime('%Y/%m/%d')
            except (ValueError, TypeError):
                report_date_str = event['reportDate'][:10] # Fallback

        card = (
            f"---\n"
            f"**Disease:** {disease}\n"
            f"*   **Country:** {country}\n"
            f"*   **Report Date:** {report_date_str}\n"
            f"*   **Reason:** {reason}\n\n"
        )
        output_text += card
    
    output_text += "What specific information can I help you find today?"
    return output_text

# --- HÀM LẤY COOKIE (Giữ nguyên) ---
def get_cloudflare_cookies():
    # ... (Giữ nguyên toàn bộ code của hàm này, không thay đổi)
    print("LOG: Bắt đầu quá trình lấy cookie Cloudflare với Selenium...")
    # ...
    # return requests_cookies

# --- API ENDPOINT ĐÃ ĐƯỢC NÂNG CẤP ---
@app.route('/get-wahis-summary', methods=['POST'])
def get_wahis_summary():
    print("LOG: Nhận được yêu cầu tóm tắt...")
    try:
        # Lấy payload từ Voiceflow (nếu có)
        filters = request.get_json() or {}
        
        payload_to_wahis = {
            "pageNumber": 1,
            "pageSize": filters.get("pageSize", 5),
            "reportFilters": {
                "country": filters.get("country", []),
            },
            # ... (thêm các bộ lọc khác nếu cần)
            "sortColName": "reportDate",
            "sortColOrder": "DESC"
        }

        # Lấy cookie và gọi API WAHIS (logic này giữ nguyên)
        # cookies = get_cloudflare_cookies()
        headers = { 'User-Agent': 'Mozilla/5.0 ...' } # Giữ nguyên header
        # response_from_wahis = requests.post(WAHIS_API_URL, json=payload_to_wahis, headers=headers, cookies=cookies)
        
        # --- BỎ QUA SELENIUM ĐỂ TEST NHANH ---
        # Đây là dữ liệu giả để test, hãy thay thế bằng code gọi API thật
        # response_from_wahis = requests.post(...)
        # wahis_json = response_from_wahis.json()
        
        # Thay vì trả về JSON thô, chúng ta sẽ định dạng nó
        # formatted_text = format_events_to_markdown(wahis_json)
        
        # --- MOCK RESPONSE ĐỂ TEST ---
        # Giả lập dữ liệu trả về từ WAHIS để test
        mock_wahis_json = {"homePageDto": [{"disease": "Test Disease", "country": "Test Country", "reportDate": "2025-10-02T10:00:00Z", "reason": "Test Reason"}]}
        formatted_text = format_events_to_markdown(mock_wahis_json)

        # Trả về một đối tượng JSON chứa chuỗi đã định dạng
        return jsonify({"summary_text": formatted_text})

    except Exception as e:
        print(f"LOG: Lỗi nghiêm trọng: {e}")
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# Endpoint kiểm tra sức khỏe (giữ nguyên)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Khởi chạy server (giữ nguyên)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)