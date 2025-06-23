# # CRAWL 1 URL
# import asyncio
# from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
# from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
# import json
# import os

# async def extract():
#     list_schema = {
#         "name": "App",
#         "baseSelector": "#charts-content-section > ol > li",
#         "fields": [
#             {"name": "NAME", "selector": ".we-clamp.we-clamp--visual", "type": "text"},
#             {"name": "URL", "selector": "a", "type": "attribute", "attribute": "href"}
#         ]
#     }
    
#     extraction_strategy = JsonCssExtractionStrategy(list_schema, verbose=True)
    
#     list_config = CrawlerRunConfig(
#         cache_mode=CacheMode.BYPASS,
#         extraction_strategy=extraction_strategy,
#         scan_full_page=True,
#         scroll_delay=2.0,
#         wait_for="js:() => document.body.getElementsByClassName('l-column--grid small-valign-top we-lockup--in-app-shelf l-column small-6 medium-3 large-2').length >= 100",
#     )
    
#     async with AsyncWebCrawler() as crawler:
#         list_result = await crawler.arun(
#             url = "https://apps.apple.com/vn/charts/ipad/giáo-dục-apps/6017?l=vi&chart=top-free",
#             config=list_config
#         )
        
#         # Debug the actual output structure
#         print("Extraction result type:", type(list_result.extracted_content))
#         print("Sample of raw extraction result:", list_result.extracted_content[:100] if list_result.extracted_content else "No content extracted")
        
#         # Process the result based on its actual structure
#         all_apps = []
#         raw_result = list_result.extracted_content
        
#         # If the result is a string, try to parse it as JSON
#         if isinstance(raw_result, str):
#             try:
#                 parsed_result = json.loads(raw_result)
#                 if isinstance(parsed_result, list):
#                     all_apps = parsed_result
#                 else:
#                     print("Warning: Parsed result is not a list. Using as is.")
#                     all_apps = [parsed_result]
#             except json.JSONDecodeError:
#                 print("Warning: Could not parse extracted content as JSON. Using raw string.")
#                 all_apps = [{"raw_content": raw_result}]
#         elif isinstance(raw_result, list):
#             # If it's already a list, check if items are dictionaries
#             if all(isinstance(item, dict) for item in raw_result):
#                 all_apps = raw_result
#             else:
#                 # If items are strings, try to process each one
#                 processed_apps = []
#                 for item in raw_result:
#                     if isinstance(item, str):
#                         try:
#                             app_obj = json.loads(item)
#                             processed_apps.append(app_obj)
#                         except json.JSONDecodeError:
#                             # If individual items can't be parsed, create simple objects
#                             processed_apps.append({"content": item})
#                     else:
#                         processed_apps.append(item)
#                 all_apps = processed_apps
#         else:
#             print("Warning: Unexpected result type. Using as is.")
#             all_apps = [{"raw_content": str(raw_result)}]
    
#     # # Ensure the data is in a readable format for humans
#     # print("\nHuman-readable App List:")
#     # if all_apps:
#     #     for i, app in enumerate(all_apps):
#     #         if isinstance(app, dict):
#     #             if "NAME" in app and "URL" in app:
#     #                 print(f"{i+1}. {app['NAME']}")
#     #                 print(f"   URL: {app['URL']}")
#     #             else:
#     #                 print(f"{i+1}. App details:")
#     #                 for key, value in app.items():
#     #                     print(f"   {key}: {value}")
#     #         else:
#     #             print(f"{i+1}. {app}")
#     #         print()
#     # else:
#     #     print("No apps extracted.")
    
#     # Construct the file path relative to the script's directory
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     output_file = os.path.join(script_dir, "final.json")
    
#     # Save data to file in a format that humans can read
#     with open(output_file, "w", encoding="utf-8") as json_file:
#         if all_apps:
#             json.dump(all_apps, json_file, ensure_ascii=False, indent=4)
#             print(f"Complete data saved to: {output_file}")
#         else:
#             # Save the raw content if processing failed
#             json_file.write(str(list_result.extracted_content))
#             print(f"Raw content saved to: {output_file}")
    
