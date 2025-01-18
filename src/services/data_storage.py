import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage=None):
        self.blob_storage = blob_storage
        # Use /tmp directory for Vercel
        self.base_dir = "/tmp"
        self.words_dir = os.path.join(self.base_dir, "words")
        self.session_file = os.path.join(self.words_dir, "session.json")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        try:
            os.makedirs(self.words_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            # Don't raise the error, just log it

    def save_session_data(self, translations):
        """Save session data locally"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            return {"local_path": self.session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            return None

    async def save_permanent_copy(self):
        """Save permanent copy to blob storage"""
        try:
            if not os.path.exists(self.session_file):
                raise FileNotFoundError("No active session to save")

            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"session_{timestamp}.json"

            if self.blob_storage:
                # Upload to blob storage
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
                return {"local_path": self.session_file}

        except Exception as e:
            logger.error(f"Error saving permanent copy: {e}")
            raise

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