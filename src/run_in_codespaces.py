import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
from prompts.prompts_class import WordGeneration, OdiaTranslation
import json

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['OPENAI_API_KEY', 'AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("Please set them in your .env file or Codespaces secrets")
        sys.exit(1)

def main():
    # Load environment variables
    load_dotenv()
    check_environment()
    
    # Initialize OpenAI client
    client = OpenAI()
    
    try:
        # 1. Generate English words
        print("\nGenerating English words...")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=WordGeneration.get_messages(),
            temperature=0.7
        )
        words = json.loads(completion.choices[0].message.content)
        print("Generated words:", words)
        
        # 2. Translate to Odia
        print("\nTranslating to Odia...")
        translation_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=OdiaTranslation.get_messages(words),
            temperature=0.3
        )
        translations = json.loads(translation_completion.choices[0].message.content)
        
        # 3. Text-to-Speech for each translation
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        speech_config.speech_synthesis_voice_name = "or-IN-SubhasiniNeural"
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # Display and speak each translation
        for t in translations:
            print(f"\nEnglish: {t['english']}")
            print(f"Odia: {t['odia']}")
            print(f"Romanized: {t['romanized_odia']}")
            print("Speaking Odia text...")
            result = synthesizer.speak_text_async(t['odia']).get()
            if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Error speaking text")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 