import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from src.gui import FileOrganizerApp

def main():
    # Настройка пути для ресурсов
    if hasattr(sys, '_MEIPASS'):
        # Если запущено из exe
        os.chdir(sys._MEIPASS)
    
    app = QApplication(sys.argv)
    app.setApplicationName("File Organizer Pro")
    app.setOrganizationName("FileOrganizer")
    
    # Загрузка стилей
    load_styles(app)
    
    window = FileOrganizerApp()
    window.show()
    
    sys.exit(app.exec_())

def load_styles(app):
    """Загрузка стилей из файла или строки"""
    style = """
    QMainWindow {
        background-color: #2b2b2b;
    }
    
    QWidget {
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #3c3c3c;
        border-radius: 8px;
        margin-top: 15px;
        padding-top: 15px;
        background-color: #363636;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 10px 0 10px;
        color: #4fc3f7;
    }
    
    QPushButton {
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        border: 1px solid #555555;
        background-color: #424242;
        min-height: 30px;
    }
    
    QPushButton:hover {
        background-color: #505050;
        border-color: #666666;
    }
    
    QPushButton:pressed {
        background-color: #333333;
    }
    
    QLineEdit, QTextEdit, QComboBox {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        selection-background-color: #1976d2;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #1976d2;
    }
    
    QLabel {
        color: #cccccc;
    }
    
    QTableWidget {
        background-color: #2b2b2b;
        alternate-background-color: #333333;
        gridline-color: #444444;
        color: #ffffff;
    }
    
    QTableWidget::item:selected {
        background-color: #1976d2;
    }
    
    QHeaderView::section {
        background-color: #424242;
        padding: 8px;
        border: 1px solid #555555;
        color: #ffffff;
    }
    
    QScrollBar:vertical {
        background-color: #2b2b2b;
        width: 15px;
        border-radius: 7px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 7px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #666666;
    }
    
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #363636;
    }
    
    QTabBar::tab {
        background-color: #424242;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #1976d2;
        color: white;
    }
    
    QCheckBox {
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
    }
    
    QCheckBox::indicator:unchecked {
        background-color: #3c3c3c;
        border: 2px solid #555555;
    }
    
    QCheckBox::indicator:checked {
        background-color: #1976d2;
        border: 2px solid #1976d2;
    }
    
    QProgressBar {
        border: 1px solid #555555;
        border-radius: 4px;
        text-align: center;
        background-color: #3c3c3c;
    }
    
    QProgressBar::chunk {
        background-color: #4caf50;
        border-radius: 4px;
    }
    """
    
    app.setStyleSheet(style)

if __name__ == "__main__":
    main()
