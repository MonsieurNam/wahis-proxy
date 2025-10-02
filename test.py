from flask import Flask, request, jsonify
import cloudscraper

# === PHẦN 1: KHỞI TẠO VÀ CẤU HÌNH ===

# Khởi tạo một ứng dụng web bằng Flask
app = Flask(__name__)

# URL của API WAHIS mà chúng ta muốn gọi
WAHIS_API_URL = "https://wahis.woah.org/pi/getReportList"

# Tạo một "scraper". Đây là một đối tượng đặc biệt từ thư viện cloudscraper
# có khả năng hoạt động như một trình duyệt thật để vượt qua Cloudflare.
scraper = cloudscraper.create_scraper()

# === PHẦN 2: ĐỊNH NGHĨA API ENDPOINT ===

# Dòng @app.route(...) định nghĩa một "địa chỉ" cho API của chúng ta.
# Voiceflow sẽ gửi yêu cầu đến địa chỉ này.
# methods=['POST'] có nghĩa là endpoint này chỉ chấp nhận yêu cầu POST.
@app.route('/get-wahis-reports', methods=['POST'])
def get_wahis_reports():
    """
    Hàm này sẽ được thực thi mỗi khi có một yêu cầu POST đến
    địa chỉ '/get-wahis-reports'.
    """
    print("LOG: Nhận được yêu cầu...")
    
    # Lấy dữ liệu JSON mà Voiceflow gửi đến trong phần body của yêu cầu
    filters_from_voiceflow = request.get_json()

    # Xây dựng payload cuối cùng để gửi đến WAHIS.
    # Chúng ta bắt đầu với một payload mặc định...
    payload_to_wahis = {
        "pageNumber": 1,
        "pageSize": 5,
        "searchText": "",
        "sortColName": "reportDate",
        "sortColOrder": "DESC",
        "reportFilters": {
            "country": [],
            "region": [],
            "diseases": [],
            "reportDate": {
                "startDate": "2005-01-01",
                "endDate": "2025-12-31"
            }
        }
    }
    
    # ...và cập nhật nó với các bộ lọc nhận được từ Voiceflow (nếu có)
    if filters_from_voiceflow:
        payload_to_wahis["pageSize"] = filters_from_voiceflow.get("pageSize", 5)
        payload_to_wahis["reportFilters"]["country"] = filters_from_voiceflow.get("country", [])
        payload_to_wahis["reportFilters"]["region"] = filters_from_voiceflow.get("region", [])
        payload_to_wahis["reportFilters"]["diseases"] = filters_from_voiceflow.get("disease", [])
        if filters_from_voiceflow.get("reportDate"):
            payload_to_wahis["reportFilters"]["reportDate"] = filters_from_voiceflow.get("reportDate")

    print(f"LOG: Payload sẽ gửi đến WAHIS: {payload_to_wahis}")

    try:
        # Dùng scraper.post thay vì requests.post. Đây là điểm mấu chốt!
        # scraper sẽ tự động xử lý các thử thách của Cloudflare.
        response_from_wahis = scraper.post(WAHIS_API_URL, json=payload_to_wahis)
        
        print(f"LOG: WAHIS API trả về mã trạng thái: {response_from_wahis.status_code}")

        # Nếu WAHIS trả về thành công (mã 200),
        # chúng ta sẽ trả dữ liệu JSON đó về lại cho Voiceflow.
        if response_from_wahis.status_code == 200:
            return jsonify(response_from_wahis.json())
        # Ngược lại, trả về một thông báo lỗi
        else:
            error_message = {
                "error": "Failed to fetch data from WAHIS", 
                "status_code": response_from_wahis.status_code,
                "response_text": response_from_wahis.text
            }
            return jsonify(error_message), 500

    except Exception as e:
        print(f"LOG: Lỗi nghiêm trọng xảy ra: {e}")
        return jsonify({"error": str(e)}), 500

# === PHẦN 3: KHỞI CHẠY SERVER (chỉ khi chạy trực tiếp file này) ===
if __name__ == '__main__':
    # Chạy ứng dụng trên cổng 5001 để thử nghiệm trên máy tính local
    app.run(host='0.0.0.0', port=5001, debug=True)
