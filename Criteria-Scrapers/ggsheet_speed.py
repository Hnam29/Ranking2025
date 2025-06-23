# import asyncio
# import pandas as pd
# import re
# import gspread
# from google.oauth2.service_account import Credentials
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
# from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
# from playwright.async_api import Page, BrowserContext

# # --- Google Sheets Setup ---
# # Define the required scope and path to your service account credentials.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# SERVICE_ACCOUNT_FILE = '/opt/airflow/credentials/credentials.json'  

# # Authenticate and create a gspread client
# credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# gc = gspread.authorize(credentials)

# # Open your input and output sheets (or worksheets within a single sheet)
# spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?pli=1&gid=775138837#gid=775138837")
# worksheet_input = spreadsheet.worksheet("Test")
# worksheet_output = spreadsheet.worksheet("Test")

# # --- Specify Header Position for Input Data ---
# # If your header is not in the first row, for example, it's in row 2:
# header_row_position = 5  # change as needed

# all_values = worksheet_input.get_all_values()
# header = all_values[header_row_position - 1]  # Adjust for zero indexing
# data_rows = all_values[header_row_position:]      # Data starting from the next row
# df = pd.DataFrame(data_rows, columns=header)
# print("Input data from Google Sheet loaded successfully with header on row", header_row_position)

# # --- Your Crawling and Extraction Function ---
# async def process_urls_from_google_sheet(df, url_column):
#     # Configure the browser
#     browser_config = BrowserConfig(
#         headless=True,
#         verbose=True,
#         user_agent_mode="random"
#     )
    
#     # Define extraction schema for accessibility score
#     schema = {
#         "name": "Result",
#         "baseSelector": "div.lh-sticky-header > a:nth-of-type(1)",
#         "fields": [
#             {"name": "speed_score", "selector": "div.lh-gauge__percentage", "type": "text"}
#         ]
#     }
    
#     # Create extraction strategy
#     extraction_strategy = JsonCssExtractionStrategy(schema)
    
#     results = []
    
#     for index, row in df.iterrows():
#         target_url = row[url_column]
#         print(f"Processing {index + 1}/{len(df)}: {target_url}")
        
#         crawler = AsyncWebCrawler(config=browser_config)
#         current_page = None
        
#         async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
#             nonlocal current_page
#             current_page = page
#             print("[HOOK] on_page_context_created - Page and context ready")
#             return page
        
#         async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
#             nonlocal current_page
#             current_page = page
#             print(f"[HOOK] after_goto - Successfully loaded URL: {url}")
            
#             if url == "https://pagespeed.web.dev/":
#                 try:
#                     await page.wait_for_load_state("networkidle", timeout=15000)
#                     await page.wait_for_selector("input[id='i4']", timeout=15000)
#                     await page.fill("input[id='i4']", target_url)
#                     print(f"Filled form with URL: {target_url}")
#                     await page.click("button[class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 c659ib']")
#                     print("Clicked submit button")
#                     await asyncio.sleep(3)
#                     try:
#                         await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
#                         print("Results loaded successfully")
#                     except Exception as e:
#                         print(f"Timeout waiting for results heading: {e}")
#                     await asyncio.sleep(5)
#                 except Exception as e:
#                     print(f"Error in form submission: {str(e)}")
            
#             if "pagespeed.web.dev/analysis" in url:
#                 try:
#                     await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
#                     print("Results loaded successfully on analysis page")
#                     await asyncio.sleep(5)
#                 except Exception as e:
#                     print(f"Timeout waiting for results on analysis page: {e}")
#             return page
        
#         crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
#         crawler.crawler_strategy.set_hook("after_goto", after_goto)
        
#         await crawler.start()
        
#         session_id = f"session_{index}"
#         crawler_run_config = CrawlerRunConfig(
#             session_id=session_id,
#             cache_mode=CacheMode.BYPASS,
#             extraction_strategy=extraction_strategy,
#             page_timeout=180000,
#         )
        
#         try:
#             result = await crawler.arun(
#                 url="https://pagespeed.web.dev/",
#                 config=crawler_run_config
#             )
            
