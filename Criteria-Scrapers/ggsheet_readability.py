# import asyncio
# import pandas as pd
# from playwright.async_api import async_playwright
# import random
# import time

# async def process_urls_from_excel(excel_file, url_column):
#     df = pd.read_excel(excel_file)
    
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context()
#         page = await context.new_page()

#         results = []
#         base_url = "https://www.webfx.com/tools/read-able/"
        
#         await page.goto(base_url, timeout=60000)

#         for index, row in df.iterrows():
#             excel_url = row[url_column]
#             print(f"Processing {index + 1}/{len(df)}: {excel_url}")
            
#             try:
#                 input_element = await page.wait_for_selector("input[id='uri']", timeout=5000)
#                 if input_element:
#                     await input_element.fill(excel_url)
#                     print(f"Filled form with URL: {excel_url}")
                
#                 button = await page.wait_for_selector("button[type='submit']", timeout=5000)
#                 if button:
#                     await button.click()
#                     print(f"Clicked submit button")
                
#                 success = False
#                 risk_rating = None
                
#                 await page.wait_for_timeout(3000)
                
#                 results_element = await page.query_selector("div#generator-results-wrapper > div > div > div")
                
#                 if results_element:
#                     success = True
#                 else:
#                     error_element = await page.query_selector("div.error-message-selector")
                    
#                     await input_element.fill("")
#                     new_url = "https://" + excel_url
#                     await input_element.fill(new_url)
#                     await button.click()
                    
#                     try:
#                         await page.wait_for_selector("div#generator-results-wrapper > div > div > div", timeout=30000)
#                         success = True
#                     except:
#                         print(f"URL not accessible even with https prefix: {excel_url}")
                
#                 if success:
#                     risk_rating = await page.evaluate("""() => {
#                         const element = document.querySelector('div#generator-results-wrapper > div > div > div');
#                         return element ? element.textContent.trim() : null;
#                     }""")
                    
#                     results.append({
#                         'url': excel_url,
#                         'readability_score': risk_rating
#                     })
                    
#                     if risk_rating:
#                         print(f"Extracted readability score: {risk_rating}")

#             except Exception as e:
#                 print(f"Error processing {excel_url}: {str(e)}")
#                 results.append({
#                     'url': excel_url,
#                     'readability_score': None,
#                     'error': str(e)
#                 })
            
#             delay = random.uniform(2, 5)
#             print(f"Waiting for {delay:.2f} seconds...")
#             time.sleep(delay)
#             await page.goto(base_url)

#         await browser.close()
#         return results

# async def main():
#     excel_file = "/Users/vuhainam/Downloads/dataa.xlsx"
#     url_column = "URL"
    
#     results = await process_urls_from_excel(excel_file, url_column)
    
#     output_df = pd.DataFrame(results)
#     output_df.to_excel("readability_results.xlsx", index=False)
#     print(f"Processed {len(results)} URLs. Results saved to readability_results.xlsx")

# if __name__ == "__main__":
#     asyncio.run(main())





import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import random
import time
import gspread
from google.oauth2.service_account import Credentials

async def process_urls_from_google_sheet(df, url_column):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        results = []
        base_url = "https://www.webfx.com/tools/read-able/"

        await page.goto(base_url, timeout=60000)

        for index, row in df.iterrows():
            sheet_url = row[url_column]
            print(f"Processing {index + 1}/{len(df)}: {sheet_url}")

            try:
                input_element = await page.wait_for_selector("input[id='uri']", timeout=5000)
                if input_element:
                    await input_element.fill(sheet_url)
                    print(f"Filled form with URL: {sheet_url}")

                button = await page.wait_for_selector("button[type='submit']", timeout=5000)
                if button:
                    await button.click()
                    print(f"Clicked submit button")

                success = False
                risk_rating = None

                await page.wait_for_timeout(3000)

                results_element = await page.query_selector("div#generator-results-wrapper > div > div > div")

                if results_element:
                    success = True
                else:
                    error_element = await page.query_selector("div.error-message-selector")

                    await input_element.fill("")
                    new_url = "https://" + sheet_url
                    await input_element.fill(new_url)
                    await button.click()

                    try:
                        await page.wait_for_selector("div#generator-results-wrapper > div > div > div", timeout=30000)
                        success = True
                    except:
                        print(f"URL not accessible even with https prefix: {sheet_url}")

                if success:
                    risk_rating = await page.evaluate("""() => {
                        const element = document.querySelector('div#generator-results-wrapper > div > div > div');
                        return element ? element.textContent.trim() : null;
                    }""")

                # Luôn thêm kết quả vào danh sách cho mỗi URL, bất kể thành công hay không
                results.append({
                    'url': sheet_url,
                    'readability_score': risk_rating
                })

                if risk_rating:
                    print(f"Extracted readability score: {risk_rating}")
                else:
                    print(f"No readability score found for: {sheet_url}")

            except Exception as e:
                print(f"Error processing {sheet_url}: {str(e)}")
                results.append({
                    'url': sheet_url,
                    'readability_score': None,
                    'error': str(e)
                })

            delay = random.uniform(2, 5)
            print(f"Waiting for {delay:.2f} seconds...")
            time.sleep(delay)
            await page.goto(base_url)

        await browser.close()
        return results
    
