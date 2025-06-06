import os
import shutil

def upload_folder_to_onedrive(local_folder, onedrive_folder):
    """
    Copies all contents from local_folder to onedrive_folder.
    Both paths must be absolute.
    """
    if not os.path.exists(local_folder):
        raise FileNotFoundError(f"Local folder '{local_folder}' does not exist.")
    if not os.path.exists(onedrive_folder):
        os.makedirs(onedrive_folder)
    for item in os.listdir(local_folder):
        src = os.path.join(local_folder, item)
        dst = os.path.join(onedrive_folder, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    print(f"Uploaded '{local_folder}' to '{onedrive_folder}'.")

# Example usage:
# Replace these paths with your actual local folder and OneDrive sync folder
local_folder = r"C:\Users\melis\OneDrive\Documents\GitHub\Tesis\ExperimentsFiles"
onedrive_folder = r"C:\Users\melis\OneDrive - Universidad Católica del Uruguay\Tesis\Etapa Caracterización\Experiments Data"

upload_folder_to_onedrive(local_folder, onedrive_folder)

