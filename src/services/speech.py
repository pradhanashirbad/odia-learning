import logging
logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self, blob_storage):
        self.blob_storage = blob_storage
        self.speech_enabled = False
        logger.info("Speech service initialized in lightweight mode")

    def speak_odia(self, text):
        """Generate speech for Odia text"""
        return None 