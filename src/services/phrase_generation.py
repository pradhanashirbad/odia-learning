from openai import OpenAI
import json
import logging
import re

logger = logging.getLogger(__name__)

class PhraseGenerationService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["word_generation"]  # using same model config

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def clean_phrase(self, phrase):
        """Clean and sanitize a phrase"""
        if not isinstance(phrase, str):
            return ""
        # Remove quotes and punctuation
        cleaned = phrase.replace('"', '').replace('?', '').replace('!', '').replace('.', '').strip()
        # Remove any non-ASCII characters
        cleaned = cleaned.encode('ascii', 'ignore').decode()
        return cleaned

    def generate_phrases(self, existing_phrases=None):
        """Generate new phrases"""
        from prompts.prompts_class import PhraseGeneration
        
        try:
            completion = self.client.chat.completions.create(
                messages=PhraseGeneration.get_messages(existing_phrases),
                model=self.model,
                **self.get_model_config()
            )

            response = completion.choices[0].message.content.strip()
            logger.info(f"Raw response: {response}")

            try:
                phrases = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                # Try to fix common JSON issues
                fixed_response = response.replace('\n', '').replace('\\', '')
                if not fixed_response.startswith('['):
                    fixed_response = '[' + fixed_response
                if not fixed_response.endswith(']'):
                    fixed_response = fixed_response + ']'
                logger.info(f"Attempting to parse fixed response: {fixed_response}")
                phrases = json.loads(fixed_response)

            if not isinstance(phrases, list):
                raise ValueError("Expected a JSON array of phrases")

            # Clean each phrase
            cleaned_phrases = [self.clean_phrase(phrase) for phrase in phrases]
            logger.info(f"Cleaned phrases: {cleaned_phrases}")

            return cleaned_phrases

        except Exception as e:
            logger.error(f"Error generating phrases: {str(e)}")
            logger.error(f"Raw response was: {completion.choices[0].message.content if 'completion' in locals() else 'No response'}")
            raise ValueError(f"Failed to generate phrases: {str(e)}") 