#             mobile_score = None
#             desktop_score = None
#             mobile_score_recheck = None
            
#             if current_page:
#                 try:
#                     mobile_score = await current_page.evaluate("""() => {
#                         const scoreElement = document.querySelector('div.lh-gauge__percentage'); 
#                         return scoreElement ? scoreElement.textContent : null;
#                     }""")
#                     if mobile_score:
#                         print(f"Extracted mobile score: {mobile_score}")
#                         current_url = current_page.url
#                         print(f"Current URL: {current_url}")
#                         if "form_factor=mobile" in current_url and "pagespeed.web.dev/analysis" in current_url:
#                             desktop_url = current_url.replace("form_factor=mobile", "form_factor=desktop")
#                             print(f"Desktop URL: {desktop_url}")
#                             print("Navigating to desktop version...")
#                             try:
#                                 await current_page.goto(desktop_url, timeout=60000)
#                                 await asyncio.sleep(3)
#                                 desktop_score = await current_page.evaluate("""() => {
#                                     const scoreElement = document.evaluate(
#                                         '/html/body/c-wiz/div[2]/div/div[2]/div[3]/div/div/div[3]/span/div/div[2]/div[2]/div/div/article/div/div[2]/div/div/div/div[2]/a[1]/div[2]', 
#                                         document, 
#                                         null, 
#                                         XPathResult.FIRST_ORDERED_NODE_TYPE, 
#                                         null
#                                         ).singleNodeValue;
#                                     return scoreElement ? scoreElement.textContent : null;
#                                 }""")
#                                 if desktop_score:
#                                     print(f"Extracted desktop score: {desktop_score}")
#                                 print("Navigating back to mobile version...")
#                                 await current_page.goto(current_url, timeout=60000)
#                                 await asyncio.sleep(5)
#                                 mobile_score_recheck = await current_page.evaluate("""() => {
#                                     const scoreElement = document.querySelector('div.lh-gauge__percentage');
#                                     return scoreElement ? scoreElement.textContent : null;
#                                 }""")
#                                 if mobile_score_recheck:
#                                     print(f"Extracted mobile score again: {mobile_score_recheck}")
#                                     if mobile_score != mobile_score_recheck:
#                                         print(f"WARNING: Mobile scores differ! First: {mobile_score}, Second: {mobile_score_recheck}")
                            
#                             except Exception as e:
#                                 print(f"Error navigating between mobile and desktop: {e}")
#                         else:
#                             print("Current URL doesn't match expected pattern for switching to desktop view")
                            
#                 except Exception as e:
#                     print(f"JavaScript extraction failed: {e}")
            
#             avg_score = None
#             if mobile_score is not None and desktop_score is not None:
#                 try:
#                     mobile_score_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(mobile_score))))
#                     desktop_score_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(desktop_score))))
#                     avg_score = (mobile_score_num + desktop_score_num) / 2
#                     print(f"Calculated average score: {avg_score}")
#                 except Exception as e:
#                     print(f"Error calculating average: {e}")
            
#             results.append({
#                 'url': target_url,
#                 'mobile_score': mobile_score,
#                 'desktop_score': desktop_score,
#                 'mobile_score_recheck': mobile_score_recheck,
#                 'average_score': avg_score,
#                 'scores_match': "Yes" if mobile_score == mobile_score_recheck else "No" if mobile_score_recheck else "N/A"
#             })
            
#         except Exception as e:
#             print(f"Error processing {target_url}: {str(e)}")
#             results.append({
#                 'url': target_url,
#                 'mobile_score': None,
#                 'desktop_score': None,
#                 'mobile_score_recheck': None,
#                 'average_score': None,
#                 'scores_match': "N/A",
#                 'error': str(e)
#             })
        
#         try:
#             await crawler.close()
#             print(f"Closed crawler for URL: {target_url}")
#         except Exception as e:
#             print(f"Error closing crawler: {e}")
        
#         await asyncio.sleep(5)
    
#     return results

# # --- Main function to tie everything together ---
# async def main():
#     # Define the name of the column in your Google Sheet containing URLs
#     url_column = "Website domain"  
    
