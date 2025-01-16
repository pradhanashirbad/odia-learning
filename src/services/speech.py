import os
import azure.cognitiveservices.speech as speechsdk

class SpeechService:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        self.speech_config.speech_synthesis_voice_name = "or-IN-SubhasiniNeural"
        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)

    def speak_odia(self, text: str):
        try:
            result = self.synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return True
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                raise Exception(f"Speech synthesis canceled: {cancellation_details.reason}")
                
        except Exception as e:
            raise Exception(f"Error in Azure speech synthesis: {e}") 