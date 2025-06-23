# ISSUE: Cannot contact SiteCheck server. Please check your Internet connection -> CANNOT CLICK ON THE BUTTON TO GET RESULT
# USE SESSION_ID TO MAINTAIN THE SESSION, AVOID OPENING AND CLOSING BROWSER AGAIN AND AGAIN
import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def process_urls_from_excel(excel_file, url_column):
    # Load Excel file
    df = pd.read_excel(excel_file)
    
    # Start playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to False to see the browser
        
        # Process each URL
        results = []
        base_url = "https://sitecheck.sucuri.net/"  # Replace with your actual form page URL
        
        for index, row in df.iterrows():
            excel_url = row[url_column]
            print(f"Processing {index + 1}/{len(df)}: {excel_url}")
            
            # Create a new context and page
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate to the form page
                await page.goto(base_url)
                
                # Fill the form with URL from Excel
                input_element = await page.wait_for_selector("input[id='websiteurl']", timeout=5000)
                if input_element:
                    await input_element.fill(excel_url)
                    print(f"Filled form with URL: {excel_url}")
                
                # Click the button
                button = await page.wait_for_selector("button[type='submit']", timeout=5000)
                if button:
                    await button.click()
                    print(f"Clicked submit button")
                
                # Wait for data to appear - using the correct selector from your HTML
                await page.wait_for_selector("div.rating-indicators > span.active", timeout=60000)
                print(f"Found security risk rating")
                
                # Extract the security risk rating
                risk_rating = await page.evaluate("""() => {
                    const element = document.querySelector('div.rating-indicators > span.active');
                    return element ? element.textContent.trim() : null;
                }""")
                
                results.append({
                    'url': excel_url,
                    'security_risk': risk_rating
                })
                
                print(f"Extracted security risk: {risk_rating}")
                
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
        
        # Close browser
        await browser.close()
        
        # Return all results
        return results

async def main():
    # Configuration
    excel_file = "/Users/vuhainam/Downloads/dataa.xlsx"  # Path to your Excel file
    url_column = "URL"        # Column name containing URLs
    
    # Process URLs
    results = await process_urls_from_excel(
        excel_file, 
        url_column
    )
    
    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_excel("security_results.xlsx", index=False)
    print(f"Processed {len(results)} URLs. Results saved to security_results.xlsx")

if __name__ == "__main__":
    asyncio.run(main())