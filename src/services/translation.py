from openai import OpenAI
import json

class TranslationService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["translation"]

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def translate_words(self, words: list):
        from prompts.prompts_class import OdiaTranslation
        
        completion = self.client.chat.completions.create(
            messages=OdiaTranslation.get_messages(words),
            model=self.model,
            **self.get_model_config()
        )

        translations = json.loads(completion.choices[0].message.content)
        if not isinstance(translations, list):
            raise ValueError("Expected a JSON array of translation objects")
        return translations 