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
            background-color: white;
        }
        .translation-card .romanized {
            color: #666;
            font-style: italic;
            margin-top: 5px;
            font-size: 0.9em;
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
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
            gap: 10px;
        }
        
        .pagination button {
            padding: 5px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        
        .pagination button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        
        .pagination span {
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Odia Learning App</h1>
    
    <div id="usernameForm">
        <h2>Enter Your Name</h2>
        <input type="text" id="username" placeholder="Your name">
        <button onclick="submitUsername()">Start Session</button>
    </div>
    
    <div id="appContent" style="display: none;">
        <p>Welcome, <span id="userDisplay"></span>!</p>
        <div class="radio-group">
            <input type="radio" id="words" name="type" value="words" checked>
            <label for="words">Words</label>
            <input type="radio" id="phrases" name="type" value="phrases">
            <label for="phrases">Phrases</label>
        </div>
        
        <button onclick="generateContent()">Generate Content</button>
        <button id="saveButton" onclick="saveAndExit()" style="display: none;">Save Session & Exit</button>
        
        <p id="loading" style="display: none;">Generating content...</p>
        <div id="results"></div>
    </div>

    <script>
        let currentUsername = '';
        let allTranslations = [];
        let currentPage = 1;
        const itemsPerPage = 5;
        const baseUrl = window.location.origin;

        function submitUsername() {
            const username = document.getElementById('username').value.trim();
            if (!username) {
                alert('Please enter a username');
                return;
            }
            
            currentUsername = username;
            
            // Load existing translations
            fetch(`${baseUrl}/load-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: username })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show main app content
                    document.getElementById('usernameForm').style.display = 'none';
                    document.getElementById('appContent').style.display = 'block';
                    document.getElementById('userDisplay').textContent = username;
                    
                    // Display existing translations if any
                    if (data.translations && data.translations.length > 0) {
                        allTranslations = data.translations;
                        displayTranslations(allTranslations);
                        document.getElementById('saveButton').style.display = 'inline-block';
                    }
                } else {
                    alert(data.error || 'Error loading session');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading session');
            });
        }

        function displayTranslations(translations) {
            const resultsElement = document.getElementById('results');
            resultsElement.innerHTML = '';
            
            if (!translations.length) {
                resultsElement.innerHTML = '<p>No translations yet. Click "Generate Content" to start.</p>';
                return;
            }

            // Calculate pagination
            const totalPages = Math.ceil(translations.length / itemsPerPage);
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = Math.min(startIndex + itemsPerPage, translations.length);
            const pageTranslations = translations.slice(startIndex, endIndex);

            // Add pagination controls at top
            resultsElement.appendChild(createPaginationControls(totalPages));

            // Add translations
            pageTranslations.forEach(translation => {
                const card = document.createElement('div');
                card.className = 'translation-card';
                card.innerHTML = `
                    <h3>English: ${translation.english}</h3>
                    <p>Odia: ${translation.odia}</p>
                    <p class="romanized">Romanized: ${translation.romanized_odia}</p>
                `;
                resultsElement.appendChild(card);
            });

            // Add pagination controls at bottom
            resultsElement.appendChild(createPaginationControls(totalPages));
        }

        function createPaginationControls(totalPages) {
            const nav = document.createElement('div');
            nav.className = 'pagination';
            nav.innerHTML = `
                <button onclick="changePage(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''}>
                    Previous
                </button>
                <span>Page ${currentPage} of ${totalPages}</span>
                <button onclick="changePage(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''}>
                    Next
                </button>
            `;
            return nav;
        }

        function changePage(newPage) {
            if (newPage >= 1 && newPage <= Math.ceil(allTranslations.length / itemsPerPage)) {
                currentPage = newPage;
                displayTranslations(allTranslations);
            }
        }

        function generateContent() {
            const loadingElement = document.getElementById('loading');
            loadingElement.style.display = 'block';
            
            fetch(`${baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: document.querySelector('input[name="type"]:checked').value,
                    username: currentUsername
                })
            })
            .then(response => response.json())
            .then(data => {
                loadingElement.style.display = 'none';
                if (data.success) {
                    // Add new translations to existing ones
                    allTranslations = allTranslations.concat(data.translations);
                    // Go to last page to show new content
                    currentPage = Math.ceil(allTranslations.length / itemsPerPage);
                    displayTranslations(allTranslations);
                    document.getElementById('saveButton').style.display = 'inline-block';
                } else {
                    alert(data.error || 'Error generating content');
                }
            })
            .catch(error => {
                loadingElement.style.display = 'none';
                console.error('Error:', error);
                alert('Error generating content');
            });
        }

        function saveAndExit() {
            fetch(`${baseUrl}/save-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: currentUsername })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reset and go back to username form
                    currentUsername = '';
                    allTranslations = [];
                    currentPage = 1;
                    document.getElementById('usernameForm').style.display = 'block';
                    document.getElementById('appContent').style.display = 'none';
                    document.getElementById('username').value = '';
                } else {
                    alert(data.error || 'Error saving session');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saving session');
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

    @app.route('/start-session', methods=['POST'])
    def start_session():
        try:
            username = request.json.get('username')
            if not username:
                raise ValueError("Username is required")
            
            logger.info(f"Starting session for user: {username}")
            
            # Start fresh session
            translations = data_storage.start_session(username)
            logger.info(f"Started new session for user: {username}")
            
            return jsonify({
                'success': True,
                'translations': translations  # Will be empty array
            })
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/generate', methods=['POST'])
    def generate():
        try:
            gen_type = request.json.get('type', 'words')
            username = request.json.get('username')
            
            if not username:
                raise ValueError("Username is required")
                
            # Get total words for prompt context
            existing_words = data_storage.get_existing_words()
            logger.info(f"Using {len(existing_words)} total words for context")
            
            # Generate new content
            new_translations = odia_phrase_service.process_phrases(
                gen_type=gen_type, 
                existing_words=existing_words
            )
            
            # Add to session and get all generated translations
            session_translations = data_storage.add_to_session(new_translations)
            
            return jsonify({
                'success': True,
                'translations': session_translations  # Return all generated translations
            })
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/save-and-exit', methods=['POST'])
    def save_and_exit():
        try:
            username = request.json.get('username')
            if not username:
                raise ValueError("Username is required")
                
            logger.info(f"Saving and ending session for user: {username}")
            
            # Save current session
            data_storage.save_session_data(username)
            
            # Save to blob storage
            storage_info = async_to_sync(data_storage.save_permanent_copy)(username)
            
            # Clear session
            data_storage.clear_session()
            
            return jsonify({
                'success': True,
                'storage_info': storage_info
            })
        except Exception as e:
            logger.error(f"Error in save_and_exit: {str(e)}")
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
            
            # Save locally first
            data_storage.save_session_data(username)
            
            # Then save to blob storage
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