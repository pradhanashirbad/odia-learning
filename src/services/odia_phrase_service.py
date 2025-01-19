from openai import OpenAI
import json
import logging
from src.prompts.prompts_class import (
    WordGeneration, OdiaTranslation, EnglishTranslation, 
    OdiaPhraseGeneration  # Changed from PhraseGeneration
)

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

    def generate_content(self, gen_type='words', existing_words=None):
        """Generate words or phrases"""
        try:
            # Use appropriate prompt class based on type
            if gen_type == 'words':
                messages = WordGeneration.get_messages(existing_words, gen_type)
            else:
                messages = OdiaPhraseGeneration.get_messages(existing_words)  # Changed from PhraseGeneration

            completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                **self.get_model_config()
            )

            content = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(content, list):
                raise ValueError(f"Expected a JSON array of {gen_type}")
            
            return content  # Return all content, validation happens in process_phrases

        except Exception as e:
            logger.error(f"Error generating {gen_type}: {str(e)}")
            raise

    def translate_to_odia(self, words):
        """Translate English words to Odia"""
        try:
            completion = self.client.chat.completions.create(
                messages=OdiaTranslation.get_messages(words),
                model=self.model,
                **self.get_model_config()
            )

            translations = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(translations, list):
                raise ValueError("Expected a JSON array of translations")
            
            # Ensure each translation has romanization
            for t in translations:
                if 'romanized_odia' not in t:
                    t['romanized_odia'] = self.get_romanization(t['odia'])
            
            return translations

        except Exception as e:
            logger.error(f"Error translating to Odia: {str(e)}")
            raise

    def get_romanization(self, odia_text):
        """Get romanization for Odia text"""
        try:
            completion = self.client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "You are an Odia romanization expert. Return only the romanized form of the Odia text."
                }, {
                    "role": "user",
                    "content": f"Romanize this Odia text: {odia_text}"
                }],
                model=self.model,
                **self.get_model_config()
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error getting romanization: {str(e)}")
            return ""

    def translate_to_english(self, odia_phrases):
        """Translate Odia phrases to English with romanization"""
        try:
            completion = self.client.chat.completions.create(
                messages=EnglishTranslation.get_messages(odia_phrases),
                model=self.model,
                **self.get_model_config()
            )

            translations = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(translations, list):
                raise ValueError("Expected a JSON array of translations")
            
            # Combine Odia, English and romanized translations
            combined = []
            for i, odia_phrase in enumerate(odia_phrases):
                if i < len(translations):
                    combined.append({
                        "english": translations[i].get("english", ""),
                        "odia": odia_phrase,
                        "romanized_odia": translations[i].get("romanized_odia", "")
                    })
            
            return combined

        except Exception as e:
            logger.error(f"Error translating to English: {str(e)}")
            raise

    def process_phrases(self, gen_type='words', existing_words=None):
        """Generate and process content"""
        try:
            if gen_type == 'words':
                # Generate English words and translate to Odia with romanization
                words = self.generate_content('words', existing_words)
                translations = self.translate_to_odia(words)
                return translations
            else:
                # Generate Odia phrases and translate to English with romanization
                odia_phrases = self.generate_content('phrases', existing_words)
                # Validate Odia phrases
                valid_phrases = [phrase for phrase in odia_phrases if self.validate_odia_text(phrase)]
                if not valid_phrases:
                    raise ValueError("No valid Odia phrases generated")
                translations = self.translate_to_english(valid_phrases)
                return translations

        except Exception as e:
            logger.error(f"Error in content processing: {str(e)}")
            raise 