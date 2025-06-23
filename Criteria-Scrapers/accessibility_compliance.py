# # ISSUE: MANUALLY SCORE 68 BUT CRAWLER SCORE 75
# # UNSOLVED: CASE URL GOT ERROR 
# import asyncio
# import pandas as pd
# import re
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
# from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
# from playwright.async_api import Page, BrowserContext

# async def process_urls_from_excel(excel_file, url_column):
#     # Load Excel file
#     df = pd.read_excel(excel_file)
    
#     # Configure the browser
#     browser_config = BrowserConfig(
#         headless=True,
#         verbose=True
#     )
    
#     # Define extraction schema for accessibility score
#     schema = {
#         "name": "Result",
#         "baseSelector": "div.progress-circle",
#         "fields": [
#             {"name": "accessibility_score", "selector": "text.accessibility-score", "type": "text"}
#         ]
#     }
    
#     # Create extraction strategy
#     extraction_strategy = JsonCssExtractionStrategy(schema)
    
#     # Results list
#     results = []
    
#     # Create a new crawler instance for each URL to prevent context closure issues
#     for index, row in df.iterrows():
#         target_url = row[url_column]
#         print(f"Processing {index + 1}/{len(df)}: {target_url}")
        
#         # Create a fresh crawler instance for each URL
#         crawler = AsyncWebCrawler(config=browser_config)
        
#         # Variable to store current page for later extraction
#         current_page = None
        
#         # Define hook for page context creation
#         async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
#             nonlocal current_page
#             current_page = page
#             print("[HOOK] on_page_context_created - Page and context ready")
#             return page
        
#         # Define hook for after navigation
#         async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
#             nonlocal current_page
#             current_page = page
#             print(f"[HOOK] after_goto - Successfully loaded URL: {url}")
            
#             # If we're on the form page, fill in the URL and submit
#             if url == "https://aeldata.com/accessibility-checker/":
#                 try:
#                     # Ensure the page is fully loaded with a generous timeout
#                     await page.wait_for_load_state("networkidle", timeout=15000)
                    
#                     # Wait for the form input field
#                     await page.wait_for_selector("input[id='asc-form-input']", timeout=15000)
                    
#                     # Fill the form with URL
#                     await page.fill("input[id='asc-form-input']", target_url)
#                     print(f"Filled form with URL: {target_url}")
                    
#                     # Click the button to submit
#                     await page.click("button[id='score-button']")
#                     print("Clicked submit button")
                    
#                     # Give the page time to start processing
#                     await asyncio.sleep(3)
                    
#                     # Wait for results to load with 60 second timeout
#                     try:
#                         await page.wait_for_selector("#asc-heading", timeout=60000)
#                         print("Results loaded successfully")
#                     except Exception as e:
#                         print(f"Timeout waiting for results heading: {e}")
#                         # Continue anyway - we'll try other methods
#                         pass
                    
#                     # Wait a bit more to ensure the score is rendered
#                     await asyncio.sleep(5)
                    
#                 except Exception as e:
#                     print(f"Error in form submission: {str(e)}")
                    
#             return page
        
#         # Attach hooks
#         crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
#         crawler.crawler_strategy.set_hook("after_goto", after_goto)
        
#         # Start the crawler
#         await crawler.start()
        
#         session_id = f"session_{index}"
        
#         # Configure the crawler run
#         crawler_run_config = CrawlerRunConfig(
#             session_id=session_id,
#             cache_mode=CacheMode.BYPASS,
#             extraction_strategy=extraction_strategy,
#             page_timeout=120000,  # 120s timeout for the whole process
#         )
        
#         try:
#             # Run the crawler
#             result = await crawler.arun(
#                 url="https://aeldata.com/accessibility-checker/",
#                 config=crawler_run_config
#             )
            
#             # Initialize score as None
#             score = None
            
#             # Method 1: Try to get the score directly from the page using JavaScript
#             if current_page:
#                 try:
#                     # Evaluate JavaScript to get the score directly from the DOM
#                     js_score = await current_page.evaluate("""() => {
#                         const scoreElement = document.querySelector('text.accessibility-score');
#                         return scoreElement ? scoreElement.textContent : null;
#                     }""")
#                     if js_score:
#                         score = js_score
#                         print(f"Extracted score via JavaScript: {score}")
#                 except Exception as e:
#                     print(f"JavaScript extraction failed: {e}")
            
