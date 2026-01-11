# run.py - ИСПРАВЛЕННЫЙ ВАРИАНТ
import sys
import os
import traceback

def main():
    try:
        # Добавляем папку src в путь Python
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Создаем необходимые папки
        folders = ['config', 'data/languages', 'logs', 'backups']
        for folder in folders:
            os.makedirs(os.path.join(os.path.dirname(__file__), folder), exist_ok=True)
        
        # Импортируем и запускаем приложение КОРРЕКТНО
        # ВАЖНО: импортируем main из папки src
        from src.main import main as app_main
        app_main()
        
    except ImportError as e:
        # Если не получается импортировать из src.main, пробуем альтернативы
        print(f"Импорт из src.main не удался: {e}")
        print("Пробуем альтернативный импорт...")
        
        try:
            # Пробуем импортировать напрямую
            from main import main as app_main
            app_main()
        except ImportError:
            # Пробуем запустить приложение напрямую
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtGui import QFont
            
            app = QApplication(sys.argv)
            app.setFont(QFont("Segoe UI", 10))
            
            # Импортируем и создаем окно
            try:
                from src.gui import FileOrganizerApp
                window = FileOrganizerApp()
            except ImportError:
                # Последняя попытка
                import src.gui as gui
                window = gui.FileOrganizerApp()
            
            window.show()
            sys.exit(app.exec_())
        
    except Exception as e:
        print("=" * 60)
        print("ОШИБКА ПРИ ЗАПУСКЕ:")
        print("=" * 60)
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        print("\n" + "=" * 60)
        print("ПОЛНАЯ ТРАССИРОВКА ОШИБКИ:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        
        # Ждем ввод пользователя перед закрытием
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()