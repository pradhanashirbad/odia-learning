from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)

class PhraseTranslationService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["translation"]

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def validate_translation(self, translation):
        """Validate a single translation entry"""
        required_keys = {'english', 'odia', 'romanized_odia'}
        
        # Check if all required keys exist and have non-empty values
        if not isinstance(translation, dict):
            return False
        
        for key in required_keys:
            if key not in translation or not isinstance(translation[key], str) or not translation[key].strip():
                return False
        
        return True

    def translate_phrases(self, phrases: list):
        """Translate English phrases to Odia"""
        from prompts.prompts_class import PhraseTranslation
        
        try:
            completion = self.client.chat.completions.create(
                messages=PhraseTranslation.get_messages(phrases),
                model=self.model,
                **self.get_model_config()
            )

            response = completion.choices[0].message.content.strip()
            logger.info(f"Raw translation response: {response}")
            
            try:
                translations = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                # Try to fix common JSON issues
                fixed_response = response.replace('\n', '').replace('\\', '')
                if not fixed_response.endswith(']'):
                    # Find the last complete translation
                    last_complete = fixed_response.rfind('}')
                    if last_complete != -1:
                        fixed_response = fixed_response[:last_complete+1] + ']'
                logger.info(f"Attempting to parse fixed response: {fixed_response}")
                translations = json.loads(fixed_response)

            if not isinstance(translations, list):
                raise ValueError("Expected a JSON array of translations")

            # Filter out invalid translations
            valid_translations = [t for t in translations if self.validate_translation(t)]
            
            if not valid_translations:
                raise ValueError("No valid translations found")
            
            logger.info(f"Valid translations: {len(valid_translations)} out of {len(translations)}")
            
            return valid_translations

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            logger.error(f"Raw response: {completion.choices[0].message.content if 'completion' in locals() else 'No response'}")
            raise ValueError(f"Failed to translate phrases: {str(e)}") 