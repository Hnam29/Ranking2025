import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import time
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'

try:
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    logger.info("Google Sheets API được khởi tạo thành công")
except Exception as e:
    logger.error(f"Lỗi khi khởi tạo Google Sheets API: {e}")
    raise

# Define spreadsheet and sheet
SPREADSHEET_ID = "15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8"
SHEET_NAME = "Blank sheet for test"

try:
    worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    logger.info(f"Đã kết nối thành công đến sheet '{SHEET_NAME}'")
except Exception as e:
    logger.error(f"Lỗi khi mở Google Sheet: {e}")
    raise

# Load Excel data
EXCEL_FILE = "/Users/vuhainam/Downloads/google_play_apps_details.xlsx"
try:
    df_excel = pd.read_excel(EXCEL_FILE)
    logger.info(f"Đã đọc thành công tệp Excel từ {EXCEL_FILE}")
    logger.info(f"Các cột trong dữ liệu Excel: {df_excel.columns.tolist()}")
except Exception as e:
    logger.error(f"Lỗi khi đọc tệp Excel: {e}")
    raise

# Đọc dữ liệu từ Google Sheets
try:
    sheet_data = worksheet.get_all_values()
    headers = sheet_data[0]  # Dòng đầu tiên là tiêu đề
    data = sheet_data[1:]    # Phần còn lại là dữ liệu
    logger.info(f"Đã đọc dữ liệu từ Google Sheets: {len(data)} dòng")
    logger.info(f"Các cột trong Google Sheets: {headers}")
except Exception as e:
    logger.error(f"Lỗi khi đọc dữ liệu từ Google Sheets: {e}")
    raise

# Tìm vị trí cột 'URL-ANDROID' trong Google Sheets
url_android_col = None
for i, header in enumerate(headers):
    if header.strip() == 'URL-ANDROID':
        url_android_col = i
        logger.info(f"Tìm thấy cột 'URL-ANDROID' tại vị trí {url_android_col}")
        break

if url_android_col is None:
    logger.error("Không tìm thấy cột 'URL-ANDROID' trong Google Sheets")
    raise ValueError("Không tìm thấy cột 'URL-ANDROID' trong Google Sheets")

# Chuẩn bị dữ liệu từ Excel cho việc tìm kiếm theo URL
# Kiểm tra xem có cột URL tương ứng trong Excel không
url_column_in_excel = None
for col in df_excel.columns:
    if 'url' in col.lower() or 'android' in col.lower():
        url_column_in_excel = col
        logger.info(f"Sử dụng cột '{url_column_in_excel}' từ Excel để tìm kiếm URL")
        break

if url_column_in_excel is None:
    # Nếu không có cột URL, thử sử dụng cột đầu tiên
    url_column_in_excel = df_excel.columns[0]
    logger.warning(f"Không tìm thấy cột URL trong Excel, sử dụng cột đầu tiên '{url_column_in_excel}' để tìm kiếm")

# Kiểm tra có dữ liệu không trống trong cột URL
if df_excel[url_column_in_excel].isna().all():
    logger.error(f"Cột '{url_column_in_excel}' trong Excel không có dữ liệu")
    raise ValueError(f"Cột '{url_column_in_excel}' trong Excel không có dữ liệu")

# Chuyển đổi DataFrame Excel thành dictionary với khóa là giá trị URL
excel_dict = {}
for _, row in df_excel.iterrows():
    key = str(row[url_column_in_excel]).strip()
    if key and not (isinstance(key, float) and (np.isnan(key) or np.isinf(key))):
        excel_dict[key] = row.to_dict()

logger.info(f"Đã tạo dictionary từ dữ liệu Excel với {len(excel_dict)} mục")

# Xác định các cột cần cập nhật
excel_columns = df_excel.columns.tolist()
logger.info(f"Các cột có sẵn trong Excel: {excel_columns}")

