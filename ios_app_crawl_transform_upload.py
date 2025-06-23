import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    
def transform_data(text):
    """
    Phân tích chuỗi văn bản để trích xuất Rate_Number và Rate + đồng thời chuẩn hóa định dạng đầu ra.
    
    Ví dụ: 
        "4.5 • 1.2K"     -> ("1,2k", "4,5")
        "4,5 • 1,2N"     -> ("1,2k", "4,5") 
        "4.5 • 1.2Tr"    -> ("1,2M", "4,5")
        "4,5 • 1,2 triệu" -> ("1,2M", "4,5")
    """
    if not text:
        return None, None
    
    # Xử lý ký tự phân tách giữa Rating và Rate_Number
    separators = ['•', '·', '|', '-', '\\s{2,}']
    separator_pattern = '|'.join(separators)
    
    # Pattern cơ bản để nhận diện định dạng
    pattern = r'([\d.,]+)\s*(?:' + separator_pattern + r')\s*([\d.,]+\s*[KkMmBbNnTt][RrIiÌiỶỷEeĂăMmUuỆệNn]*\+*|[\d.,]+)'
    
    match = re.search(pattern, text)
    if match:
        rating = match.group(1)
        rate_number = match.group(2)
    else:
        # Thử pattern ngược lại (Rate_Number đứng trước Rating)
        pattern_reverse = r'([\d.,]+\s*[KkMmBbNnTt][RrIiÌiỶỷEeĂăMmUuỆệNn]*\+*|[\d.,]+)\s*(?:' + separator_pattern + r')\s*([\d.,]+)'
        
        match_reverse = re.search(pattern_reverse, text)
        if match_reverse:
            rate_number = match_reverse.group(1)
            rating = match_reverse.group(2)
        else:
            return None, None
    
    # Chuẩn hóa Rating (thay dấu "." bằng ",")
    if rating:
        rating = rating.replace('.', ',')
    
    # Chuẩn hóa Rate_Number
    if rate_number:
        # Tách số và đơn vị
        number_match = re.match(r'([\d.,]+)\s*([KkMmBbNnTt][RrIiÌiỶỷEeĂăMmUuỆệNn]*\+*)?', rate_number)
        if number_match:
            number_part = number_match.group(1).replace('.', ',')
            unit_part = number_match.group(2).upper() if number_match.group(2) else ""
            
            # Chuẩn hóa đơn vị
            if unit_part in ["K", "K+", "THOUSAND", "THOUSAND+", "N", "N+", "NGHÌN", "NGHÌN+"]:
                unit = "k"
            elif unit_part in ["M", "M+", "MILLION", "MILLION+", "TR", "TR+", "TRIỆU", "TRIỆU+"]:
                unit = "M"
            elif unit_part in ["B", "B+", "BILLION", "BILLION+", "TỶ", "TỶ+"]:
                unit = "B"
            else:
                unit = ""
            
            # Kết hợp số và đơn vị
            rate_number = number_part + unit
    
    return rate_number, rating

# Cấu hình Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
SPREADSHEET_ID = "15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8"
SHEET_NAME = "Auto_Crawl_App"

def setup_google_sheets():
    """Thiết lập kết nối với Google Sheets API"""
    try:
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        logger.info("Kết nối Google Sheets API thành công")
        return sheet
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập Google Sheets API: {e}")
        raise

