from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import sys
import tempfile
import logging

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from openai import OpenAI
from config.settings import Settings
from services.word_generation import WordGenerationService
from services.odia_phrase_service import OdiaPhraseService
from services.translation_words import WordTranslationService
from services.speech import SpeechService
from services.blob_storage import BlobStorageService
from services.data_storage import DataStorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_session():
    """Clean up session file on app startup"""
    try:
        session_path = os.path.join('data', 'words', 'session.json')
        if os.path.exists(session_path):
            os.remove(session_path)
            logger.info("Previous session file cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up session file: {e}")

# Create Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
logger.info(f"Template directory set to: {template_dir}")
app = Flask(__name__, 
    template_folder=template_dir,
    static_folder=static_dir
)
CORS(app)

# Initialize settings and services
try:
    # Clean up previous session file
    cleanup_session()
    
    # Initialize services
    settings = Settings()
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )
    blob_storage = BlobStorageService(settings.config)
    data_storage = DataStorageService(blob_storage)
    word_service = WordGenerationService(client, settings.config, settings.model_configs)
    odia_phrase_service = OdiaPhraseService(client, settings.config, settings.model_configs)
    word_translation_service = WordTranslationService(client, settings.config, settings.model_configs)
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
        # Get existing words from session
        existing_words = data_storage.get_existing_words()
        
        # Get generation type from request
        gen_type = request.json.get('type', 'words')
        
        # Generate new words
        if gen_type == 'words':
            items = word_service.generate_words(existing_words)
            new_translations = word_translation_service.translate_words(items)
        else:
            # Generate phrases starting with Odia
            new_translations = odia_phrase_service.process_phrases(existing_words)
            
            if len(new_translations) < 10:
                logger.warning(f"Generated fewer translations than expected: {len(new_translations)}")
        
        # Save session data (this will now append to existing translations)
        storage_info = data_storage.save_session_data(new_translations)
        
        # Get all translations after saving
        all_translations = data_storage.get_all_translations()
        
        return jsonify({
            'success': True,
            'translations': new_translations,  # Only send new translations to append
            'storage_info': storage_info
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/save-session', methods=['POST'])
def save_session():
    try:
        storage_info = data_storage.save_permanent_copy()
        return jsonify({
            'success': True,
            'storage_info': storage_info
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'No active session to save'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/sessions', methods=['GET'])
def list_sessions():
    try:
        sessions = data_storage.list_saved_files()
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/pronounce', methods=['POST'])
def pronounce():
    try:
        text = request.json.get('text')
        if not text:
            raise ValueError("No text provided")
        
        # Check if we have a cached audio URL
        cached_url = data_storage.get_audio_url(text)
        if cached_url:
            return jsonify({
                'success': True,
                'audio_url': cached_url,
                'cached': True
            })
            
        # Generate new audio if not cached
        audio_url = speech_service.speak_odia(text)
        
        # Save the URL for future use
        data_storage.save_audio_url(text, audio_url)
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'cached': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/upload-session', methods=['POST'])
def upload_session():
    try:
        data = request.json
        
        # Validate the uploaded data
        if not data or 'translations' not in data or not isinstance(data['translations'], list):
            raise ValueError("Invalid session file format")
        
        # Extract existing words from the uploaded translations
        translations = data['translations']
        if not translations:
            raise ValueError("No translations found in session file")
            
        # Save the uploaded session
        storage_info = data_storage.save_session_data(translations)
        
        return jsonify({
            'success': True,
            'translations': translations,
            'storage_info': storage_info
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    ) 