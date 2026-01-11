# widgets.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CategoryWidget(QWidget):
    def __init__(self, category_name="", extensions="", parent=None):
        super().__init__(parent)
        self.setup_ui(category_name, extensions)
    
    def setup_ui(self, category_name, extensions):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)
        
        # Поле для названия категории
        self.name_edit = QLineEdit(category_name)
        self.name_edit.setPlaceholderText("Название папки")
        self.name_edit.setMinimumWidth(180)
        self.name_edit.setMaximumWidth(200)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding: 8px;
                background-color: #2d2d2d;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #64b5f6;
                background-color: #252525;
            }
            QLineEdit:hover {
                border-color: #5a5a5a;
            }
        """)
        
        # Поле для расширений
        self.ext_edit = QLineEdit(extensions)
        self.ext_edit.setPlaceholderText(".jpg, .png, .pdf...")
        self.ext_edit.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding: 8px;
                background-color: #2d2d2d;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #64b5f6;
                background-color: #252525;
            }
            QLineEdit:hover {
                border-color: #5a5a5a;
            }
        """)
        
        # Кнопка удаления
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(36, 36)
        self.delete_btn.setToolTip("Удалить категорию")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: #ff6b6b;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #ff6b6b;
                color: #ff4444;
            }
            QPushButton:pressed {
                background-color: #333333;
                border-color: #ff4444;
            }
        """)
        
        # Метки
        name_label = QLabel("Папка:")
        name_label.setStyleSheet("color: #b0b0b0; font-size: 13px; font-weight: 500;")
        ext_label = QLabel("Расширения:")
        ext_label.setStyleSheet("color: #b0b0b0; font-size: 13px; font-weight: 500;")
        
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(ext_label)
        layout.addWidget(self.ext_edit, 1)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)
    
    def get_data(self):
        name = self.name_edit.text().strip()
        extensions = [ext.strip() for ext in self.ext_edit.text().split(',') if ext.strip()]
        return name, extensions


class FilePreviewTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["📄 Файл", "📝 Тип", "📁 Категория", "📍 Новая папка"])
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setShowGrid(False)
        
        # Настраиваем заголовки
        header = self.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #3a3a3a;
                color: #b0b0b0;
                font-weight: 600;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Настраиваем таблицу
        self.setStyleSheet("""
            QTableWidget {
                background-color: #252525;
                alternate-background-color: #2a2a2a;
                gridline-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                font-size: 12px;
                outline: none;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            QTableWidget::item:selected {
                background-color: #1976d2;
                color: white;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
    
    def clear(self):
        self.setRowCount(0)


class StatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(400)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 16px;
                color: #e0e0e0;
                font-size: 13px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QTextEdit:focus {
                border: 1px solid #64b5f6;
            }
        """)
        
        layout.addWidget(self.stats_text)
        self.setLayout(layout)