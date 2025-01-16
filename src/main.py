import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

from config.settings import Settings
from services.word_generation import WordGenerationService
from services.translation import TranslationService
from services.speech import SpeechService

def main():
    # Initialize settings and services
    settings = Settings()
    client = OpenAI()
    
    word_service = WordGenerationService(client, settings.config, settings.model_configs)
    translation_service = TranslationService(client, settings.config, settings.model_configs)
    speech_service = SpeechService()
    
    try:
        # Generate words
        words = word_service.generate_words()
        print("\nGenerated English words:")
        for word in words:
            print(f"- {word}")
        
        # Get translations
        print("\nTranslating to Odia...")
        translations = translation_service.translate_words(words)
        
        # Display translations and play audio
        print("\nTranslations:")
        for translation in translations:
            print(f"\nEnglish: {translation['english']}")
            print(f"Odia: {translation['odia']}")
            print(f"Romanized: {translation['romanized_odia']}")
            print("Playing audio...")
            speech_service.speak_odia(translation['odia'])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 