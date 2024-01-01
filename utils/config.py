import os

def get_clingy_app_download_path() -> str:
    # Get the path to the user's home directory and create a folder there for all Clingy downloads
    home_dir = os.path.expanduser("~")
    download_dir = "clingy_app_files"
    full_path = os.path.join(home_dir, download_dir)
    # Create the directory if it doesn't exist
    os.makedirs(full_path, exist_ok=True)

    return full_path