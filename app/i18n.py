import json
import os
from typing import Dict, Any

class I18n:
    def __init__(self, locales_dir: str = "app/locales", default_lang: str = "de"):
        self.locales_dir = locales_dir
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()

    def load_translations(self):
        if not os.path.exists(self.locales_dir):
            print(f"Warning: Locales directory {self.locales_dir} not found.")
            return

        for filename in os.listdir(self.locales_dir):
            if filename.endswith(".json"):
                lang = filename[:-5]
                try:
                    with open(os.path.join(self.locales_dir, filename), "r", encoding="utf-8") as f:
                        self.translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading locale {lang}: {e}")

    def get_translation(self, lang: str, key: str) -> str:
        """
        Get translation for a key. Key format: 'section.key' (e.g., 'common.save')
        Falls back to default language if key not found in requested language.
        """
        # Try requested language
        val = self._lookup(lang, key)
        if val is not None:
            return val

        # Try default language
        if lang != self.default_lang:
            val = self._lookup(self.default_lang, key)
            if val is not None:
                return val

        # Fallback to key itself
        return key

    def _lookup(self, lang: str, key: str) -> str | None:
        if lang not in self.translations:
            return None

        data = self.translations[lang]
        parts = key.split(".")

        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return None

        if isinstance(data, str):
            return data
        return None

# Singleton instance
i18n = I18n()
