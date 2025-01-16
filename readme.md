# Odia Learning App

A simple command-line application for learning Odia words through English translations and speech.

## Running in GitHub Codespaces

1. Click "Code" and select "Open with Codespaces"
2. The devcontainer will automatically:
   - Set up Python environment
   - Configure audio support
   - Install dependencies

3. Set up your environment variables:
   - Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   AZURE_SPEECH_KEY=your_azure_speech_key
   AZURE_SPEECH_REGION=your_azure_speech_region
   ```
   Or set these in your Codespaces secrets.

4. Run the application:
   ```bash
   python src/run_in_codespaces.py
   ```

## Features

- Generates 5 random English words
- Translates them to Odia
- Provides romanized Odia text
- Speaks the Odia translations using Azure Text-to-Speech

## Requirements

- OpenAI API key
- Azure Speech Services key and region

## Development Container

This project includes a devcontainer configuration that:
- Sets up Python 3.10
- Configures audio support for text-to-speech
- Installs all required dependencies
- Provides VS Code extensions for Python development

The container automatically configures:
- PulseAudio for audio output
- Python environment
- Project dependencies
