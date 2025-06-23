# import asyncio
# import pandas as pd
# from playwright.async_api import async_playwright
# import random
# import time
# import gspread
# from google.oauth2.service_account import Credentials

# async def process_urls_from_google_sheet(df, url_column):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context()
#         page = await context.new_page()

#         results = []
#         base_url = "https://ahrefs.com/website-authority-checker/"

#         await page.goto(base_url, timeout=60000)

#         for index, row in df.iterrows():
#             sheet_url = row[url_column]
#             print(f"Processing {index + 1}/{len(df)}: {sheet_url}")

#             try:
#                 input_element = await page.wait_for_selector("input[class='css-hfjebg css-1mk4k1q css-wcs6']", timeout=5000)
#                 if input_element:
#                     await input_element.fill(sheet_url)
#                     print(f"Filled form with URL: {sheet_url}")

#                 button = await page.wait_for_selector("button[class='css-ygijhp css-1tyndxa css-1ip10c0 css-9cz4sg css-115l1wb']", timeout=5000)
#                 if button:
#                     await button.click()
#                     time.sleep(30)
#                     print(f"Clicked submit button")

#                 risk_rating = None

#                 await page.wait_for_timeout(3000)

#                 results_element = await page.query_selector("div.css-10y00fk-content.css-die2lc.css-v2v3ur-contentFullWidth.css-agqhba-contentNoScrollMobile.css-1tt6ytp-contentAfterOpen > div > div > div[2] > div > div > div[2]")

#                 if results_element:
#                     risk_rating = await page.evaluate("""() => {
#                         const element = document.querySelector('div.css-10y00fk-content.css-die2lc.css-v2v3ur-contentFullWidth.css-agqhba-contentNoScrollMobile.css-1tt6ytp-contentAfterOpen > div > div > div[2] > div > div > div[2]');
#                         return element ? element.textContent.trim() : null;
#                     }""")

#                     results.append({
#                         'url': sheet_url,
#                         'authority_score': risk_rating
#                     })

#                     if risk_rating:
#                         print(f"Extracted authority score: {risk_rating}")

#             except Exception as e:
#                 print(f"Error processing {sheet_url}: {str(e)}")
#                 results.append({
#                     'url': sheet_url,
#                     'authority_score': None,
#                     'error': str(e)
#                 })

#             delay = random.uniform(2, 5)
#             print(f"Waiting for {delay:.2f} seconds...")
#             time.sleep(delay)
#             await page.goto(base_url)

#         await browser.close()
#         return results
    
# def column_to_letter(n):
#     """Convert 1-indexed column number to Excel column letter."""
#     string = ""
#     while n:
#         n, remainder = divmod(n - 1, 26)
#         string = chr(65 + remainder) + string
#     return string

# async def main():
#     # --- Google Sheets Setup ---
#     SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
#     SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
#     credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     gc = gspread.authorize(credentials)

#     # Open the spreadsheet by URL and select the worksheets for input and output
#     spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?pli=1&gid=137734733#gid=137734733")
#     worksheet_input = spreadsheet.worksheet("Test")
#     worksheet_output = spreadsheet.worksheet("Test")

#     # --- Specify Header Position for Input Data ---
#     header_row_position = 5  
#     all_values = worksheet_input.get_all_values()
#     header = all_values[header_row_position - 1]  
#     data_rows = all_values[header_row_position:]  
#     df = pd.DataFrame(data_rows, columns=header)
#     print("Input data from Google Sheet loaded successfully with header on row", header_row_position)

#     # Define the name of the column in your Google Sheet containing URLs
#     url_column = "Website domain"  
#     results = await process_urls_from_google_sheet(df, url_column)

#     import numpy as np
#     # Convert results to DataFrame and sanitize non-finite values
#     output_df = pd.DataFrame(results)
#     output_df = output_df.replace([np.inf, -np.inf, np.nan], None)

#     # Let's assume you want to write the "readability_score" values into the column that has header "Readability"
#     output_header = "Authority"