#     # # Also save a plaintext version for easier reading
#     # text_file = os.path.join(script_dir, "apps_list.txt")
#     # with open(text_file, "w", encoding="utf-8") as f:
#     #     for i, app in enumerate(all_apps):
#     #         if isinstance(app, dict):
#     #             if "NAME" in app and "URL" in app:
#     #                 f.write(f"{i+1}. {app['NAME']}\n")
#     #                 f.write(f"   URL: {app['URL']}\n")
#     #             else:
#     #                 f.write(f"{i+1}. App details:\n")
#     #                 for key, value in app.items():
#     #                     f.write(f"   {key}: {value}\n")
#     #         else:
#     #             f.write(f"{i+1}. {app}\n")
#     #         f.write("\n")
#     # print(f"Plain text list saved to: {text_file}")

# if __name__ == "__main__":
#     asyncio.run(extract())










# CRAWL BATCH OF URLS
import asyncio
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai import CrawlerMonitor, DisplayMode
import json
import os

async def extract():
    list_schema = {
        "name": "App",
        "baseSelector": "#charts-content-section > ol > li",
        "fields": [
            {"name": "NAME", "selector": ".we-clamp.we-clamp--visual", "type": "text"},
            {"name": "URL", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(list_schema, verbose=True)
    
    list_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        scan_full_page=True,
        scroll_delay=2.0,
        wait_for="js:() => document.body.getElementsByClassName('l-column--grid small-valign-top we-lockup--in-app-shelf l-column small-6 medium-3 large-2').length >= 100",
    )
    
    # Setup dispatcher for parallel crawling
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=80.0,  # Pause if memory exceeds 70%
        check_interval=1.0,             # Check memory every second
        max_session_permit=2,           # Allow 4 concurrent tasks
        monitor=CrawlerMonitor(
            max_visible_rows=15,
            display_mode=DisplayMode.DETAILED
        )
    )
    
    # List of URLs to crawl
    urls = [
        "https://apps.apple.com/vn/charts/ipad/giáo-dục-apps/6017?l=vi&chart=top-free",
        "https://apps.apple.com/vn/charts/iphone/giáo-dục-apps/6017?l=vi&chart=top-free",
        "https://apps.apple.com/vn/charts/iphone/giáo-dục-apps/6017?l=vi&chart=top-paid",
        "https://apps.apple.com/vn/charts/ipad/giáo-dục-apps/6017?l=vi&chart=top-paid"
    ]
    
    async with AsyncWebCrawler() as crawler:
        # Use arun_many to process URLs in parallel
        results = await crawler.arun_many(
            urls=urls,
            config=list_config,
            dispatcher=dispatcher
        )
        
        # Process all results
        all_apps = []
        for result in results:
            if not result.success:
                print(f"Failed to crawl {result.url}: {result.error_message}")
                continue
                
            raw_result = result.extracted_content
            
            # Process the raw content
            if isinstance(raw_result, str):
                try:
                    parsed_result = json.loads(raw_result)
                    if isinstance(parsed_result, list):
                        all_apps.extend(parsed_result)
                    else:
                        all_apps.append(parsed_result)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse content from {result.url}")
            elif isinstance(raw_result, list):
                # If it's already a list, process accordingly
                processed_items = []
                for item in raw_result:
                    if isinstance(item, dict):
                        processed_items.append(item)
                    elif isinstance(item, str):
                        try:
                            app_obj = json.loads(item)
                            processed_items.append(app_obj)
                        except json.JSONDecodeError:
                            processed_items.append({"content": item})
                all_apps.extend(processed_items)
    
    # Save results to file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "app_store_search_results.json")
    
    with open(output_file, "w", encoding="utf-8") as json_file:
        if all_apps:
            json.dump(all_apps, json_file, ensure_ascii=False, indent=4)
            print(f"Complete data saved to: {output_file}")

        else:
            json_file.write("[]")
            print(f"No data was extracted. Empty array saved to: {output_file}")

    import pandas as pd
    # Load JSON data into a DataFrame
    df = pd.read_json(output_file, encoding='utf-8-sig')
    # Construct the output file path relative to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "app_store_search_results.xlsx")
    # Export DataFrame to Excel
    df.to_excel(output_file, index=False)
    
if __name__ == "__main__":
    asyncio.run(extract())