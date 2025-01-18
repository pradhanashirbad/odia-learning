import os
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage_service, base_dir="data"):
        self.blob_storage = blob_storage_service
        self.base_dir = base_dir
        self.words_dir = os.path.join(base_dir, "words")
        self.session_file = os.path.join(self.words_dir, "session.json")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.words_dir, exist_ok=True)

    def save_session_data(self, translations):
        """Save session data without immediate blob upload"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            return {"local_path": self.session_file}
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            raise

    def save_permanent_copy(self):
        """Save permanent copy to blob storage asynchronously"""
        try:
            if not os.path.exists(self.session_file):
                raise FileNotFoundError("No active session to save")

            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"session_{timestamp}.json"

            # Upload to blob storage
            blob_url = self.blob_storage.upload_blob(
                json.dumps(data, ensure_ascii=False).encode('utf-8'),
                blob_name
            )

            if not blob_url:
                raise Exception("Failed to upload to blob storage")

            return {
                "blob_url": blob_url,
                "filename": blob_name
            }

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

    def list_saved_files(self):
        """
        List all saved session files (excluding current session.json)
        """
        try:
            files = []
            for filename in os.listdir(self.words_dir):
                if filename.startswith('saved_') and filename.endswith('.json'):
                    file_path = os.path.join(self.words_dir, filename)
                    files.append({
                        "filename": filename,
                        "path": file_path,
                        "timestamp": os.path.getmtime(file_path)
                    })
            return sorted(files, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logger.error(f"Error listing saved files: {e}")
            raise 

    def get_all_translations(self):
        """Get all translations from the current session"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('translations', [])
            return []
        except Exception as e:
            logger.error(f"Error reading translations: {e}")
            return [] 

    def save_audio_url(self, odia_text: str, audio_url: str):
        """Save audio URL mapping for an Odia word"""
        try:
            audio_map = {}
            audio_map_file = os.path.join(self.words_dir, 'audio_map.json')
            
            # Load existing mappings if any
            if os.path.exists(audio_map_file):
                with open(audio_map_file, 'r', encoding='utf-8') as f:
                    audio_map = json.load(f)
            
            # Add new mapping
            audio_map[odia_text] = audio_url
            
            # Save updated mappings
            with open(audio_map_file, 'w', encoding='utf-8') as f:
                json.dump(audio_map, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Audio URL saved for: {odia_text}")
            
        except Exception as e:
            logger.error(f"Error saving audio URL: {e}")
            raise

    def get_audio_url(self, odia_text: str) -> str:
        """Get cached audio URL for an Odia word if it exists"""
        try:
            audio_map_file = os.path.join(self.words_dir, 'audio_map.json')
            if os.path.exists(audio_map_file):
                with open(audio_map_file, 'r', encoding='utf-8') as f:
                    audio_map = json.load(f)
                    return audio_map.get(odia_text)
            return None
        except Exception as e:
            logger.error(f"Error getting audio URL: {e}")
            return None 