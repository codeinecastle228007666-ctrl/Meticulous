# main.py
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.gui import FileOrganizerApp
from src.styles import get_stylesheet

def main():
    # Настройка пути для ресурсов
    if hasattr(sys, '_MEIPASS'):
        # Если запущено из exe
        os.chdir(sys._MEIPASS)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Meticulous")
    app.setOrganizationName("Meticulous")
    
    # Устанавливаем шрифт по умолчанию
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Загрузка стилей
    app.setStyleSheet(get_stylesheet())
    
    # Создаем и показываем главное окно
    window = FileOrganizerApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()