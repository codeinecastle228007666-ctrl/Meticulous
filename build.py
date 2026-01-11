# build_simple.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 50)
    print("   🛠️  СБОРКА METICULOUS.EXE")
    print("=" * 50)
    print()
    
    # Получаем текущую папку и переходим в нее
    current_dir = Path(__file__).parent
    print(f"📁 Текущая папка: {current_dir}")
    
    # Переходим в папку проекта
    os.chdir(current_dir)
    print(f"📁 Рабочая папка: {os.getcwd()}")
    
    # Проверяем иконку
    icon_file = "icon.ico"
    if not Path(icon_file).exists():
        print("❌ Файл icon.ico не найден!")
        print("Создайте иконку 256x256 и сохраните как icon.ico")
        input("\nНажмите Enter для выхода...")
        return
    
    # Проверяем папки
    required_folders = ['src', 'data', 'config']
    for folder in required_folders:
        if not Path(folder).exists():
            print(f"❌ Папка {folder}/ не найдена!")
            input("\nНажмите Enter для выхода...")
            return
    
    # Создаем папку dist если нет
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Простая команда сборки - БЕЗ полных путей в аргументах
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=Meticulous",
        "--onefile",
        "--windowed",
        "--icon=icon.ico",
        "--add-data=src;src",
        "--add-data=data;data",
        "--add-data=config;config",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.sip",
        "--clean",
        "run.py"
    ]
    
    print("🔨 Запуск сборки...")
    print(f"📋 Команда: {' '.join(cmd)}")
    print()
    
    try:
        # Запускаем сборку с текущей рабочей директорией
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            cwd=current_dir  # Указываем рабочую директорию
        )
        
        print("✅ Сборка завершена успешно!")
        
        # Проверяем созданный файл
        exe_path = dist_dir / "Meticulous.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Файл создан: {exe_path}")
            print(f"   📏 Размер: {size_mb:.2f} МБ")
            
            # Создаем батник для тестирования
            create_test_bat(exe_path)
            
        else:
            print("❌ Файл не создан")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке:")
        if e.stderr:
            print("STDERR:", e.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout)
    
    print()
    input("Нажмите Enter для выхода...")

def create_test_bat(exe_path):
    """Создаем батник для тестирования"""
    bat_content = f"""@echo off
chcp 65001 > nul
echo ================================
echo   Тестирование Meticulous.exe
echo ================================
echo.
echo Запуск: {exe_path.name}
echo.
"{exe_path}"
echo.
echo Программа завершена.
pause
"""
    
    bat_path = exe_path.parent / "test_meticulous.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print(f"   📄 Создан тестовый файл: {bat_path.name}")

if __name__ == "__main__":
    main()