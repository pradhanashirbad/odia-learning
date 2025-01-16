import os
import json
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        load_dotenv()
        self.config = self._load_config()
        self.model_configs = self._load_model_configs()

    def _load_config(self):
        with open('src/config/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_model_configs(self):
        with open('src/config/model_configs.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    def word_generation_model(self):
        return self.config["models"]["word_generation"]

    @property
    def translation_model(self):
        return self.config["models"]["translation"] 