class WordGeneration:
    @staticmethod
    def get_system_prompt(gen_type='words'):
        content = """You are a language learning assistant specializing in generating {type}.
        You must respond with ONLY a JSON array of 10 {type}.
        VERY IMPORTANT: Your response must be EXACTLY in this format with NO OTHER CHARACTERS:
        {example}
        - No punctuation marks in the content
        - No special characters
        - No line breaks
        - Just a simple JSON array of strings"""

        if gen_type == 'words':
            example = '["eat","book","water","house","walk","run","sleep","read","write","speak"]'
            type_desc = "everyday English words"
        else:
            example = '["how are you","I am going home","please help me","what is your name","the weather is nice"]'
            type_desc = "simple English phrases or short sentences"

        return {
            "role": "system",
            "content": content.format(type=type_desc, example=example)
        }

    @staticmethod
    def get_generation_prompt(existing_words=None, gen_type='words'):
        """Create prompt for word/phrase generation"""
        type_desc = "words" if gen_type == 'words' else "phrases or short sentences"
        
        base_content = """Return EXACTLY a JSON array of 10 simple English {type}.
        Format must be EXACTLY like this: ["item1","item2","item3"]
        - No punctuation marks
        - No special characters
        - No line breaks
        - Just simple text in a JSON array"""
        
        if existing_words:
            content = f"""These are the existing items: {', '.join(existing_words)}
            {base_content.format(type=type_desc)}
            Do not repeat any existing items."""
        else:
            content = base_content.format(type=type_desc)

        return {
            "role": "user",
            "content": content
        }

    @staticmethod
    def get_messages(existing_words=None, gen_type='words'):
        """Returns a list of messages for generation"""
        messages = [WordGeneration.get_system_prompt(gen_type)]
        messages.append(WordGeneration.get_generation_prompt(existing_words, gen_type))
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


class PhraseTranslation:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are an English to Odia translator specializing in phrases and sentences.
            Return a simple JSON array. Each array item must be exactly in this format:
            {"english":"I like to play","odia":"ମୁଁ ଖେଳିବାକୁ ଭଲପାଏ","romanized_odia":"mun khelibaku bhalapaae"}
            Example complete response:
            [{"english":"how are you","odia":"ତୁମେ କେମିତି ଅଛ","romanized_odia":"tume kemiti acha"},
             {"english":"I am fine","odia":"ମୁଁ ଭଲ ଅଛି","romanized_odia":"mun bhala achhi"}]"""
        }

    @staticmethod
    def get_translation_prompt(phrases):
        """Create translation prompt for phrases"""
        phrases_list = ", ".join([f'"{phrase}"' for phrase in phrases])
        
        return {
            "role": "user",
            "content": f"""Translate these English phrases to Odia: {phrases_list}
            Return a single-line JSON array with no extra whitespace or formatting.
            Format: [{{"english":"I am going home","odia":"ମୁଁ ଘରକୁ ଯାଉଛି","romanized_odia":"mun gharaku jauchhi"}}]"""
        }

    @staticmethod
    def get_messages(phrases):
        """Returns a list of messages for translation"""
        messages = [PhraseTranslation.get_system_prompt()]
        messages.append(PhraseTranslation.get_translation_prompt(phrases))
        return messages 


class PhraseGeneration:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are a language learning assistant that generates simple English phrases.
            Return ONLY a JSON array of 10 simple phrases.
            Example format: ["hello how are you","I am fine","nice to meet you"]
            Rules:
            - No punctuation marks
            - No special characters
            - No quotes within phrases
            - Keep phrases simple and natural
            - One line JSON array only"""
        }

    @staticmethod
    def get_generation_prompt(existing_phrases=None):
        if existing_phrases:
            content = f"""Existing phrases: {', '.join(existing_phrases)}
            Generate 10 NEW simple English phrases (different from existing ones).
            Return as simple JSON array: ["phrase one","phrase two","phrase three"]
            No punctuation or special characters."""
        else:
            content = """Generate 10 simple English phrases.
            Return as simple JSON array: ["phrase one","phrase two","phrase three"]
            No punctuation or special characters."""

        return {
            "role": "user",
            "content": content
        }

    @staticmethod
    def get_messages(existing_phrases=None):
        messages = [PhraseGeneration.get_system_prompt()]
        messages.append(PhraseGeneration.get_generation_prompt(existing_phrases))
        return messages 


