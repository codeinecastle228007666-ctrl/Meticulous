import sys
import os
import traceback

# Добавляем папку src в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    try:
        # Попробуем импортировать и запустить приложение
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
