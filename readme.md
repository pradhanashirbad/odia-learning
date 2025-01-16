# Odia Learning App

A PyQt6-based application for learning the Odia language.

## Development in GitHub Codespaces

1. Click the "Code" button and select "Open with Codespaces"
2. Wait for the container to build and initialize
3. Access the GUI through the Simple Browser:
   - Click the "Ports" tab
   - Find port 6080
   - Click the globe icon to open in browser
   - Login with password: `vscode`

### Running the Application

Run the application
python src/run_in_codespaces.py
Build the executable (if needed)
python build_exe.py


## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

## Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region
```
