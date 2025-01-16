# Odia Learning App

A simple command-line application for learning Odia words through English translations and speech.

## Running in GitHub Codespaces

1. Click "Code" and select "Open with Codespaces"
2. Once the Codespace is ready, set up your environment variables:
   - Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   AZURE_SPEECH_KEY=your_azure_speech_key
   AZURE_SPEECH_REGION=your_azure_speech_region
   ```
   Or set these in your Codespaces secrets.

3. Install dependencies:
   ```bash
   pip install -e .
   ```

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
