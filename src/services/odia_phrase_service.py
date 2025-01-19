from openai import OpenAI
import json
import logging
from src.prompts.prompts_class import WordGeneration, OdiaTranslation, EnglishTranslation

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
                messages = PhraseGeneration.get_messages(existing_words)

            completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                **self.get_model_config()
            )

            content = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(content, list):
                raise ValueError(f"Expected a JSON array of {gen_type}")
            
            if gen_type == 'words':
                return content
            else:
                valid_phrases = [phrase for phrase in content if self.validate_odia_text(phrase)]
                if not valid_phrases:
                    raise ValueError("No valid Odia phrases generated")
                return valid_phrases

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
            
            return translations

        except Exception as e:
            logger.error(f"Error translating to Odia: {str(e)}")
            raise

    def translate_to_english(self, odia_phrases):
        """Translate Odia phrases to English"""
        try:
            completion = self.client.chat.completions.create(
                messages=EnglishTranslation.get_messages(odia_phrases),
                model=self.model,
                **self.get_model_config()
            )

            translations = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(translations, list):
                raise ValueError("Expected a JSON array of translations")
            
            # Combine Odia and English translations
            combined = []
            for i, odia_phrase in enumerate(odia_phrases):
                if i < len(translations):
                    combined.append({
                        "english": translations[i].get("english", ""),
                        "odia": odia_phrase
                    })
            
            return combined

        except Exception as e:
            logger.error(f"Error translating to English: {str(e)}")
            raise

    def process_phrases(self, gen_type='words', existing_words=None):
        """Generate and process content"""
        try:
            if gen_type == 'words':
                # Generate English words and translate to Odia
                words = self.generate_content('words', existing_words)
                translations = self.translate_to_odia(words)
                return translations
            else:
                # Generate Odia phrases and translate to English
                odia_phrases = self.generate_content('phrases', existing_words)
                translations = self.translate_to_english(odia_phrases)
                return translations

        except Exception as e:
            logger.error(f"Error in content processing: {str(e)}")
            raise 