class OdiaPhraseGeneration:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are an Odia language expert who generates common Odia phrases.
            Return ONLY a JSON array of 3 Odia phrases.
            Example format: ["ତୁମେ କେମିତି ଅଛ","ମୁଁ ଭଲ ଅଛି","ଆପଣଙ୍କୁ ଦେଖି ଖୁସି ଲାଗିଲା"]
            Rules:
            - Generate natural, everyday phrases
            - Use proper Odia script
            - One line JSON array only
            - No English or romanized text"""
        }

    @staticmethod
    def get_generation_prompt(existing_phrases=None):
        if existing_phrases:
            content = f"""Existing Odia phrases: {', '.join(existing_phrases)}
            Generate 3 NEW common Odia phrases (different from existing ones).
            Return as simple JSON array: ["ଓଡ଼ିଆ ବାକ୍ୟ","ଆଉ ଏକ ବାକ୍ୟ","ତୃତୀୟ ବାକ୍ୟ"]"""
        else:
            content = """Generate 3 common Odia phrases used in daily life.
            Return as simple JSON array: ["ଓଡ଼ିଆ ବାକ୍ୟ","ଆଉ ଏକ ବାକ୍ୟ","ତୃତୀୟ ବାକ୍ୟ"]"""

        return {
            "role": "user",
            "content": content
        }

    @staticmethod
    def get_messages(existing_phrases=None):
        messages = [OdiaPhraseGeneration.get_system_prompt()]
        messages.append(OdiaPhraseGeneration.get_generation_prompt(existing_phrases))
        return messages


class EnglishTranslation:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are an Odia to English translator.
            Return a JSON array where each item contains the Odia text and its English translation.
            Format: [{"odia":"ଓଡ଼ିଆ ବାକ୍ୟ","english":"English sentence"}]
            IMPORTANT: You must return a valid JSON array.
            - The response must start with [ and end with ]
            - Each item must be a complete JSON object
            - No trailing commas
            - No line breaks in the output"""
        }

    @staticmethod
    def get_translation_prompt(odia_phrases):
        phrases_list = ", ".join([f'"{phrase}"' for phrase in odia_phrases])
        return {
            "role": "user",
            "content": f"""Translate these Odia phrases to English: {phrases_list}
            Return as JSON array: [{{"odia":"ତୁମେ କେମିତି ଅଛ","english":"how are you"}}]
            IMPORTANT: Return ONLY the JSON array, nothing else.
            Ensure the response is valid JSON that can be parsed."""
        }

    @staticmethod
    def get_messages(phrases):
        messages = [EnglishTranslation.get_system_prompt()]
        messages.append(EnglishTranslation.get_translation_prompt(phrases))
        return messages


class RomanizedGeneration:
    @staticmethod
    def get_system_prompt():
        return {
            "role": "system",
            "content": """You are an expert in romanizing Odia text.
            Return a JSON array with Odia text and its romanized form.
            Format: [{"odia":"ଓଡ଼ିଆ","romanized":"odia"}]
            IMPORTANT: 
            - Response must be valid JSON
            - Must start with [ and end with ]
            - Each item must have both 'odia' and 'romanized' fields
            - No line breaks in the output
            Use standard romanization rules for Odia."""
        }

    @staticmethod
    def get_romanization_prompt(odia_phrases):
        phrases_list = ", ".join([f'"{phrase}"' for phrase in odia_phrases])
        return {
            "role": "user",
            "content": f"""Romanize these Odia phrases: {phrases_list}
            Return as JSON array: [{{"odia":"ତୁମେ କେମିତି ଅଛ","romanized":"tume kemiti acha"}}]"""
        }

    @staticmethod
    def get_messages(phrases):
        messages = [RomanizedGeneration.get_system_prompt()]
        messages.append(RomanizedGeneration.get_romanization_prompt(phrases))
        return messages 