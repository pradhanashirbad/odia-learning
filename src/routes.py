from flask import jsonify, request, render_template_string
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
            margin: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .controls {
            margin: 20px 0;
        }
        .radio-group {
            margin: 10px 0;
        }
        .pagination {
            margin-top: 20px;
            display: none;
            justify-content: center;
            gap: 10px;
        }
        .pagination button {
            background-color: #2196F3;
        }
        .pagination button:hover {
            background-color: #1976D2;
        }
    </style>
</head>
<body>
    <h1>Odia Learning App</h1>
    
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
    </div>
    
    <p id="loading" class="loading">Generating content...</p>
    
    <div id="results"></div>
    
    <div id="pagination" class="pagination">
        <button onclick="showPreviousPage()" id="prevButton">Previous</button>
        <button onclick="showNextPage()" id="nextButton">Next</button>
    </div>

    <script>
        const baseUrl = window.location.origin;
        const ITEMS_PER_PAGE = 5;
        let allTranslations = [];
        let currentPageIndex = 0;
        
        function getSelectedType() {
            return document.querySelector('input[name="genType"]:checked').value;
        }
        
        function generateContent() {
            const loadingElement = document.getElementById('loading');
            const resultsElement = document.getElementById('results');
            const paginationElement = document.getElementById('pagination');
            
            loadingElement.style.display = 'block';
            resultsElement.innerHTML = '';
            paginationElement.style.display = 'none';
            
            fetch(`${baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: getSelectedType() })
            })
            .then(response => response.json())
            .then(data => {
                loadingElement.style.display = 'none';
                
                if (data.success) {
                    allTranslations = data.translations;
                    currentPageIndex = 0;
                    displayCurrentPage();
                    paginationElement.style.display = 'flex';
                } else {
                    resultsElement.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            })
            .catch(error => {
                loadingElement.style.display = 'none';
                resultsElement.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
            });
        }
        
        function displayCurrentPage() {
            const resultsElement = document.getElementById('results');
            const startIndex = currentPageIndex * ITEMS_PER_PAGE;
            const endIndex = startIndex + ITEMS_PER_PAGE;
            const currentItems = allTranslations.slice(startIndex, endIndex);
            
            resultsElement.innerHTML = '';
            currentItems.forEach(translation => {
                const card = document.createElement('div');
                card.className = 'translation-card';
                card.innerHTML = `
                    <h3>English: ${translation.english}</h3>
                    <p>Odia: ${translation.odia}</p>
                `;
                resultsElement.appendChild(card);
            });
            
            updatePaginationButtons();
        }
        
        function showNextPage() {
            if ((currentPageIndex + 1) * ITEMS_PER_PAGE < allTranslations.length) {
                currentPageIndex++;
                displayCurrentPage();
            }
        }
        
        function showPreviousPage() {
            if (currentPageIndex > 0) {
                currentPageIndex--;
                displayCurrentPage();
            }
        }
        
        function updatePaginationButtons() {
            const prevButton = document.getElementById('prevButton');
            const nextButton = document.getElementById('nextButton');
            
            prevButton.disabled = currentPageIndex === 0;
            nextButton.disabled = (currentPageIndex + 1) * ITEMS_PER_PAGE >= allTranslations.length;
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
            gen_type = request.json.get('type', 'words')
            new_translations = odia_phrase_service.process_phrases(gen_type=gen_type)
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