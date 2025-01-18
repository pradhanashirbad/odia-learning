import os
import json
import logging

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage_service=None, base_dir="data"):
        self.blob_storage = blob_storage_service
        self.base_dir = base_dir
        self.words_dir = os.path.join(base_dir, "words")
        self.session_file = os.path.join(self.words_dir, "session.json")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.words_dir, exist_ok=True)

    def save_session_data(self, translations):
        """Save session data locally only"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            return {"local_path": self.session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    def get_existing_words(self):
        """Get existing words from local session"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [item.get('english', '') for item in data if 'english' in item]
            return []
        except Exception:
            return [] 