#     # Find the column index of the specified header in the sheet
#     try:
#         col_index = header.index(output_header)  
#         print(f"Found header '{output_header}' at column index {col_index}")
#     except ValueError:
#         print(f"Header '{output_header}' not found in the sheet!")
#         return

#     # Convert the zero-indexed column number to a column letter (Excel style; 1-indexed)
#     output_col_letter = column_to_letter(col_index + 1)
#     print(f"Header '{output_header}' is in column {output_col_letter}")

#     # Data rows in the sheet start at header_row_position+1
#     data_start_row = header_row_position + 1
#     num_data_rows = len(df)

#     # Prepare output data as a list of lists (each inner list is one cell value)
#     output_values = [[val] for val in output_df['authority_score'].tolist()]

#     # Build the range string for bulk update
#     update_range = f"{output_col_letter}{data_start_row}:{output_col_letter}{data_start_row + num_data_rows - 1}"
#     print(f"Updating range: {update_range}")

#     # Update the worksheet in the found range
#     worksheet_output.update(range_name=update_range, values=output_values)
#     print(f"Processed {len(results)} URLs. Output data updated to Google Sheet in range {update_range}.")

# if __name__ == "__main__":
#     asyncio.run(main())





import asyncio
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from playwright.async_api import Page, BrowserContext