#             # Method 2: Try to parse the extracted content 
#             if not score and result.extracted_content:
#                 try:
#                     # Print the raw extracted content for debugging
#                     print(f"Raw extracted content: {result.extracted_content}")
                    
#                     # Handle various formats of extracted content
#                     if isinstance(result.extracted_content, dict):
#                         items = result.extracted_content.get("Result", [])
#                         if items and isinstance(items, list) and len(items) > 0:
#                             if isinstance(items[0], dict):
#                                 score = items[0].get("accessibility_score")
#                             elif isinstance(items[0], str):
#                                 score = items[0]
#                     elif isinstance(result.extracted_content, str):
#                         # Sometimes the result might be directly a string
#                         score = result.extracted_content
                        
#                     if score:
#                         print(f"Extracted score from content structure: {score}")
#                 except Exception as e:
#                     print(f"Content structure extraction failed: {e}")
            
#             # Method 3: Fallback to regex on HTML
#             if not score and result.html:
#                 try:
#                     # Try multiple regex patterns to find the score
#                     patterns = [
#                         r'<text[^>]*class="accessibility-score"[^>]*>(\d+)</text>',
#                         r'class="accessibility-score"[^>]*>(\d+)<',
#                         r'id="accessibility-score"[^>]*>(\d+)<',
#                         r'"accessibility-score">(\d+)<',
#                     ]
                    
#                     for pattern in patterns:
#                         score_match = re.search(pattern, result.html)
#                         if score_match:
#                             score = score_match.group(1)
#                             print(f"Found score in HTML using pattern: {pattern}")
#                             print(f"Score: {score}")
#                             break
                    
#                     # If we still don't have a score, save a sample of the HTML
#                     if not score:
#                         print("No score found in HTML. Saving sample...")
#                         # Save the HTML to a file for analysis
#                         with open(f"html_sample_{target_url.replace('/', '_')}.html", "w", encoding="utf-8") as f:
#                             f.write(result.html[:10000])  # Save first 10K chars
#                         print(f"HTML sample saved to html_sample_{target_url.replace('/', '_')}.html")
#                 except Exception as e:
#                     print(f"Regex extraction failed: {e}")
            
#             # Store the result
#             results.append({
#                 'url': target_url,
#                 'accessibility_compliance': score
#             })
            
#         except Exception as e:
#             print(f"Error processing {target_url}: {str(e)}")
#             results.append({
#                 'url': target_url,
#                 'accessibility_compliance': None,
#                 'error': str(e)
#             })
        
#         # Clean up and close this crawler instance
#         try:
#             await crawler.close()
#             print(f"Closed crawler for URL: {target_url}")
#         except Exception as e:
#             print(f"Error closing crawler: {e}")
        
#         # Add a delay between URLs to prevent rate limiting
#         await asyncio.sleep(5)
    
#     # Return results
#     return results

# async def main():
#     # Configuration
#     excel_file = "/Users/vuhainam/Downloads/dataa.xlsx"  # Path to your Excel file
#     url_column = "URL"   # Column name containing URLs
    
#     # Process URLs
#     results = await process_urls_from_excel(
#         excel_file, 
#         url_column
#     )
    
#     # Save results
#     output_df = pd.DataFrame(results)
#     import os
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     output_file = os.path.join(script_dir, "accessibility_results.xlsx")
#     output_df.to_excel(output_file, index=False)
#     print(f"Processed {len(results)} URLs. Results saved to accessibility_results.xlsx")

# if __name__ == "__main__":
#     asyncio.run(main())



# # ISSUE SOLVED: MANUALLY SCORE 68 BUT CRAWLER SCORE 75 => CANNOT LOAD OR OUT OF TIMEOUT, SCORE AUTO 75 => BECAUSE OF TIMEOUT VALUE TOO SHORT (MAYBE)
import asyncio
import pandas as pd
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from playwright.async_api import Page, BrowserContext

