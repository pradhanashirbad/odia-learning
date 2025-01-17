import os
import json
import time
from datetime import datetime
import logging
import shutil
import tempfile

logger = logging.getLogger(__name__)

class DataStorageService:
    def __init__(self, blob_storage_service, base_dir=None):
        """Initialize with configurable base directory"""
        self.blob_storage = blob_storage_service
        
        # Use /tmp for Render deployment
        self.base_dir = base_dir or os.path.join(tempfile.gettempdir(), "odia_app_data")
        self.words_dir = os.path.join(self.base_dir, "words")
        self.session_file = os.path.join(self.words_dir, "session.json")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.words_dir, exist_ok=True)

    def get_existing_words(self):
        """
        Get existing English words from the current session
        """
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [t['english'] for t in data.get('translations', [])]
            return []
        except Exception as e:
            logger.error(f"Error reading existing words: {e}")
            return []

    def save_session_data(self, translations, save_to_blob=True):
        """
        Append new translations to session.json
        Returns the paths/urls where the data was saved
        """
        try:
            # Load existing translations if any
            existing_translations = []
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing_translations = data.get('translations', [])

            # Combine existing and new translations
            all_translations = existing_translations + translations

            # Create session data with timestamp
            session_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "translations": all_translations
            }

            # Save updated session file
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Session data saved to: {self.session_file}")
            
            blob_url = None
            if save_to_blob:
                # Save to blob storage
                blob_name = "words/session.json"
                blob_url = self.blob_storage.upload_file(self.session_file, blob_name)
                logger.info(f"Session data saved to blob storage: {blob_url}")

            return {
                "local_path": self.session_file,
                "blob_url": blob_url
            }

        except Exception as e:
            logger.error(f"Error saving session data: {e}")
            raise

    def save_permanent_copy(self):
        """
        Save a permanent copy of the current session file with timestamp
        """
        try:
            if not os.path.exists(self.session_file):
                raise FileNotFoundError("No active session file found")

            # Generate filename with datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_filename = f"saved_{timestamp}.json"
            save_path = os.path.join(self.words_dir, save_filename)

            # Copy session file to saved file
            shutil.copy2(self.session_file, save_path)
            
            # Upload to blob if session was in blob
            blob_url = None
            try:
                blob_name = f"words/{save_filename}"
                blob_url = self.blob_storage.upload_file(save_path, blob_name)
                logger.info(f"Saved session data to blob storage: {blob_url}")
            except Exception as e:
                logger.warning(f"Failed to save to blob storage: {e}")

            logger.info(f"Session saved permanently to: {save_path}")
            
            return {
                "local_path": save_path,
                "blob_url": blob_url
            }

        except Exception as e:
            logger.error(f"Error saving permanent copy: {e}")
            raise

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