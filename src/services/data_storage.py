import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage=None):
        self.blob_storage = blob_storage
        # Use absolute path for datafiles directory
        self.base_dir = os.path.join(os.getcwd(), "datafiles")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure datafiles directory exists"""
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(self.base_dir):
                os.makedirs(self.base_dir, exist_ok=True)
                logger.info(f"Created directory: {self.base_dir}")
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            # Use /tmp as fallback for Vercel
            self.base_dir = "/tmp"
            os.makedirs(self.base_dir, exist_ok=True)
            logger.info("Using /tmp directory as fallback")

    def _get_session_filepath(self, username):
        """Get full path to session file"""
        if not username:
            raise ValueError("Username is required")
        return os.path.join(self.base_dir, f"{username}_session.json")

    def save_session_data(self, translations, username=None):
        """Save session data locally by appending new translations"""
        try:
            session_file = self._get_session_filepath(username)
            logger.info(f"Saving session data to: {session_file}")
            
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

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(session_file), exist_ok=True)

            # Save combined data
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            return {"local_path": session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    def load_session_data(self, username):
        """Load existing session data for a user"""
        try:
            session_file = self._get_session_filepath(username)
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
            return []

    async def save_permanent_copy(self, username=None):
        """Save permanent copy to blob storage"""
        try:
            session_file = self._get_session_filepath(username)
            logger.info(f"Saving permanent copy from: {session_file}")
            
            # If file doesn't exist, create an empty one
            if not os.path.exists(session_file):
                os.makedirs(os.path.dirname(session_file), exist_ok=True)
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"Created new session file for user: {username}")

            # Read the file (whether it was just created or existed)
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if self.blob_storage:
                # Use consistent filename for the user
                blob_name = f"{username}_session.json"
                
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