async def process_urls_from_google_sheet(df, url_column):
    # Updated browser configuration
    browser_config = BrowserConfig(
        headless=False,
        verbose=True,
        # use_managed_browser=True,
        # user_data_dir="/Users/vuhainam/my_chrome_profile",
        # browser_type="chromium"
    )
    
    # Define extraction schema for accessibility score
    schema = {
    "name": "Result",
    "baseSelector": "div.css-10y00fk-content.css-die2lc.css-v2v3ur-contentFullWidth.css-agqhba-contentNoScrollMobile.css-1tt6ytp-contentAfterOpen",
    "fields": [
        {"name": "authority_score", "selector": "body > div:nth-child(6) > div > div > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > div:nth-child(2) > div > div > div > span", "type": "text"}
    ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema)
    results = []
    
    # Loop over the rows in the DataFrame (each row contains a target URL)
    for index, row in df.iterrows():
        target_url = row[url_column]
        print(f"Processing {index + 1}/{len(df)}: {target_url}")
        
        crawler = AsyncWebCrawler(config=browser_config)
        current_page = None
        
        # Hook: When page context is created
        async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
            nonlocal current_page
            current_page = page
            print("[HOOK] on_page_context_created - Page and context ready")
            return page
        
        # Hook: After navigating to a page
        async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
            nonlocal current_page
            current_page = page
            print(f"[HOOK] after_goto - Successfully loaded URL: {url}")
            
            # If we are on the accessibility checker form page, fill in the target URL and submit
            if url == "https://ahrefs.com/website-authority-checker/":
                try:
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    await page.wait_for_selector("input[class='css-hfjebg css-1mk4k1q css-wcs6']", timeout=60000)
                    await page.fill("input[class='css-hfjebg css-1mk4k1q css-wcs6']", target_url)
                    print(f"Filled form with URL: {target_url}")
                    await page.click("button[class='css-ygijhp css-1tyndxa css-1ip10c0 css-9cz4sg css-115l1wb']")
                    print("Clicked submit button")
                    await asyncio.sleep(1)

                    # Check if captcha appears in the known iframe using frame_locator
                    try:
                        # Wait for the iframe to load and be attached to the page
                        await page.wait_for_selector("iframe#cf-chl-widget-kmjv6", timeout=90000)

                        # Use frame_locator to target the iframe by its id
                        captcha_frame = page.frame_locator("iframe#cf-chl-widget-kmjv6").frame_element()

                        if captcha_frame:
                            # Wait for the captcha div to appear within the iframe
                            await captcha_frame.locator("div#content").wait_for(timeout=90000)
                            captcha_div = await captcha_frame.locator("div#content").element_handle()

                            if captcha_div:
                                checkbox = await captcha_frame.locator("input[type='checkbox']").element_handle()
                                if checkbox:
                                    print("Captcha detected in iframe. Clicking the checkbox for verification.")
                                    await checkbox.click()
                                    await asyncio.sleep(2)  # wait 2 seconds

                                    # Wait for the iframe to disappear (captcha solved)
                                    await page.wait_for_function("""
                                        () => {
                                            return document.querySelector('iframe#cf-chl-widget-kmjv6') === null;
                                        }
                                    """, timeout=90000)

                                    print("Captcha solved, iframe disappeared. Clicking submit button again.")
                                    await page.click("button[class='css-ygijhp css-1tyndxa css-1ip10c0 css-9cz4sg css-115l1wb']")
                                    print("Clicked submit button again after captcha")
                                    await asyncio.sleep(1)

                                else:
                                    print("Captcha checkbox not found in the iframe.")
                        else:
                            print("Captcha iframe not found.")

                    except Exception as e:
                        print(f"Captcha or iframe error: {e}")

                    # Check for error message
                    try:
                        error_visible = await page.evaluate("""() => {
                            const errorElement = document.querySelector("#fail[style*='display: grid'][style*='visibility: visible']");
                            return errorElement &&
                                (errorElement.style.display !== 'none') &&
                                errorElement.textContent &&
                                errorElement.textContent.trim() !== '';
                        }""")
                        if (error_visible):
                            error_message = await page.evaluate("""() => {
                                const errorElement = document.querySelector("#fail[style*='display: grid'][style*='visibility: visible']");
                                return errorElement ? errorElement.textContent.trim() : 'Unknown error';
                            }""")
                            print(f"Error detected for URL '{target_url}': {error_message}")
                            results.append({
                                'url': target_url,
                                'authority_score': None,
                                'error': f"Invalid URL: {error_message}"
                            })
                            return page  # Early return if error detected
                    except Exception as e:
                        print(f"Error checking for error message: {e}")

                    try:
                        await page.wait_for_selector("xpath=//div[@class='css-10y00fk-content css-die2lc css-v2v3ur-contentFullWidth css-agqhba-contentNoScrollMobile css-1tt6ytp-contentAfterOpen']", timeout=90000)
                        print("Results loaded successfully")

                        # Extract content here. Example: extract text from a specific element
                        try:
                            content_element = await page.query_selector("div[class='css-10y00fk-content css-die2lc css-v2v3ur-contentFullWidth css-agqhba-contentNoScrollMobile css-1tt6ytp-contentAfterOpen']")
                            if content_element:
                                content_text = await content_element.text_content()
                                print(f"Extracted content: {content_text}")
                                results.append({'url': target_url, 'content': content_text, 'error': None}) # example of adding extracted content to results.
                            else:
                                print ("Content element not found")
                                results.append({'url': target_url, 'content': None, 'error': 'Content element not found.'})
                        except Exception as extract_error:
                            print(f"Error extracting content: {extract_error}")
                            results.append({'url': target_url, 'content': None, 'error': f'Error extracting content: {extract_error}'})

                    except Exception as e:
                        print(f"Timeout waiting for results heading: {e}")
                        results.append({'url': target_url, 'content': None, 'error': f'Timeout waiting for results: {e}'})
                    await asyncio.sleep(5)

                except Exception as e:
                    print(f"Error in form submission: {str(e)}")
                    results.append({'url': target_url, 'content': None, 'error': f'Error in form submission: {str(e)}'})
                    
            return page
        
        crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
        crawler.crawler_strategy.set_hook("after_goto", after_goto)
        
        await crawler.start()
        
        session_id = f"session_{index}"
        crawler_run_config = CrawlerRunConfig(
            magic=True,
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy,
            page_timeout=120000,  # 120s timeout for the whole process
        )
        
        try:
            result = await crawler.arun(
                url="https://ahrefs.com/website-authority-checker/",
                config=crawler_run_config
            )
            
            # If the URL was already processed as invalid, skip further extraction
            if any(r['url'] == target_url and r.get('error', '').startswith('Invalid URL:') for r in results):
                print(f"Skipping extraction for already identified invalid URL: {target_url}")
                try:
                    await crawler.close()
                    print(f"Closed crawler for invalid URL: {target_url}")
                except Exception as e:
                    print(f"Error closing crawler: {e}")
                continue
            
            score = None
            
            # Method 1: Try to extract score directly using JavaScript
            if current_page:
                try:
                    error_visible = await current_page.evaluate("""() => {
                        const errorElement = document.querySelector("#fail[style*='display: grid'][style*='visibility: visible']");
                        return errorElement &&
                               (errorElement.style.display !== 'none') &&
                               errorElement.textContent &&
                               errorElement.textContent.trim() !== '';
                    }""")
                    
                    if error_visible:
                        error_message = await current_page.evaluate("""() => {
                            const errorElement = document.querySelector("#fail[style*='display: grid'][style*='visibility: visible']");
                            return errorElement ? errorElement.textContent.trim() : 'Unknown error';
                        }""")
                        print(f"Late error detected for URL '{target_url}': {error_message}")
                        results.append({
                            'url': target_url,
                            'authority_score': None,
                            'error': f"Invalid URL: {error_message}"
                        })
                        try:
                            await crawler.close()
                            print(f"Closed crawler for invalid URL: {target_url}")
                        except Exception as e:
                            print(f"Error closing crawler: {e}")
                        continue
                    
                    js_score = await current_page.evaluate("""() => {
                        const node = document.evaluate(
                            '/html/body/div[6]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/span',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        const scoreElement = node ? node.textContent : null;
                    }""")
                    if js_score:
                        score = js_score
                        print(f"Extracted score via JavaScript: {score}")
                except Exception as e:
                    print(f"JavaScript extraction failed: {e}")
            
            # Save the result if not already saved as an error
            if not any(r['url'] == target_url for r in results):
                results.append({
                    'url': target_url,
                    'authority_score': score
                })
            
        except Exception as e:
            print(f"Error processing {target_url}: {str(e)}")
            results.append({
                'url': target_url,
                'authority_score': None,
                'error': str(e)
            })
        
        try:
            await crawler.close()
            print(f"Closed crawler for URL: {target_url}")
        except Exception as e:
            print(f"Error closing crawler: {e}")
        
        # Delay between URLs to prevent rate limiting
        await asyncio.sleep(5)
    
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
    SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    # Open the spreadsheet by URL and select the worksheets for input and output
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8/edit?pli=1&gid=137734733#gid=137734733")
    worksheet_input = spreadsheet.worksheet("Test")
    worksheet_output = spreadsheet.worksheet("Test")

    # --- Specify Header Position for Input Data ---
    header_row_position = 5  
    all_values = worksheet_input.get_all_values()
    header = all_values[header_row_position - 1]  
    data_rows = all_values[header_row_position:]  
    df = pd.DataFrame(data_rows, columns=header)
    print("Input data from Google Sheet loaded successfully with header on row", header_row_position)

    # Define the name of the column in your Google Sheet containing URLs
    url_column = "Website domain"  
    results = await process_urls_from_google_sheet(df, url_column)

    # Convert results to DataFrame and sanitize non-finite values
    output_df = pd.DataFrame(results)
    output_df = output_df.replace([np.inf, -np.inf, np.nan], None)

    # Let's assume you want to write the "readability_score" values into the column that has header "Readability"
    output_header = "Authority"

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
    output_values = [[val] for val in output_df['authority_score'].tolist()]

    # Build the range string for bulk update
    update_range = f"{output_col_letter}{data_start_row}:{output_col_letter}{data_start_row + num_data_rows - 1}"
    print(f"Updating range: {update_range}")

    # Update the worksheet in the found range
    worksheet_output.update(range_name=update_range, values=output_values)
    print(f"Processed {len(results)} URLs. Output data updated to Google Sheet in range {update_range}.")

if __name__ == "__main__":
    asyncio.run(main())
