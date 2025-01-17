from openai import OpenAI
import json
import logging
from src.prompts.prompts_class import OdiaPhraseGeneration

logger = logging.getLogger(__name__)

class OdiaPhraseService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["word_generation"]

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def validate_odia_text(self, text):
        """Check if text contains Odia characters"""
        return any('\u0B00' <= char <= '\u0B7F' for char in text)

    def generate_odia_phrases(self):
        """Generate Odia phrases"""
        try:
            completion = self.client.chat.completions.create(
                messages=OdiaPhraseGeneration.get_messages(),
                model=self.model,
                **self.get_model_config()
            )

            odia_phrases = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(odia_phrases, list):
                raise ValueError("Expected a JSON array of Odia phrases")
            
            valid_phrases = [phrase for phrase in odia_phrases if self.validate_odia_text(phrase)]
            if not valid_phrases:
                raise ValueError("No valid Odia phrases generated")
            
            return valid_phrases

        except Exception as e:
            logger.error(f"Error generating Odia phrases: {str(e)}")
            raise

    def process_phrases(self):
        """Generate just Odia phrases for now"""
        try:
            # Just generate Odia phrases
            odia_phrases = self.generate_odia_phrases()
            
            # Return simple format
            return [{"odia": phrase} for phrase in odia_phrases]

        except Exception as e:
            logger.error(f"Error in phrase processing: {str(e)}")
            raise 