# Tạo ánh xạ từ cột Excel sang vị trí cột trong Google Sheets
column_mapping = {}
for excel_col in excel_columns:
    for i, sheet_col in enumerate(headers):
        # So sánh không phân biệt chữ hoa/thường và bỏ khoảng trắng
        if excel_col.strip().lower() == sheet_col.strip().lower():
            column_mapping[excel_col] = i
            logger.info(f"Ánh xạ cột Excel '{excel_col}' sang cột Google Sheets '{sheet_col}' (vị trí {i})")
            break

logger.info(f"Tìm thấy {len(column_mapping)} cột khớp giữa Excel và Google Sheets")

# Cập nhật dữ liệu
updated_rows = []
update_count = 0
not_found_count = 0
urls_not_found = []

for row_idx, row in enumerate(data):
    url_android = row[url_android_col].strip() if url_android_col < len(row) else ""
    updated_row = row.copy()  # Tạo bản sao của dòng hiện tại
    
    if url_android and url_android in excel_dict:
        # Nếu tìm thấy URL trong Excel
        excel_row_data = excel_dict[url_android]
        update_count += 1
        
        # Cập nhật từng cột dựa trên ánh xạ
        for excel_col, excel_value in excel_row_data.items():
            # Chuyển đổi giá trị NaN hoặc None thành chuỗi rỗng
            if isinstance(excel_value, float) and (np.isnan(excel_value) or np.isinf(excel_value)):
                excel_value = ""
            
            # Nếu cột tồn tại trong ánh xạ, cập nhật vào đúng vị trí
            if excel_col in column_mapping:
                sheet_col_idx = column_mapping[excel_col]
                updated_row[sheet_col_idx] = excel_value
        
        logger.debug(f"Đã cập nhật dòng {row_idx+2} với URL: {url_android}")
    else:
        if url_android:  # Chỉ ghi log nếu URL không trống
            not_found_count += 1
            urls_not_found.append(url_android)
    
    updated_rows.append(updated_row)

# Ghi log URL không tìm thấy (giới hạn số lượng để tránh log quá dài)
if urls_not_found:
    sample_not_found = urls_not_found[:5]
    logger.info(f"Mẫu URL không tìm thấy: {sample_not_found}")
    if len(urls_not_found) > 5:
        logger.info(f"...và {len(urls_not_found) - 5} URL khác")

logger.info(f"Đã cập nhật {update_count} dòng, {not_found_count} URL không tìm thấy trong dữ liệu Excel")

# Kiểm tra xem có dữ liệu nào được cập nhật không
if update_count == 0:
    logger.warning("Không có dữ liệu nào được cập nhật. Kiểm tra lại dữ liệu đầu vào!")
    # In ra một vài URL từ Google Sheets để debug
    sample_urls = [row[url_android_col] for row in data[:5] if url_android_col < len(row)]
    logger.info(f"Mẫu URLs từ Google Sheets: {sample_urls}")
    # In ra một vài khóa từ dictionary Excel
    sample_excel_keys = list(excel_dict.keys())[:5]
    logger.info(f"Mẫu khóa từ Excel: {sample_excel_keys}")

# Cập nhật Google Sheets
try:
    # Thêm debug trước khi cập nhật
    logger.info(f"Chuẩn bị cập nhật {len(updated_rows)} dòng vào Google Sheets")
    
    batch_size = 1000  # Giới hạn số dòng cập nhật mỗi lần để tránh vượt quá giới hạn API
    for i in range(0, len(updated_rows), batch_size):
        batch = updated_rows[i:i+batch_size]
        worksheet.update([headers] + batch, value_input_option='RAW')
        
        # Thêm độ trễ để tránh giới hạn tốc độ API
        if i + batch_size < len(updated_rows):
            logger.info(f"Đã cập nhật batch {i//batch_size + 1}, nghỉ 1 giây...")
            time.sleep(1)
    
    logger.info("Cập nhật Google Sheet thành công!")
except Exception as e:
    logger.error(f"Lỗi khi cập nhật Google Sheet: {e}")
    raise