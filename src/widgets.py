from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CategoryWidget(QWidget):
    def __init__(self, category_name="", extensions="", parent=None):
        super().__init__(parent)
        self.setup_ui(category_name, extensions)
    
    def setup_ui(self, category_name, extensions):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Поле для названия категории
        self.name_edit = QLineEdit(category_name)
        self.name_edit.setPlaceholderText("Название категории")
        self.name_edit.setMinimumWidth(150)
        
        # Поле для расширений
        self.ext_edit = QLineEdit(extensions)
        self.ext_edit.setPlaceholderText(".jpg, .png, .pdf...")
        
        # Кнопка удаления
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        
        layout.addWidget(QLabel("Папка:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Расширения:"))
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
        self.setHorizontalHeaderLabels(["Файл", "Тип", "Категория", "Новая папка"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
    
    def clear(self):
        self.setRowCount(0)


class StatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(300)
        
        layout.addWidget(self.stats_text)
        self.setLayout(layout)
