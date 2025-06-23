from google_play_scraper import search
import pandas as pd
import os

# List of keywords to search for
keywords = ["ngoại ngữ", "giải bài tập", "học"]

# Initialize an empty list to store results
all_results = []

# Define the URL prefix and suffix
url_prefix = "https://play.google.com/store/apps/details?id="
url_suffix = "&hl=vi"

# Iterate over each keyword
for keyword in keywords:
    # Perform the search
    results = search(
        keyword,
        lang="vi",     # Language set to Vietnamese
        country="vn",  # Country set to Vietnam
        n_hits=30,       # Number of results to fetch
    )
    # Process each result
    for result in results:
        # Create a dictionary with the desired fields
        app_data = {
            "appId": f"{url_prefix}{result['appId']}{url_suffix}",
            "title": result["title"],
            "keyword": keyword  # Add the keyword to the result
        }
        # Append the dictionary to the list
        all_results.append(app_data)

# Convert the list of results to a DataFrame
df = pd.DataFrame(all_results)

# Construct the output file path relative to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "google_play_search_results.xlsx")

# Export DataFrame to Excel
df.to_excel(output_file, index=False)