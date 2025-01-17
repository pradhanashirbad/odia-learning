from openai import OpenAI
import json
import logging
import re

logger = logging.getLogger(__name__)

class WordGenerationService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["word_generation"]

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def sanitize_text(self, text):
        """Clean text to make it JSON-safe"""
        # Remove any non-ASCII characters
        text = text.encode('ascii', 'ignore').decode()
        # Remove any quotes except those needed for JSON structure
        text = re.sub(r'(?<!\\)"(?!,|\]|$)', '', text)
        # Remove punctuation from the actual content
        text = text.replace('?', '').replace('!', '').replace('.', '')
        return text.strip()

    def generate_words(self, existing_words=None, gen_type='words'):
        """Generate new words or phrases, taking into account existing ones"""
        from prompts.prompts_class import WordGeneration
        
        try:
            completion = self.client.chat.completions.create(
                messages=WordGeneration.get_messages(existing_words, gen_type),
                model=self.model,
                **self.get_model_config()
            )

            # Get the raw response
            raw_response = completion.choices[0].message.content
            logger.info(f"Raw response received: {raw_response}")

            # Clean the response
            response_text = raw_response.strip()
            logger.info(f"Stripped response: {response_text}")

            # Ensure it starts and ends with brackets
            if not (response_text.startswith('[') and response_text.endswith(']')):
                logger.error("Response is not a valid JSON array")
                raise ValueError("Response is not a valid JSON array")

            try:
                # First try to parse as is
                words = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parsing failed: {e}")
                # Try to clean each item individually
                cleaned_response = '['
                items = response_text[1:-1].split('","')
                cleaned_items = []
                for item in items:
                    cleaned_item = self.sanitize_text(item)
                    if cleaned_item:
                        cleaned_items.append(f'"{cleaned_item}"')
                cleaned_response += ','.join(cleaned_items) + ']'
                logger.info(f"Cleaned response: {cleaned_response}")
                words = json.loads(cleaned_response)

            if not isinstance(words, list):
                raise ValueError("Expected a JSON array of words")

            # Final cleaning of each word
            cleaned_words = [self.sanitize_text(word) for word in words]
            logger.info(f"Final cleaned words: {cleaned_words}")

            return cleaned_words

        except Exception as e:
            logger.error(f"Error in generate_words: {str(e)}")
            logger.error(f"Raw response was: {completion.choices[0].message.content if 'completion' in locals() else 'No response'}")
            raise ValueError(f"Failed to generate content: {str(e)}") 