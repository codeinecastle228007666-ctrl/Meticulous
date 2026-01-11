import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class FileOrganizer:
    def __init__(self):
        self.default_categories = {
            'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'Документы': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx'],
            'Архивы': ['.zip', '.rar', '.7z', '.tar'],
            'Музыка': ['.mp3', '.wav', '.flac'],
            'Видео': ['.mp4', '.avi', '.mkv'],
        }
    
    def organize_files(self, source_dir: str, categories: Dict, organize_by_date: bool = True, date_format: str = "%Y-%m-%d"):
        """Основная функция сортировки"""
        source_path = Path(source_dir)
        results = {'moved': 0, 'errors': 0}
        
        for file_path in source_path.iterdir():
            if file_path.is_file():
                try:
                    ext = file_path.suffix.lower()
                    
                    # Находим категорию
                    category = "Разное"
                    for cat_name, extensions in categories.items():
                        if ext in [e.lower() for e in extensions]:
                            category = cat_name
                            break
                    
                    # Создаем путь назначения
                    if organize_by_date:
                        try:
                            timestamp = os.path.getctime(file_path)
                            date_str = datetime.fromtimestamp(timestamp).strftime(date_format)
                            target_dir = source_path / category / date_str
                        except:
                            target_dir = source_path / category
                    else:
                        target_dir = source_path / category
                    
                    # Создаем папки
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Перемещаем файл
                    target_file = target_dir / file_path.name
                    counter = 1
                    while target_file.exists():
                        new_name = f"{file_path.stem}_{counter}{file_path.suffix}"
                        target_file = target_dir / new_name
                        counter += 1
                    
                    shutil.move(str(file_path), str(target_file))
                    results['moved'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    print(f"Ошибка с {file_path.name}: {e}")
        
        return results
