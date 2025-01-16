import os
import azure.cognitiveservices.speech as speechsdk
import tempfile
import time

class SpeechService:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        self.speech_config.speech_synthesis_voice_name = "or-IN-SubhasiniNeural"
        
        # Create temp directory for audio files if it doesn't exist
        self.audio_dir = os.path.join(tempfile.gettempdir(), 'odia_audio')
        os.makedirs(self.audio_dir, exist_ok=True)

    def speak_odia(self, text: str):
        try:
            # Create a unique filename using hash of text and timestamp
            filename = f"{hash(text)}_{int(time.time())}.wav"
            audio_file = os.path.join(self.audio_dir, filename)
            
            # Create an audio output config with a file
            audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)
            
            # Create the synthesizer with the file output
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config, 
                audio_config=audio_config
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return audio_file
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                raise Exception(f"Speech synthesis canceled: {cancellation_details.reason}")
                
        except Exception as e:
            raise Exception(f"Error in Azure speech synthesis: {e}") 