import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage=None):
        self.blob_storage = blob_storage
        self.base_dir = os.path.join(os.getcwd(), "datafiles")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure datafiles directory exists"""
        try:
            if not os.path.exists(self.base_dir):
                os.makedirs(self.base_dir, exist_ok=True)
                logger.info(f"Created directory: {self.base_dir}")
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            self.base_dir = "/tmp"
            os.makedirs(self.base_dir, exist_ok=True)
            logger.info("Using /tmp directory as fallback")

    def _get_session_filepath(self, username):
        """Get full path to session file with timestamp"""
        if not username:
            raise ValueError("Username is required")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.base_dir, f"{username}_session_{timestamp}.json")

    def save_session_data(self, translations, username=None):
        """Save session data to a new timestamped file"""
        try:
            session_file = self._get_session_filepath(username)
            logger.info(f"Saving session data to: {session_file}")
            
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(session_file), exist_ok=True)

            # Save data with pretty formatting
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=4)
            return {"local_path": session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    async def save_permanent_copy(self, username=None):
        """Save permanent copy to blob storage"""
        try:
            session_file = self._get_session_filepath(username)
            logger.info(f"Saving permanent copy from: {session_file}")
            
            # Create new file with current translations
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            
            if self.blob_storage:
                # Use timestamped filename for blob storage
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                blob_name = f"{username}_session_{timestamp}.json"
                
                # Get the most recent translations
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Upload to blob storage with pretty formatting
                blob_url = await self.blob_storage.upload_blob(
                    json.dumps(data, ensure_ascii=False, indent=4),
                    blob_name
                )

                if not blob_url:
                    raise Exception("Failed to upload to blob storage")

                return {
                    "blob_url": blob_url,
                    "filename": blob_name
                }
            else:
                logger.warning("No blob storage configured")
                return {"local_path": session_file}

        except Exception as e:
            logger.error(f"Error saving permanent copy: {e}")
            raise

    def get_existing_words(self, username=None):
        """Get existing words from user's session"""
        try:
            # For this implementation, we don't need to check existing words
            # since we're creating new files each time
            return []
        except Exception as e:
            logger.error(f"Error getting existing words: {e}")
            return [] 