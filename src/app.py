from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import sys
import tempfile
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config.settings import Settings
from services.word_generation import WordGenerationService
from services.translation import TranslationService
from services.speech import SpeechService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize settings and services
try:
    settings = Settings()
    client = OpenAI()
    word_service = WordGenerationService(client, settings.config, settings.model_configs)
    translation_service = TranslationService(client, settings.config, settings.model_configs)
    speech_service = SpeechService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    raise

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files from the temporary directory"""
    audio_dir = os.path.join(tempfile.gettempdir(), 'odia_audio')
    return send_file(
        os.path.join(audio_dir, filename),
        mimetype='audio/wav'
    )

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Generate words
        words = word_service.generate_words()
        
        # Get translations
        translations = translation_service.translate_words(words)
        
        # Generate speech for each translation and add audio URLs
        for translation in translations:
            audio_file = speech_service.speak_odia(translation['odia'])
            # Get just the filename from the full path
            audio_filename = os.path.basename(audio_file)
            # Add the audio URL to the translation
            translation['audio_url'] = f'/audio/{audio_filename}'
        
        return jsonify({
            'success': True,
            'translations': translations
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting Flask app on port {port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        raise 