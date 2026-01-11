# run.py
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
        
        # Импортируем и запускаем приложение
        from main import main as app_main
        app_main()
        
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
