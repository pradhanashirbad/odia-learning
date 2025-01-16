import PyInstaller.__main__
import os
import sys

# Detect if running in Codespaces
IN_CODESPACES = os.environ.get('CODESPACES') == 'true'

# Base configuration
config = [
    'src/main.py',
    '--name=OdiaLearning',
    '--add-data=src/config/config.json:config',
    '--add-data=src/config/model_configs.json:config',
    '--add-data=src/prompts/prompts_class.py:prompts',
    '--add-data=src/services/word_generation.py:services',
    '--add-data=src/services/translation.py:services',
    '--add-data=src/services/speech.py:services',
    '--hidden-import=azure.cognitiveservices.speech',
    '--hidden-import=openai',
    '--hidden-import=dotenv',
    '--collect-all=azure-cognitiveservices-speech',
]

# Add platform-specific options
if IN_CODESPACES:
    config.extend([
        '--onefile',
        '--console',  # Show console in Codespaces
    ])
else:
    config.extend([
        '--onefile',
        '--windowed',  # Hide console on desktop
    ])

PyInstaller.__main__.run(config) 