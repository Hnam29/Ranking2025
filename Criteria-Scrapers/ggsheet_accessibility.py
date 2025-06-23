import asyncio
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from playwright.async_api import Page, BrowserContext
import re
import logging
from datetime import datetime
import time
from requests.exceptions import ConnectionError

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"accessibility_checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """
    Kiểm tra xem một chuỗi có phải là URL hợp lệ hay không.
    """
    if not isinstance(url, str):
        return False
    
    url = url.strip()
    if not url:
        return False
    
    # Kiểm tra URL có bắt đầu bằng http:// hoặc https:// không
    if not (url.startswith('http://') or url.startswith('https://')):
        # Thêm https:// nếu không có
        url = 'https://' + url
    
    # Regex mẫu cho URL hợp lệ
    pattern = re.compile(
        r'^(?:http|https)://'  # http:// hoặc https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # tên miền
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # hoặc địa chỉ IP
        r'(?::\d+)?'  # cổng tùy chọn
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(pattern.match(url))

def normalize_url(url):
    """
    Chuẩn hóa URL để đảm bảo nó có định dạng hợp lệ.
    """
    url = url.strip()
    
    # Thêm https:// nếu URL không bắt đầu bằng http:// hoặc https://
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
        
    return url

async def process_urls_from_google_sheet(df, url_column):
    """
    Xử lý các URL từ DataFrame và trả về kết quả đánh giá khả năng truy cập.
    Chỉ xử lý các URL hợp lệ.
    """
    # Lọc DataFrame chỉ giữ lại các hàng có URL hợp lệ
    valid_urls_mask = df[url_column].apply(lambda x: is_valid_url(x) if isinstance(x, str) else False)
    valid_df = df[valid_urls_mask].copy()
    
    logger.info(f"Tìm thấy {len(valid_df)}/{len(df)} URL hợp lệ để xử lý")
    
    # Chuẩn hóa tất cả URL
    valid_df[url_column] = valid_df[url_column].apply(normalize_url)
    
    # Nếu không có URL hợp lệ nào, trả về danh sách kết quả trống
    if len(valid_df) == 0:
        logger.warning("Không tìm thấy URL hợp lệ nào để xử lý")
        return []
    
    # Cấu hình trình duyệt
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )
    
    # Định nghĩa schema trích xuất cho điểm khả năng truy cập
    schema = {
        "name": "Result",
        "baseSelector": "div.progress-circle",
        "fields": [
            {"name": "accessibility_score", "selector": "text.accessibility-score", "type": "text"}
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema)
    results = []
    
    # Lặp qua các hàng trong DataFrame hợp lệ (mỗi hàng chứa một URL mục tiêu)
    for index, row in valid_df.iterrows():
        target_url = row[url_column]
        logger.info(f"Đang xử lý {len(results) + 1}/{len(valid_df)}: {target_url}")
        
        crawler = AsyncWebCrawler(config=browser_config)
        current_page = None
        
        # Hook: Khi page context được tạo
        async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
            nonlocal current_page
            current_page = page
            logger.debug("[HOOK] on_page_context_created - Page và context đã sẵn sàng")
            return page
        
        # Hook: Sau khi điều hướng đến một trang
        async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
            nonlocal current_page
            current_page = page
            logger.debug(f"[HOOK] after_goto - Đã tải thành công URL: {url}")
            
            # Nếu chúng ta đang ở trang form kiểm tra khả năng truy cập, điền vào URL mục tiêu và gửi
            if url == "https://aeldata.com/accessibility-checker/":
                try:
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    await page.wait_for_selector("input[id='asc-form-input']", timeout=60000)
                    await page.fill("input[id='asc-form-input']", target_url)
                    logger.info(f"Đã điền form với URL: {target_url}")
                    await page.click("button[id='score-button']")
                    logger.info("Đã nhấp nút gửi")
                    await asyncio.sleep(3)
                    
                    # Kiểm tra thông báo lỗi
                    try:
                        error_visible = await page.evaluate("""() => {
                            const errorElement = document.querySelector('#error-message');
                            return errorElement &&
                                   (errorElement.style.display !== 'none') &&
                                   errorElement.textContent &&
                                   errorElement.textContent.trim() !== '';
                        }""")
                        if error_visible:
                            error_message = await page.evaluate("""() => {
                                const errorElement = document.querySelector('#error-message');
                                return errorElement ? errorElement.textContent.trim() : 'Lỗi không xác định';
                            }""")
                            logger.warning(f"Phát hiện lỗi cho URL '{target_url}': {error_message}")
                            results.append({
                                'url': target_url,
                                'accessibility_compliance': None,
                                'error': f"URL không hợp lệ: {error_message}"
                            })
                            return page  # Trả về sớm nếu phát hiện lỗi
                    except Exception as e:
                        logger.error(f"Lỗi khi kiểm tra thông báo lỗi: {e}")
                    
                    try:
                        await page.wait_for_selector("#progress-containers", timeout=90000)
                        logger.info("Kết quả đã tải thành công")
                    except Exception as e:
                        logger.error(f"Đã hết thời gian chờ kết quả: {e}")
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Lỗi trong quá trình gửi form: {str(e)}")
                    
            return page
        
        crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
        crawler.crawler_strategy.set_hook("after_goto", after_goto)
        
        await crawler.start()
        
        session_id = f"session_{index}"
        crawler_run_config = CrawlerRunConfig(
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy,
            page_timeout=120000,  # 120s timeout cho toàn bộ quá trình
        )
        
        try:
            result = await crawler.arun(
                url="https://aeldata.com/accessibility-checker/",
                config=crawler_run_config
            )
            
            # Nếu URL đã được xử lý là không hợp lệ, bỏ qua việc trích xuất thêm
            if any(r['url'] == target_url and r.get('error', '').startswith('URL không hợp lệ:') for r in results):
                logger.info(f"Bỏ qua trích xuất cho URL không hợp lệ đã được xác định: {target_url}")
                try:
                    await crawler.close()
                    logger.info(f"Đã đóng crawler cho URL không hợp lệ: {target_url}")
                except Exception as e:
                    logger.error(f"Lỗi khi đóng crawler: {e}")
                continue
            
            score = None
            
            # Phương pháp 1: Thử trích xuất điểm trực tiếp bằng JavaScript
            if current_page:
                try:
                    error_visible = await current_page.evaluate("""() => {
                        const errorElement = document.querySelector('#error-message');
                        return errorElement &&
                               (errorElement.style.display !== 'none') &&
                               errorElement.textContent &&
                               errorElement.textContent.trim() !== '';
                    }""")
                    
                    if error_visible:
                        error_message = await current_page.evaluate("""() => {
                            const errorElement = document.querySelector('#error-message');
                            return errorElement ? errorElement.textContent.trim() : 'Lỗi không xác định';
                        }""")
                        logger.warning(f"Phát hiện lỗi muộn cho URL '{target_url}': {error_message}")
                        results.append({
                            'url': target_url,
                            'accessibility_compliance': None,
                            'error': f"URL không hợp lệ: {error_message}"
                        })
                        try:
                            await crawler.close()
                            logger.info(f"Đã đóng crawler cho URL không hợp lệ: {target_url}")
                        except Exception as e:
                            logger.error(f"Lỗi khi đóng crawler: {e}")
                        continue
                    
                    js_score = await current_page.evaluate("""() => {
                        const scoreElement = document.querySelector('text.accessibility-score');
                        return scoreElement ? scoreElement.textContent : null;
                    }""")
                    if js_score:
                        score = js_score
                        logger.info(f"Đã trích xuất điểm qua JavaScript: {score}")
                except Exception as e:
                    logger.error(f"Trích xuất JavaScript thất bại: {e}")
            
            # Lưu kết quả nếu chưa được lưu dưới dạng lỗi
            if not any(r['url'] == target_url for r in results):
                if score:
                    # Trích xuất số điểm từ kết quả (vd: "85/100" -> "85")
                    score_value = score.split('/')[0].strip() if '/' in score else score.strip()
                    results.append({
                        'url': target_url,
                        'accessibility_compliance': score_value
                    })
                else:
                    results.append({
                        'url': target_url,
                        'accessibility_compliance': None,
                        'error': "Không thể trích xuất điểm"
                    })
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý {target_url}: {str(e)}")
            results.append({
                'url': target_url,
                'accessibility_compliance': None,
                'error': str(e)
            })
        
        try:
            await crawler.close()
            logger.info(f"Đã đóng crawler cho URL: {target_url}")
        except Exception as e:
            logger.error(f"Lỗi khi đóng crawler: {e}")
        
        # Tạo độ trễ giữa các URL để tránh giới hạn tốc độ
        delay = 5
        logger.info(f"Chờ {delay} giây...")
        await asyncio.sleep(delay)
    
    # Tạo kết quả trống cho các URL không hợp lệ để lưu vào Google Sheet
    full_results = []
    for index, row in df.iterrows():
        url = row[url_column] if isinstance(row[url_column], str) else ""
        
        # Tìm kết quả cho URL này trong danh sách kết quả đã trích xuất
        normalized_url = normalize_url(url) if is_valid_url(url) else None
        matching_result = next((r for r in results if r['url'] == normalized_url), None)
        
        if matching_result:
            # Đã có kết quả cho URL này
            full_results.append(matching_result)
        else:
            # Không có kết quả cho URL này (không hợp lệ hoặc bị bỏ qua)
            if not is_valid_url(url):
                full_results.append({
                    'url': url,
                    'accessibility_compliance': None,
                    'error': "URL không hợp lệ hoặc trống"
                })
            else:
                # URL hợp lệ nhưng không có kết quả (bất thường)
                full_results.append({
                    'url': url,
                    'accessibility_compliance': None,
                    'error': "Không có kết quả"
                })
    
    return full_results

def safe_update(ws, range_name, values, max_retries=3, delay=5):
    """
    Cập nhật Google Sheet với xử lý lỗi và thử lại.
    """
    for attempt in range(1, max_retries + 1):
        try:
            ws.update(range_name=range_name, values=values)
            logger.info(f"Cập nhật thành công ở lần thử {attempt}")
            return
        except ConnectionError as e:
            logger.error(f"Lỗi kết nối ở lần thử {attempt}: {e}")
            if attempt < max_retries:
                logger.info(f"Thử lại sau {delay} giây...")
                time.sleep(delay)
            else:
                logger.error("Đã đạt số lần thử lại tối đa. Cập nhật thất bại.")

def column_to_letter(n):
    """Chuyển đổi số cột 1-indexed thành chữ cái cột Excel."""
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

# --- Hàm Chính ---
async def main():
    try:
        logger.info("Bắt đầu tiến trình kiểm tra khả năng truy cập...")
        
        # --- Thiết lập Google Sheets ---
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = '/opt/airflow/credentials/credentials.json'
        
        logger.info("Đang xác thực với Google Sheets...")
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(credentials)

        # Mở bảng tính bằng URL và chọn các worksheet cho input và output
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?pli=1&gid=775138837#gid=775138837"
        logger.info(f"Đang mở bảng tính: {spreadsheet_url}")
        
        spreadsheet = gc.open_by_url(spreadsheet_url)
        worksheet_input = spreadsheet.worksheet("Test")
        worksheet_output = spreadsheet.worksheet("Test")

        # --- Xác định vị trí Header cho dữ liệu đầu vào ---
        header_row_position = 1
        logger.info(f"Đọc dữ liệu với header ở hàng {header_row_position}")
        
        all_values = worksheet_input.get_all_values()
        header = all_values[header_row_position - 1]  
        data_rows = all_values[header_row_position:]  
        df = pd.DataFrame(data_rows, columns=header)
        logger.info(f"Đã đọc {len(df)} hàng dữ liệu từ Google Sheet")

        # Xác định tên cột trong Google Sheet chứa URL
        url_column = "Website domain"  
        if url_column not in df.columns:
            raise ValueError(f"Không tìm thấy cột '{url_column}' trong dữ liệu đầu vào")
        
        results = await process_urls_from_google_sheet(df, url_column)

        import numpy as np
        # Chuyển đổi kết quả thành DataFrame và làm sạch giá trị không hợp lệ
        output_df = pd.DataFrame(results)
        output_df = output_df.replace([np.inf, -np.inf, np.nan], None)

        # Xác định cột đầu ra trong Google Sheet
        output_header = "Accessibility"

        # Tìm chỉ mục cột của header được chỉ định trong bảng tính
        try:
            col_index = header.index(output_header)  
            logger.info(f"Tìm thấy header '{output_header}' tại chỉ mục cột {col_index}")
        except ValueError:
            logger.error(f"Header '{output_header}' không tìm thấy trong bảng tính!")
            return

        # Chuyển đổi số cột zero-indexed thành chữ cái cột (kiểu Excel; 1-indexed)
        output_col_letter = column_to_letter(col_index + 1)
        logger.info(f"Header '{output_header}' nằm ở cột {output_col_letter}")

        # Hàng dữ liệu trong bảng tính bắt đầu từ header_row_position+1
        data_start_row = header_row_position + 1
        num_data_rows = len(df)

        # Chuẩn bị dữ liệu đầu ra dưới dạng danh sách của danh sách (mỗi danh sách bên trong là một giá trị ô)
        output_values = [[val] for val in output_df['accessibility_compliance'].tolist()]

        # Xây dựng chuỗi phạm vi cho cập nhật hàng loạt
        update_range = f"{output_col_letter}{data_start_row}:{output_col_letter}{data_start_row + num_data_rows - 1}"
        logger.info(f"Cập nhật phạm vi: {update_range}")
        
        # Chỉ cập nhật phạm vi đã chỉ định để cột URL không bị ghi đè.
        safe_update(worksheet_output, range_name=update_range, values=output_values)
        logger.info(f"Đã xử lý {len(results)} URL. Dữ liệu đầu ra đã được cập nhật lên Google Sheet trong phạm vi {update_range}.")
        
        # Tóm tắt kết quả
        valid_results = [r for r in results if r.get('accessibility_compliance') is not None]
        invalid_results = [r for r in results if r.get('accessibility_compliance') is None]
        
        logger.info(f"Tóm tắt: {len(valid_results)} URL thành công, {len(invalid_results)} URL thất bại")
        
    except Exception as e:
        logger.critical(f"Lỗi nghiêm trọng trong hàm main(): {str(e)}", exc_info=True)
    
    logger.info("Tiến trình kiểm tra khả năng truy cập đã hoàn tất.")

if __name__ == "__main__":
    asyncio.run(main())