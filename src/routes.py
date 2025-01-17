from flask import jsonify, request
from src.services.odia_phrase_service import OdiaPhraseService
from src.config.settings import Settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    settings = Settings()
    client = OpenAI()
    odia_phrase_service = OdiaPhraseService(client, settings.config, settings.model_configs)

    @app.route('/generate', methods=['POST'])
    def generate():
        try:
            # Generate phrases starting with Odia
            new_translations = odia_phrase_service.process_phrases()
            
            return jsonify({
                'success': True,
                'translations': new_translations
            })
        
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/pronounce', methods=['POST'])
    def pronounce():
        return jsonify({
            'success': False,
            'error': 'Speech synthesis not available in this environment',
            'feature_disabled': True
        }), 503

    # Add other routes here... 