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
from services.blob_storage import BlobStorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
logger.info(f"Template directory set to: {template_dir}")
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Initialize settings and services
try:
    settings = Settings()
    client = OpenAI()
    blob_storage = BlobStorageService(settings.config)
    word_service = WordGenerationService(client, settings.config, settings.model_configs)
    translation_service = TranslationService(client, settings.config, settings.model_configs)
    speech_service = SpeechService(blob_storage)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    raise

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    template_path = os.path.join(template_dir, 'index.html')
    logger.info(f"Looking for template at: {template_path}")
    if os.path.exists(template_path):
        logger.info("Template file found!")
    else:
        logger.error(f"Template file NOT found at: {template_path}")
        # List contents of templates directory
        if os.path.exists(template_dir):
            logger.info(f"Contents of {template_dir}:")
            for file in os.listdir(template_dir):
                logger.info(f"- {file}")
        else:
            logger.error(f"Templates directory does not exist at: {template_dir}")
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Generate words
        words = word_service.generate_words()
        
        # Get translations
        translations = translation_service.translate_words(words)
        
        # Generate speech for each translation and add audio URLs
        for translation in translations:
            audio_url = speech_service.speak_odia(translation['odia'])
            # Add the SAS URL directly to the translation
            translation['audio_url'] = audio_url
        
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
        port = int(os.environ.get('PORT', 5001))
        logger.info(f"Starting Flask app on port {port}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
        
        # Check if we can bind to the port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            logger.warning(f"Port {port} is already in use")
        sock.close()
        
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