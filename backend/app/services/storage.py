import os
import shutil
from abc import ABC, abstractmethod
from backend.app.core.config import settings
from backend.app.core.logger import logger

class StorageInterface(ABC):
    @abstractmethod
    def save_file(self, file_content: bytes, destination_name: str) -> str:
        """
        Saves a file to storage and returns the local/remote path.
        """
        pass

    @abstractmethod
    def get_file(self, file_path: str) -> bytes:
        """
        Retrieves file bytes from storage.
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Deletes file from storage.
        """
        pass


class LocalStorageService(StorageInterface):
    def __init__(self, upload_dir: str = "storage"):
        # Put storage inside the workspace root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.upload_path = os.path.join(base_dir, upload_dir)
        os.makedirs(self.upload_path, exist_ok=True)
        logger.info(f"LocalStorageService initialized at: {self.upload_path}")

    def save_file(self, file_content: bytes, destination_name: str) -> str:
        dest_file_path = os.path.join(self.upload_path, destination_name)
        try:
            with open(dest_file_path, "wb") as buffer:
                buffer.write(file_content)
            logger.info(f"File successfully saved locally to: {dest_file_path}")
            return dest_file_path
        except Exception as e:
            logger.error(f"Failed to save file locally: {str(e)}")
            raise e

    def get_file(self, file_path: str) -> bytes:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "rb") as f:
            return f.read()

    def delete_file(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        logger.warn(f"File not found for deletion: {file_path}")
        return False

# Global instance
storage_service = LocalStorageService()
