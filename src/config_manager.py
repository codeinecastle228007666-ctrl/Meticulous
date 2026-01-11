# config_manager.py
import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.app_dir = Path(os.path.dirname(__file__)).parent
        self.config_dir = self.app_dir / "config"
        self.config_file = self.config_dir / "organizer_config.json"
        
        # Создаем структуру папок
        self.setup_directories()
    
    def setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.config_dir,
            self.app_dir / "data" / "languages",
            self.app_dir / "logs",
            self.app_dir / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """Загрузка конфигурации"""
        default_config = {
            'source_folder': str(Path.home() / "Downloads"),
            'categories': {
                'Изображения': ['.jpg', '.jpeg', '.png', '.gif'],
                'Документы': ['.pdf', '.doc', '.docx', '.txt'],
                'Архивы': ['.zip', '.rar', '.7z']
            },
            'organize_by_date': True,
            'date_format': 0,
            'language': 'ru',
            'duplicate_method': 0,
            'duplicate_size_threshold': 10
        }
        
        if not self.config_file.exists():
            self.save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Объединяем с дефолтными значениями
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            
            return config
            
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            return default_config
    
    def save_config(self, config):
        """Сохранение конфигурации"""
        try:
            # Создаем резервную копию
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.backup')
                import shutil
                shutil.copy2(self.config_file, backup_file)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            return True
            
        except PermissionError:
            # Пробуем сохранить в папке пользователя
            user_config = Path.home() / ".file_organizer" / "config.json"
            user_config.parent.mkdir(parents=True, exist_ok=True)
            
            with open(user_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            self.config_file = user_config
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
            return False
    
    def get_config_path(self):
        """Получение пути к файлу конфигурации"""
        return str(self.config_file)
