import os
from dotenv import load_dotenv
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from tempfile import NamedTemporaryFile
from faster_whisper import WhisperModel
import json

# Load environment variables from .env file
load_dotenv()

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

config, model_configs = load_config()

# Initialize Whisper model
transcription_model = config["models"]["transcription"]
model = WhisperModel(
    transcription_model,
    **get_model_config(transcription_model, model_configs)
)

def record_audio(duration=1, sample_rate=44100):
    """
    Record audio from microphone
    duration: recording time in seconds
    sample_rate: sample rate in Hz
    """
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate),
                      samplerate=sample_rate,
                      channels=1,
                      dtype=np.int16)
    sd.wait()
    print("Recording finished!")
    
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        wav.write(temp_audio.name, sample_rate, recording)
        return temp_audio.name

def transcribe_from_mic(duration=5):
    """
    Record and transcribe audio from microphone using Whisper
    """
    audio_file = record_audio(duration=duration)
    segments, info = model.transcribe(audio_file, beam_size=5)
    transcript_text = " ".join([segment.text for segment in segments])
    os.remove(audio_file)
    return transcript_text

def main():
    print("Whisper Transcription from Microphone:")
    transcript_text = transcribe_from_mic(duration=5)
    print("Transcription:", transcript_text)

if __name__ == "__main__":
    main() 