def column_to_letter(n):
    """Convert 1-indexed column number to Excel column letter."""
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

async def main():
    # --- Google Sheets Setup ---
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = '/opt/airflow/credentials/credentials.json'
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    # Open the spreadsheet by URL and select the worksheets for input and output
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?pli=1&gid=137734733#gid=137734733")
    worksheet_input = spreadsheet.worksheet("Test")
    worksheet_output = spreadsheet.worksheet("Test")

    # --- Specify Header Position for Input Data ---
    header_row_position = 1
    all_values = worksheet_input.get_all_values()
    header = all_values[header_row_position - 1]  
    data_rows = all_values[header_row_position:]  
    df = pd.DataFrame(data_rows, columns=header)
    print("Input data from Google Sheet loaded successfully with header on row", header_row_position)

    # Define the name of the column in your Google Sheet containing URLs
    url_column = "Website domain"  
    results = await process_urls_from_google_sheet(df, url_column)

    import numpy as np
    # Convert results to DataFrame and sanitize non-finite values
    output_df = pd.DataFrame(results)
    output_df = output_df.replace([np.inf, -np.inf, np.nan], None)

    # Đảm bảo thứ tự đầu ra khớp với thứ tự đầu vào bằng cách so sánh URL
    # Tạo một danh sách để lưu các điểm số theo thứ tự URL gốc
    ordered_scores = []
    input_urls = df[url_column].tolist()
    
    # Tạo dictionary từ kết quả để dễ dàng tra cứu
    results_dict = {result['url']: result['readability_score'] for result in results}
    
    # Duyệt qua URLs theo thứ tự gốc và lấy điểm số tương ứng
    for url in input_urls:
        ordered_scores.append(results_dict.get(url, None))
    
    # Kiểm tra xem số lượng scores có khớp với số lượng URLs không
    print(f"Input URLs: {len(input_urls)}, Output scores: {len(ordered_scores)}")
    
    # Let's assume you want to write the "readability_score" values into the column that has header "Readability"
    output_header = "Readability"

    # Find the column index of the specified header in the sheet
    try:
        col_index = header.index(output_header)  
        print(f"Found header '{output_header}' at column index {col_index}")
    except ValueError:
        print(f"Header '{output_header}' not found in the sheet!")
        return

    # Convert the zero-indexed column number to a column letter (Excel style; 1-indexed)
    output_col_letter = column_to_letter(col_index + 1)
    print(f"Header '{output_header}' is in column {output_col_letter}")

    # Data rows in the sheet start at header_row_position+1
    data_start_row = header_row_position + 1
    num_data_rows = len(df)

    # Prepare output data as a list of lists (each inner list is one cell value)
    output_values = [[val] for val in ordered_scores]  # Sử dụng ordered_scores thay vì output_df

    # Build the range string for bulk update
    update_range = f"{output_col_letter}{data_start_row}:{output_col_letter}{data_start_row + num_data_rows - 1}"
    print(f"Updating range: {update_range}")

    # Update the worksheet in the found range
    worksheet_output.update(range_name=update_range, values=output_values)
    print(f"Processed {len(results)} URLs. Output data updated to Google Sheet in range {update_range}.")
    
if __name__ == "__main__":
    asyncio.run(main())