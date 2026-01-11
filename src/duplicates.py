import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class DuplicateFinder:
    def __init__(self):
        self.duplicates = {}
    
    def find_duplicates(self, directory, method='hash'):
        """Поиск дубликатов файлов"""
        directory = Path(directory)
        
        if method == 'hash':
            return self._find_by_hash(directory)
        elif method == 'name_size':
            return self._find_by_name_size(directory)
        elif method == 'content':
            return self._find_by_content(directory)
        else:
            return self._find_by_hash(directory)
    
    def _find_by_hash(self, directory):
        """Поиск по хэшу файла"""
        files_by_hash = defaultdict(list)
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    file_hash = self._calculate_hash(file_path)
                    
                    files_by_hash[file_hash].append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'ctime': file_path.stat().st_ctime,
                        'mtime': file_path.stat().st_mtime
                    })
                except Exception as e:
                    continue
        
        # Оставляем только дубликаты (2+ файла с одинаковым хэшем)
        return {k: v for k, v in files_by_hash.items() if len(v) > 1}
    
    def _find_by_name_size(self, directory):
        """Поиск по имени и размеру (быстрый)"""
        files_by_key = defaultdict(list)
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    key = f"{file_path.name}_{file_path.stat().st_size}"
                    
                    files_by_key[key].append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'ctime': file_path.stat().st_ctime,
                        'mtime': file_path.stat().st_mtime
                    })
                except:
                    continue
        
        return {k: v for k, v in files_by_key.items() if len(v) > 1}
    
    def _find_by_content(self, directory):
        """Поиск по содержимому (точный, но медленный)"""
        # Реализация сравнения содержимого файлов
        return self._find_by_hash(directory)  # Используем хэш как временное решение
    
    def _calculate_hash(self, file_path, chunk_size=8192):
        """Вычисление MD5 хэша файла"""
        md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
        
        return md5.hexdigest()
    
    def remove_duplicates(self, duplicates_data):
        """Удаление дубликатов, сохранение только самых новых"""
        deleted_count = 0
        
        for hash_val, files in duplicates_data.items():
            # Сортируем по дате создания (новые первыми)
            files.sort(key=lambda x: x['ctime'], reverse=True)
            
            # Сохраняем самый новый, остальные удаляем
            for file_info in files[1:]:
                try:
                    Path(file_info['path']).unlink()
                    deleted_count += 1
                except:
                    continue
        
        return deleted_count