#     # Process the URLs using the DataFrame read from Google Sheets
#     results = await process_urls_from_google_sheet(df, url_column)
    
#     import numpy as np
#     # Convert results to DataFrame and sanitize any non-finite values
#     output_df = pd.DataFrame(results)
#     output_df = output_df.replace([np.inf, -np.inf, np.nan], None)
    
#     # extract the specified column as a list of lists (e.g. "accessibility_compliance")
#     output_values = [[val] for val in output_df['average_score'].tolist()]
#     # # Extract two or more columns (each row becomes a list of two items)
#     # output_values = output_df[['accessibility_compliance', 'another_metric']].values.tolist()

#     # Determine the range to update.
#     start_row = 6
#     end_row = start_row + len(output_values) - 1
#     update_range = f"D{start_row}:D{end_row}"

#     # Update the output worksheet starting at cell D5 using named arguments
#     worksheet_output.update(range_name="D5", values=output_values)
#     print(f"Processed {len(results)} URLs. Output data updated to Google Sheet in range {update_range}.")

# if __name__ == "__main__":
#     asyncio.run(main())





# ISSUE: Error in form submission -> TIMEOUT -> CLOSE
import asyncio
import pandas as pd
import numpy as np
import re
import time
import gspread
from google.oauth2.service_account import Credentials
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from playwright.async_api import Page, BrowserContext
from requests.exceptions import ConnectionError

# --- Utility: Convert Column Number to Letter ---
def column_to_letter(n):
    """Convert 1-indexed column number to Excel column letter."""
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

