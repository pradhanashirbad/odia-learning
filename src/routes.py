from flask import jsonify, request
from src.services.odia_phrase_service import OdiaPhraseService
from src.services.word_generation import WordGenerationService
from src.services.translation_words import WordTranslationService
from src.services.speech import SpeechService
from src.services.blob_storage import BlobStorageService
from src.services.data_storage import DataStorageService
from src.config.settings import Settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    settings = Settings()
    client = OpenAI()
    blob_storage = BlobStorageService(settings.config)
    data_storage = DataStorageService(blob_storage)
    word_service = WordGenerationService(client, settings.config, settings.model_configs)
    odia_phrase_service = OdiaPhraseService(client, settings.config, settings.model_configs)
    word_translation_service = WordTranslationService(client, settings.config, settings.model_configs)
    speech_service = SpeechService(blob_storage)

    @app.route('/generate', methods=['POST'])
    def generate():
        try:
            existing_words = data_storage.get_existing_words()
            gen_type = request.json.get('type', 'words')
            
            if gen_type == 'words':
                items = word_service.generate_words(existing_words)
                new_translations = word_translation_service.translate_words(items)
            else:
                new_translations = odia_phrase_service.process_phrases(existing_words)
                
            storage_info = data_storage.save_session_data(new_translations)
            
            return jsonify({
                'success': True,
                'translations': new_translations,
                'storage_info': storage_info
            })
        
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Add other routes here... 