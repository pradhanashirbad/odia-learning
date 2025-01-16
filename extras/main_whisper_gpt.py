import os
from dotenv import load_dotenv
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
import json
from extras.prompts import WordGeneration, OdiaTranslation

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Load config
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    with open('model_configs.json', 'r', encoding='utf-8') as f:
        model_configs = json.load(f)
    return config, model_configs

def get_model_config(model_name, model_configs):
    """
    Get the configuration for a specific model
    """
    return model_configs.get(model_name, {})

def speak_text_azure_odia(text):
    """
    Convert text to speech using Azure TTS with Odia voice
    """
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        speech_config.speech_synthesis_voice_name = "or-IN-SubhasiniNeural"
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = speech_synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized successfully")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
    except Exception as e:
        print(f"Error in Azure speech synthesis: {e}")

def main():
    config, model_configs = load_config()
    
    # Generate English words
    generation_model = config["models"]["word_generation"]
    generation_completion = client.chat.completions.create(
        messages=WordGeneration.get_messages(),
        model=generation_model,
        **get_model_config(generation_model, model_configs)
    )

    # Parse the generated words
    generated_items = json.loads(generation_completion.choices[0].message.content)
    if isinstance(generated_items, dict) and 'words' in generated_items:
        texts_to_translate = generated_items['words']
    elif isinstance(generated_items, list):
        texts_to_translate = generated_items
    else:
        raise ValueError("Expected a JSON array of strings")
    print(f"Generated words: {texts_to_translate}")

    # Translate to Odia
    print("\nStarting Odia translation...")
    translation_model = config["models"]["translation"]
    translation_completion = client.chat.completions.create(
        messages=OdiaTranslation.get_messages(texts_to_translate),
        model=translation_model,
        **get_model_config(translation_model, model_configs)
    )

    # Process translations
    translations = json.loads(translation_completion.choices[0].message.content)
    if not isinstance(translations, list):
        raise ValueError("Expected a JSON array of translation objects")
    
    for t in translations:
        print("\nEnglish:", t["english"])
        print("Odia:", t["odia"])
        print("Romanized:", t["romanized_odia"])
        speak_text_azure_odia(t["odia"])

if __name__ == "__main__":
    main() 