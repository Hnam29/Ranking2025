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

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transform_download_value(download_text):
    """
    Chuyển đổi giá trị số lượt tải xuống
    Ví dụ: "1 N+" -> "1k", "1 TR+" -> "1M", "5 TRĂM+" -> "500"
    """
    if not download_text:
        return None
        
    download_text = download_text.upper()
    
    # Xử lý các trường hợp tiếng Việt
    if "N+" in download_text:
        # Trường hợp nghìn: "1 N+" -> "1k"
        number = re.search(r'(\d+[\.,]?\d*)', download_text)
        if number:
            return f"{number.group(1)}k"
    elif "TR+" in download_text or "TRIỆU+" in download_text:
        # Trường hợp triệu: "1 TR+" hoặc "1 TRIỆU+" -> "1M"
        number = re.search(r'(\d+[\.,]?\d*)', download_text)
        if number:
            return f"{number.group(1)}M"
    elif "TRĂM+" in download_text:
        # Trường hợp trăm: "5 TRĂM+" -> "500"
        number = re.search(r'(\d+)', download_text)
        if number:
            return str(int(number.group(1)) * 100)
    elif "TỶ+" in download_text:
        # Trường hợp tỷ: "1 TỶ+" -> "1B"
        number = re.search(r'(\d+[\.,]?\d*)', download_text)
        if number:
            return f"{number.group(1)}B"
            
    # Xử lý các trường hợp tiếng Anh
    if "K+" in download_text or "THOUSAND+" in download_text:
        # Trường hợp nghìn: "1K+" -> "1k"
        number = re.search(r'(\d+[\.,]?\d*)', download_text)
        if number:
            return f"{number.group(1)}k"
    elif "M+" in download_text or "MILLION+" in download_text:
        # Trường hợp triệu: "1M+" -> "1M"
        number = re.search(r'(\d+[\.,]?\d*)', download_text)
        if number:
            return f"{number.group(1)}M"
    elif "HUNDRED+" in download_text:
        # Trường hợp trăm: "5 HUNDRED+" -> "500"
        number = re.search(r'(\d+)', download_text)
        if number:
            return str(int(number.group(1)) * 100)
    elif "B+" in download_text or "BILLION+" in download_text:
        # Trường hợp tỷ: "1B+" -> "1B"
        number = re.search(r'(\d+[\.,]?\d*)', download_text)
        if number:
            return f"{number.group(1)}B"
    
    # Nếu chỉ là số không có đơn vị
    number_match = re.search(r'(\d+[\.,]?\d*)', download_text)
    if number_match:
        return number_match.group(1)
        
    # Trả về giá trị gốc nếu không thể chuyển đổi
    return download_text
    
def transform_rate_number(rate_number_text):
    """
    Chuyển đổi giá trị số lượng đánh giá
    Ví dụ: "21 star reviews" -> "21", "12,96k star reviews" -> "12,96k"
    """
    if not rate_number_text:
        return None
        
    # Tách số lượng đánh giá từ chuỗi
    # Tìm kiếm các số có dấu phân cách hàng nghìn và có thể có đơn vị k, M, B
    match = re.search(r'([\d,\.]+[kKmMbB]?)', rate_number_text)
    if match:
        return match.group(1)
    
    # Nếu không có đơn vị k, M, B, tìm kiếm chỉ số
    match = re.search(r'(\d[\d,\.]*)', rate_number_text)
    if match:
        return match.group(1)
        
    # Trả về giá trị gốc nếu không thể chuyển đổi
    return rate_number_text

def transform_rate(rate_text):
    """
    Chuyển đổi giá trị số sao
    Ví dụ: "3,6 \n star" -> "3,6"
    """
    if not rate_text:
        return None
        
    # Tìm kiếm phần số trong chuỗi (hỗ trợ dấu phẩy và dấu chấm)
    match = re.search(r'([\d,\.]+)', rate_text)
    if match:
        return match.group(1)
        
    # Trả về giá trị gốc nếu không thể chuyển đổi
    return rate_text

