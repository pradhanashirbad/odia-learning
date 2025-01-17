from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)

class OdiaPhraseService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["word_generation"]  # using same model config

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def validate_odia_text(self, text):
        """Check if text contains Odia characters"""
        # Odia Unicode range: 0B00-0B7F
        return any('\u0B00' <= char <= '\u0B7F' for char in text)

    def generate_odia_phrases(self, existing_phrases=None):
        """Generate Odia phrases"""
        from prompts.prompts_class import OdiaPhraseGeneration
        
        try:
            completion = self.client.chat.completions.create(
                messages=OdiaPhraseGeneration.get_messages(existing_phrases),
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

    def translate_to_english(self, odia_phrases):
        """Translate Odia phrases to English"""
        from prompts.prompts_class import EnglishTranslation
        
        valid_phrases = [phrase for phrase in odia_phrases if self.validate_odia_text(phrase)]
        if not valid_phrases:
            raise ValueError("No valid Odia phrases to translate")
            
        try:
            completion = self.client.chat.completions.create(
                messages=EnglishTranslation.get_messages(valid_phrases),
                model=self.model,
                **self.get_model_config()
            )

            translations = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(translations, list):
                raise ValueError("Expected a JSON array of translations")
            
            return translations

        except Exception as e:
            logger.error(f"Error translating to English: {str(e)}")
            raise

    def generate_romanized(self, odia_phrases):
        """Generate romanized versions of Odia phrases"""
        from prompts.prompts_class import RomanizedGeneration
        
        valid_odia = [phrase for phrase in odia_phrases if self.validate_odia_text(phrase)]
        if not valid_odia:
            raise ValueError("No valid Odia text found to romanize")
        
        try:
            completion = self.client.chat.completions.create(
                messages=RomanizedGeneration.get_messages(valid_odia),
                model=self.model,
                **self.get_model_config()
            )

            romanized = json.loads(completion.choices[0].message.content.strip())
            if not isinstance(romanized, list):
                raise ValueError("Expected a JSON array of romanized texts")
            
            valid_romanized = [entry for entry in romanized 
                             if isinstance(entry, dict) and 'odia' in entry and 'romanized' in entry]
            
            if not valid_romanized:
                raise ValueError("No valid romanized entries found in response")
            
            return valid_romanized

        except Exception as e:
            logger.error(f"Error generating romanized versions: {str(e)}")
            raise

    def process_phrases(self, existing_phrases=None):
        """Complete process to generate phrases with translations"""
        try:
            # Step 1: Generate Odia phrases
            odia_phrases = self.generate_odia_phrases(existing_phrases)
            
            # Step 2: Get English translations
            translations = self.translate_to_english(odia_phrases)
            
            # Step 3: Get romanized versions
            romanized = self.generate_romanized(odia_phrases)

            # Step 4: Combine all information
            combined = []
            for i, odia_phrase in enumerate(odia_phrases):
                try:
                    if (i < len(translations) and i < len(romanized) and
                        isinstance(translations[i], dict) and isinstance(romanized[i], dict) and
                        translations[i].get("english") and translations[i].get("odia") and
                        romanized[i].get("odia") and romanized[i].get("romanized")):
                        
                        entry = {
                            "english": translations[i].get("english", "").strip(),
                            "odia": odia_phrase.strip(),
                            "romanized_odia": romanized[i].get("romanized", "").strip()
                        }
                        
                        if all(entry.values()):
                            combined.append(entry)

                except Exception as e:
                    continue

            if not combined:
                raise ValueError("No complete valid entries were generated")

            logger.info(f"Generated {len(combined)} complete phrases")
            return combined

        except Exception as e:
            logger.error(f"Error in phrase processing: {str(e)}")
            raise 