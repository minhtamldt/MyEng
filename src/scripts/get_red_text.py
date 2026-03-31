import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ==========================================
# CẤU HÌNH THÔNG TIN TẠI ĐÂY
# ==========================================
# 1. Tên file key bạn tải về từ Google Cloud Console
# (Code tự động tìm file này trong cùng thư mục với script)
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

# 2. Bạn hãy copy ID của Google Sheet từ URL (đoạn giữa /d/ và /edit)
# Ví dụ: https://docs.google.com/spreadsheets/d/abc123xyz/edit -> ID là 'abc123xyz'
SPREADSHEET_ID = '' 

# 3. Vùng dữ liệu bạn muốn quét (TênSheet!Vùng)
RANGE_NAME = '19-01!A1:K1434' 

def is_red(color_obj):
    """
    Kiểm tra nếu màu là đỏ. 
    Google Sheets trả về RGB dưới dạng số thực từ 0 đến 1.
    (1, 0, 0) là đỏ chuẩn #ff0000.
    """
    if not color_obj:
        return False
    
    red = color_obj.get('red', 0)
    green = color_obj.get('green', 0)
    blue = color_obj.get('blue', 0)
    
    # Logic nhận diện màu đỏ: Thành phần đỏ chiếm ưu thế tuyệt đối
    return red > 0.8 and green < 0.2 and blue < 0.2

def main():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ LỖI: Không tìm thấy file '{SERVICE_ACCOUNT_FILE}' trong thư mục này.")
        print("Hãy làm theo hướng dẫn trên Google Cloud Console để tải file JSON về.")
        return

    try:
        # Xác thực với Google
        print("🔄 Đang kết nối tới Google API...")
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=creds)

        # Lấy dữ liệu kèm theo định dạng (includeGridData=True)
        print(f"🔍 Đang quét vùng {RANGE_NAME} để tìm chữ màu đỏ...")
        request = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID,
            ranges=[RANGE_NAME],
            includeGridData=True
        )
        response = request.execute()

        sheet_data = response.get('sheets', [])[0]
        data = sheet_data.get('data', [])[0]
        row_data = data.get('rowData', [])

        red_texts = []

        # Duyệt qua từng hàng
        for r_idx, row in enumerate(row_data):
            values = row.get('values', [])
            # Duyệt qua từng ô trong hàng
            for c_idx, cell in enumerate(values):
                cell_text = cell.get('effectiveValue', {}).get('stringValue', '')
                if not cell_text: 
                    continue

                # 1. TRƯỜNG HỢP: Cả ô có màu đỏ (Định dạng chung của ô)
                effective_format = cell.get('effectiveFormat', {})
                text_format = effective_format.get('textFormat', {})
                foreground_color = text_format.get('foregroundColor', {})
                
                if is_red(foreground_color):
                    red_texts.append({
                        "pos": f"Ô {chr(65+c_idx)}{r_idx+1}", 
                        "text": cell_text
                    })
                else:
                    # 2. TRƯỜNG HỢP: Chỉ một vài từ trong ô có màu đỏ (Rich Text)
                    text_format_runs = cell.get('textFormatRuns', [])
                    if text_format_runs:
                        for i in range(len(text_format_runs)):
                            run = text_format_runs[i]
                            run_format = run.get('format', {}).get('foregroundColor', {})
                            
                            if is_red(run_format):
                                start_idx = run.get('startIndex', 0)
                                # Lấy index kết thúc (là điểm bắt đầu của run tiếp theo hoặc cuối chuỗi)
                                if i + 1 < len(text_format_runs):
                                    end_idx = text_format_runs[i+1].get('startIndex', len(cell_text))
                                else:
                                    end_idx = len(cell_text)
                                
                                part_text = cell_text[start_idx:end_idx].strip()
                                if part_text:
                                    red_texts.append({
                                        "pos": f"Ô {chr(65+c_idx)}{r_idx+1} (Dòng {i+1})",
                                        "text": part_text
                                    })

        # HIỂN THỊ KẾT QUẢ
        print("\n" + "="*40)
        if not red_texts:
            print("📭 Không tìm thấy từ nào màu đỏ cả!")
        else:
            # 1. Lọc trùng lặp từ vựng (Unique words only)
            unique_words = {}
            for item in red_texts:
                word = item['text'].lower().strip()
                if word not in unique_words:
                    unique_words[word] = item['pos']

            print(f"✅ ĐÃ TÌM THẤY {len(red_texts)} ĐOẠN CHỮ ĐỎ (Trong đó có {len(unique_words)} từ duy nhất):")
            
            print("\n--- DANH SÁCH TỪ VỰNG ĐÃ LỌC TRÙNG ---")
            for idx, (word, pos) in enumerate(unique_words.items(), 1):
                print(f"{idx}. {word.capitalize()} (Xuất hiện đầu tiên tại: {pos})")

            # Nếu bạn muốn xem lại full danh sách chi tiết (tùy chọn)
            # print("\n--- CHI TIẾT VỊ TRÍ ---")
            # for item in red_texts:
            #     print(f"📍 {item['pos']}: {item['text']}")
            
        print("="*40 + "\n")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {str(e)}")
        if "404" in str(e):
            print("Lưu ý: Hãy kiểm tra lại SPREADSHEET_ID của bạn có đúng không.")
        elif "403" in str(e):
            print("Lưu ý: Hãy kiểm tra xem bạn đã Share file Sheet cho email của Service Account chưa.")

if __name__ == '__main__':
    main()
