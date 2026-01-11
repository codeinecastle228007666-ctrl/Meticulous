import json
from pathlib import Path

class LanguageManager:
    def __init__(self):
        self.languages = {}
        self.current_language = "ru"
        self.load_languages()
    
    def load_languages(self):
        """Загрузка языков из файлов"""
        lang_dir = Path("data/languages")
        
        for lang_file in lang_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)
            except:
                print(f"Error loading language: {lang_code}")
        
        # Если нет языков, создаем английский по умолчанию
        if not self.languages:
            self.languages['en'] = self.get_default_english()
    
    def set_language(self, lang_code):
        """Установка языка"""
        if lang_code in self.languages:
            self.current_language = lang_code
            return True
        return False
    
    def get_text(self, key, default=None):
        """Получить текст по ключу"""
        try:
            keys = key.split('.')
            value = self.languages[self.current_language]
            
            for k in keys:
                value = value[k]
            
            return value
        except:
            return default or key
    
    def get_texts(self):
        """Получить все тексты для текущего языка"""
        return self.languages.get(self.current_language, {})
    
    def get_default_english(self):
        return {
            "app_name": "File Organizer Pro",
            "tabs": {
                "main": "🏠 Organization",
                "duplicates": "🔄 Duplicates",
                "settings": "⚙️ Settings",
                "stats": "📈 Statistics"
            },
            "buttons": {
                "browse": "📁 Browse",
                "scan": "🔍 Scan",
                "preview": "👁 Preview",
                "organize": "🚀 Organize",
                "find_duplicates": "🔍 Find Duplicates",
                "clean_duplicates": "🗑️ Clean Duplicates"
            }
            # ... остальные тексты
        }
