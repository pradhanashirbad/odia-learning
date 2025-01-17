import os
import azure.cognitiveservices.speech as speechsdk
import tempfile
import time
import logging

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self, blob_storage_service):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        self.speech_config.speech_synthesis_voice_name = "or-IN-SubhasiniNeural"
        self.blob_storage = blob_storage_service
        
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
                try:
                    # Upload to blob storage and get SAS URL
                    sas_url = self.blob_storage.upload_file(audio_file, filename)
                    return sas_url
                except Exception as upload_error:
                    logger.error(f"Error uploading to blob storage: {upload_error}")
                    raise
                finally:
                    # Try to clean up the file in a separate try block
                    try:
                        if os.path.exists(audio_file):
                            # Add a small delay to ensure file is released
                            time.sleep(0.5)
                            os.remove(audio_file)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not remove temporary file {audio_file}: {cleanup_error}")
                        
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                raise Exception(f"Speech synthesis canceled: {cancellation_details.reason}")
                
        except Exception as e:
            logger.error(f"Error in Azure speech synthesis: {e}")
            raise Exception(f"Error in Azure speech synthesis: {e}") 