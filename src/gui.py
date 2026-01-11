import json
import os
import shutil
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
from .config_manager import ConfigManager
from .utils import *

class ModernButton(QPushButton):
    def __init__(self, text, icon=None, primary=False, danger=False, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setMinimumWidth(120)
        
        if icon:
            self.setIcon(QIcon(icon))
        
        # Устанавливаем свойства для стилей
        if primary:
            self.setProperty("primary", "true")
        if danger:
            self.setProperty("danger", "true")
        
        self.setCursor(Qt.PointingHandCursor)

class FileOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.config_file = self.config_manager.get_config_path()
        self.language_manager = LanguageManager()
        self.organizer = FileOrganizer()
        self.duplicate_finder = DuplicateFinder()
        self.current_language = "ru"
        self.is_scanning = False
        
        self.setup_ui()
        self.load_config()
        self.load_language()
        
        # Загрузка пресета категорий, если нет категорий
        if self.categories_layout.count() == 0:
            self.load_preset_categories()
    
    def setup_ui(self):
        self.setWindowTitle("Meticulous")
        self.setGeometry(100, 100, 1400, 900)
        
        # Центральный виджет с табами
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
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
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Статус лейбл
        self.status_label = QLabel("Готов к работе")
        self.status_bar.addWidget(self.status_label, 1)
    
    def setup_main_tab(self):
        """Основная вкладка сортировки"""
        main_tab = QWidget()
        layout = QVBoxLayout(main_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Панель быстрого доступа
        quick_panel = QHBoxLayout()
        quick_panel.setSpacing(10)
        
        self.source_btn = ModernButton("📁 Выбрать папку", primary=True)
        self.source_btn.setIcon(QIcon.fromTheme("folder"))
        self.source_btn.clicked.connect(self.browse_folder)
        
        self.scan_btn = ModernButton("🔍 Сканировать", primary=True)
        self.scan_btn.setIcon(QIcon.fromTheme("search"))
        self.scan_btn.clicked.connect(self.scan_folder)
        
        self.preview_btn = ModernButton("👁 Предпросмотр")
        self.preview_btn.setIcon(QIcon.fromTheme("view-list"))
        self.preview_btn.clicked.connect(self.preview_organization)
        
        self.organize_btn = ModernButton("🚀 Запустить сортировку", primary=True)
        self.organize_btn.setIcon(QIcon.fromTheme("go-next"))
        self.organize_btn.clicked.connect(self.organize_files)
        
        quick_panel.addWidget(self.source_btn)
        quick_panel.addWidget(self.scan_btn)
        quick_panel.addWidget(self.preview_btn)
        quick_panel.addWidget(self.organize_btn)
        quick_panel.addStretch()
        
        layout.addLayout(quick_panel)
        
        # Основная область в виде splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Левая панель - настройки
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(12)
        
        # Папка источника
        folder_group = QGroupBox("Исходная папка")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setSpacing(10)
        
        self.source_path = QLineEdit(str(Path.home() / "Downloads"))
        self.source_path.setReadOnly(True)
        self.source_path.setMinimumHeight(36)
        
        folder_info_layout = QHBoxLayout()
        folder_info_layout.addWidget(QLabel("Путь:"))
        folder_info_layout.addWidget(self.source_path, 1)
        
        self.folder_stats = QLabel("Выберите папку для сканирования")
        self.folder_stats.setWordWrap(True)
        self.folder_stats.setStyleSheet("color: #90caf9; font-weight: 500;")
        
        folder_layout.addLayout(folder_info_layout)
        folder_layout.addWidget(self.folder_stats)
        
        left_layout.addWidget(folder_group)
        
        # Категории
        categories_group = QGroupBox("Категории файлов")
        categories_layout = QVBoxLayout(categories_group)
        categories_layout.setSpacing(10)
        
        # Прокручиваемая область для категорий
        self.categories_scroll = QScrollArea()
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setFrameShape(QFrame.NoFrame)
        self.categories_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setAlignment(Qt.AlignTop)
        self.categories_layout.setSpacing(8)
        self.categories_layout.setContentsMargins(2, 2, 2, 2)
        
        self.categories_scroll.setWidget(self.categories_container)
        
        # Кнопки управления категориями
        category_buttons = QHBoxLayout()
        category_buttons.setSpacing(8)
        
        self.add_category_btn = ModernButton("➕ Добавить")
        self.add_category_btn.setMaximumWidth(120)
        self.add_category_btn.clicked.connect(self.add_category)
        
        self.load_preset_btn = ModernButton("📋 Пресет")
        self.load_preset_btn.setMaximumWidth(120)
        self.load_preset_btn.clicked.connect(self.load_preset_categories)
        
        self.clear_categories_btn = ModernButton("🗑️ Очистить", danger=True)
        self.clear_categories_btn.setMaximumWidth(120)
        self.clear_categories_btn.clicked.connect(self.clear_categories)
        
        category_buttons.addWidget(self.add_category_btn)
        category_buttons.addWidget(self.load_preset_btn)
        category_buttons.addWidget(self.clear_categories_btn)
        category_buttons.addStretch()
        
        categories_layout.addWidget(self.categories_scroll, 1)
        categories_layout.addLayout(category_buttons)
        
        left_layout.addWidget(categories_group, 1)
        
        # Правая панель - предпросмотр
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(12)
        
        preview_group = QGroupBox("Предпросмотр сортировки")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(10)
        
        self.preview_table = FilePreviewTable()
        
        preview_buttons = QHBoxLayout()
        preview_buttons.setSpacing(8)
        
        self.clear_preview_btn = ModernButton("🗑️ Очистить", danger=True)
        self.clear_preview_btn.setMaximumWidth(120)
        self.clear_preview_btn.clicked.connect(self.preview_table.clear)
        
        self.export_preview_btn = ModernButton("📊 Экспорт")
        self.export_preview_btn.setMaximumWidth(120)
        self.export_preview_btn.clicked.connect(self.export_preview)
        
        preview_buttons.addWidget(self.clear_preview_btn)
        preview_buttons.addWidget(self.export_preview_btn)
        preview_buttons.addStretch()
        
        preview_layout.addWidget(self.preview_table, 1)
        preview_layout.addLayout(preview_buttons)
        
        right_layout.addWidget(preview_group)
        
        # Добавляем панели в splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 700])
        splitter.setHandleWidth(4)
        
        layout.addWidget(splitter, 1)
        
        self.tab_widget.addTab(main_tab, "🏠 Сортировка")
    
    def setup_duplicates_tab(self):
        """Вкладка поиска дубликатов"""
        dup_tab = QWidget()
        layout = QVBoxLayout(dup_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Панель управления
        control_panel = QHBoxLayout()
        control_panel.setSpacing(10)
        
        self.dup_source_label = QLabel("Папка для поиска:")
        self.dup_source_label.setStyleSheet("font-weight: 500;")
        
        self.dup_source_path = QLineEdit(str(Path.home() / "Downloads"))
        self.dup_source_path.setReadOnly(True)
        self.dup_source_path.setMinimumHeight(36)
        
        self.dup_browse_btn = ModernButton("📁 Выбрать")
        self.dup_browse_btn.setMaximumWidth(120)
        self.dup_browse_btn.clicked.connect(lambda: self.browse_folder(dup=True))
        
        self.find_dups_btn = ModernButton("🔍 Найти дубликаты", primary=True)
        self.find_dups_btn.setIcon(QIcon.fromTheme("search"))
        self.find_dups_btn.clicked.connect(self.find_duplicates)
        
        self.clean_dups_btn = ModernButton("🗑️ Очистить", danger=True)
        self.clean_dups_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.clean_dups_btn.clicked.connect(self.clean_duplicates)
        
        control_panel.addWidget(self.dup_source_label)
        control_panel.addWidget(self.dup_source_path, 1)
        control_panel.addWidget(self.dup_browse_btn)
        control_panel.addWidget(self.find_dups_btn)
        control_panel.addWidget(self.clean_dups_btn)
        
        layout.addLayout(control_panel)
        
        # Splitter для результатов
        dup_splitter = QSplitter(Qt.Horizontal)
        dup_splitter.setChildrenCollapsible(False)
        
        # Таблица дубликатов
        self.dup_table = QTableWidget()
        self.dup_table.setColumnCount(5)
        self.dup_table.setHorizontalHeaderLabels(["📄 Имя файла", "📁 Путь", "📏 Размер", "📅 Дата создания", "🔑 Хэш"])
        self.dup_table.horizontalHeader().setStretchLastSection(True)
        self.dup_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.dup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dup_table.setAlternatingRowColors(True)
        self.dup_table.setSortingEnabled(True)
        self.dup_table.setShowGrid(False)
        
        # Настройка ширины колонок
        self.dup_table.setColumnWidth(0, 200)  # Имя
        self.dup_table.setColumnWidth(1, 350)  # Путь
        self.dup_table.setColumnWidth(2, 100)  # Размер
        self.dup_table.setColumnWidth(3, 150)  # Дата
        # Хэш - растягивается
        
        # Детальная информация
        detail_panel = QWidget()
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(12)
        
        detail_group = QGroupBox("Детали файла")
        detail_group_layout = QVBoxLayout(detail_group)
        detail_group_layout.setSpacing(10)
        
        self.dup_info = QTextEdit()
        self.dup_info.setReadOnly(True)
        self.dup_info.setMaximumHeight(180)
        self.dup_info.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        preview_group = QGroupBox("Предпросмотр")
        preview_group_layout = QVBoxLayout(preview_group)
        preview_group_layout.setSpacing(8)
        
        self.dup_image_preview = QLabel()
        self.dup_image_preview.setAlignment(Qt.AlignCenter)
        self.dup_image_preview.setMinimumHeight(200)
        self.dup_image_preview.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #888888;
                font-style: italic;
            }
        """)
        self.dup_image_preview.setText("Выберите файл для просмотра")
        
        preview_group_layout.addWidget(self.dup_image_preview)
        
        detail_group_layout.addWidget(self.dup_info)
        detail_group_layout.addWidget(preview_group, 1)
        
        detail_layout.addWidget(detail_group)
        
        dup_splitter.addWidget(self.dup_table)
        dup_splitter.addWidget(detail_panel)
        dup_splitter.setSizes([800, 400])
        dup_splitter.setHandleWidth(4)
        
        layout.addWidget(dup_splitter, 1)
        
        # Статистика
        self.dup_stats = QLabel("Готов к поиску дубликатов")
        self.dup_stats.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-weight: 500;
                padding: 8px;
                background-color: #252525;
                border-radius: 4px;
                border: 1px solid #3a3a3a;
            }
        """)
        self.dup_stats.setWordWrap(True)
        
        layout.addWidget(self.dup_stats)
        
        self.tab_widget.addTab(dup_tab, "🔄 Дубликаты")
        
        # Подключаем выделение в таблице
        self.dup_table.itemSelectionChanged.connect(self.on_duplicate_selected)
    
    def setup_settings_tab(self):
        """Вкладка настроек"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Настройки сортировки
        sort_group = QGroupBox("Настройки сортировки")
        sort_layout = QVBoxLayout(sort_group)
        sort_layout.setSpacing(12)
        
        # Группировка по дате
        date_layout = QVBoxLayout()
        date_layout.setSpacing(8)
        
        self.date_checkbox = QCheckBox("Создавать папки по дате")
        self.date_checkbox.setChecked(True)
        
        date_format_layout = QHBoxLayout()
        date_format_layout.setSpacing(8)
        
        date_format_label = QLabel("Формат даты:")
        date_format_label.setStyleSheet("font-weight: 500;")
        
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "ГГГГ-ММ-ДД (2024-01-15)",
            "ДД-ММ-ГГГГ (15-01-2024)",
            "ГГГГ/ММ/ДД (2024/01/15)",
            "ММ-ДД-ГГГГ (01-15-2024)",
            "ДД Мес ГГГГ (15 Янв 2024)"
        ])
        self.date_format_combo.setMinimumHeight(36)
        self.date_format_combo.setMaximumWidth(300)
        
        date_format_layout.addWidget(date_format_label)
        date_format_layout.addWidget(self.date_format_combo)
        date_format_layout.addStretch()
        
        date_layout.addWidget(self.date_checkbox)
        date_layout.addLayout(date_format_layout)
        
        sort_layout.addLayout(date_layout)
        
        # Дополнительные настройки
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(8)
        
        self.conflict_checkbox = QCheckBox("Автоматически разрешать конфликты имен")
        self.conflict_checkbox.setChecked(True)
        self.conflict_checkbox.setToolTip("При конфликте имен файлы будут переименовываться")
        
        self.backup_checkbox = QCheckBox("Создавать резервную копию перед сортировкой")
        self.backup_checkbox.setToolTip("Создает копию исходной папки перед перемещением файлов")
        
        advanced_layout.addWidget(self.conflict_checkbox)
        advanced_layout.addWidget(self.backup_checkbox)
        
        sort_layout.addLayout(advanced_layout)
        
        # Настройки дубликатов
        dup_group = QGroupBox("Настройки поиска дубликатов")
        dup_layout = QVBoxLayout(dup_group)
        dup_layout.setSpacing(12)
        
        # Метод сравнения
        method_layout = QHBoxLayout()
        method_layout.setSpacing(8)
        
        method_label = QLabel("Метод сравнения:")
        method_label.setStyleSheet("font-weight: 500;")
        
        self.dup_method_combo = QComboBox()
        self.dup_method_combo.addItems(["По хэшу (точно)", "По имени и размеру (быстро)", "По содержимому (медленно)"])
        self.dup_method_combo.setMinimumHeight(36)
        self.dup_method_combo.setMaximumWidth(300)
        self.dup_method_combo.setToolTip("""По хэшу - самый точный, но медленный
По имени и размеру - быстрый, но менее точный
По содержимому - самый точный, но очень медленный""")
        
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.dup_method_combo)
        method_layout.addStretch()
        
        # Минимальный размер
        size_layout = QHBoxLayout()
        size_layout.setSpacing(8)
        
        size_label = QLabel("Минимальный размер для проверки:")
        size_label.setStyleSheet("font-weight: 500;")
        
        self.dup_size_threshold = QSpinBox()
        self.dup_size_threshold.setRange(1, 1000)
        self.dup_size_threshold.setValue(10)
        self.dup_size_threshold.setSuffix(" МБ")
        self.dup_size_threshold.setMinimumHeight(36)
        self.dup_size_threshold.setMaximumWidth(150)
        self.dup_size_threshold.setButtonSymbols(QSpinBox.UpDownArrows)
        self.dup_size_threshold.setToolTip("Файлы меньше этого размера не проверяются на дубликаты")
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.dup_size_threshold)
        size_layout.addStretch()
        
        dup_layout.addLayout(method_layout)
        dup_layout.addLayout(size_layout)
        
        # Язык
        lang_group = QGroupBox("Язык интерфейса")
        lang_layout = QHBoxLayout(lang_group)
        lang_layout.setSpacing(8)
        
        lang_label = QLabel("Язык:")
        lang_label.setStyleSheet("font-weight: 500;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English", "中文"])
        self.lang_combo.setMinimumHeight(36)
        self.lang_combo.setMaximumWidth(200)
        self.lang_combo.currentTextChanged.connect(self.change_language)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.save_settings_btn = ModernButton("💾 Сохранить настройки", primary=True)
        self.save_settings_btn.setIcon(QIcon.fromTheme("document-save"))
        self.save_settings_btn.clicked.connect(self.save_config)
        
        self.reset_settings_btn = ModernButton("🔄 Сбросить настройки")
        self.reset_settings_btn.setIcon(QIcon.fromTheme("edit-undo"))
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_settings_btn)
        button_layout.addWidget(self.reset_settings_btn)
        button_layout.addStretch()
        
        # Добавляем все группы
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        self.stats_widget = StatisticsWidget()
        layout.addWidget(self.stats_widget, 1)
        
        # Кнопки обновления
        stats_buttons = QHBoxLayout()
        stats_buttons.setSpacing(10)
        
        self.refresh_stats_btn = ModernButton("🔄 Обновить статистику", primary=True)
        self.refresh_stats_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_stats_btn.clicked.connect(self.update_statistics)
        
        self.export_stats_btn = ModernButton("📊 Экспорт статистики")
        self.export_stats_btn.setIcon(QIcon.fromTheme("document-save"))
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
        file_menu = menubar.addMenu("📁 Файл")
        
        new_action = QAction("📄 Новая конфигурация", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        load_action = QAction("📂 Загрузить конфигурацию...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_config_dialog)
        file_menu.addAction(load_action)
        
        save_action = QAction("💾 Сохранить конфигурацию...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_config_dialog)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("📤 Экспорт настроек", self)
        export_action.triggered.connect(self.export_settings)
        file_menu.addAction(export_action)
        
        import_action = QAction("📥 Импорт настроек", self)
        import_action.triggered.connect(self.import_settings)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Инструменты
        tools_menu = menubar.addMenu("🔧 Инструменты")
        
        backup_action = QAction("💾 Создать резервную копию", self)
        backup_action.setShortcut("Ctrl+B")
        backup_action.triggered.connect(self.create_backup)
        tools_menu.addAction(backup_action)
        
        cleanup_action = QAction("🧹 Очистить пустые папки", self)
        cleanup_action.triggered.connect(self.cleanup_empty_folders)
        tools_menu.addAction(cleanup_action)
        
        tools_menu.addSeparator()
        
        open_log_action = QAction("📋 Открыть лог", self)
        open_log_action.triggered.connect(self.open_log)
        tools_menu.addAction(open_log_action)
        
        # Справка
        help_menu = menubar.addMenu("❓ Справка")
        
        docs_action = QAction("📚 Документация", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # === МЕТОДЫ ДЛЯ ОСНОВНОЙ ВКЛАДКИ ===
    
    def browse_folder(self, dup=False):
        """Выбор папки"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку",
            str(Path.home() / "Downloads"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            if dup:
                self.dup_source_path.setText(folder)
                self.status_label.setText(f"Выбрана папка для поиска дубликатов: {folder}")
            else:
                self.source_path.setText(folder)
                self.status_label.setText(f"Выбрана исходная папка: {folder}")
    
    def scan_folder(self):
        """Сканирование папки"""
        if self.is_scanning:
            return
            
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        # Показываем прогресс
        self.is_scanning = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Индетерминированный прогресс
        self.status_label.setText("Сканирование...")
        QApplication.processEvents()
        
        try:
            # Сканируем в отдельном потоке
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class ScanThread(QThread):
                finished = pyqtSignal(int, int)
                error = pyqtSignal(str)
                
                def __init__(self, source_dir):
                    super().__init__()
                    self.source_dir = source_dir
                
                def run(self):
                    try:
                        file_count = 0
                        total_size = 0
                        for file_path in self.source_dir.rglob('*'):
                            if file_path.is_file():
                                file_count += 1
                                total_size += file_path.stat().st_size
                        
                        self.finished.emit(file_count, total_size)
                    except Exception as e:
                        self.error.emit(str(e))
            
            self.scan_thread = ScanThread(source_dir)
            self.scan_thread.finished.connect(self.on_scan_finished)
            self.scan_thread.error.connect(self.on_scan_error)
            self.scan_thread.start()
            
        except Exception as e:
            self.is_scanning = False
            self.progress_bar.setVisible(False)
            QMessageBox.warning(self, "Ошибка", f"Ошибка при сканировании: {str(e)}")
    
    def on_scan_finished(self, file_count, total_size):
        """Завершение сканирования"""
        self.is_scanning = False
        self.progress_bar.setVisible(False)
        
        self.folder_stats.setText(
            f"📊 Найдено файлов: <b>{file_count}</b><br>"
            f"📏 Общий размер: <b>{self.format_size(total_size)}</b>"
        )
        self.status_label.setText(f"Сканирование завершено: {file_count} файлов")
        
        # Обновляем статистику
        self.update_statistics()
    
    def on_scan_error(self, error_msg):
        """Ошибка сканирования"""
        self.is_scanning = False
        self.progress_bar.setVisible(False)
        QMessageBox.warning(self, "Ошибка сканирования", f"Ошибка: {error_msg}")
        self.status_label.setText("Ошибка сканирования")
    
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
        
        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Подготовка предпросмотра...")
        QApplication.processEvents()
        
        try:
            # Очищаем таблицу предпросмотра
            self.preview_table.clear()
            self.preview_table.setRowCount(0)
            
            # Определяем формат даты
            date_format_map = {
                0: "%Y-%m-%d",
                1: "%d-%m-%Y",
                2: "%Y/%m/%d",
                3: "%m-%d-%Y",
                4: "%d %b %Y"
            }
            date_format = date_format_map.get(self.date_format_combo.currentIndex(), "%Y-%m-%d")
            
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
                            date_str = datetime.fromtimestamp(timestamp).strftime(date_format)
                            new_folder = f"{category}/{date_str}"
                        except:
                            new_folder = category
                    else:
                        new_folder = category
                    
                    self.preview_table.setItem(row, 3, QTableWidgetItem(new_folder))
                    file_count += 1
            
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Предпросмотр готов: {file_count} файлов")
            
            if file_count == 0:
                QMessageBox.information(self, "Предпросмотр", "В выбранной папке нет файлов для сортировки")
            else:
                QMessageBox.information(self, "Предпросмотр", 
                    f"📊 <b>Готово к сортировке:</b><br><br>"
                    f"📁 Файлов: <b>{file_count}</b><br>"
                    f"📂 Категорий: <b>{len(categories)}</b><br>"
                    f"📅 Группировка по дате: <b>{'Да' if self.date_checkbox.isChecked() else 'Нет'}</b>")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.warning(self, "Ошибка", f"Ошибка при предпросмотре: {str(e)}")
    
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
            self, 'Подтверждение сортировки',
            f'<b>Начать сортировку файлов?</b><br><br>'
            f'📁 Папка: {source_dir}<br>'
            f'📊 Категорий: {len(categories)}<br>'
            f'📅 Группировка по дате: {"Да" if self.date_checkbox.isChecked() else "Нет"}<br><br>'
            f'<i>Это действие переместит файлы в новые папки.</i>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Создаем резервную копию если нужно
        if self.backup_checkbox.isChecked():
            try:
                backup_dir = source_dir.parent / f"{source_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copytree(source_dir, backup_dir)
                QMessageBox.information(self, "Резервная копия", 
                    f"Резервная копия создана:<br><b>{backup_dir}</b>")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка резервного копирования", 
                    f"Не удалось создать резервную копию: {str(e)}<br>Продолжить без резервной копии?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
        
        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Сортировка файлов...")
        QApplication.processEvents()
        
        # Запускаем сортировку
        try:
            results = self.organizer.organize_files(
                source_dir=str(source_dir),
                categories=categories,
                organize_by_date=self.date_checkbox.isChecked(),
                date_format=date_format
            )
            
            self.progress_bar.setVisible(False)
            
            QMessageBox.information(
                self, 
                "Сортировка завершена",
                f"<b>✅ Сортировка завершена успешно!</b><br><br>"
                f"📊 Результаты:<br>"
                f"• 📁 Перемещено файлов: <b>{results['moved']}</b><br>"
                f"• ⚠️ Ошибок: <b>{results['errors']}</b><br><br>"
                f"<i>Файлы отсортированы по категориям в папке {source_dir}</i>"
            )
            
            # Обновляем статистику
            self.scan_folder()
            self.preview_table.clear()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Ошибка сортировки", 
                f"<b>❌ Ошибка при сортировке:</b><br>{str(e)}")
    
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
        self.clear_categories()
        
        # Добавляем категории по умолчанию
        default_categories = {
            "Изображения": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Документы": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx"],
            "Архивы": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Музыка": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
            "Видео": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
            "Программы": [".exe", ".msi", ".dmg", ".apk", ".deb", ".rpm"],
            "Скрипты": [".py", ".js", ".java", ".cpp", ".c", ".html", ".css", ".php"]
        }
        
        for name, exts in default_categories.items():
            category_widget = CategoryWidget(name, ", ".join(exts))
            category_widget.delete_btn.clicked.connect(
                lambda checked, w=category_widget: self.remove_category(w)
            )
            self.categories_layout.addWidget(category_widget)
        
        self.status_label.setText("Загружен пресет категорий")
    
    def clear_categories(self):
        """Очистка всех категорий"""
        for i in reversed(range(self.categories_layout.count())):
            widget = self.categories_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
    
    def export_preview(self):
        """Экспорт списка предпросмотра"""
        if self.preview_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт списка файлов",
            f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f, delimiter=';')
                    
                    # Заголовки
                    headers = ["Файл", "Тип", "Категория", "Новая папка"]
                    writer.writerow(headers)
                    
                    # Данные
                    for row in range(self.preview_table.rowCount()):
                        row_data = []
                        for col in range(self.preview_table.columnCount()):
                            item = self.preview_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                self.status_label.setText(f"Список экспортирован: {file_path}")
                QMessageBox.information(self, "Экспорт завершен", 
                    f"<b>✅ Список успешно экспортирован</b><br><br>"
                    f"📁 Файл: <b>{file_path}</b><br>"
                    f"📊 Записей: <b>{self.preview_table.rowCount()}</b>")
                
            except Exception as e:
                QMessageBox.warning(self, "Ошибка экспорта", 
                    f"<b>❌ Ошибка при экспорте:</b><br>{str(e)}")
    
    # === МЕТОДЫ ДЛЯ ВКЛАДКИ ДУБЛИКАТОВ ===
    
    def find_duplicates(self):
        """Поиск дубликатов файлов"""
        if self.is_scanning:
            return
            
        source_dir = Path(self.dup_source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        # Показываем прогресс
        self.is_scanning = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Поиск дубликатов...")
        QApplication.processEvents()
        
        # Ищем дубликаты в отдельном потоке
        from PyQt5.QtCore import QThread, pyqtSignal
        
        class DupFinderThread(QThread):
            finished = pyqtSignal(dict)
            progress = pyqtSignal(int)
            
            def __init__(self, source_dir, method):
                super().__init__()
                self.source_dir = source_dir
                self.method = method
                self.finder = DuplicateFinder()
            
            def run(self):
                try:
                    method_map = {
                        0: 'hash',
                        1: 'name_size',
                        2: 'content'
                    }
                    method = method_map.get(self.method, 'hash')
                    
                    duplicates = self.finder.find_duplicates(str(self.source_dir), method=method)
                    self.finished.emit(duplicates)
                except Exception as e:
                    print(f"Ошибка поиска дубликатов: {e}")
                    self.finished.emit({})
        
        self.dup_thread = DupFinderThread(
            source_dir, 
            self.dup_method_combo.currentIndex()
        )
        self.dup_thread.finished.connect(self.display_duplicates)
        self.dup_thread.start()
    
    def display_duplicates(self, duplicates):
        """Отображение найденных дубликатов"""
        self.is_scanning = False
        self.progress_bar.setVisible(False)
        
        self.dup_table.setRowCount(0)
        
        if not duplicates:
            self.dup_stats.setText("❌ Дубликаты не найдены")
            self.status_label.setText("Поиск завершен: дубликаты не найдены")
            QMessageBox.information(self, "Поиск завершен", "Дубликаты не найдены")
            return
        
        total_size = 0
        total_files = 0
        group_num = 1
        
        for i, (hash_val, files) in enumerate(duplicates.items()):
            for file_info in files:
                row = self.dup_table.rowCount()
                self.dup_table.insertRow(row)
                
                # Группа
                group_item = QTableWidgetItem(f"Группа {group_num}")
                group_item.setData(Qt.UserRole, hash_val)
                
                self.dup_table.setItem(row, 0, QTableWidgetItem(file_info['name']))
                self.dup_table.setItem(row, 1, QTableWidgetItem(file_info['path']))
                self.dup_table.setItem(row, 2, QTableWidgetItem(self.format_size(file_info['size'])))
                self.dup_table.setItem(row, 3, QTableWidgetItem(
                    datetime.fromtimestamp(file_info['ctime']).strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.dup_table.setItem(row, 4, QTableWidgetItem(hash_val[:16]))
                
                total_size += file_info['size']
                total_files += 1
            
            group_num += 1
        
        # Подсчитываем экономию места
        wasted_space = 0
        for hash_val, files in duplicates.items():
            if len(files) > 1:
                # Сортируем по дате, оставляем самый новый
                files_sorted = sorted(files, key=lambda x: x['ctime'], reverse=True)
                # Суммируем размер всех кроме первого (самого нового)
                for file_info in files_sorted[1:]:
                    wasted_space += file_info['size']
        
        self.dup_stats.setText(
            f"✅ <b>Найдено:</b> {len(duplicates)} групп, {total_files} файлов<br>"
            f"📏 <b>Общий размер:</b> {self.format_size(total_size)}<br>"
            f"🗑️ <b>Можно освободить:</b> {self.format_size(wasted_space)}"
        )
        
        self.status_label.setText(
            f"Найдено {len(duplicates)} групп дубликатов, "
            f"можно освободить {self.format_size(wasted_space)}"
        )
    
    def on_duplicate_selected(self):
        """Обработка выбора дубликата"""
        selected = self.dup_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        path = self.dup_table.item(row, 1).text()
        file_name = self.dup_table.item(row, 0).text()
        file_size = self.dup_table.item(row, 2).text()
        file_date = self.dup_table.item(row, 3).text()
        file_hash = self.dup_table.item(row, 4).text()
        
        # Показываем информацию о файле
        file_info = f"📄 <b>Имя файла:</b> {file_name}\n"
        file_info += f"📁 <b>Путь:</b> {path}\n"
        file_info += f"📏 <b>Размер:</b> {file_size}\n"
        file_info += f"📅 <b>Создан:</b> {file_date}\n"
        file_info += f"🔑 <b>Хэш:</b> {file_hash}\n\n"
        
        # Получаем информацию о группе
        hash_val = self.dup_table.item(row, 4).text()
        group_files = []
        for r in range(self.dup_table.rowCount()):
            if self.dup_table.item(r, 4).text() == hash_val:
                group_files.append({
                    'path': self.dup_table.item(r, 1).text(),
                    'date': self.dup_table.item(r, 3).text()
                })
        
        if len(group_files) > 1:
            file_info += f"👥 <b>В группе:</b> {len(group_files)} файлов\n"
            # Находим самый новый файл
            newest_file = max(group_files, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"))
            if newest_file['path'] == path:
                file_info += "✅ <b>Это самый новый файл в группе</b>\n"
            else:
                file_info += f"⚠️ <b>Самый новый файл:</b> {Path(newest_file['path']).name}\n"
        
        self.dup_info.setText(file_info)
        
        # Пытаемся показать превью изображения
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Масштабируем с сохранением пропорций
                    scaled_pixmap = pixmap.scaled(
                        self.dup_image_preview.width() - 20,
                        self.dup_image_preview.height() - 20,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.dup_image_preview.setPixmap(scaled_pixmap)
                else:
                    self.dup_image_preview.setText("⚠️ Не удалось загрузить изображение")
            except:
                self.dup_image_preview.setText("⚠️ Ошибка загрузки изображения")
        else:
            self.dup_image_preview.setText("📄 Файл не является изображением")
    
    def clean_duplicates(self):
        """Очистка дубликатов"""
        if self.dup_table.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Нет дубликатов для очистки")
            return
        
        # Собираем данные о дубликатах
        duplicates_data = {}
        for row in range(self.dup_table.rowCount()):
            hash_val = self.dup_table.item(row, 4).text()
            if hash_val not in duplicates_data:
                duplicates_data[hash_val] = []
            
            path = self.dup_table.item(row, 1).text()
            size_str = self.dup_table.item(row, 2).text()
            date_str = self.dup_table.item(row, 3).text()
            
            file_info = {
                'path': path,
                'name': Path(path).name,
                'size': self.parse_size(size_str),
                'ctime': datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timestamp()
            }
            duplicates_data[hash_val].append(file_info)
        
        # Подсчитываем сколько можно удалить
        total_to_delete = 0
        total_space = 0
        for hash_val, files in duplicates_data.items():
            if len(files) > 1:
                files_sorted = sorted(files, key=lambda x: x['ctime'], reverse=True)
                total_to_delete += len(files_sorted) - 1
                for file_info in files_sorted[1:]:
                    total_space += file_info['size']
        
        if total_to_delete == 0:
            QMessageBox.information(self, "Информация", "Нет файлов для удаления")
            return
        
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'<b>Удалить дубликаты?</b><br><br>'
            f'📊 Будет удалено: <b>{total_to_delete} файлов</b><br>'
            f'🗑️ Освободится: <b>{self.format_size(total_space)}</b><br><br>'
            f'<i>В каждой группе будет сохранен только самый новый файл.</i>',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                deleted = self.duplicate_finder.remove_duplicates(duplicates_data)
                
                self.status_label.setText(f"Удалено {deleted} дубликатов")
                QMessageBox.information(self, "Очистка завершена",
                    f"<b>✅ Очистка завершена успешно!</b><br><br>"
                    f"🗑️ Удалено файлов: <b>{deleted}</b><br>"
                    f"📏 Освобождено места: <b>{self.format_size(total_space)}</b>")
                
                # Обновляем таблицу
                self.find_duplicates()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка удаления",
                    f"<b>❌ Ошибка при удалении файлов:</b><br>{str(e)}")
    
    def parse_size(self, size_str):
        """Парсинг размера из строки"""
        units = {'Б': 1, 'КБ': 1024, 'МБ': 1024**2, 'ГБ': 1024**3, 'ТБ': 1024**4}
        try:
            # Убираем лишние пробелы
            size_str = size_str.strip()
            # Разделяем число и единицу измерения
            for unit in units:
                if size_str.endswith(unit):
                    num_str = size_str[:-len(unit)].strip()
                    num = float(num_str.replace(',', '.'))
                    return int(num * units[unit])
            # Если не нашли единицу измерения, пробуем парсить как число
            return int(float(size_str))
        except:
            return 0
    
    # === КОНФИГУРАЦИЯ И НАСТРОЙКИ ===
    
    def load_config(self):
        """Загрузка конфигурации"""
        config = self.config_manager.load_config()
        
        # Загружаем настройки
        if 'source_folder' in config and config['source_folder']:
            self.source_path.setText(config['source_folder'])
            self.dup_source_path.setText(config['source_folder'])
        
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
        
        if 'duplicate_method' in config:
            self.dup_method_combo.setCurrentIndex(config['duplicate_method'])
        
        if 'duplicate_size_threshold' in config:
            self.dup_size_threshold.setValue(config['duplicate_size_threshold'])
        
        # Загружаем язык
        if 'language' in config:
            lang_index = {"ru": 0, "en": 1, "zh": 2}.get(config['language'], 0)
            self.lang_combo.setCurrentIndex(lang_index)
            self.change_language(self.lang_combo.currentText())
        
        self.status_label.setText("Конфигурация загружена")
    
    def save_config(self):
        """Сохранение конфигурации"""
        config = {
            'source_folder': self.source_path.text(),
            'categories': self.get_categories(),
            'organize_by_date': self.date_checkbox.isChecked(),
            'date_format': self.date_format_combo.currentIndex(),
            'language': self.current_language,
            'duplicate_method': self.dup_method_combo.currentIndex(),
            'duplicate_size_threshold': self.dup_size_threshold.value()
        }
        
        if self.config_manager.save_config(config):
            self.status_label.setText("Настройки сохранены")
        else:
            QMessageBox.warning(self, "Ошибка", 
                "<b>❌ Не удалось сохранить настройки</b><br><br>"
                "Проверьте права доступа к файлу конфигурации.")
    
    def load_language(self):
        """Загрузка языка интерфейса"""
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
        try:
            texts = self.language_manager.get_texts()
            
            # Обновляем названия табов
            self.tab_widget.setTabText(0, texts['tabs']['main'])
            self.tab_widget.setTabText(1, texts['tabs']['duplicates'])
            self.tab_widget.setTabText(2, texts['tabs']['settings'])
            self.tab_widget.setTabText(3, texts['tabs']['stats'])
            
            # Обновляем кнопки и другие тексты
            self.source_btn.setText(texts['buttons']['browse'])
            self.preview_btn.setText(texts['buttons']['preview'])
            self.organize_btn.setText(texts['buttons']['organize'])
            self.find_dups_btn.setText(texts['buttons']['find_duplicates'])
            self.clean_dups_btn.setText(texts['buttons']['clean_duplicates'])
            self.save_settings_btn.setText(texts['buttons']['save'])
            self.reset_settings_btn.setText(texts['buttons']['reset'])
            
        except Exception as e:
            print(f"Ошибка обновления текстов: {e}")
    
    # === МЕТОДЫ МЕНЮ ===
    
    def new_config(self):
        """Новая конфигурация"""
        reply = QMessageBox.question(
            self, 'Новая конфигурация',
            '<b>Создать новую конфигурацию?</b><br><br>'
            '<i>Текущие настройки будут сброшены к значениям по умолчанию.</i>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Сбрасываем настройки
            default_path = str(Path.home() / "Downloads")
            self.source_path.setText(default_path)
            self.dup_source_path.setText(default_path)
            self.date_checkbox.setChecked(True)
            self.date_format_combo.setCurrentIndex(0)
            self.conflict_checkbox.setChecked(True)
            self.backup_checkbox.setChecked(False)
            self.dup_method_combo.setCurrentIndex(0)
            self.dup_size_threshold.setValue(10)
            self.lang_combo.setCurrentIndex(0)
            
            # Очищаем категории
            self.clear_categories()
            
            # Загружаем пресет
            self.load_preset_categories()
            
            self.status_label.setText("Конфигурация сброшена к значениям по умолчанию")
    
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
            self.status_label.setText(f"Конфигурация загружена: {file_path}")
    
    def save_config_dialog(self):
        """Диалог сохранения конфигурации"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            f"organizer_config_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            old_config_file = self.config_file
            self.config_file = file_path
            
            if self.save_config():
                self.config_file = old_config_file
                QMessageBox.information(self, "Сохранение",
                    f"<b>✅ Конфигурация сохранена</b><br><br>"
                    f"📁 Файл: <b>{file_path}</b>")
            else:
                self.config_file = old_config_file
    
    def export_settings(self):
        """Экспорт настроек"""
        config = {
            'source_folder': self.source_path.text(),
            'categories': self.get_categories(),
            'organize_by_date': self.date_checkbox.isChecked(),
            'date_format': self.date_format_combo.currentIndex(),
            'language': self.current_language,
            'duplicate_method': self.dup_method_combo.currentIndex(),
            'duplicate_size_threshold': self.dup_size_threshold.value(),
            'export_date': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт настроек",
            f"file_organizer_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                
                QMessageBox.information(self, "Экспорт",
                    f"<b>✅ Настройки экспортированы</b><br><br>"
                    f"📁 Файл: <b>{file_path}</b>")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка",
                    f"<b>❌ Ошибка экспорта:</b><br>{str(e)}")
    
    def import_settings(self):
        """Импорт настроек"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Импорт настроек",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Применяем настройки
                if 'source_folder' in config:
                    self.source_path.setText(config['source_folder'])
                    self.dup_source_path.setText(config['source_folder'])
                
                if 'categories' in config:
                    self.clear_categories()
                    for name, exts in config['categories'].items():
                        category_widget = CategoryWidget(name, ", ".join(exts))
                        category_widget.delete_btn.clicked.connect(
                            lambda checked, w=category_widget: self.remove_category(w)
                        )
                        self.categories_layout.addWidget(category_widget)
                
                if 'organize_by_date' in config:
                    self.date_checkbox.setChecked(config['organize_by_date'])
                
                if 'date_format' in config:
                    self.date_format_combo.setCurrentIndex(config['date_format'])
                
                if 'duplicate_method' in config:
                    self.dup_method_combo.setCurrentIndex(config['duplicate_method'])
                
                if 'duplicate_size_threshold' in config:
                    self.dup_size_threshold.setValue(config['duplicate_size_threshold'])
                
                self.status_label.setText(f"Настройки импортированы: {file_path}")
                QMessageBox.information(self, "Импорт",
                    f"<b>✅ Настройки импортированы</b><br><br>"
                    f"📁 Файл: <b>{file_path}</b>")
                
            except Exception as e:
                QMessageBox.warning(self, "Ошибка",
                    f"<b>❌ Ошибка импорта:</b><br>{str(e)}")
    
    def create_backup(self):
        """Создание резервной копии"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        backup_dir = source_dir.parent / f"{source_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        reply = QMessageBox.question(
            self, 'Создание резервной копии',
            f'<b>Создать резервную копию папки?</b><br><br>'
            f'📁 Исходная: <b>{source_dir}</b><br>'
            f'📁 Копия: <b>{backup_dir}</b><br><br>'
            f'<i>Это может занять некоторое время.</i>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Показываем прогресс
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.status_label.setText("Создание резервной копии...")
            QApplication.processEvents()
            
            try:
                shutil.copytree(source_dir, backup_dir)
                
                self.progress_bar.setVisible(False)
                self.status_label.setText(f"Резервная копия создана: {backup_dir}")
                
                QMessageBox.information(self, "Резервная копия",
                    f"<b>✅ Резервная копия создана успешно!</b><br><br>"
                    f"📁 Расположение: <b>{backup_dir}</b>")
                
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.warning(self, "Ошибка",
                    f"<b>❌ Ошибка при создании резервной копии:</b><br>{str(e)}")
    
    def cleanup_empty_folders(self):
        """Очистка пустых папок"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует!")
            return
        
        reply = QMessageBox.question(
            self, 'Очистка пустых папок',
            f'<b>Удалить все пустые папки?</b><br><br>'
            f'📁 Папка: <b>{source_dir}</b><br><br>'
            f'<i>Будут удалены только полностью пустые папки.</i>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Показываем прогресс
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.status_label.setText("Поиск пустых папок...")
            QApplication.processEvents()
            
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
                
                self.progress_bar.setVisible(False)
                
                if empty_folders:
                    self.status_label.setText(f"Удалено {len(empty_folders)} пустых папок")
                    QMessageBox.information(self, "Очистка завершена",
                        f"<b>✅ Очистка завершена успешно!</b><br><br>"
                        f"🗑️ Удалено папок: <b>{len(empty_folders)}</b><br><br>"
                        f"<i>Первые 10 удаленных папок:</i><br>"
                        f"{'<br>'.join(empty_folders[:10])}")
                else:
                    self.status_label.setText("Пустые папки не найдены")
                    QMessageBox.information(self, "Очистка", "Пустые папки не найдены")
                
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.warning(self, "Ошибка",
                    f"<b>❌ Ошибка при очистке:</b><br>{str(e)}")
    
    def open_log(self):
        """Открыть лог"""
        log_dir = Path(self.config_manager.app_dir) / "logs"
        log_file = log_dir / f"file_organizer_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Создаем лог файл если не существует
        log_dir.mkdir(exist_ok=True)
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Сессия {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"Папка: {self.source_path.text()}\n")
                f.write(f"Категорий: {len(self.get_categories())}\n")
                f.write("=" * 50 + "\n")
            
            # Показываем содержимое лога
            log_text = ""
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_text = f.read()
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Лог программы")
            dialog.setGeometry(200, 200, 800, 600)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(log_text if log_text else "Лог пуст")
            text_edit.setFont(QFont("Consolas", 10))
            
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.rejected.connect(dialog.reject)
            
            layout.addWidget(text_edit)
            layout.addWidget(button_box)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка",
                f"<b>❌ Ошибка при открытии лога:</b><br>{str(e)}")
    
    def show_documentation(self):
        """Показать документацию"""
        docs_text = """
        <h1>Meticulous - Документация</h1>
        
        <h2>📁 Основная сортировка</h2>
        <p><b>1. Выберите папку</b> - укажите папку с файлами для сортировки</p>
        <p><b>2. Настройте категории</b> - добавьте или отредактируйте категории файлов</p>
        <p><b>3. Предпросмотр</b> - посмотрите как файлы будут отсортированы</p>
        <p><b>4. Запустите сортировку</b> - начните автоматическую сортировку</p>
        
        <h2>🔄 Поиск дубликатов</h2>
        <p><b>Методы поиска:</b></p>
        <ul>
            <li><b>По хэшу</b> - самый точный метод, сравнивает содержимое файлов</li>
            <li><b>По имени и размеру</b> - быстрый, но менее точный</li>
            <li><b>По содержимому</b> - самый точный, но очень медленный</li>
        </ul>
        
        <h2>⚙️ Настройки</h2>
        <p><b>Сортировка:</b></p>
        <ul>
            <li>Группировка по дате - создает подпапки с датами</li>
            <li>Разрешение конфликтов - автоматическое переименование файлов</li>
            <li>Резервное копирование - создает копию перед сортировкой</li>
        </ul>
        
        <h2>📈 Статистика</h2>
        <p>Показывает подробную информацию о файлах в выбранной папке</p>
        
        <h2>🔧 Инструменты</h2>
        <ul>
            <li>Создание резервных копий</li>
            <li>Очистка пустых папок</li>
            <li>Просмотр логов</li>
        </ul>
        
        <h2>💡 Советы</h2>
        <ul>
            <li>Перед сортировкой сделайте предпросмотр</li>
            <li>Используйте резервное копирование для важных данных</li>
            <li>Для больших папок используйте быстрый метод поиска дубликатов</li>
        </ul>
        
        <p><b>Версия:</b> 1.3<br>
        <b>Дата:</b> 2026</p>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Документация")
        dialog.setGeometry(200, 200, 700, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(docs_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(text_edit)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе Meticulous",
            """
            <h1>Meticulous</h1>
            
            <p><b>Версия:</b> 1.3</p>
            <p><b>Разработчик:</b> codeinecastle</p>
            <p><b>Дата сборки:</b> 2026</p>
            
            <h2>Функции:</h2>
            <ul>
                <li>📁 Автоматическая сортировка файлов по категориям</li>
                <li>🔄 Поиск и удаление дубликатов файлов</li>
                <li>📊 Подробная статистика файлов</li>
                <li>🌍 Поддержка нескольких языков</li>
                <li>💾 Резервное копирование и восстановление</li>
                <li>⚙️ Гибкая настройка категорий и правил</li>
            </ul>
            
            <h2>Технологии:</h2>
            <ul>
                <li>Python 3.3</li>
                <li>PyQt5 для графического интерфейса</li>
            </ul>
            
            <p><b>Лицензия:</b> MIT License</p>
            <p><b>GitHub:</b> github.com/Meticulous</p>
            
            <p style="color: #888; font-size: 10px;">
                © 2026 Meticulous. Все права защищены.<br>
                Это программное обеспечение предоставляется "как есть", без каких-либо гарантий.
            </p>
            """
        )
    
    def update_statistics(self):
        """Обновление статистики"""
        source_dir = Path(self.source_path.text())
        
        if not source_dir.exists():
            self.stats_widget.stats_text.setText("<h2 style='color: #ff6b6b;'>❌ Папка не существует!</h2>")
            return
        
        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Сбор статистики...")
        QApplication.processEvents()
        
        try:
            # Собираем статистику
            stats_text = "<h1 style='color: #64b5f6;'>📊 Статистика файлов</h1>"
            stats_text += f"<p><b>📁 Папка:</b> <code>{source_dir}</code></p>"
            
            file_count = 0
            total_size = 0
            files_by_ext = {}
            files_by_category = {}
            categories = self.get_categories()
            
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
                    
                    # Определяем категорию
                    category = "Разное"
                    for cat_name, extensions in categories.items():
                        if ext in [e.lower() for e in extensions]:
                            category = cat_name
                            break
                    files_by_category[category] = files_by_category.get(category, 0) + 1
            
            # Общая статистика
            stats_text += f"<h2>📈 Общая статистика</h2>"
            stats_text += f"<p><b>📄 Всего файлов:</b> {file_count:,}</p>"
            stats_text += f"<p><b>📏 Общий размер:</b> {self.format_size(total_size)}</p>"
            
            if file_count > 0:
                avg_size = total_size / file_count
                stats_text += f"<p><b>📊 Средний размер файла:</b> {self.format_size(avg_size)}</p>"
            
            # Статистика по расширениям
            stats_text += "<h2>📝 Статистика по расширениям</h2>"
            stats_text += "<table border='1' cellpadding='8' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
            stats_text += "<tr style='background-color: #2d2d2d; color: #ffffff; font-weight: bold;'>"
            stats_text += "<th>Расширение</th><th>Количество</th><th>Процент</th><th>Общий размер</th></tr>"
            
            ext_counter = 0
            for ext, count in sorted(files_by_ext.items(), key=lambda x: x[1], reverse=True):
                percent = (count / file_count * 100) if file_count > 0 else 0
                # Приблизительный размер для расширения
                ext_size = (total_size / file_count * count) if file_count > 0 else 0
                
                color = "#4caf50" if percent > 10 else "#ff9800" if percent > 5 else "#f44336"
                
                stats_text += f"<tr style='background-color: {'#252525' if ext_counter % 2 == 0 else '#2a2a2a'};'>"
                stats_text += f"<td><b>{ext}</b></td>"
                stats_text += f"<td>{count:,}</td>"
                stats_text += f"<td><span style='color: {color};'>{percent:.1f}%</span></td>"
                stats_text += f"<td>{self.format_size(ext_size)}</td>"
                stats_text += "</tr>"
                ext_counter += 1
            
            stats_text += "</table>"
            
            # Статистика по категориям
            stats_text += "<h2>📁 Статистика по категориям</h2>"
            stats_text += "<table border='1' cellpadding='8' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
            stats_text += "<tr style='background-color: #2d2d2d; color: #ffffff; font-weight: bold;'>"
            stats_text += "<th>Категория</th><th>Количество</th><th>Процент</th></tr>"
            
            cat_counter = 0
            for category, count in sorted(files_by_category.items(), key=lambda x: x[1], reverse=True):
                percent = (count / file_count * 100) if file_count > 0 else 0
                
                stats_text += f"<tr style='background-color: {'#252525' if cat_counter % 2 == 0 else '#2a2a2a'};'>"
                stats_text += f"<td><b>{category}</b></td>"
                stats_text += f"<td>{count:,}</td>"
                stats_text += f"<td><span style='color: #64b5f6;'>{percent:.1f}%</span></td>"
                stats_text += "</tr>"
                cat_counter += 1
            
            stats_text += "</table>"
            
            # Информация о самой большой и маленькой папке
            if file_count > 0:
                try:
                    dir_sizes = {}
                    for item in source_dir.rglob('*'):
                        if item.is_dir():
                            dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                            if dir_size > 0:
                                dir_sizes[item] = dir_size
                    
                    if dir_sizes:
                        largest_dir = max(dir_sizes.items(), key=lambda x: x[1])
                        smallest_dir = min(dir_sizes.items(), key=lambda x: x[1])
                        
                        stats_text += "<h2>📂 Анализ папок</h2>"
                        stats_text += f"<p><b>📈 Самая большая папка:</b> {largest_dir[0].relative_to(source_dir)} "
                        stats_text += f"({self.format_size(largest_dir[1])})</p>"
                        stats_text += f"<p><b>📉 Самая маленькая папка:</b> {smallest_dir[0].relative_to(source_dir)} "
                        stats_text += f"({self.format_size(smallest_dir[1])})</p>"
                except:
                    pass
            
            self.stats_widget.stats_text.setHtml(stats_text)
            
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Статистика обновлена: {file_count} файлов")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.stats_widget.stats_text.setText(
                f"<h2 style='color: #ff6b6b;'>❌ Ошибка при сборе статистики</h2>"
                f"<p><b>Ошибка:</b> {str(e)}</p>"
            )
    
    def export_statistics(self):
        """Экспорт статистики"""
        if not self.stats_widget.stats_text.toPlainText():
            QMessageBox.warning(self, "Ошибка", "Нет статистики для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт статистики",
            f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Files (*.html);;PDF Files (*.pdf);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                content = self.stats_widget.stats_text.toHtml()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.html'):
                        f.write(content)
                    else:
                        f.write(self.stats_widget.stats_text.toPlainText())
                
                self.status_label.setText(f"Статистика экспортирована: {file_path}")
                QMessageBox.information(self, "Экспорт",
                    f"<b>✅ Статистика экспортирована</b><br><br>"
                    f"📁 Файл: <b>{file_path}</b>")
                
            except Exception as e:
                QMessageBox.warning(self, "Ошибка",
                    f"<b>❌ Ошибка при экспорте:</b><br>{str(e)}")
    
    def reset_settings(self):
        """Сброс настроек"""
        reply = QMessageBox.question(
            self, 'Сброс настроек',
            '<b>Сбросить все настройки?</b><br><br>'
            '<i>Это действие вернет все настройки к значениям по умолчанию.</i>',
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
            self.status_label.setText("Настройки сброшены")
    
    def format_size(self, size_bytes):
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0 Б"
        
        for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} ПБ"
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.is_scanning:
            reply = QMessageBox.question(
                self, 'Выход',
                'Идет сканирование файлов. Вы уверены, что хотите выйти?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                event.ignore()
                return
        
        # Сохраняем настройки перед выходом
        self.save_config()
        event.accept()