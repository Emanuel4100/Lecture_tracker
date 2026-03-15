import json
import os

class Translator:
    def __init__(self, lang="he"):
        self.lang = lang
        self.translations = {}
        self.load_translations()

    def set_language(self, lang):
        self.lang = lang
        self.load_translations()

    def load_translations(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "locales", f"{self.lang}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            self.translations = {}

    def get(self, key, **kwargs):
        keys = key.split('.')
        val = self.translations
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return kwargs.get('default', key)
        
        if kwargs and isinstance(val, str):
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return val

translator = Translator("he")

def t(key, **kwargs):
    return translator.get(key, **kwargs)