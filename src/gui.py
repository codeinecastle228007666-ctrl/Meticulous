import json
import os
from datetime import datetime
from pathlib import Path
import hashlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .widgets import CategoryWidget, FilePreviewTable, StatisticsWidget
from .organizer import FileOrganizer
from .duplicates import DuplicateFinder
from .languages import LanguageManager
from .utils import *

class ModernButton(QPushButton):
    def __init__(self, text, icon=None, primary=False, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        
        if icon:
            self.setIcon(QIcon(icon))
        
        if primary:
            self.setStyleSheet("""
                ModernButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                    border-radius: 6px;
                }
                ModernButton:hover {
                    background-color: #1976D2;
                }
                ModernButton:pressed {
                    background-color: #0D47A1;
                }
            """)
        else:
            self.setStyleSheet("""
                ModernButton {
                    background-color: #424242;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border: 1px solid #555555;
                    border-radius: 6px;
                }
                ModernButton:hover {
                    background-color: #505050;
                }
            """)

class FileOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = "config/organizer_config.json"
        self.language_manager = LanguageManager()
        self.organizer = FileOrganizer()
        self.duplicate_finder = DuplicateFinder()
        self.current_language = "ru"
        
        self.setup_ui()
        self.load_config()
        self.load_language()
    
    def setup_ui(self):
        self.setWindowTitle("File Organizer Pro")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет с табами
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Создаем табы
        self.setup_main_tab()
        self.setup_duplicates_tab()
        self.setup_settings_tab()
        self.setup_stats_tab()
        
        # Создаем меню
        self.setup_menu()
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
    
    def setup_main_tab(self):
        """Основная вкладка сортировки"""
        main_tab = QWidget()
        layout = QVBoxLayout(main_tab)
        
        # Панель быстрого доступа
        quick_panel = QHBoxLayout()
        
        self.source_btn = ModernButton("📁 Выбрать папку", primary=True)
        self.source_btn.clicked.connect(self.browse_folder)
        
        self.preview_btn = ModernButton("👁 Предпросмотр")
        self.preview_btn.clicked.connect(self.preview_organization)
        
        self.organize_btn = ModernButton("🚀 Запустить сортировку", primary=True)
        self.organize_btn.clicked.connect(self.organize_files)
        
        quick_panel.addWidget(self.source_btn)
        quick_panel.addWidget(self.preview_btn)
        quick_panel.addWidget(self.organize_btn)
        quick_panel.addStretch()
        
        layout.addLayout(quick_panel)
        
        # Основная область в виде splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - настройки
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Папка источника
        folder_group = QGroupBox("Исходная папка")
        folder_layout = QVBoxLayout()
        
        self.source_path = QLineEdit(str(Path.home() / "Downloads"))
        self.source_path.setReadOnly(True)
        
        self.scan_btn = QPushButton("🔍 Сканировать")
        self.scan_btn.clicked.connect(self.scan_folder)
        
        folder_info_layout = QHBoxLayout()
        folder_info_layout.addWidget(QLabel("Путь:"))
        folder_info_layout.addWidget(self.source_path, 1)
        folder_info_layout.addWidget(self.scan_btn)
        
        self.folder_stats = QLabel("Выберите папку для сканирования")
        
        folder_layout.addLayout(folder_info_layout)
        folder_layout.addWidget(self.folder_stats)
        folder_group.setLayout(folder_layout)
        
        left_layout.addWidget(folder_group)
        
        # Категории
        categories_group = QGroupBox("Категории файлов")
        categories_layout = QVBoxLayout()
        
        # Прокручиваемая область для категорий
        self.categories_scroll = QScrollArea()
        self.categories_scroll.setWidgetResizable(True)
        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setAlignment(Qt.AlignTop)
        
        self.categories_scroll.setWidget(self.categories_container)
        
        # Кнопки управления категориями
        category_buttons = QHBoxLayout()
        self.add_category_btn = ModernButton("+ Добавить категорию")
        self.add_category_btn.clicked.connect(self.add_category)
        self.load_preset_btn = ModernButton("📋 Загрузить пресет")
        self.load_preset_btn.clicked.connect(self.load_preset_categories)
        
        category_buttons.addWidget(self.add_category_btn)
        category_buttons.addWidget(self.load_preset_btn)
        category_buttons.addStretch()
        
        categories_layout.addWidget(self.categories_scroll)
        categories_layout.addLayout(category_buttons)
        categories_group.setLayout(categories_layout)
        
        left_layout.addWidget(categories_group, 1)
        
        # Правая панель - предпросмотр
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        
        self.preview_table = FilePreviewTable()
        
        preview_buttons = QHBoxLayout()
        self.clear_preview_btn = ModernButton("Очистить")
        self.clear_preview_btn.clicked.connect(self.preview_table.clear)
        self.export_preview_btn = ModernButton("Экспорт списка")
        self.export_preview_btn.clicked.connect(self.export_preview)
        
        preview_buttons.addWidget(self.clear_preview_btn)
        preview_buttons.addWidget(self.export_preview_btn)
        preview_buttons.addStretch()
        
        preview_layout.addWidget(self.preview_table)
        preview_layout.addLayout(preview_buttons)
        preview_group.setLayout(preview_layout)
        
        right_layout.addWidget(preview_group)
        
        # Добавляем панели в splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter, 1)
        
        self.tab_widget.addTab(main_tab, "🏠 Сортировка")
    
    def setup_duplicates_tab(self):
        """Вкладка поиска дубликатов"""
        dup_tab = QWidget()
        layout = QVBoxLayout(dup_tab)
        
        # Панель управления
        control_panel = QHBoxLayout()
        
        self.dup_source_btn = ModernButton("📁 Выбрать папку")
        self.dup_source_btn.clicked.connect(lambda: self.browse_folder(dup=True))
        
        self.find_dups_btn = ModernButton("🔍 Найти дубликаты", primary=True)
        self.find_dups_btn.clicked.connect(self.find_duplicates)
        
        self.clean_dups_btn = ModernButton("🗑️ Очистить дубликаты")
        self.clean_dups_btn.clicked.connect(self.clean_duplicates)
        
        control_panel.addWidget(self.dup_source_btn)
        control_panel.addWidget(self.find_dups_btn)
        control_panel.addWidget(self.clean_dups_btn)
        control_panel.addStretch()
        
        layout.addLayout(control_panel)
        
        # Splitter для результатов
        dup_splitter = QSplitter(Qt.Horizontal)
        
        # Таблица дубликатов
        self.dup_table = QTableWidget()
        self.dup_table.setColumnCount(5)
        self.dup_table.setHorizontalHeaderLabels(["Имя файла", "Путь", "Размер", "Дата создания", "Хэш"])
        self.dup_table.horizontalHeader().setStretchLastSection(True)
        self.dup_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Детальная информация
        detail_panel = QWidget()
        detail_layout = QVBoxLayout(detail_panel)
        
        self.dup_info = QTextEdit()
        self.dup_info.setReadOnly(True)
        
        self.dup_image_preview = QLabel()
        self.dup_image_preview.setAlignment(Qt.AlignCenter)
        self.dup_image_preview.setMinimumHeight(200)
        
        detail_layout.addWidget(QLabel("Детали:"))
        detail_layout.addWidget(self.dup_info)
        detail_layout.addWidget(QLabel("Предпросмотр:"))
        detail_layout.addWidget(self.dup_image_preview, 1)
        
        dup_splitter.addWidget(self.dup_table)
        dup_splitter.addWidget(detail_panel)
        dup_splitter.setSizes([700, 300])
        
        layout.addWidget(dup_splitter, 1)
        
        # Статистика
        self.dup_stats = QLabel("Готов к поиску дубликатов")
        layout.addWidget(self.dup_stats)
        
        self.tab_widget.addTab(dup_tab, "🔄 Дубликаты")
        
        # Подключаем выделение в таблице
        self.dup_table.itemSelectionChanged.connect(self.on_duplicate_selected)
    
    def setup_settings_tab(self):
        """Вкладка настроек"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # Настройки сортировки
        sort_group = QGroupBox("Настройки сортировки")
        sort_layout = QVBoxLayout()
        
        self.date_checkbox = QCheckBox("Создавать папки по дате")
        self.date_checkbox.setChecked(True)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Формат даты:"))
        
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "ГГГГ-ММ-ДД (2024-01-15)",
            "ДД-ММ-ГГГГ (15-01-2024)",
            "ГГГГ/ММ/ДД (2024/01/15)",
            "ММ-ДД-ГГГГ (01-15-2024)",
            "ДД Мес ГГГГ (15 Янв 2024)"
        ])
        
        date_layout.addWidget(self.date_format_combo)
        date_layout.addStretch()
        
        sort_layout.addWidget(self.date_checkbox)
        sort_layout.addLayout(date_layout)
        
        self.conflict_checkbox = QCheckBox("Автоматически разрешать конфликты имен")
        self.conflict_checkbox.setChecked(True)
        
        self.backup_checkbox = QCheckBox("Создавать резервную копию перед перемещением")
        
        sort_layout.addWidget(self.conflict_checkbox)
        sort_layout.addWidget(self.backup_checkbox)
        
        sort_group.setLayout(sort_layout)
        
        # Настройки дубликатов
        dup_group = QGroupBox("Настройки поиска дубликатов")
        dup_layout = QVBoxLayout()
        
        dup_method_layout = QHBoxLayout()
        dup_method_layout.addWidget(QLabel("Метод сравнения:"))
        
        self.dup_method_combo = QComboBox()
        self.dup_method_combo.addItems(["По хэшу (точно)", "По имени и размеру (быстро)", "По содержимому (медленно)"])
        
        dup_method_layout.addWidget(self.dup_method_combo)
        dup_method_layout.addStretch()
        
        self.dup_size_threshold = QSpinBox()
        self.dup_size_threshold.setRange(1, 1000)
        self.dup_size_threshold.setValue(10)
        self.dup_size_threshold.setSuffix(" МБ минимум")
        
        dup_layout.addLayout(dup_method_layout)
        dup_layout.addWidget(QLabel("Минимальный размер для проверки:"))
        dup_layout.addWidget(self.dup_size_threshold)
        
        dup_group.setLayout(dup_layout)
        
        # Язык
        lang_group = QGroupBox("Язык интерфейса")
        lang_layout = QHBoxLayout()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English", "中文"])
        self.lang_combo.currentTextChanged.connect(self.change_language)
        
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        lang_group.setLayout(lang_layout)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.save_settings_btn = ModernButton("💾 Сохранить настройки", primary=True)
        self.save_settings_btn.clicked.connect(self.save_config)
        
        self.reset_settings_btn = ModernButton("🔄 Сбросить настройки")
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_settings_btn)
        button_layout.addWidget(self.reset_settings_btn)
        button_layout.addStretch()
        
        layout.addWidget(sort_group)
        layout.addWidget(dup_group)
        layout.addWidget(lang_group)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(settings_tab, "⚙️ Настройки")
    
    def setup_stats_tab(self):
        """Вкладка статистики"""
        stats_tab = QWidget()
        layout = QVBoxLayout(stats_tab)
        
        self.stats_widget = StatisticsWidget()
        layout.addWidget(self.stats_widget)
        
        # Кнопки обновления
        stats_buttons = QHBoxLayout()
        self.refresh_stats_btn = ModernButton("🔄 Обновить статистику")
        self.refresh_stats_btn.clicked.connect(self.update_statistics)
        self.export_stats_btn = ModernButton("📊 Экспорт статистики")
        self.export_stats_btn.clicked.connect(self.export_statistics)
        
        stats_buttons.addWidget(self.refresh_stats_btn)
        stats_buttons.addWidget(self.export_stats_btn)
        stats_buttons.addStretch()
        
        layout.addLayout(stats_buttons)
        
        self.tab_widget.addTab(stats_tab, "📈 Статистика")
    
    def setup_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        
        new_action = QAction("Новая конфигурация", self)
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        load_action = QAction("Загрузить конфигурацию", self)
        load_action.triggered.connect(self.load_config_dialog)
        file_menu.addAction(load_action)
        
        save_action = QAction("Сохранить конфигурацию", self)
        save_action.triggered.connect(self.save_config_dialog)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Инструменты
        tools_menu = menubar.addMenu("Инструменты")
        
        backup_action = QAction("Создать резервную копию", self)
        backup_action.triggered.connect(self.create_backup)
        tools_menu.addAction(backup_action)
        
        cleanup_action = QAction("Очистить пустые папки", self)
        cleanup_action.triggered.connect(self.cleanup_empty_folders)
        tools_menu.addAction(cleanup_action)
        
        # Справка
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # === МЕТОДЫ ДЛЯ ОСНОВНОЙ ВКЛАДКИ ===
    
    def browse_folder(self, dup=False):
        """Выбор папки"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку",
            str(Path.home() / "Downloads"),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            if dup:
                # Для вкладки дубликатов - просто показываем путь в статусе
                self.status_bar.showMessage(f"Выбрана папка для поиска дубликатов: {folder}")
            else:
                self.source_path.setText(folder)
    
    def scan_folder(self):
        """Сканирование папки"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        # Подсчет файлов
        try:
            file_count = 0
            total_size = 0
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
            
            self.folder_stats.setText(f"Найдено файлов: {file_count}, Общий размер: {self.format_size(total_size)}")
            self.status_bar.showMessage(f"Сканирование завершено. Найдено {file_count} файлов")
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при сканировании: {str(e)}")
    
    def preview_organization(self):
        """Предпросмотр сортировки"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        # Получаем категории
        categories = self.get_categories()
        if not categories:
            QMessageBox.warning(self, "Ошибка", "Не заданы категории!")
            return
        
        # Очищаем таблицу предпросмотра
        self.preview_table.clear()
        self.preview_table.setRowCount(0)
        
        # Заполняем таблицу предпросмотра
        file_count = 0
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                # Находим категорию
                category = "Разное"
                for cat_name, extensions in categories.items():
                    if ext in [e.lower() for e in extensions]:
                        category = cat_name
                        break
                
                # Добавляем в таблицу
                row = self.preview_table.rowCount()
                self.preview_table.insertRow(row)
                self.preview_table.setItem(row, 0, QTableWidgetItem(file_path.name))
                self.preview_table.setItem(row, 1, QTableWidgetItem(ext if ext else "без расширения"))
                self.preview_table.setItem(row, 2, QTableWidgetItem(category))
                
                # Определяем новую папку
                if self.date_checkbox.isChecked():
                    try:
                        timestamp = os.path.getctime(file_path)
                        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                        new_folder = f"{category}/{date_str}"
                    except:
                        new_folder = category
                else:
                    new_folder = category
                
                self.preview_table.setItem(row, 3, QTableWidgetItem(new_folder))
                file_count += 1
        
        self.status_bar.showMessage(f"Предпросмотр: {file_count} файлов будет отсортировано")
        QMessageBox.information(self, "Предпросмотр", f"Будет отсортировано {file_count} файлов")
    
    def organize_files(self):
        """Запуск сортировки файлов"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        # Получаем категории
        categories = self.get_categories()
        if not categories:
            QMessageBox.warning(self, "Ошибка", "Не заданы категории!")
            return
        
        # Подтверждение
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f'Начать сортировку файлов в папке?\n{source_dir}',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Определяем формат даты
        date_format_map = {
            0: "%Y-%m-%d",
            1: "%d-%m-%Y",
            2: "%Y/%m/%d",
            3: "%m-%d-%Y",
            4: "%d %b %Y"
        }
        date_format = date_format_map.get(self.date_format_combo.currentIndex(), "%Y-%m-%d")
        
        # Запускаем сортировку
        try:
            results = self.organizer.organize_files(
                source_dir=str(source_dir),
                categories=categories,
                organize_by_date=self.date_checkbox.isChecked(),
                date_format=date_format
            )
            
            QMessageBox.information(
                self, 
                "Готово", 
                f"Сортировка завершена!\nПеремещено: {results['moved']} файлов\nОшибок: {results['errors']}"
            )
            
            # Обновляем статистику
            self.scan_folder()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сортировке: {str(e)}")
    
    def get_categories(self):
        """Получение категорий из виджетов"""
        categories = {}
        for i in range(self.categories_layout.count()):
            widget = self.categories_layout.itemAt(i).widget()
            if isinstance(widget, CategoryWidget):
                name, exts = widget.get_data()
                if name and exts:
                    categories[name] = exts
        return categories
    
    def add_category(self):
        """Добавление новой категории"""
        category_widget = CategoryWidget()
        category_widget.delete_btn.clicked.connect(
            lambda: self.remove_category(category_widget)
        )
        self.categories_layout.addWidget(category_widget)
    
    def remove_category(self, widget):
        """Удаление категории"""
        widget.deleteLater()
    
    def load_preset_categories(self):
        """Загрузка пресета категорий"""
        # Очищаем текущие категории
        for i in reversed(range(self.categories_layout.count())):
            widget = self.categories_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Добавляем категории по умолчанию
        default_categories = {
            "Изображения": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Документы": [".pdf", ".doc", ".docx", ".txt", ".xlsx"],
            "Архивы": [".zip", ".rar", ".7z", ".tar"],
            "Музыка": [".mp3", ".wav", ".flac"],
            "Видео": [".mp4", ".avi", ".mkv"],
        }
        
        for name, exts in default_categories.items():
            category_widget = CategoryWidget(name, ", ".join(exts))
            category_widget.delete_btn.clicked.connect(
                lambda checked, w=category_widget: self.remove_category(w)
            )
            self.categories_layout.addWidget(category_widget)
    
    def export_preview(self):
        """Экспорт списка предпросмотра"""
        if self.preview_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт списка файлов",
            "preview_list.csv",
            "CSV Files (*.csv);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Заголовки
                    headers = ["Файл", "Тип", "Категория", "Новая папка"]
                    f.write(";".join(headers) + "\n")
                    
                    # Данные
                    for row in range(self.preview_table.rowCount()):
                        row_data = []
                        for col in range(self.preview_table.columnCount()):
                            item = self.preview_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        f.write(";".join(row_data) + "\n")
                
                QMessageBox.information(self, "Успех", f"Список экспортирован в {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    # === МЕТОДЫ ДЛЯ ВКЛАДКИ ДУБЛИКАТОВ ===
    
    def find_duplicates(self):
        """Поиск дубликатов файлов"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        # Показываем прогресс
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        # Ищем дубликаты в отдельном потоке
        from PyQt5.QtCore import QThread, pyqtSignal
        
        class DupFinderThread(QThread):
            finished = pyqtSignal(dict)
            progress = pyqtSignal(int)
            
            def __init__(self, source_dir, method):
                super().__init__()
                self.source_dir = source_dir
                self.method = method
            
            def run(self):
                finder = DuplicateFinder()
                method_map = {
                    0: 'hash',
                    1: 'name_size',
                    2: 'content'
                }
                method = method_map.get(self.method, 'hash')
                
                duplicates = finder.find_duplicates(str(self.source_dir), method=method)
                self.finished.emit(duplicates)
        
        self.dup_thread = DupFinderThread(
            source_dir, 
            self.dup_method_combo.currentIndex()
        )
        self.dup_thread.finished.connect(self.display_duplicates)
        self.dup_thread.start()
        
        self.status_bar.showMessage("Поиск дубликатов...")
    
    def display_duplicates(self, duplicates):
        """Отображение найденных дубликатов"""
        self.progress_bar.hide()
        
        self.dup_table.setRowCount(0)
        
        total_size = 0
        total_files = 0
        for i, (hash_val, files) in enumerate(duplicates.items()):
            for file_info in files:
                row = self.dup_table.rowCount()
                self.dup_table.insertRow(row)
                
                self.dup_table.setItem(row, 0, QTableWidgetItem(file_info['name']))
                self.dup_table.setItem(row, 1, QTableWidgetItem(file_info['path']))
                self.dup_table.setItem(row, 2, QTableWidgetItem(self.format_size(file_info['size'])))
                self.dup_table.setItem(row, 3, QTableWidgetItem(
                    datetime.fromtimestamp(file_info['ctime']).strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.dup_table.setItem(row, 4, QTableWidgetItem(hash_val[:16]))
                
                total_size += file_info['size']
                total_files += 1
        
        self.dup_stats.setText(
            f"Найдено дубликатов: {len(duplicates)} групп, "
            f"Файлов: {total_files}, "
            f"Общий размер: {self.format_size(total_size)}"
        )
        
        self.status_bar.showMessage(f"Найдено {len(duplicates)} групп дубликатов")
    
    def on_duplicate_selected(self):
        """Обработка выбора дубликата"""
        selected = self.dup_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        path = self.dup_table.item(row, 1).text()
        
        # Показываем информацию о файле
        file_info = f"Путь: {path}\n"
        file_info += f"Имя: {self.dup_table.item(row, 0).text()}\n"
        file_info += f"Размер: {self.dup_table.item(row, 2).text()}\n"
        file_info += f"Создан: {self.dup_table.item(row, 3).text()}\n"
        file_info += f"Хэш: {self.dup_table.item(row, 4).text()}"
        
        self.dup_info.setText(file_info)
        
        # Пытаемся показать превью изображения
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.dup_image_preview.setPixmap(pixmap)
            else:
                self.dup_image_preview.setText("Не удалось загрузить изображение")
        else:
            self.dup_image_preview.setText("Превью недоступно")
    
    def clean_duplicates(self):
        """Очистка дубликатов"""
        if self.dup_table.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Нет дубликатов для очистки")
            return
        
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Удалить все найденные дубликаты?\n'
            'Будет сохранен только самый новый файл в каждой группе.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Собираем данные о дубликатах из таблицы
            duplicates_data = {}
            current_row = 0
            while current_row < self.dup_table.rowCount():
                hash_val = self.dup_table.item(current_row, 4).text()
                if hash_val not in duplicates_data:
                    duplicates_data[hash_val] = []
                
                file_info = {
                    'path': self.dup_table.item(current_row, 1).text(),
                    'name': self.dup_table.item(current_row, 0).text(),
                    'size': self.parse_size(self.dup_table.item(current_row, 2).text()),
                    'ctime': datetime.strptime(self.dup_table.item(current_row, 3).text(), "%Y-%m-%d %H:%M:%S").timestamp()
                }
                duplicates_data[hash_val].append(file_info)
                current_row += 1
            
            # Удаляем дубликаты
            deleted = self.duplicate_finder.remove_duplicates(duplicates_data)
            self.status_bar.showMessage(f"Удалено {deleted} дубликатов")
            
            # Обновляем таблицу
            self.find_duplicates()
    
    def parse_size(self, size_str):
        """Парсинг размера из строки"""
        units = {'Б': 1, 'КБ': 1024, 'МБ': 1024**2, 'ГБ': 1024**3, 'ТБ': 1024**4}
        try:
            num, unit = size_str.split()
            num = float(num)
            return int(num * units.get(unit, 1))
        except:
            return 0
    
    # === НАСТРОЙКИ И КОНФИГУРАЦИЯ ===
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Загружаем настройки
            if 'source_folder' in config and config['source_folder']:
                self.source_path.setText(config['source_folder'])
            
            # Загружаем категории
            if 'categories' in config:
                for name, exts in config['categories'].items():
                    category_widget = CategoryWidget(name, ", ".join(exts))
                    category_widget.delete_btn.clicked.connect(
                        lambda checked, w=category_widget: self.remove_category(w)
                    )
                    self.categories_layout.addWidget(category_widget)
            
            # Другие настройки
            if 'organize_by_date' in config:
                self.date_checkbox.setChecked(config['organize_by_date'])
            
            if 'date_format' in config:
                self.date_format_combo.setCurrentIndex(config['date_format'])
            
            # Загружаем язык
            if 'language' in config:
                lang_index = {"ru": 0, "en": 1, "zh": 2}.get(config['language'], 0)
                self.lang_combo.setCurrentIndex(lang_index)
                self.change_language(self.lang_combo.currentText())
                
        except FileNotFoundError:
            print("Конфиг не найден, используются настройки по умолчанию")
            self.load_preset_categories()
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            self.load_preset_categories()
    
    def save_config(self):
        """Сохранение конфигурации"""
        config = {
            'source_folder': self.source_path.text(),
            'categories': self.get_categories(),
            'organize_by_date': self.date_checkbox.isChecked(),
            'date_format': self.date_format_combo.currentIndex(),
            'language': self.current_language
        }
        
        try:
            # Создаем папку config если ее нет
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            self.status_bar.showMessage("Конфигурация сохранена", 3000)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить конфигурацию: {e}")
    
    def load_language(self):
        """Загрузка языка интерфейса"""
        # Устанавливаем русский по умолчанию
        self.language_manager.set_language("ru")
        self.current_language = "ru"
    
    def change_language(self, language):
        """Изменение языка интерфейса"""
        lang_map = {"Русский": "ru", "English": "en", "中文": "zh"}
        lang_code = lang_map.get(language, "ru")
        
        if self.language_manager.set_language(lang_code):
            self.current_language = lang_code
            self.update_ui_texts()
            self.save_config()
    
    def update_ui_texts(self):
        """Обновление текстов интерфейса"""
        texts = self.language_manager.get_texts()
        
        # Обновляем названия табов
        self.tab_widget.setTabText(0, texts['tabs']['main'])
        self.tab_widget.setTabText(1, texts['tabs']['duplicates'])
        self.tab_widget.setTabText(2, texts['tabs']['settings'])
        self.tab_widget.setTabText(3, texts['tabs']['stats'])
        
        # Обновляем кнопки
        self.source_btn.setText(texts['buttons']['browse'])
        self.scan_btn.setText(texts['buttons']['scan'])
        self.preview_btn.setText(texts['buttons']['preview'])
        self.organize_btn.setText(texts['buttons']['organize'])
        self.find_dups_btn.setText(texts['buttons']['find_duplicates'])
        self.clean_dups_btn.setText(texts['buttons']['clean_duplicates'])
    
    # === МЕТОДЫ МЕНЮ ===
    
    def new_config(self):
        """Новая конфигурация"""
        reply = QMessageBox.question(
            self, 'Новая конфигурация',
            'Создать новую конфигурацию? Текущие настройки будут сброшены.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Сбрасываем настройки
            self.source_path.setText(str(Path.home() / "Downloads"))
            self.date_checkbox.setChecked(True)
            self.date_format_combo.setCurrentIndex(0)
            
            # Очищаем категории
            for i in reversed(range(self.categories_layout.count())):
                widget = self.categories_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Загружаем пресет
            self.load_preset_categories()
            
            self.status_bar.showMessage("Конфигурация сброшена", 3000)
    
    def load_config_dialog(self):
        """Диалог загрузки конфигурации"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить конфигурацию",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            self.config_file = file_path
            self.load_config()
    
    def save_config_dialog(self):
        """Диалог сохранения конфигурации"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            "organizer_config.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            self.config_file = file_path
            self.save_config()
    
    def create_backup(self):
        """Создание резервной копии"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        backup_dir = source_dir.parent / f"{source_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        reply = QMessageBox.question(
            self, 'Создание резервной копии',
            f'Создать резервную копию папки в:\n{backup_dir}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                import shutil
                shutil.copytree(source_dir, backup_dir)
                QMessageBox.information(self, "Успех", f"Резервная копия создана: {backup_dir}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при создании резервной копии: {e}")
    
    def cleanup_empty_folders(self):
        """Очистка пустых папок"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        reply = QMessageBox.question(
            self, 'Очистка пустых папок',
            f'Удалить все пустые папки в:\n{source_dir}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                empty_folders = []
                for root, dirs, files in os.walk(str(source_dir), topdown=False):
                    for dir_name in dirs:
                        dir_path = Path(root) / dir_name
                        try:
                            if not any(dir_path.iterdir()):
                                dir_path.rmdir()
                                empty_folders.append(str(dir_path))
                        except:
                            pass
                
                QMessageBox.information(self, "Успех", f"Удалено {len(empty_folders)} пустых папок")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при очистке: {e}")
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе File Organizer Pro",
            "<h2>File Organizer Pro</h2>"
            "<p>Версия 1.0</p>"
            "<p>Приложение для автоматической сортировки файлов</p>"
            "<p>Функции:</p>"
            "<ul>"
            "<li>Сортировка файлов по категориям</li>"
            "<li>Поиск дубликатов файлов</li>"
            "<li>Поддержка нескольких языков</li>"
            "<li>Создание резервных копий</li>"
            "</ul>"
            "<p>© 2024 Все права защищены</p>"
        )
    
    def update_statistics(self):
        """Обновление статистики"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            self.stats_widget.stats_text.setText("Папка не существует!")
            return
        
        try:
            stats_text = "<h2>Статистика файлов</h2>"
            stats_text += f"<p><b>Папка:</b> {source_dir}</p>"
            
            # Собираем статистику
            file_count = 0
            total_size = 0
            files_by_ext = {}
            
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    size = file_path.stat().st_size
                    total_size += size
                    
                    ext = file_path.suffix.lower()
                    if ext:
                        files_by_ext[ext] = files_by_ext.get(ext, 0) + 1
                    else:
                        files_by_ext["без расширения"] = files_by_ext.get("без расширения", 0) + 1
            
            stats_text += f"<p><b>Всего файлов:</b> {file_count}</p>"
            stats_text += f"<p><b>Общий размер:</b> {self.format_size(total_size)}</p>"
            
            # Статистика по расширениям
            stats_text += "<h3>По расширениям:</h3>"
            stats_text += "<table border='1' cellpadding='5'>"
            stats_text += "<tr><th>Расширение</th><th>Количество</th><th>Процент</th></tr>"
            
            for ext, count in sorted(files_by_ext.items(), key=lambda x: x[1], reverse=True):
                percent = (count / file_count * 100) if file_count > 0 else 0
                stats_text += f"<tr><td>{ext}</td><td>{count}</td><td>{percent:.1f}%</td></tr>"
            
            stats_text += "</table>"
            
            self.stats_widget.stats_text.setText(stats_text)
            
        except Exception as e:
            self.stats_widget.stats_text.setText(f"Ошибка при сборе статистики: {str(e)}")
    
    def export_statistics(self):
        """Экспорт статистики"""
        if not self.stats_widget.stats_text.toPlainText():
            QMessageBox.warning(self, "Ошибка", "Нет статистики для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт статистики",
            "statistics.html",
            "HTML Files (*.html);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.stats_widget.stats_text.toHtml() if file_path.endswith('.html') 
                           else self.stats_widget.stats_text.toPlainText())
                
                QMessageBox.information(self, "Успех", f"Статистика экспортирована в {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def reset_settings(self):
        """Сброс настроек"""
        reply = QMessageBox.question(
            self, 'Сброс настроек',
            'Сбросить все настройки к значениям по умолчанию?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.date_checkbox.setChecked(True)
            self.date_format_combo.setCurrentIndex(0)
            self.conflict_checkbox.setChecked(True)
            self.backup_checkbox.setChecked(False)
            self.dup_method_combo.setCurrentIndex(0)
            self.dup_size_threshold.setValue(10)
            self.lang_combo.setCurrentIndex(0)
            self.save_config()
            self.status_bar.showMessage("Настройки сброшены", 3000)
    
    def format_size(self, size_bytes):
        """Форматирование размера файла"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} ПБ"