def is_star_rate(text):
    """
    Kiểm tra xem văn bản có phải là giá trị đánh giá sao hay không
    Ví dụ: "4,5" hoặc "4.7" hoặc "4,5 \n star" là giá trị đánh giá sao
    """
    if not text:
        return False
        
    # Kiểm tra xem văn bản có chứa số có dấu phẩy hoặc dấu chấm từ 0-5 không
    match = re.search(r'(^|\s)([0-5]([\.,]\d+)?)', text)
    
    # Kiểm tra xem văn bản có chứa từ "star" hoặc không phải là số download
    has_star = "star" in text.lower()
    not_download = not any(x in text.upper() for x in ["+", "K+", "M+", "B+", "N+", "TR+", "TỶ+", "HUNDRED+", "THOUSAND+", "MILLION+", "BILLION+"])
    
    return match is not None and (has_star or not_download)

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
        
        # TRƯỜNG HỢP ĐẶC BIỆT: Xử lý khi app chỉ có download number
        # Trích xuất phần tử ở vị trí STAR RATE để kiểm tra
        try:
            first_element_text = None

            # Try locating the first element
            try:
                first_element_text = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='yDmH0d']/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[1]/div[1]/div/div"))).text
            except Exception as e:
                pass  # If not found, move to the next XPath

            # Try locating the second element only if the first one is not found
            if not first_element_text:
                try:
                    first_element_text = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='yDmH0d']/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[1]/div[1]"))).text
                except Exception:
                    pass  # If not found, it remains None
            
            # Kiểm tra xem đây có phải là giá trị đánh giá sao hay không
            if is_star_rate(first_element_text):
                # TRƯỜNG HỢP BÌNH THƯỜNG: Có cả STAR RATE
                logger.info(f"Ứng dụng có đánh giá sao: {first_element_text}")
                
                # Chuyển đổi và lưu STAR RATE
                data['Rate'] = transform_rate(first_element_text)
                
                # Trích xuất DOWNLOAD
                try:
                    raw_download = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//*[@id='yDmH0d']/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[2]/div[1]")
                    )).text
                    
                    # Chuyển đổi giá trị Download
                    data['Download'] = transform_download_value(raw_download)
                    logger.debug(f"Đã trích xuất Download: {raw_download} -> {data['Download']}")
                except Exception as e:
                    logger.warning(f"Không thể trích xuất Download: {e}")
                    data['Download'] = None
                    
                # Trích xuất RATE NUMBER
                try:
                    raw_rate_number = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//*[@id='yDmH0d']/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[1]/div[2]")
                    )).text
                    
                    # Chuyển đổi giá trị Rate_Number
                    data['Rate_Number'] = transform_rate_number(raw_rate_number)
                    logger.debug(f"Đã trích xuất Rate_Number: {raw_rate_number} -> {data['Rate_Number']}")
                except Exception as e:
                    logger.warning(f"Không thể trích xuất Rate_Number: {e}")
                    data['Rate_Number'] = None
            else:
                # TRƯỜNG HỢP ĐẶC BIỆT: Không có STAR RATE, phần tử này chứa DOWNLOAD
                logger.info("Ứng dụng không có đánh giá sao, chỉ có lượt tải")
                
                # Đặt Rate và Rate_Number là None
                data['Rate'] = None
                data['Rate_Number'] = None
                
                # Lưu giá trị DOWNLOAD từ phần tử đầu tiên
                data['Download'] = transform_download_value(first_element_text)
                logger.debug(f"Đã trích xuất Download từ vị trí đặc biệt: {first_element_text} -> {data['Download']}")
                
        except Exception as e:
            logger.warning(f"Không thể trích xuất dữ liệu từ vị trí của Star Rate: {e}")
            data['Rate'] = None
            data['Download'] = None
            data['Rate_Number'] = None
            
    except Exception as e:
        logger.error(f"Lỗi khi xử lý URL {url}: {e}")
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
        download_col = headers.index('Download') + 1 if 'Download' in headers else None
        rate_number_col = headers.index('Rate_Number') + 1 if 'Rate_Number' in headers else None
        
        if rate_col is None or download_col is None or rate_number_col is None:
            logger.error("Không tìm thấy một hoặc nhiều cột yêu cầu trong bảng tính")
            return False
        
        # Tìm vị trí của liên kết trong bảng tính
        if app_data['App URL'] in all_links:
            row_idx = all_links.index(app_data['App URL']) + 2  # +2 vì chỉ mục bắt đầu từ 1 và có hàng tiêu đề
            
            # Cập nhật các ô riêng lẻ
            if app_data['Rate'] is not None:
                sheet.update_cell(row_idx, rate_col, app_data['Rate'])
            
            if app_data['Download'] is not None:
                sheet.update_cell(row_idx, download_col, app_data['Download'])
            
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