async def process_urls_from_excel(excel_file, url_column):
    # Load Excel file
    df = pd.read_excel(excel_file)
    
    # Configure the browser
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )
    
    # Define extraction schema for accessibility score
    schema = {
        "name": "Result",
        "baseSelector": "div.progress-circle",
        "fields": [
            {"name": "accessibility_score", "selector": "text.accessibility-score", "type": "text"}
        ]
    }
    
    # Create extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema)
    
    # Results list
    results = []
    
    # Create a new crawler instance for each URL to prevent context closure issues
    for index, row in df.iterrows():
        target_url = row[url_column]
        print(f"Processing {index + 1}/{len(df)}: {target_url}")
        
        # Create a fresh crawler instance for each URL
        crawler = AsyncWebCrawler(config=browser_config)
        
        # Variable to store current page for later extraction
        current_page = None
        
        # Define hook for page context creation
        async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
            nonlocal current_page
            current_page = page
            print("[HOOK] on_page_context_created - Page and context ready")
            return page
        
        # Define hook for after navigation
        async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
            nonlocal current_page
            current_page = page
            print(f"[HOOK] after_goto - Successfully loaded URL: {url}")
            
            # If we're on the form page, fill in the URL and submit
            if url == "https://aeldata.com/accessibility-checker/":
                try:
                    # Ensure the page is fully loaded with a generous timeout
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    
                    # Wait for the form input field
                    await page.wait_for_selector("input[id='asc-form-input']", timeout=60000)
                    
                    # Fill the form with URL
                    await page.fill("input[id='asc-form-input']", target_url)
                    print(f"Filled form with URL: {target_url}")
                    
                    # Click the button to submit
                    await page.click("button[id='score-button']")
                    print("Clicked submit button")
                    
                    # Give the page time to start processing
                    await asyncio.sleep(3)
                    
                    # Check for error message first
                    try:
                        # Check if error message is visible
                        error_visible = await page.evaluate("""() => {
                            const errorElement = document.querySelector('#error-message');
                            return errorElement && 
                                  (errorElement.style.display !== 'none') && 
                                  errorElement.textContent && 
                                  errorElement.textContent.trim() !== '';
                        }""")
                        
                        if error_visible:
                            # Extract the error message text
                            error_message = await page.evaluate("""() => {
                                const errorElement = document.querySelector('#error-message');
                                return errorElement ? errorElement.textContent.trim() : 'Unknown error';
                            }""")
                            
                            print(f"Error detected for URL '{target_url}': {error_message}")
                            # Add to results with error message and skip further processing
                            results.append({
                                'url': target_url,
                                'accessibility_compliance': None,
                                'error': f"Invalid URL: {error_message}"
                            })
                            return page  # Return early to skip further processing
                    except Exception as e:
                        print(f"Error checking for error message: {e}")
                    
                    # If no error, wait for results to load with 60 second timeout
                    try:
                        await page.wait_for_selector("#asc-heading", timeout=60000)
                        print("Results loaded successfully")
                    except Exception as e:
                        print(f"Timeout waiting for results heading: {e}")
                        # Continue anyway - we'll try other methods
                        pass
                    
                    # Wait a bit more to ensure the score is rendered
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    print(f"Error in form submission: {str(e)}")
                    
            return page
        
        # Attach hooks
        crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
        crawler.crawler_strategy.set_hook("after_goto", after_goto)
        
        # Start the crawler
        await crawler.start()
        
        session_id = f"session_{index}"
        
        # Configure the crawler run
        crawler_run_config = CrawlerRunConfig(
            session_id=session_id,
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy,
            page_timeout=120000,  # 120s timeout for the whole process
        )
        
        try:
            # Run the crawler
            result = await crawler.arun(
                url="https://aeldata.com/accessibility-checker/",
                config=crawler_run_config
            )
            
            # Check if we already processed this URL as invalid in the after_goto hook
            if any(r['url'] == target_url and r['error'] and r['error'].startswith('Invalid URL:') for r in results):
                print(f"Skipping extraction for already identified invalid URL: {target_url}")
                
                # Clean up and close this crawler instance
                try:
                    await crawler.close()
                    print(f"Closed crawler for invalid URL: {target_url}")
                except Exception as e:
                    print(f"Error closing crawler: {e}")
                
                # Skip to the next URL
                continue
            
            # Initialize score as None
            score = None
            
            # Method 1: Try to get the score directly from the page using JavaScript
            if current_page:
                try:
                    # Check again for error message (in case it appeared after our initial check)
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
                            return errorElement ? errorElement.textContent.trim() : 'Unknown error';
                        }""")
                        
                        print(f"Late error detected for URL '{target_url}': {error_message}")
                        results.append({
                            'url': target_url,
                            'accessibility_compliance': None,
                            'error': f"Invalid URL: {error_message}"
                        })
                        
                        # Clean up and close this crawler instance
                        try:
                            await crawler.close()
                            print(f"Closed crawler for invalid URL: {target_url}")
                        except Exception as e:
                            print(f"Error closing crawler: {e}")
                        
                        continue  # Skip to the next URL
                    
                    # Evaluate JavaScript to get the score directly from the DOM
                    js_score = await current_page.evaluate("""() => {
                        const scoreElement = document.querySelector('text.accessibility-score');
                        return scoreElement ? scoreElement.textContent : null;
                    }""")
                    if js_score:
                        score = js_score
                        print(f"Extracted score via JavaScript: {score}")
                except Exception as e:
                    print(f"JavaScript extraction failed: {e}")
            
            # Method 2: Try to parse the extracted content 
            if not score and result.extracted_content:
                try:
                    # Print the raw extracted content for debugging
                    print(f"Raw extracted content: {result.extracted_content}")
                    
                    # Handle various formats of extracted content
                    if isinstance(result.extracted_content, dict):
                        items = result.extracted_content.get("Result", [])
                        if items and isinstance(items, list) and len(items) > 0:
                            if isinstance(items[0], dict):
                                score = items[0].get("accessibility_score")
                            elif isinstance(items[0], str):
                                score = items[0]
                    elif isinstance(result.extracted_content, str):
                        # Sometimes the result might be directly a string
                        score = result.extracted_content
                        
                    if score:
                        print(f"Extracted score from content structure: {score}")
                except Exception as e:
                    print(f"Content structure extraction failed: {e}")
            
            # Method 3: Fallback to regex on HTML
            if not score and result.html:
                try:
                    # Try multiple regex patterns to find the score
                    patterns = [
                        r'<text[^>]*class="accessibility-score"[^>]*>(\d+)</text>',
                        r'class="accessibility-score"[^>]*>(\d+)<',
                        r'id="accessibility-score"[^>]*>(\d+)<',
                        r'"accessibility-score">(\d+)<',
                    ]
                    
                    for pattern in patterns:
                        score_match = re.search(pattern, result.html)
                        if score_match:
                            score = score_match.group(1)
                            print(f"Found score in HTML using pattern: {pattern}")
                            print(f"Score: {score}")
                            break
                    
                    # If we still don't have a score, save a sample of the HTML
                    if not score:
                        print("No score found in HTML. Saving sample...")
                        # Save the HTML to a file for analysis
                        with open(f"html_sample_{target_url.replace('/', '_')}.html", "w", encoding="utf-8") as f:
                            f.write(result.html[:10000])  # Save first 10K chars
                        print(f"HTML sample saved to html_sample_{target_url.replace('/', '_')}.html")
                except Exception as e:
                    print(f"Regex extraction failed: {e}")
            
            # Store the result if we haven't already stored it as an error
            if not any(r['url'] == target_url for r in results):
                results.append({
                    'url': target_url,
                    'accessibility_compliance': score
                })
            
        except Exception as e:
            print(f"Error processing {target_url}: {str(e)}")
            results.append({
                'url': target_url,
                'accessibility_compliance': None,
                'error': str(e)
            })
        
        # Clean up and close this crawler instance
        try:
            await crawler.close()
            print(f"Closed crawler for URL: {target_url}")
        except Exception as e:
            print(f"Error closing crawler: {e}")
        
        # Add a delay between URLs to prevent rate limiting
        await asyncio.sleep(5)
    
    # Return results
    return results

async def main():
    # Configuration
    excel_file = "/Users/vuhainam/Downloads/dataa.xlsx"  # Path to your Excel file
    url_column = "URL"   # Column name containing URLs
    
    # Process URLs
    results = await process_urls_from_excel(
        excel_file, 
        url_column
    )
    
    # Save results
    output_df = pd.DataFrame(results)
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "accessibility_results.xlsx")
    output_df.to_excel(output_file, index=False)
    print(f"Processed {len(results)} URLs. Results saved to accessibility_results.xlsx")

if __name__ == "__main__":
    asyncio.run(main())