# --- Your Crawling and Extraction Function ---
async def process_urls_from_google_sheet(df, url_column):
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        user_agent_mode="random"
    )
    
    # Define extraction schema (example: extracting speed score)
    schema = {
        "name": "Result",
        "baseSelector": "div.lh-sticky-header > a:nth-of-type(1)",
        "fields": [
            {"name": "speed_score", "selector": "div.lh-gauge__percentage", "type": "text"}
        ]
    }
    extraction_strategy = JsonCssExtractionStrategy(schema)
    results = []
    
    for index, row in df.iterrows():
        target_url = row[url_column]
        print(f"Processing {index + 1}/{len(df)}: {target_url}")
        
        crawler = AsyncWebCrawler(config=browser_config)
        current_page = None
        
        async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
            nonlocal current_page
            current_page = page
            print("[HOOK] on_page_context_created - Page and context ready")
            return page
        
        async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
            nonlocal current_page
            current_page = page
            print(f"[HOOK] after_goto - Successfully loaded URL: {url}")
            if url == "https://pagespeed.web.dev/":
                try:
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    await page.wait_for_selector("input[id='i4']", timeout=15000)
                    await page.fill("input[id='i4']", target_url)
                    print(f"Filled form with URL: {target_url}")
                    await page.click("button[class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 c659ib']")
                    print("Clicked submit button")
                    await asyncio.sleep(3)
                    try:
                        await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
                        print("Results loaded successfully")
                    except Exception as e:
                        print(f"Timeout waiting for results heading: {e}")
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"Error in form submission: {str(e)}")
            
            if "pagespeed.web.dev/analysis" in url:
                try:
                    await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
                    print("Results loaded successfully on analysis page")
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"Timeout waiting for results on analysis page: {e}")
            return page
        
        crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
        crawler.crawler_strategy.set_hook("after_goto", after_goto)
        
        await crawler.start()
        
        session_id = f"session_{index}"
        crawler_run_config = CrawlerRunConfig(
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy,
            page_timeout=180000,
        )
        
        try:
            result = await crawler.arun(
                url="https://pagespeed.web.dev/",
                config=crawler_run_config
            )
            
            mobile_score = None
            desktop_score = None
            mobile_score_recheck = None
            
            if current_page:
                try:
                    mobile_score = await current_page.evaluate("""() => {
                        const scoreElement = document.querySelector('div.lh-gauge__percentage'); 
                        return scoreElement ? scoreElement.textContent : null;
                    }""")
                    if mobile_score:
                        print(f"Extracted mobile score: {mobile_score}")
                        current_url = current_page.url
                        print(f"Current URL: {current_url}")
                        if "form_factor=mobile" in current_url and "pagespeed.web.dev/analysis" in current_url:
                            desktop_url = current_url.replace("form_factor=mobile", "form_factor=desktop")
                            print(f"Desktop URL: {desktop_url}")
                            print("Navigating to desktop version...")
                            try:
                                await current_page.goto(desktop_url, timeout=60000)
                                await asyncio.sleep(3)
                                desktop_score = await current_page.evaluate("""() => {
                                    const scoreElement = document.evaluate(
                                        '/html/body/c-wiz/div[2]/div/div[2]/div[3]/div/div/div[3]/span/div/div[2]/div[2]/div/div/article/div/div[2]/div/div/div/div[2]/a[1]/div[2]', 
                                        document, 
                                        null, 
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, 
                                        null
                                        ).singleNodeValue;
                                    return scoreElement ? scoreElement.textContent : null;
                                }""")
                                if desktop_score:
                                    print(f"Extracted desktop score: {desktop_score}")
                                print("Navigating back to mobile version...")
                                await current_page.goto(current_url, timeout=60000)
                                await asyncio.sleep(5)
                                mobile_score_recheck = await current_page.evaluate("""() => {
                                    const scoreElement = document.querySelector('div.lh-gauge__percentage');
                                    return scoreElement ? scoreElement.textContent : null;
                                }""")
                                if mobile_score_recheck:
                                    print(f"Extracted mobile score again: {mobile_score_recheck}")
                                    if mobile_score != mobile_score_recheck:
                                        print(f"WARNING: Mobile scores differ! First: {mobile_score}, Second: {mobile_score_recheck}")
                            except Exception as e:
                                print(f"Error navigating between mobile and desktop: {e}")
                        else:
                            print("Current URL doesn't match expected pattern for switching to desktop view")
                except Exception as e:
                    print(f"JavaScript extraction failed: {e}")
            
            avg_score = None
            if mobile_score is not None and desktop_score is not None:
                try:
                    mobile_score_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(mobile_score))))
                    desktop_score_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(desktop_score))))
                    avg_score = (mobile_score_num + desktop_score_num) / 2
                    print(f"Calculated average score: {avg_score}")
                except Exception as e:
                    print(f"Error calculating average: {e}")
            
            results.append({
                'url': target_url,
                'mobile_score': mobile_score,
                'desktop_score': desktop_score,
                'mobile_score_recheck': mobile_score_recheck,
                'average_score': avg_score,
                'scores_match': "Yes" if mobile_score == mobile_score_recheck else "No" if mobile_score_recheck else "N/A"
            })
        except Exception as e:
            print(f"Error processing {target_url}: {str(e)}")
            results.append({
                'url': target_url,
                'mobile_score': None,
                'desktop_score': None,
                'mobile_score_recheck': None,
                'average_score': None,
                'scores_match': "N/A",
                'error': str(e)
            })
        
        try:
            await crawler.close()
            print(f"Closed crawler for URL: {target_url}")
        except Exception as e:
            print(f"Error closing crawler: {e}")
        
        await asyncio.sleep(5)
    
    return results

# --- Main function to tie everything together ---
async def main():
    # --- Google Sheets Setup ---
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = '/opt/airflow/credentials/credentials.json'
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    # Open the spreadsheet by URL and select the worksheets for input and output
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?gid=775138837#gid=775138837")
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

    # Let's assume you want to write the "readability_score" values into the column that has header "Readability"
    output_header = "Speed"

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
    output_values = [[val] for val in output_df['average_score'].tolist()]

    # Build the range string for bulk update
    update_range = f"{output_col_letter}{data_start_row}:{output_col_letter}{data_start_row + num_data_rows - 1}"
    print(f"Updating range: {update_range}")

    # Update the worksheet in the found range
    worksheet_output.update(range_name=update_range, values=output_values)
    print(f"Processed {len(results)} URLs. Output data updated to Google Sheet in range {update_range}.")

if __name__ == "__main__":
    asyncio.run(main())