import os
import shutil

def clean_and_copy_logos(folder_path, output_folder):
    """
    Processes logo file names by:
    - Removing leading underscores
    - Removing '_x0008_'
    - Removing '_logo' suffix
    - Copies and renames cleaned files into a new output folder

    Parameters:
    - folder_path (str): Path to the original logos folder
    - output_folder (str): Path to save cleaned logo copies
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        src_path = os.path.join(folder_path, filename)
        if not os.path.isfile(src_path):
            continue

        name, ext = os.path.splitext(filename)
        if ext.lower() not in ['.png', '.jpg', '.jpeg', '.svg']:
            continue

        # Cleaning logic
        new_name = name
        if new_name.startswith('_'):
            new_name = new_name[1:]
        new_name = new_name.replace('x0008_', '')
        if new_name.endswith('_logo'):
            new_name = new_name[:-5]

        new_filename = f"{new_name}{ext}"
        dst_path = os.path.join(output_folder, new_filename)

        shutil.copy2(src_path, dst_path)
        print(f"Copied: {filename} → {new_filename}")

# clean_and_copy_logos('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/logos_web','logo_processed_web')
# clean_and_copy_logos('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/logos_app','logo_processed_app')