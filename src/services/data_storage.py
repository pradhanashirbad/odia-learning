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
        self.current_translations = None  # Store current translations in memory

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

    def _get_user_dir(self, username):
        """Get user-specific directory"""
        return os.path.join(self.base_dir, username)

    def _get_session_filepath(self, username):
        """Get full path to session file with timestamp"""
        if not username:
            raise ValueError("Username is required")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_dir = self._get_user_dir(username)
        return os.path.join(user_dir, f"session_{timestamp}.json")

    def save_session_data(self, translations, username=None):
        """Save session data to a new timestamped file"""
        try:
            # Create user directory if it doesn't exist
            user_dir = self._get_user_dir(username)
            os.makedirs(user_dir, exist_ok=True)
            
            session_file = self._get_session_filepath(username)
            logger.info(f"Saving session data to: {session_file}")

            # Save data with pretty formatting
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=4)
            
            # Store current translations in memory
            self.current_translations = translations
            return {"local_path": session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    def get_all_user_translations(self, username):
        """Get all translations from user's previous sessions"""
        try:
            user_dir = self._get_user_dir(username)
            if not os.path.exists(user_dir):
                return []

            all_translations = []
            # Read all JSON files in user's directory
            for filename in os.listdir(user_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(user_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                        if isinstance(translations, list):
                            all_translations.extend(translations)

            logger.info(f"Found {len(all_translations)} previous translations for user: {username}")
            return all_translations
        except Exception as e:
            logger.error(f"Error reading user translations: {e}")
            return []

    def get_existing_words(self, username=None):
        """Get existing words from user's previous sessions"""
        translations = self.get_all_user_translations(username)
        return [item.get('english', '') for item in translations if 'english' in item]

    async def save_permanent_copy(self, username=None):
        """Save permanent copy to blob storage"""
        try:
            if not self.current_translations:
                raise ValueError("No translations available to save")

            if self.blob_storage:
                # Use timestamped filename for blob storage
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                blob_name = f"{username}/session_{timestamp}.json"
                
                # Upload to blob storage with pretty formatting
                blob_url = await self.blob_storage.upload_blob(
                    json.dumps(self.current_translations, ensure_ascii=False, indent=4),
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
                return {"local_path": None}

        except Exception as e:
            logger.error(f"Error saving permanent copy: {e}")
            raise 