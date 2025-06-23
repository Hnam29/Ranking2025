# # Error processing "...": 'AsyncWebCrawler' object has no attribute 'current_page'
# import asyncio
# import pandas as pd
# import re
# import os
# import logging
# from datetime import datetime
# from typing import List, Dict, Any, Optional
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
# from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
# from playwright.async_api import Page, BrowserContext

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("pagespeed_crawler.log"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger("pagespeed_crawler")

# class PageSpeedCrawler:
#     """Class to handle PageSpeed Insights crawling and score extraction"""
    
#     def __init__(self, headless: bool = True, verbose: bool = True):
#         """Initialize the crawler with configuration"""
#         self.browser_config = BrowserConfig(
#             headless=headless,
#             verbose=verbose,
#             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
#         )
        
#         # Define extraction schema
#         self.schema = {
#             "name": "Results",
#             "baseSelector": "div.lh-sticky-header",
#             "fields": [
#                 {"name": "performance_score", "selector": "div.lh-gauge--pwa__wrapper:nth-child(1) div.lh-gauge__percentage", "type": "text"},
#                 {"name": "accessibility_score", "selector": "div.lh-gauge--pwa__wrapper:nth-child(2) div.lh-gauge__percentage", "type": "text"},
#                 {"name": "best_practices_score", "selector": "div.lh-gauge--pwa__wrapper:nth-child(3) div.lh-gauge__percentage", "type": "text"},
#                 {"name": "seo_score", "selector": "div.lh-gauge--pwa__wrapper:nth-child(4) div.lh-gauge__percentage", "type": "text"}
#             ]
#         }
        
#         self.extraction_strategy = JsonCssExtractionStrategy(self.schema)
#         self.crawler = None

#     async def setup(self):
#         """Set up the crawler with hooks"""
#         if self.crawler is None:
#             self.crawler = AsyncWebCrawler(config=self.browser_config)
            
#             # Attach hooks
#             self.crawler.crawler_strategy.set_hook("on_page_context_created", self._on_page_context_created)
#             self.crawler.crawler_strategy.set_hook("after_goto", self._after_goto)
            
#             # Start the crawler
#             await self.crawler.start()
    
#     async def _on_page_context_created(self, page: Page, context: BrowserContext, **kwargs):
#         """Hook called when page context is created"""
#         logger.info("Page and context ready")
#         # Set default navigation timeout to 60 seconds
#         page.set_default_navigation_timeout(60000)
#         return page
    
#     async def _after_goto(self, page: Page, context: BrowserContext, url: str, response, **kwargs):
#         """Hook called after page navigation"""
#         logger.info(f"Successfully loaded URL: {url}")
        
#         # Store the current target URL from the instance
#         target_url = getattr(self, "current_target_url", None)
        
#         # If we're on the form page and have a target URL, fill in the URL and submit
#         if url == "https://pagespeed.web.dev/" and target_url:
#             try:
#                 # Wait for the page to be fully loaded
#                 await page.wait_for_load_state("networkidle", timeout=15000)
                
#                 # Wait for the form input field
#                 await page.wait_for_selector("input[id='i4']", timeout=15000)
                
#                 # Fill the form with URL
#                 await page.fill("input[id='i4']", target_url)
#                 logger.info(f"Filled form with URL: {target_url}")
                
#                 # Click the button to submit
#                 await page.click("button[class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 c659ib']")
#                 logger.info("Clicked submit button")
                
#                 # Wait for results to load (looking for different selectors)
#                 selectors = [
#                     ".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']",
#                     "div.lh-gauge__percentage"
#                 ]
                
#                 for selector in selectors:
#                     try:
#                         await page.wait_for_selector(selector, timeout=90000)  # 90 seconds timeout
#                         logger.info(f"Results loaded successfully, found selector: {selector}")
#                         break
#                     except Exception as e:
#                         logger.warning(f"Selector {selector} not found: {e}")
                
#                 # Extra wait to ensure scores are fully loaded
#                 await asyncio.sleep(5)
                
#             except Exception as e:
#                 logger.error(f"Error in form submission: {str(e)}")
        
#         return page
    
#     async def extract_scores(self, page: Page) -> Dict[str, Any]:
#         """Extract scores using multiple methods"""
#         scores = {}
        
#         # Method 1: Try to get scores directly using JavaScript
#         try:
#             js_scores = await page.evaluate("""() => {
#                 const scores = {};
#                 const scoreElements = document.querySelectorAll('div.lh-gauge__percentage');
#                 const categories = ['performance', 'accessibility', 'best_practices', 'seo'];
                
#                 scoreElements.forEach((element, index) => {
#                     if (index < categories.length) {
#                         scores[categories[index]] = element.textContent;
#                     }
#                 });
                
#                 return scores;
#             }""")
            
#             if js_scores:
#                 scores.update(js_scores)
#                 logger.info(f"Extracted scores via JavaScript: {js_scores}")
#         except Exception as e:
#             logger.warning(f"JavaScript extraction failed: {e}")
        
#         # Method 2: Try screenshot for debugging
#         try:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             await page.screenshot(path=f"debug_screenshot_{timestamp}.png", full_page=True)
#             logger.info(f"Saved debug screenshot: debug_screenshot_{timestamp}.png")
#         except Exception as e:
#             logger.warning(f"Screenshot capture failed: {e}")
            
#         return scores
    
#     async def process_url(self, url: str) -> Dict[str, Any]:
#         """Process a single URL and return the results"""
#         result = {
#             'url': url,
#             'timestamp': datetime.now().isoformat(),
#             'success': False,
#         }
        
#         try:
#             # Set current target URL for the hooks to use
#             self.current_target_url = url
            
#             # Ensure crawler is set up
#             await self.setup()
            
#             session_id = f"session_{url.replace('://', '_').replace('/', '_')}"
            
#             # Configure the crawler run
#             crawler_run_config = CrawlerRunConfig(
#                 session_id=session_id,
#                 cache_mode=CacheMode.BYPASS,
#                 extraction_strategy=self.extraction_strategy,
#                 page_timeout=120000,  # 120s timeout
#             )
            
#             # Run the crawler
#             crawl_result = await self.crawler.arun(
#                 url="https://pagespeed.web.dev/",
#                 config=crawler_run_config
#             )
            
#             # Get the current page
#             current_page = self.crawler.current_page
            
#             # Extract scores
#             if current_page:
#                 scores = await self.extract_scores(current_page)
#                 result.update(scores)
#                 result['success'] = bool(scores)
                
#             # Additional data from crawl result
#             if hasattr(crawl_result, 'extracted_content') and crawl_result.extracted_content:
#                 logger.info(f"Raw extracted content: {crawl_result.extracted_content}")
#                 if isinstance(crawl_result.extracted_content, dict):
#                     extracted_results = crawl_result.extracted_content.get("Results", [])
#                     if extracted_results and isinstance(extracted_results, list):
#                         for item in extracted_results:
#                             if isinstance(item, dict):
#                                 result.update(item)
            
#         except Exception as e:
#             logger.error(f"Error processing {url}: {str(e)}")
#             result['error'] = str(e)
        
#         return result
    
#     async def close(self):
#         """Close the crawler and clean up resources"""
#         if self.crawler:
#             await self.crawler.close()
#             self.crawler = None
#             logger.info("Closed crawler")

# async def process_urls_from_excel(excel_file: str, url_column: str, batch_size: int = 10) -> List[Dict[str, Any]]:
#     """Process URLs from an Excel file in batches"""
#     # Load Excel file
#     df = pd.read_excel(excel_file)
    
#     # Get list of URLs
#     urls = df[url_column].tolist()
    
#     # Results list
#     all_results = []
    
#     # Create crawler
#     crawler = PageSpeedCrawler(headless=True, verbose=True)
    
#     # Process URLs in batches
#     for i in range(0, len(urls), batch_size):
#         batch = urls[i:i+batch_size]
#         logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
        
#         # Process each URL in the batch
#         for j, url in enumerate(batch):
#             logger.info(f"Processing {i+j+1}/{len(urls)}: {url}")
            
#             # Process the URL
#             result = await crawler.process_url(url)
#             all_results.append(result)
            
#             # Delay between URLs to prevent rate limiting
#             await asyncio.sleep(3)
        
#         # Save intermediate results
#         save_results_to_excel(all_results, "speed_results_intermediate.xlsx")
#         logger.info(f"Saved intermediate results for {len(all_results)} URLs")
    
#     # Clean up
#     await crawler.close()
    
#     return all_results

# def save_results_to_excel(results: List[Dict[str, Any]], filename: str):
#     """Save results to an Excel file"""
#     output_df = pd.DataFrame(results)
#     output_df.to_excel(filename, index=False)
#     logger.info(f"Results saved to {filename}")

# async def main():
#     # Configuration
#     excel_file = input("Enter path to Excel file: ").strip() or "/Users/vuhainam/Downloads/dataa.xlsx"
#     url_column = input("Enter column name containing URLs: ").strip() or "URL"
    
#     # Create output directory
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     output_dir = os.path.join(script_dir, "results")
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Process URLs
#     start_time = datetime.now()
#     logger.info(f"Starting processing at {start_time}")
    
#     results = await process_urls_from_excel(excel_file, url_column)
    
#     # Save final results
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_file = os.path.join(output_dir, f"speed_results_{timestamp}.xlsx")
#     save_results_to_excel(results, output_file)
    
#     end_time = datetime.now()
#     duration = end_time - start_time
#     logger.info(f"Completed processing {len(results)} URLs in {duration}")
#     logger.info(f"Results saved to {output_file}")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Process interrupted by user")
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")






# # WORKED
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
#         "baseSelector": "div.lh-sticky-header > a:nth-of-type(1)",
#         "fields": [
#             {"name": "speed_score", "selector": "div.lh-gauge__percentage", "type": "text"}
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
#             if url == "https://pagespeed.web.dev/":
#                 try:
#                     # Ensure the page is fully loaded with a generous timeout
#                     await page.wait_for_load_state("networkidle", timeout=15000)
                    
#                     # Wait for the form input field
#                     await page.wait_for_selector("input[id='i4']", timeout=15000)
                    
#                     # Fill the form with URL
#                     await page.fill("input[id='i4']", target_url)
#                     print(f"Filled form with URL: {target_url}")
                    
#                     # Click the button to submit
#                     await page.click("button[class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 c659ib']")
#                     print("Clicked submit button")
                    
#                     # Give the page time to start processing
#                     await asyncio.sleep(3)
                    
#                     # Wait for results to load with 60 second timeout
#                     try:
#                         await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
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
#                 url="https://pagespeed.web.dev/",
#                 config=crawler_run_config
#             )
            
#             # Initialize score as None
#             score = None
            
#             # Method 1: Try to get the score directly from the page using JavaScript
#             if current_page:
#                 try:
#                     # Evaluate JavaScript to get the score directly from the DOM
#                     js_score = await current_page.evaluate("""() => {
#                         const scoreElement = document.querySelector('div.lh-gauge__percentage');
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
#                                 score = items[0].get("speed_score")
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
#                 'speed_results': score
#             })
            
#         except Exception as e:
#             print(f"Error processing {target_url}: {str(e)}")
#             results.append({
#                 'url': target_url,
#                 'speed_results': None,
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
#     output_file = os.path.join(script_dir, "speed_results.xlsx")
#     output_df.to_excel(output_file, index=False)
#     print(f"Processed {len(results)} URLs. Results saved to speed_results.xlsx")

# if __name__ == "__main__":
#     asyncio.run(main())





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
        verbose=True,
        user_agent_mode="random"
    )
    
    # Define extraction schema for accessibility score
    schema = {
        "name": "Result",
        "baseSelector": "div.lh-sticky-header > a:nth-of-type(1)",
        "fields": [
            {"name": "speed_score", "selector": "div.lh-gauge__percentage", "type": "text"}
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
            if url == "https://pagespeed.web.dev/":
                try:
                    # Ensure the page is fully loaded with a generous timeout
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    
                    # Wait for the form input field
                    await page.wait_for_selector("input[id='i4']", timeout=15000)
                    
                    # Fill the form with URL
                    await page.fill("input[id='i4']", target_url)
                    print(f"Filled form with URL: {target_url}")
                    
                    # Click the button to submit
                    await page.click("button[class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 c659ib']")
                    print("Clicked submit button")
                    
                    # Give the page time to start processing
                    await asyncio.sleep(3)
                    
                    # Wait for results to load with 60 second timeout
                    try:
                        await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
                        print("Results loaded successfully")
                    except Exception as e:
                        print(f"Timeout waiting for results heading: {e}")
                        # Continue anyway - we'll try other methods
                        pass
                    
                    # Wait a bit more to ensure the score is rendered
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    print(f"Error in form submission: {str(e)}")
            
            # Additional handler for when we're on a desktop or mobile results page
            if "pagespeed.web.dev/analysis" in url:
                try:
                    # Wait for results to load
                    await page.wait_for_selector(".VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.eFAcqd[jsname='mxdR1e']", timeout=60000)
                    print("Results loaded successfully on analysis page")
                    # Wait a bit more to ensure the score is rendered
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"Timeout waiting for results on analysis page: {e}")
                    # Continue anyway
                    pass
                    
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
            page_timeout=180000,  # 180s timeout for the whole process (extended for multiple navigations)
        )
        
        try:
            # Run the crawler
            result = await crawler.arun(
                url="https://pagespeed.web.dev/",
                config=crawler_run_config
            )
            
            # Initialize scores
            mobile_score = None
            desktop_score = None
            mobile_score_recheck = None
            
            # Extract the initial mobile score
            if current_page:
                try:
                    # Evaluate JavaScript to get the first score directly from the DOM
                    mobile_score = await current_page.evaluate("""() => {
                        const scoreElement = document.querySelector('div.lh-gauge__percentage'); 
                        return scoreElement ? scoreElement.textContent : null;
                    }""")
                    if mobile_score:
                        print(f"Extracted mobile score via JavaScript: {mobile_score}")
                        
                        # Get the current URL (which should be the analysis URL with unique ID)
                        current_url = current_page.url
                        print(f"Current URL: {current_url}")
                        
                        # Check if we have a proper analysis URL with mobile factor
                        if "form_factor=mobile" in current_url and "pagespeed.web.dev/analysis" in current_url:
                            # Create desktop URL by replacing mobile with desktop
                            desktop_url = current_url.replace("form_factor=mobile", "form_factor=desktop")
                            print(f"Desktop URL: {desktop_url}")
                            
                            # Navigate to desktop URL
                            print("Navigating to desktop version...")
                            try:
                                await current_page.goto(desktop_url, timeout=60000)
                                # Wait for desktop results to load
                                await asyncio.sleep(3)  # Give some time for initial load
                                
                                # Extract desktop score
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
                                    print(f"Extracted desktop score via JavaScript: {desktop_score}")
                                
                                # Navigate back to the mobile version
                                print("Navigating back to mobile version...")
                                await current_page.goto(current_url, timeout=60000)
                                await asyncio.sleep(5)  # Give some time for reload
                                
                                # Extract mobile score again as a verification
                                mobile_score_recheck = await current_page.evaluate("""() => {
                                    const scoreElement = document.querySelector('div.lh-gauge__percentage');
                                    return scoreElement ? scoreElement.textContent : null;
                                }""")
                                
                                if mobile_score_recheck:
                                    print(f"Extracted mobile score again: {mobile_score_recheck}")
                                    
                                    # Compare the two mobile scores
                                    if mobile_score != mobile_score_recheck:
                                        print(f"WARNING: Mobile scores differ! First: {mobile_score}, Second: {mobile_score_recheck}")
                            
                            except Exception as e:
                                print(f"Error navigating between mobile and desktop: {e}")
                        else:
                            print("Current URL doesn't match expected pattern for switching to desktop view")
                            
                except Exception as e:
                    print(f"JavaScript extraction failed: {e}")
            
            # # Method 2: Try to parse the extracted content if we still don't have the mobile score
            # if not mobile_score and result.extracted_content:
            #     try:
            #         # Print the raw extracted content for debugging
            #         print(f"Raw extracted content: {result.extracted_content}")
                    
            #         # Handle various formats of extracted content
            #         if isinstance(result.extracted_content, dict):
            #             items = result.extracted_content.get("Result", [])
            #             if items and isinstance(items, list) and len(items) > 0:
            #                 if isinstance(items[0], dict):
            #                     mobile_score = items[0].get("speed_score")
            #                 elif isinstance(items[0], str):
            #                     mobile_score = items[0]
            #         elif isinstance(result.extracted_content, str):
            #             # Sometimes the result might be directly a string
            #             mobile_score = result.extracted_content
                        
            #         if mobile_score:
            #             print(f"Extracted mobile score from content structure: {mobile_score}")
            #     except Exception as e:
            #         print(f"Content structure extraction failed: {e}")
            
            # # Method 3: Fallback to regex on HTML if we still don't have the mobile score
            # if not mobile_score and result.html:
            #     try:
            #         # Try multiple regex patterns to find the score
            #         patterns = [
            #             r'<text[^>]*class="accessibility-score"[^>]*>(\d+)</text>',
            #             r'class="accessibility-score"[^>]*>(\d+)<',
            #             r'id="accessibility-score"[^>]*>(\d+)<',
            #             r'"accessibility-score">(\d+)<',
            #         ]
                    
            #         for pattern in patterns:
            #             score_match = re.search(pattern, result.html)
            #             if score_match:
            #                 mobile_score = score_match.group(1)
            #                 print(f"Found mobile score in HTML using pattern: {pattern}")
            #                 print(f"Mobile Score: {mobile_score}")
            #                 break
                    
            #         # If we still don't have a score, save a sample of the HTML
            #         if not mobile_score:
            #             print("No score found in HTML. Saving sample...")
            #             # Save the HTML to a file for analysis
            #             with open(f"html_sample_{target_url.replace('/', '_')}.html", "w", encoding="utf-8") as f:
            #                 f.write(result.html[:10000])  # Save first 10K chars
            #             print(f"HTML sample saved to html_sample_{target_url.replace('/', '_')}.html")
            #     except Exception as e:
            #         print(f"Regex extraction failed: {e}")
            
            # Calculate average if we have both scores
            avg_score = None
            if mobile_score is not None and desktop_score is not None:
                try:
                    # Convert scores to numbers (removing any non-numeric characters)
                    mobile_score_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(mobile_score))))
                    desktop_score_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(desktop_score))))
                    
                    # Calculate average
                    avg_score = (mobile_score_num + desktop_score_num) / 2
                    print(f"Calculated average score: {avg_score}")
                except Exception as e:
                    print(f"Error calculating average: {e}")
            
            # Store the results
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
    output_file = os.path.join(script_dir, "speed_results.xlsx")
    output_df.to_excel(output_file, index=False)
    print(f"Processed {len(results)} URLs. Results saved to speed_results.xlsx")

if __name__ == "__main__":
    asyncio.run(main())