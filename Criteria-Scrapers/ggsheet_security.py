# import asyncio
# import pandas as pd
# from playwright.async_api import async_playwright
# import random
# import time

# async def process_urls_from_excel(excel_file, url_column):
#     df = pd.read_excel(excel_file)
    
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # Keep browser open
#         context = await browser.new_context()  # Create a single context
#         page = await context.new_page()
        
#         results = []
#         base_url = "https://sitecheck.sucuri.net/"
        
#         await page.goto(base_url) #navigate once to the base url

#         for index, row in df.iterrows():
#             excel_url = row[url_column]
#             print(f"Processing {index + 1}/{len(df)}: {excel_url}")
            
#             try:
#                 # Fill the form with URL from Excel
#                 input_element = await page.wait_for_selector("input[id='websiteurl']", timeout=5000)
#                 if input_element:
#                     await input_element.fill(excel_url)
#                     print(f"Filled form with URL: {excel_url}")
                
#                 # Click the button
#                 button = await page.wait_for_selector("button[type='submit']", timeout=5000)
#                 if button:
#                     await button.click()
#                     print(f"Clicked submit button")
                
#                 # Wait for data to appear
#                 await page.wait_for_selector("div.rating-indicators > span.active", timeout=60000)
#                 print(f"Found security risk rating")
                
#                 # Extract the security risk rating
#                 risk_rating = await page.evaluate("""() => {
#                     const element = document.querySelector('div.rating-indicators > span.active');
#                     return element ? element.textContent.trim() : null;
#                 }""")
                
#                 results.append({
#                     'url': excel_url,
#                     'security_risk': risk_rating
#                 })
                
#                 print(f"Extracted security risk: {risk_rating}")
                
#             except Exception as e:
#                 print(f"Error processing {excel_url}: {str(e)}")
#                 results.append({
#                     'url': excel_url,
#                     'security_risk': None,
#                     'error': str(e)
#                 })
            
#             # Add delay with randomization
#             delay = random.uniform(2, 5)  # Random delay between 2 and 5 seconds
#             print(f"Waiting for {delay:.2f} seconds...")
#             time.sleep(delay)

#             await page.goto(base_url) #return to the base url.
        
#         await browser.close()  # Close the browser only once
#         return results

# async def main():
#     excel_file = "/Users/vuhainam/Downloads/dataa.xlsx"
#     url_column = "URL"
    
#     results = await process_urls_from_excel(excel_file, url_column)
    
#     output_df = pd.DataFrame(results)
#     output_df.to_excel("security_results.xlsx", index=False)
#     print(f"Processed {len(results)} URLs. Results saved to security_results.xlsx")

# if __name__ == "__main__":
#     asyncio.run(main())






import asyncio
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import random
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import logging
from datetime import datetime


# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"security_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def process_urls_from_google_sheet(df, url_column):
    """
    Xử lý các URL từ DataFrame và trả về kết quả đánh giá bảo mật.
    Sử dụng chiến lược chờ và tái thử thông minh.
    """
    async with async_playwright() as p:
        # Khởi tạo trình duyệt với các tùy chọn tối ưu
        browser = await p.chromium.launch(
            headless=False,  
            args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        results = []
        base_url = "https://sitecheck.sucuri.net/"
        
        for index, row in df.iterrows():
            sheet_url = row[url_column].strip()
            if not sheet_url:
                logger.warning(f"URL trống tại dòng {index + 1}, bỏ qua")
                results.append({'url': sheet_url, 'security_risk': "N/A", 'error': "URL trống"})
                continue
                
            logger.info(f"Đang xử lý {index + 1}/{len(df)}: {sheet_url}")
            
            # Tạo context mới cho mỗi URL để tránh vấn đề cache và cookie
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
            )
            page = await context.new_page()
            
            # Thiết lập interceptors (tùy chọn) để chặn các tài nguyên không cần thiết
            await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
            
            risk_rating = None
            error_message = None
            retry_count = 0
            max_retries = 2
            
            while retry_count <= max_retries and not risk_rating:
                try:
                    # Mở trang với timeout hợp lý
                    await page.goto(base_url, timeout=40000, wait_until="domcontentloaded")
                    
                    # Đảm bảo trang đã tải xong
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Kiểm tra xem form có hiển thị không
                    input_visible = await page.is_visible("input[id='websiteurl']", timeout=5000)
                    if not input_visible:
                        raise Exception("Form input không hiển thị")
                        
                    # Điền form với URL
                    await page.fill("input[id='websiteurl']", sheet_url)
                    logger.info(f"Đã điền form với URL: {sheet_url}")
                    
                    # Click nút gửi
                    await page.click("button[type='submit']")
                    logger.info(f"Đã nhấp nút gửi")
                    
                    # Sử dụng promise.race để xử lý đồng thời trường hợp thành công và thất bại
                    success_selector = "div.rating-indicators > span.active"
                    error_selector = "div.alert-danger, div.error-message"
                    
                    # Chờ đợi một trong hai selector xuất hiện
                    result = await page.wait_for_selector(f"{success_selector}, {error_selector}", 
                                                         timeout=60000)
                    
                    # Kiểm tra kết quả nào xuất hiện
                    if await page.is_visible(success_selector):
                        risk_rating = await page.evaluate("""() => {
                            const element = document.querySelector('div.rating-indicators > span.active');
                            return element ? element.textContent.trim() : null;
                        }""")
                        logger.info(f"Đã trích xuất đánh giá rủi ro bảo mật: {risk_rating}")
                        break
                    elif await page.is_visible(error_selector):
                        error_text = await page.evaluate("""() => {
                            const element = document.querySelector('div.alert-danger, div.error-message');
                            return element ? element.textContent.trim() : "Lỗi không xác định";
                        }""")
                        error_message = f"Trang báo lỗi: {error_text}"
                        logger.warning(f"Trang báo lỗi cho {sheet_url}: {error_text}")
                        break
                        
                except PlaywrightTimeoutError as e:
                    error_message = f"Timeout: {str(e)}"
                    logger.warning(f"Timeout khi xử lý {sheet_url}: {str(e)}")
                except Exception as e:
                    error_message = f"Lỗi: {str(e)}"
                    logger.error(f"Lỗi khi xử lý {sheet_url}: {str(e)}", exc_info=True)
                
                retry_count += 1
                if retry_count <= max_retries:
                    logger.info(f"Thử lại {retry_count}/{max_retries} cho {sheet_url}")
                    # Sử dụng asyncio.sleep thay vì time.sleep để không chặn event loop
                    await asyncio.sleep(random.uniform(5, 10))
            
            # Lưu kết quả
            results.append({
                'url': sheet_url,
                'security_risk': risk_rating if risk_rating else "Không thể xác định",
                'error': error_message if error_message else None
            })
            
            # Đóng context hiện tại để giải phóng tài nguyên
            await context.close()
            
            # Thêm độ trễ ngẫu nhiên giữa các yêu cầu
            delay = random.uniform(3, 7)  # Độ trễ ngẫu nhiên từ 3-7 giây
            logger.info(f"Chờ {delay:.2f} giây...")
            await asyncio.sleep(delay)  # Sử dụng asyncio.sleep thay vì time.sleep
        
        await browser.close()  # Đóng trình duyệt sau khi hoàn thành
        return results


def column_to_letter(n):
    """Chuyển đổi số cột 1-indexed thành chữ cái cột Excel."""
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


async def main():
    try:
        logger.info("Bắt đầu tiến trình scraping bảo mật...")
        
        # --- Thiết lập Google Sheets ---
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
        
        logger.info("Đang xác thực với Google Sheets...")
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(credentials)

        # Mở bảng tính bằng URL và chọn các worksheet cho input và output
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?pli=1&gid=137734733#gid=137734733"
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

        # Chuyển đổi kết quả thành DataFrame và làm sạch giá trị không hợp lệ
        output_df = pd.DataFrame(results)
        output_df = output_df.replace([np.inf, -np.inf, np.nan], None)

        # Xác định cột đầu ra trong Google Sheet
        output_header = "Security"

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
        output_values = [[val] for val in output_df['security_risk'].tolist()]

        # Xây dựng chuỗi phạm vi cho cập nhật hàng loạt
        update_range = f"{output_col_letter}{data_start_row}:{output_col_letter}{data_start_row + num_data_rows - 1}"
        logger.info(f"Cập nhật phạm vi: {update_range}")

        # Cập nhật worksheet trong phạm vi tìm thấy
        worksheet_output.update(range_name=update_range, values=output_values)
        logger.info(f"Đã xử lý {len(results)} URL. Dữ liệu đầu ra đã được cập nhật lên Google Sheet trong phạm vi {update_range}.")

        # Kiểm tra nếu có lỗi nào trong quá trình scraping
        error_urls = [r['url'] for r in results if r.get('error')]
        if error_urls:
            logger.warning(f"Có {len(error_urls)} URL gặp lỗi trong quá trình scraping")
            for url in error_urls[:5]:  # Chỉ ghi log 5 URL đầu tiên để tránh quá dài
                logger.warning(f"URL lỗi: {url}")
            if len(error_urls) > 5:
                logger.warning(f"... và {len(error_urls) - 5} URL lỗi khác")
    
    except Exception as e:
        logger.critical(f"Lỗi nghiêm trọng trong hàm main(): {str(e)}", exc_info=True)
    
    logger.info("Tiến trình scraping bảo mật đã hoàn tất.")


if __name__ == "__main__":
    asyncio.run(main())