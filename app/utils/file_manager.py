# app/utils/file_manager.py
import os
import uuid
from fastapi import UploadFile

class FileManager:
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """Creates target directory structures if they do not exist on disk."""
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    async def save_uploaded_file(upload_file: UploadFile, destination_dir: str) -> str:
        """
        Saves an incoming FastAPI UploadFile stream safely to the destination directory.
        Returns the finalized file path configuration string.

        A unique prefix is added to the original filename so two uploads
        with the same name (e.g. two phones both saving "IMG_001.jpg")
        don't silently overwrite each other on disk.
        """
        FileManager.ensure_directory_exists(destination_dir)

        original_name = upload_file.filename or "upload.jpg"
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        file_path = os.path.join(destination_dir, unique_name)

        # Standardize path slashes for cross-platform robustness
        file_path = file_path.replace("\\", "/")
        
        with open(file_path, "wb") as buffer:
            buffer.write(await upload_file.read())
            
        return file_path