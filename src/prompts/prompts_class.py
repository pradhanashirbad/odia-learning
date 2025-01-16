class WordGeneration:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are a language learning assistant specializing in generating everyday English words.
            You must respond with ONLY a JSON array of 5 words.
            Example of EXACT format required:
            ["eat", "book", "water", "house", "walk"]
            Do not wrap the array in any object or add any other fields."""
        }

    @staticmethod
    def get_generation_prompt(category=None):
        """
        Create prompt for word generation
        """
        content = """Return ONLY a JSON array of 5 simple English words.
        The response must be EXACTLY in this format, nothing more:
        ["word1", "word2", "word3", "word4", "word5"]
        Do not include any other structure or fields."""

        return {
            "role": "user",
            "content": content
        }

    @staticmethod
    def get_messages(category=None):
        """
        Returns a list of messages for word generation
        """
        messages = [WordGeneration.get_system_prompt()]
        messages.append(WordGeneration.get_generation_prompt(category))
        return messages


class OdiaTranslation:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are an English to Odia translator. Return a simple JSON array.
            Each array item must be exactly in this format, no extra whitespace or formatting:
            {"english":"word","odia":"ଶବ୍ଦ","romanized_odia":"sabda"}
            Example complete response:
            [{"english":"water","odia":"ପାଣି","romanized_odia":"paani"},{"english":"book","odia":"ବହି","romanized_odia":"bahi"}]"""
        }

    @staticmethod
    def get_translation_prompt(texts):
        """
        Create translation prompt for the given texts
        """
        words_list = ", ".join(texts)
        
        return {
            "role": "user",
            "content": f"""Translate these words to Odia: {words_list}
            Return a single-line JSON array with no extra whitespace or formatting.
            Format: [{{"english":"word","odia":"ଶବ୍ଦ","romanized_odia":"sabda"}}]"""
        }

    @staticmethod
    def get_messages(texts):
        """
        Returns a list of messages for translation
        """
        messages = [OdiaTranslation.get_system_prompt()]
        messages.append(OdiaTranslation.get_translation_prompt(texts))
        return messages 