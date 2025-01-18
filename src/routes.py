from flask import jsonify, request, render_template_string
from src.services.odia_phrase_service import OdiaPhraseService
from src.config.settings import Settings
from openai import OpenAI
import logging
from src.services.vercel_blob_storage import VercelBlobStorage
from src.services.data_storage import DataStorageService
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

# HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Odia Learning App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .translation-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .loading {
            display: none;
            color: #666;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .radio-group {
            margin: 10px 0;
        }
        .controls {
            margin: 20px 0;
        }
        #saveButton {
            background-color: #2196F3;
            margin-left: 10px;
            display: none;
        }
        #saveButton:hover {
            background-color: #1976D2;
        }
        #saveButton:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        #appContent {
            display: none;
        }
        #usernameForm {
            text-align: center;
            margin-top: 50px;
        }
        input[type="text"] {
            padding: 10px;
            font-size: 16px;
            margin-right: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="usernameForm">
        <h1>Welcome to Odia Learning App</h1>
        <input type="text" id="username" placeholder="Enter your username" required>
        <button onclick="submitUsername()">Start Learning</button>
    </div>

    <div id="appContent">
        <h1>Odia Learning App</h1>
        <p>Welcome, <span id="userDisplay"></span>!</p>
        
        <div class="controls">
            <div class="radio-group">
                <label>
                    <input type="radio" name="genType" value="words" checked> Words
                </label>
                <label>
                    <input type="radio" name="genType" value="phrases"> Phrases
                </label>
            </div>
            <button onclick="generateContent()">Generate Content</button>
            <button id="saveButton" onclick="saveSession()">Save Session</button>
        </div>
        
        <p id="loading" class="loading">Generating content...</p>
        <div id="results"></div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        let currentUsername = '';
        
        function submitUsername() {
            const usernameInput = document.getElementById('username');
            const username = usernameInput.value.trim();
            
            if (username) {
                currentUsername = username;
                document.getElementById('usernameForm').style.display = 'none';
                document.getElementById('appContent').style.display = 'block';
                document.getElementById('userDisplay').textContent = username;
            } else {
                alert('Please enter a username');
            }
        }
        
        function getSelectedType() {
            return document.querySelector('input[name="genType"]:checked').value;
        }
        
        function generateContent() {
            const loadingElement = document.getElementById('loading');
            const resultsElement = document.getElementById('results');
            const saveButton = document.getElementById('saveButton');
            
            loadingElement.style.display = 'block';
            resultsElement.innerHTML = '';
            
            fetch(`${baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    type: getSelectedType(),
                    username: currentUsername
                })
            })
            .then(response => response.json())
            .then(data => {
                loadingElement.style.display = 'none';
                
                if (data.success) {
                    data.translations.forEach(translation => {
                        const card = document.createElement('div');
                        card.className = 'translation-card';
                        card.innerHTML = `
                            <h3>English: ${translation.english}</h3>
                            <p>Odia: ${translation.odia}</p>
                        `;
                        resultsElement.appendChild(card);
                    });
                    saveButton.style.display = 'inline-block';
                } else {
                    resultsElement.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            })
            .catch(error => {
                loadingElement.style.display = 'none';
                resultsElement.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
            });
        }

        function saveSession() {
            const saveButton = document.getElementById('saveButton');
            saveButton.disabled = true;
            saveButton.textContent = 'Saving...';
            
            fetch(`${baseUrl}/save-session`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: currentUsername })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Session saved successfully!');
                } else {
                    alert(`Error saving session: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`Error saving session: ${error}`);
            })
            .finally(() => {
                saveButton.disabled = false;
                saveButton.textContent = 'Save Session';
            });
        }
    </script>
</body>
</html>
"""

def register_routes(app):
    settings = Settings()
    client = OpenAI()
    blob_storage = VercelBlobStorage(settings.config)
    data_storage = DataStorageService(blob_storage)
    odia_phrase_service = OdiaPhraseService(client, settings.config, settings.model_configs)

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/generate', methods=['POST'])
    def generate():
        try:
            gen_type = request.json.get('type', 'words')
            username = request.json.get('username')
            
            if not username:
                raise ValueError("Username is required")
                
            # Get existing words for duplicate checking
            existing_words = data_storage.get_existing_words(username)
            logger.info(f"Found {len(existing_words)} existing words for user: {username}")
            
            # Pass existing words to avoid duplicates
            new_translations = odia_phrase_service.process_phrases(
                gen_type=gen_type, 
                existing_words=existing_words
            )
            
            # Save locally with username
            data_storage.save_session_data(new_translations, username)
            
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

    @app.route('/save-session', methods=['POST'])
    def save_session():
        try:
            username = request.json.get('username')
            if not username:
                raise ValueError("Username is required")
                
            logger.info(f"Starting save_session operation for user: {username}")
            
            # Convert async function to sync
            storage_info = async_to_sync(data_storage.save_permanent_copy)(username)
            
            logger.info(f"Save operation completed: {storage_info}")
            return jsonify({
                'success': True,
                'storage_info': storage_info
            })
        except Exception as e:
            logger.error(f"Detailed error in save_session: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500 

    @app.route('/load-session', methods=['POST'])
    def load_session():
        try:
            username = request.json.get('username')
            if not username:
                raise ValueError("Username is required")
                
            logger.info(f"Loading previous sessions for user: {username}")
            
            # Get all previous translations
            translations = data_storage.get_all_user_translations(username)
            
            return jsonify({
                'success': True,
                'translations': translations
            })
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500 