def setup_webdriver():
    """Thiết lập trình duyệt Selenium WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        logger.info("WebDriver được thiết lập thành công")
        return driver, wait
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập WebDriver: {e}")
        raise

def extract_app_info(driver, url, wait):
    """Trích xuất thông tin ứng dụng từ Google Play Store"""
    data = {}
    data['App URL'] = url  # Lưu URL làm khóa duy nhất
    
    try:
        # Mở trang ứng dụng
        driver.get(url)
        logger.info(f"Đang truy cập: {url}")
        
        try:
            # # Trích xuất dữ liệu thô
            # raw_text = wait.until(EC.presence_of_element_located(
            #     (By.XPATH, "/html/body/div[3]/main/div[2]/section[1]/div/div[2]/header/ul[1]/li/ul/li/figure/figcaption")
            # )).text
            # Thử XPath tương đối thay vì tuyệt đối
            raw_text = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "figure figcaption")
            )).text
            
            logger.info(f"Dữ liệu thô: {raw_text}")
            
            # Chuyển đổi dữ liệu thô thành Rate_Number và Rate
            rate_number, rate = transform_data(raw_text)
            
            # Gán các giá trị đã chuyển đổi
            data['Rate_Number'] = rate_number
            data['Rate'] = rate
            
            logger.info(f"Đã phân tích: Rate_Number={rate_number}, Rate={rate}")
                
        except Exception as e:
            # In ra lỗi chi tiết để debug
            import traceback
            logger.warning(f"Không thể trích xuất dữ liệu: {str(e)}")
            logger.warning(traceback.format_exc())
            data['Rate'] = None
            data['Rate_Number'] = None
            
    except Exception as e:
        logger.error(f"Lỗi khi xử lý URL {url}: {str(e)}")
        return None
        
    return data

def update_google_sheet(sheet, app_data):
    """Cập nhật dữ liệu vào Google Sheet dựa trên khóa 'App URL'"""
    try:
        # Lấy tất cả dữ liệu từ bảng tính
        all_data = sheet.get_all_records()
        
        # Lấy tất cả liên kết từ bảng tính
        all_links = sheet.col_values(1)[1:]  # Bỏ qua tiêu đề
        
        # Lấy tiêu đề cột
        headers = sheet.row_values(1)
        
        # Tìm chỉ số cột cho các trường cần cập nhật
        rate_col = headers.index('Rate') + 1 if 'Rate' in headers else None
        rate_number_col = headers.index('Rate_Number') + 1 if 'Rate_Number' in headers else None
        
        if rate_col is None or rate_number_col is None:
            logger.error("Không tìm thấy một hoặc nhiều cột yêu cầu trong bảng tính")
            return False
        
        # Tìm vị trí của liên kết trong bảng tính
        if app_data['App URL'] in all_links:
            row_idx = all_links.index(app_data['App URL']) + 2  # +2 vì chỉ mục bắt đầu từ 1 và có hàng tiêu đề
            
            # Cập nhật các ô riêng lẻ
            if app_data['Rate'] is not None:
                sheet.update_cell(row_idx, rate_col, app_data['Rate'])
            
            if app_data['Rate_Number'] is not None:
                sheet.update_cell(row_idx, rate_number_col, app_data['Rate_Number'])
                
            logger.info(f"Đã cập nhật dữ liệu cho {app_data['App URL']}")
            return True
        else:
            logger.warning(f"Không tìm thấy liên kết {app_data['App URL']} trong bảng tính")
            return False
            
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật Google Sheet: {e}")
        return False

def main():
    """Hàm chính để điều phối quá trình scraping và cập nhật dữ liệu"""
    try:
        # Thiết lập Google Sheets
        sheet = setup_google_sheets()
        
        # Thiết lập WebDriver
        driver, wait = setup_webdriver()
        
        # Đọc danh sách liên kết từ Google Sheet
        all_data = sheet.get_all_records()
        app_links = [row['App URL'] for row in all_data if 'App URL' in row and row['App URL']]
        logger.info(f"Đã đọc {len(app_links)} liên kết từ Google Sheet")
        
        # Đếm số lượng cập nhật thành công
        success_count = 0
        
        # Xử lý từng liên kết
        for url in app_links:
            try:
                # Trích xuất thông tin ứng dụng
                app_data = extract_app_info(driver, url, wait)
                
                if app_data:
                    # Cập nhật dữ liệu vào Google Sheet
                    if update_google_sheet(sheet, app_data):
                        success_count += 1
                    
                    # Tạm dừng để tránh bị chặn
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Lỗi khi xử lý {url}: {e}")
                continue
                
        logger.info(f"Đã cập nhật thành công {success_count}/{len(app_links)} ứng dụng")
        
    except Exception as e:
        logger.error(f"Lỗi trong quá trình xử lý: {e}")
    finally:
        # Đóng WebDriver
        if 'driver' in locals():
            driver.quit()
            logger.info("WebDriver đã đóng")

if __name__ == "__main__":
    main()