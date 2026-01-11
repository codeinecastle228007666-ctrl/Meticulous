# styles.py
"""
Современные стили для File Organizer Pro
"""

def get_stylesheet():
    """Возвращает стили для всего приложения"""
    return """
    /* ===== ОСНОВНЫЕ СТИЛИ ===== */
    QMainWindow {
        background-color: #1e1e1e;
        border: none;
    }
    
    QWidget {
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 13px;
        selection-background-color: #1976d2;
        selection-color: white;
    }
    
    /* ===== ТЕКСТ И МЕТКИ ===== */
    QLabel {
        color: #b0b0b0;
        font-size: 13px;
        padding: 2px;
    }
    
    QLabel[important="true"] {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* ===== ГРУППОВЫЕ ПАНЕЛИ ===== */
    QGroupBox {
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 15px;
        background-color: #252525;
        color: #ffffff;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        padding: 0 8px 0 8px;
        color: #64b5f6;
        background-color: #252525;
        font-weight: 600;
    }
    
    /* ===== КНОПКИ ===== */
    QPushButton {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 13px;
        border: 1px solid #4a4a4a;
        background-color: #333333;
        color: #ffffff;
        min-height: 32px;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background-color: #3a3a3a;
        border-color: #5a5a5a;
    }
    
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    
    QPushButton:disabled {
        background-color: #252525;
        color: #666666;
        border-color: #3a3a3a;
    }
    
    /* Специальные кнопки */
    QPushButton[primary="true"] {
        background-color: #2196f3;
        border-color: #2196f3;
        font-weight: 600;
    }
    
    QPushButton[primary="true"]:hover {
        background-color: #1976d2;
        border-color: #1976d2;
    }
    
    QPushButton[primary="true"]:pressed {
        background-color: #0d47a1;
        border-color: #0d47a1;
    }
    
    QPushButton[danger="true"] {
        background-color: #f44336;
        border-color: #f44336;
    }
    
    QPushButton[danger="true"]:hover {
        background-color: #d32f2f;
        border-color: #d32f2f;
    }
    
    /* ===== ПОЛЯ ВВОДА ===== */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        font-size: 13px;
        selection-background-color: #1976d2;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #64b5f6;
        background-color: #252525;
    }
    
    QLineEdit:disabled, QTextEdit:disabled {
        background-color: #2a2a2a;
        color: #888888;
        border-color: #3a3a3a;
    }
    
    QLineEdit[error="true"] {
        border: 1px solid #f44336;
    }
    
    /* ===== ВЫПАДАЮЩИЕ СПИСКИ ===== */
    QComboBox {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 8px;
        padding-right: 30px;
        color: #ffffff;
        font-size: 13px;
        min-height: 32px;
    }
    
    QComboBox:hover {
        border-color: #5a5a5a;
    }
    
    QComboBox:focus {
        border: 1px solid #64b5f6;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #b0b0b0;
        width: 0;
        height: 0;
        margin-right: 10px;
    }
    
    QComboBox::down-arrow:on {
        border-top: 5px solid #64b5f6;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 4px;
        color: #ffffff;
        selection-background-color: #1976d2;
        selection-color: white;
        outline: none;
    }
    
    QComboBox QAbstractItemView::item {
        padding: 8px;
        border-radius: 2px;
    }
    
    QComboBox QAbstractItemView::item:hover {
        background-color: #3a3a3a;
    }
    
    QComboBox QAbstractItemView::item:selected {
        background-color: #1976d2;
    }
    
    /* ===== СПИНБОКСЫ ===== */
    QSpinBox, QDoubleSpinBox {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        font-size: 13px;
        min-height: 32px;
    }
    
    QSpinBox:hover, QDoubleSpinBox:hover {
        border-color: #5a5a5a;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #64b5f6;
    }
    
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        background-color: #3a3a3a;
        border: none;
        border-radius: 2px;
        width: 20px;
    }
    
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-bottom: 5px solid #b0b0b0;
        width: 0;
        height: 0;
    }
    
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #b0b0b0;
        width: 0;
        height: 0;
    }
    
    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #4a4a4a;
    }
    
    /* ===== ЧЕКБОКСЫ И РАДИОКНОПКИ ===== */
    QCheckBox, QRadioButton {
        spacing: 8px;
        color: #b0b0b0;
        font-size: 13px;
    }
    
    QCheckBox:hover, QRadioButton:hover {
        color: #ffffff;
    }
    
    QCheckBox::indicator, QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 2px solid #5a5a5a;
        background-color: #2d2d2d;
    }
    
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #7a7a7a;
    }
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #2196f3;
        border-color: #2196f3;
    }
    
    QRadioButton::indicator {
        border-radius: 9px;
    }
    
    QCheckBox::indicator:checked {
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE4IiBoZWlnaHQ9IjE4IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTkgMTYuMTdMNC44MyAxMmwtMS40MiAxLjQxTDkgMTkgMjEgN2wtMS40MS0xLjQxeiIvPjwvc3ZnPg==);
    }
    
    QRadioButton::indicator:checked {
        background-color: #2196f3;
        border-color: #2196f3;
    }
    
    /* ===== ТАБЛИЦЫ ===== */
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
        padding: 8px;
        border-bottom: 1px solid #3a3a3a;
    }
    
    QTableWidget::item:selected {
        background-color: #1976d2;
        color: white;
    }
    
    QTableWidget::item:hover {
        background-color: #3a3a3a;
    }
    
    QHeaderView::section {
        background-color: #2d2d2d;
        padding: 10px;
        border: none;
        border-right: 1px solid #3a3a3a;
        border-bottom: 2px solid #3a3a3a;
        color: #b0b0b0;
        font-weight: 600;
        font-size: 12px;
    }
    
    QHeaderView::section:last {
        border-right: none;
    }
    
    QHeaderView::section:hover {
        background-color: #3a3a3a;
    }
    
    /* ===== ТАБЫ ===== */
    QTabWidget::pane {
        border: 1px solid #3a3a3a;
        border-radius: 6px;
        background-color: #252525;
        margin-top: -1px;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        border: 1px solid #3a3a3a;
        border-bottom: none;
        color: #b0b0b0;
        font-weight: 500;
        font-size: 13px;
    }
    
    QTabBar::tab:hover {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    
    QTabBar::tab:selected {
        background-color: #252525;
        color: #64b5f6;
        border-bottom: 2px solid #64b5f6;
        font-weight: 600;
    }
    
    /* ===== СПЛИТТЕРЫ ===== */
    QSplitter::handle {
        background-color: #3a3a3a;
        width: 4px;
        height: 4px;
    }
    
    QSplitter::handle:hover {
        background-color: #5a5a5a;
    }
    
    QSplitter::handle:horizontal {
        image: none;
        border-left: 1px solid #4a4a4a;
        border-right: 1px solid #4a4a4a;
    }
    
    QSplitter::handle:vertical {
        image: none;
        border-top: 1px solid #4a4a4a;
        border-bottom: 1px solid #4a4a4a;
    }
    
    /* ===== ПРОГРЕСС БАР ===== */
    QProgressBar {
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        text-align: center;
        background-color: #2d2d2d;
        color: #ffffff;
        font-size: 12px;
        padding: 1px;
    }
    
    QProgressBar::chunk {
        background-color: #4caf50;
        border-radius: 3px;
        border: none;
    }
    
    /* ===== СКРОЛЛБАРЫ ===== */
    QScrollBar:vertical {
        background-color: #252525;
        width: 14px;
        border-radius: 7px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a4a4a;
        border-radius: 7px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #5a5a5a;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #252525;
        height: 14px;
        border-radius: 7px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #4a4a4a;
        border-radius: 7px;
        min-width: 30px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #5a5a5a;
    }
    
    /* ===== ТЕКСТОВЫЕ ОБЛАСТИ ===== */
    QTextEdit {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 8px;
        color: #e0e0e0;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
    }
    
    QTextEdit:focus {
        border: 1px solid #64b5f6;
    }
    
    /* ===== МЕНЮ ===== */
    QMenuBar {
        background-color: #252525;
        color: #b0b0b0;
        font-size: 13px;
        border-bottom: 1px solid #3a3a3a;
    }
    
    QMenuBar::item {
        padding: 8px 16px;
        background-color: transparent;
    }
    
    QMenuBar::item:selected {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    
    QMenu {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 4px;
        color: #e0e0e0;
    }
    
    QMenu::item {
        padding: 8px 32px 8px 16px;
        border-radius: 3px;
    }
    
    QMenu::item:selected {
        background-color: #1976d2;
        color: white;
    }
    
    QMenu::separator {
        height: 1px;
        background-color: #4a4a4a;
        margin: 4px 8px;
    }
    
    /* ===== СТАТУС БАР ===== */
    QStatusBar {
        background-color: #252525;
        color: #b0b0b0;
        border-top: 1px solid #3a3a3a;
        font-size: 12px;
    }
    
    QStatusBar::item {
        border: none;
    }
    
    /* ===== ПЛАВАЮЩИЕ ПАНЕЛИ ===== */
    QDockWidget {
        background-color: #252525;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        titlebar-close-icon: url(close.png);
        titlebar-normal-icon: url(float.png);
    }
    
    QDockWidget::title {
        background-color: #2d2d2d;
        padding: 6px;
        border-bottom: 1px solid #3a3a3a;
    }
    
    /* ===== ДИАЛОГИ ===== */
    QDialog {
        background-color: #252525;
        border: 1px solid #3a3a3a;
        border-radius: 6px;
    }
    
    QMessageBox {
        background-color: #252525;
        color: #e0e0e0;
    }
    
    QMessageBox QLabel {
        color: #e0e0e0;
        font-size: 13px;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
        padding: 8px 16px;
    }
    
    /* ===== ОСОБЫЕ ВИДЖЕТЫ ===== */
    QToolButton {
        background-color: #333333;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 6px;
        color: #b0b0b0;
    }
    
    QToolButton:hover {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    
    QToolButton:pressed {
        background-color: #2a2a2a;
    }
    
    /* Улучшенный QListWidget */
    QListWidget {
        background-color: #252525;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        color: #e0e0e0;
        outline: none;
    }
    
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #3a3a3a;
    }
    
    QListWidget::item:selected {
        background-color: #1976d2;
        color: white;
        border: none;
    }
    
    QListWidget::item:hover {
        background-color: #3a3a3a;
    }
    
    /* Улучшенный QTreeWidget */
    QTreeWidget {
        background-color: #252525;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        color: #e0e0e0;
        outline: none;
    }
    
    QTreeWidget::item {
        padding: 4px;
        border-bottom: 1px solid #3a3a3a;
    }
    
    QTreeWidget::item:selected {
        background-color: #1976d2;
        color: white;
        border: none;
    }
    
    QTreeWidget::item:hover {
        background-color: #3a3a3a;
    }
    """
