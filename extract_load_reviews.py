import os
import pandas as pd

def extract_app_id_from_filename(filename):
    """Extracts app_id from filename formatted as 'android_{app_id}.csv'"""
    if filename.startswith("android_") and filename.endswith(".csv"):
        return filename[8:-4]  # Remove "android_" prefix and ".csv" suffix
    return None

def extract_app_id_from_folder(folder_name):
    """Extracts app_id from folder formatted as 'android_{app_id}'"""
    if folder_name.startswith("android_"):
        return folder_name[8:]  # Remove "android_" prefix
    return None

def collect_reviews_data(root_folder):
    """Extract & Load raw reviews data first"""
    all_data = []
    
    # Iterate through the root folder
    for entry in os.scandir(root_folder):
        if entry.is_dir():  
            app_id = extract_app_id_from_folder(entry.name)
            reviews_path = os.path.join(entry.path, "reviews.csv")
            content_column = "content"  
        elif entry.is_file() and entry.name.endswith(".csv"):  
            app_id = extract_app_id_from_filename(entry.name)
            reviews_path = entry.path
            content_column = "review"  
        else:
            continue  

        # Read the reviews.csv file if found
        if app_id and os.path.exists(reviews_path):
            try:
                df = pd.read_csv(reviews_path)
                if content_column in df.columns and "score" in df.columns and "at" in df.columns:
                    df = df[[content_column, "score", "at"]]
                    df.rename(columns={content_column: "content"}, inplace=True)
                    df.insert(0, "app_id", app_id)  
                    all_data.append(df)
                else:
                    print(f"Skipping {reviews_path} - Missing expected columns")
            except Exception as e:
                print(f"Error reading {reviews_path}: {e}")

    # Load raw data into a DataFrame
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        # Transform: Convert 'at' to Date (Optimized for Large Data)
        final_df["at"] = pd.to_datetime(final_df["at"], errors="coerce").dt.date  

        # Save final processed data
        final_df.to_csv(os.path.join(root_folder, "total.csv"), index=False)
        print(f"total.csv created with {len(final_df)} reviews!")
    else:
        print("No reviews data found!")

# Replace 'your_folder_path' with the actual path of your reviews folder
collect_reviews_data("/Users/vuhainam/Downloads/Reviews/Android")