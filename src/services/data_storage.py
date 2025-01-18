import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage=None):
        self.blob_storage = blob_storage
        # Use datafiles directory in root
        self.base_dir = "datafiles"
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure datafiles directory exists"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            # Don't raise the error, just log it

    def _get_session_filepath(self, username):
        """Get full path to session file"""
        if not username:
            raise ValueError("Username is required")
        return os.path.join(self.base_dir, f"{username}_session.json")

    def save_session_data(self, translations, username=None):
        """Save session data locally by appending new translations"""
        try:
            session_file = self._get_session_filepath(username)
            
            # Read existing data if file exists
            existing_data = []
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Append new translations
            if isinstance(existing_data, list):
                existing_data.extend(translations)
            else:
                existing_data = translations

            # Save combined data
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            return {"local_path": session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    async def save_permanent_copy(self, username=None):
        """Save permanent copy to blob storage"""
        try:
            session_file = self._get_session_filepath(username)
            
            # If file doesn't exist, create an empty one
            if not os.path.exists(session_file):
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"Created new session file for user: {username}")

            # Read the file (whether it was just created or existed)
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if self.blob_storage:
                # Upload to blob storage with the same filename
                blob_name = f"datafiles/{os.path.basename(session_file)}"
                
                # Upload to blob storage (this will overwrite existing file)
                blob_url = await self.blob_storage.upload_blob(
                    json.dumps(data, ensure_ascii=False).encode('utf-8'),
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
            session_file = self._get_session_filepath(username)
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [item.get('english', '') for item in data if 'english' in item]
            return []
        except Exception as e:
            logger.error(f"Error getting existing words: {e}")
            return [] 