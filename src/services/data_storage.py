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
        self.previous_words = []  # Words from previous sessions
        self.generated_words = []  # Words from current session for display
        self.total_words = []     # Combined words for prompt context

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

    def get_previous_words(self, username=None):
        """Get Odia words/phrases from previous sessions only"""
        translations = self.get_all_user_translations(username)
        return [item.get('odia', '') for item in translations if 'odia' in item]

    def get_existing_words(self):
        """Get all words for prompt context"""
        return list(self.total_words)

    def start_session(self, username):
        """Start new session and load previous words"""
        try:
            if not username:
                raise ValueError("Username is required")
            
            logger.info(f"Starting new session for user: {username}")
            
            # Clear current session
            self.generated_words = []
            
            # Load previous words from all sessions
            previous_translations = self.get_all_user_translations(username)
            self.previous_words = [item.get('odia', '') for item in previous_translations if 'odia' in item]
            
            # Initialize total words with previous words
            self.total_words = list(self.previous_words)
            
            logger.info(f"Loaded {len(self.previous_words)} previous words for context")
            return []  # Return empty list for fresh session display
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            self.previous_words = []
            self.generated_words = []
            self.total_words = []
            return []

    def add_to_session(self, new_translations):
        """Add new translations to current session"""
        # Add to generated words for display
        self.generated_words.extend(new_translations)
        
        # Add new Odia words to total words for prompt context
        new_odia = [t.get('odia', '') for t in new_translations if 'odia' in t]
        self.total_words.extend(new_odia)
        
        logger.info(f"Added {len(new_translations)} new translations. Total context words: {len(self.total_words)}")
        
        # Return only current session translations for display
        return list(self.generated_words)

    def save_session_data(self, username=None):
        """Save current session data"""
        try:
            if not username:
                raise ValueError("Username is required")
            if not self.generated_words:
                raise ValueError("No translations to save")

            session_file = self._get_session_filepath(username)
            logger.info(f"Saving session data to: {session_file}")

            # Save only current session generated words
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.generated_words, f, ensure_ascii=False, indent=4)

            return {"local_path": session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    def clear_session(self):
        """Clear current session"""
        self.generated_words = []  # Clear only generated words
        # Keep previous_words and total_words until completely new session

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

    async def save_permanent_copy(self, username=None):
        """Save permanent copy to blob storage"""
        try:
            if not self.generated_words:
                raise ValueError("No translations available to save")

            if self.blob_storage:
                # Use timestamped filename for blob storage
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                blob_name = f"{username}/session_{timestamp}.json"
                
                # Upload to blob storage with pretty formatting
                blob_url = await self.blob_storage.upload_blob(
                    json.dumps(self.generated_words, ensure_ascii=False, indent=4),
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