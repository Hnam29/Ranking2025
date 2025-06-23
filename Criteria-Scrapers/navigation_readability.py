# SOLVE UNABLE TO LOOKUP URL (DONE)
# USE SESSION_ID TO MAINTAIN THE SESSION, AVOID OPENING AND CLOSING BROWSER AGAIN AND AGAIN

import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def process_urls_from_excel(excel_file, url_column):
    # Load Excel file
    df = pd.read_excel(excel_file)
    
    # Start playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  
        
        # Process each URL
        results = []
        base_url = "https://www.webfx.com/tools/read-able/"  
        
        for index, row in df.iterrows():
            excel_url = row[url_column]
            print(f"Processing {index + 1}/{len(df)}: {excel_url}")
            
            # Create a new context and page
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate and fill form
                await page.goto(base_url)
                input_element = await page.wait_for_selector("input[id='uri']", timeout=5000)
                await input_element.fill(excel_url)
                
                # Click submit
                button = await page.wait_for_selector("button[type='submit']", timeout=5000)
                await button.click()
                
                success = False
                risk_rating = None
                
                # Wait briefly for any response
                await page.wait_for_timeout(3000)
                
                # Check if results appeared
                results_element = await page.query_selector("div#generator-results-wrapper > div > div > div")
                
                if results_element:
                    # Results found on first try
                    success = True
                else:
                    # Results not found, check if it's a URL format issue
                    error_element = await page.query_selector("div.error-message-selector")
                    
                    # Try with https prefix
                    await input_element.fill("")
                    new_url = "https://" + excel_url
                    await input_element.fill(new_url)
                    await button.click()
                    
                    try:
                        # Wait for results after second attempt
                        await page.wait_for_selector("div#generator-results-wrapper > div > div > div", timeout=30000)
                        success = True
                    except:
                        # Second attempt also failed
                        print(f"URL not accessible even with https prefix: {excel_url}")
                
                if success:
                    # Extract the risk rating
                    risk_rating = await page.evaluate("""() => {
                        const element = document.querySelector('div#generator-results-wrapper > div > div > div');
                        return element ? element.textContent.trim() : null;
                    }""")
                    
                    results.append({
                        'url': excel_url,
                        'readability_score': risk_rating
                    })
                    
                    if risk_rating:
                        print(f"Extracted readability score: {risk_rating}")

            except Exception as e:
                print(f"Error processing {excel_url}: {str(e)}")
                results.append({
                    'url': excel_url,
                    'security_risk': None,
                    'error': str(e)
                })
            finally:
                # Close the context
                await context.close()
        
        # Return all results
        return results

async def main():
    # Configuration
    excel_file = "/Users/vuhainam/Downloads/dataa.xlsx"  
    url_column = "URL"       
    
    # Process URLs
    results = await process_urls_from_excel(
        excel_file, 
        url_column
    )
    
    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_excel("readability_results.xlsx", index=False)
    print(f"Processed {len(results)} URLs. Results saved to readability_results.xlsx")

if __name__ == "__main__":
    asyncio.run(main())