from openai import OpenAI
import json

class WordGenerationService:
    def __init__(self, client: OpenAI, config: dict, model_configs: dict):
        self.client = client
        self.config = config
        self.model_configs = model_configs
        self.model = config["models"]["word_generation"]

    def get_model_config(self):
        return self.model_configs.get(self.model, {})

    def generate_words(self):
        from prompts.prompts_class import WordGeneration
        
        completion = self.client.chat.completions.create(
            messages=WordGeneration.get_messages(),
            model=self.model,
            **self.get_model_config()
        )

        generated_items = json.loads(completion.choices[0].message.content)
        if isinstance(generated_items, dict) and 'words' in generated_items:
            return generated_items['words']
        elif isinstance(generated_items, list):
            return generated_items
        else:
            raise ValueError("Expected a JSON array of strings") 