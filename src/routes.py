from flask import jsonify, request, send_from_directory, render_template_string
from src.services.odia_phrase_service import OdiaPhraseService
from src.config.settings import Settings
from openai import OpenAI
import logging

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
    </style>
</head>
<body>
    <h1>Odia Learning App</h1>
    
    <button onclick="generatePhrases()">Generate Odia Phrases</button>
    <p id="loading" class="loading">Generating phrases...</p>
    
    <div id="results"></div>

    <script>
        const baseUrl = window.location.origin;
        
        function generatePhrases() {
            const loadingElement = document.getElementById('loading');
            const resultsElement = document.getElementById('results');
            
            loadingElement.style.display = 'block';
            resultsElement.innerHTML = '';
            
            fetch(`${baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: 'phrases' })
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
                } else {
                    resultsElement.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            })
            .catch(error => {
                loadingElement.style.display = 'none';
                resultsElement.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
            });
        }
    </script>
</body>
</html>
"""

def register_routes(app):
    settings = Settings()
    client = OpenAI()
    odia_phrase_service = OdiaPhraseService(client, settings.config, settings.model_configs)

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/generate', methods=['POST'])
    def generate():
        try:
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