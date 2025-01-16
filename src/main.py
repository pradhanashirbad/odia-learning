import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from openai import OpenAI

from config.settings import Settings
from services.word_generation import WordGenerationService
from services.translation import TranslationService
from services.speech import SpeechService
from ui.main_window import MainWindow

def main():
    # Initialize settings and services
    settings = Settings()
    client = OpenAI()
    
    word_service = WordGenerationService(client, settings.config, settings.model_configs)
    translation_service = TranslationService(client, settings.config, settings.model_configs)
    speech_service = SpeechService()
    
    # Create and show UI
    app = QApplication(sys.argv)
    window = MainWindow(word_service, translation_service, speech_service)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 