# from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, BrowserConfig
# import asyncio
# import requests
# from bs4 import BeautifulSoup
# import re

# async def extract_with_crawl4ai():
#     browser_config = BrowserConfig(
#         headless=True,  # Try with visible browser
#         # timeout=60000,   # Longer timeout (60 seconds)
#         # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#         # viewport={"width": 1920, "height": 1080}
#     )
    
#     crawler_config = CrawlerRunConfig(
#         cache_mode=CacheMode.BYPASS,
#         wait_for="body",
#         # wait_time=10,  # Wait 10 seconds after page load
#         # javascript_enabled=True,
#         # follow_redirects=True
#     )

#     url = "https://bicvietnam.net/ho-so-mua-nha-o-xa-hoi.html"
    
#     async with AsyncWebCrawler() as crawler:
#         print("Attempting to crawl with AsyncWebCrawler...")
#         result = await crawler.arun(
#             url,
#             config=crawler_config,
#             browser_config=browser_config
#         )
        
#         if result.success:
#             print("Crawl successful!")
#             internal_links = result.links.get("internal", [])
#             external_links = result.links.get("external", [])
#             print(f"Found {len(internal_links)} internal links.")
#             print(f"Found {len(external_links)} external links.")
#             print(f"Found {len(result.media)} media items.")
            
#             if internal_links:
#                 print("Sample Internal Link:", internal_links[0])
#             return True
#         else:
#             print(f"Crawl4AI failed: {result.error_message}")
#             if hasattr(result, 'html') and result.html:
#                 print(f"HTML was returned but processing failed. HTML length: {len(result.html)}")
#             return False

# def extract_with_requests():
#     print("\nAttempting fallback with direct requests...")
#     url = "https://bicvietnam.net/ho-so-mua-nha-o-xa-hoi.html"
    
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.5",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1"
#         }
        
#         response = requests.get(url, headers=headers, timeout=30)
#         print(f"Request status: {response.status_code}")
        
#         if response.status_code == 200:
#             html_content = response.text
#             print(f"Retrieved HTML length: {len(html_content)}")
            
#             # Basic link extraction with regex for debugging
#             base_url = "https://bicvietnam.net"
#             internal_links = []
            
#             # Try to parse with BeautifulSoup
#             try:
#                 soup = BeautifulSoup(html_content, 'html.parser')
#                 print("Successfully parsed with BeautifulSoup")
                
#                 for a_tag in soup.find_all('a', href=True):
#                     href = a_tag['href']
#                     if href.startswith('/') or href.startswith(base_url) or not (href.startswith('http') or href.startswith('https')):
#                         # This is an internal link
#                         full_url = href if href.startswith('http') else f"{base_url}{href if href.startswith('/') else '/' + href}"
#                         internal_links.append({
#                             "href": full_url,
#                             "text": a_tag.text.strip(),
#                             "base_domain": "bicvietnam.net"
#                         })
                
#                 print(f"Found {len(internal_links)} internal links with BeautifulSoup")
#                 if internal_links:
#                     print("Sample: ", internal_links[0])
                
#                 return True
#             except Exception as bs_error:
#                 print(f"BeautifulSoup parsing failed: {str(bs_error)}")
                
#                 # Fallback to regex for basic link extraction
#                 print("Falling back to regex extraction...")
#                 links = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html_content)
#                 print(f"Found {len(links)} links with regex")
#                 if links:
#                     print("Sample link:", links[0])
                
#                 return len(links) > 0
#         else:
#             print(f"Request failed with status code: {response.status_code}")
#             return False
#     except Exception as e:
#         print(f"Requests approach failed: {str(e)}")
#         return False

# async def main():
#     success = await extract_with_crawl4ai()
#     if not success:
#         success = extract_with_requests()
        
#     if not success:
#         print("\nBoth approaches failed. The website might be using techniques to prevent scraping.")
#         print("Recommendations:")
#         print("1. Try visiting the site manually to check if it's accessible")
#         print("2. The site might need specific cookies or session data")
#         print("3. Consider using a more specialized scraping tool like Selenium with custom scripts")
#         print("4. The site might have changed its structure or URL")

# if __name__ == "__main__":
#     asyncio.run(main())


import requests
from bs4 import BeautifulSoup
import asyncio
from urllib.parse import urljoin

async def extract_links_and_media(url):
    # Set up headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract base domain for determining internal vs external links
        base_domain = url.split('//', 1)[1].split('/', 1)[0].lower()
        if base_domain.startswith('www.'):
            base_domain = base_domain[4:]
            
        # Initialize containers for links and media
        internal_links = []
        external_links = []
        media_items = []
        
        # Extract links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)  # Handle relative URLs
            
            link_info = {
                "href": full_url,
                "text": a_tag.text.strip(),
                "title": a_tag.get('title', ''),
                "base_domain": full_url.split('//', 1)[1].split('/', 1)[0].lower() if '//' in full_url else base_domain
            }
            
            # Determine if internal or external link
            link_domain = link_info["base_domain"]
            if link_domain.startswith('www.'):
                link_domain = link_domain[4:]
                
            if link_domain == base_domain:
                internal_links.append(link_info)
            else:
                external_links.append(link_info)
        
        # Extract media (images)
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            full_url = urljoin(url, src)
            
            media_info = {
                "src": full_url,
                "alt": img_tag.get('alt', ''),
                "type": "image",
                "width": img_tag.get('width', ''),
                "height": img_tag.get('height', '')
            }
            
            media_items.append(media_info)
            
        # Print results
        print(f"Found {len(internal_links)} internal links.")
        print(f"Found {len(external_links)} external links.")
        print(f"Found {len(media_items)} media items.")
        
        if internal_links:
            print("\nSample Internal Link:", internal_links[0])
            
        if external_links:
            print("\nSample External Link:", external_links[0])
            
        if media_items:
            print("\nSample Media Item:", media_items[0])
            
        # Return the results as a dictionary similar to Crawl4AI structure
        return {
            "success": True,
            "url": url,
            "links": {
                "internal": internal_links,
                "external": external_links
            },
            "media": media_items
        }
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            "success": False,
            "url": url,
            "error_message": str(e)
        }

async def main():
    url = "https://bicvietnam.net/ho-so-mua-nha-o-xa-hoi.html"
    result = await extract_links_and_media(url)
    
    # You can use the result dictionary here for further processing
    if result["success"]:
        print("\nScraped successfully!")
        # Example: save to file, process further, etc.
    else:
        print("\nFailed to scrape:", result["error_message"])

if __name__ == "__main__":
    asyncio.run(main())