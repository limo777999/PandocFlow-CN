# Theme Stylesheet for PandocFlow

APP_STYLE = """
/* Global Window Styles */
QMainWindow {
    background-color: #0b0f19;
}

QWidget {
    color: #f1f5f9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Card/Container Frame */
QFrame#cardFrame {
    background-color: #151f32;
    border-radius: 12px;
    border: 1px solid #1e293b;
}

QFrame#statusFrame {
    background-color: #131c2e;
    border-radius: 8px;
    border: 1px solid #27354a;
}

/* Titles and Headers */
QLabel#appTitle {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
    background: transparent;
}

QLabel#appSubtitle {
    font-size: 12px;
    color: #64748b;
    background: transparent;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #38bdf8;
    background: transparent;
}

QLabel#statusText {
    font-size: 12px;
    font-weight: 500;
    color: #94a3b8;
}

/* Drag & Drop Area */
QFrame#dragDropZone {
    background-color: #111a2e;
    border: 2px dashed #3b82f6;
    border-radius: 10px;
}

QFrame#dragDropZone[dragActive="true"] {
    background-color: #1e2e4f;
    border: 2px dashed #60a5fa;
}

QLabel#dragDropText {
    font-size: 14px;
    color: #94a3b8;
    font-weight: 500;
    background: transparent;
}

QLabel#dragDropHint {
    font-size: 11px;
    color: #475569;
    background: transparent;
}

/* Buttons */
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #2563eb;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #475569;
    border: 1px solid #334155;
}

QPushButton#btnSecondary {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
}

QPushButton#btnSecondary:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton#btnSecondary:pressed {
    background-color: #1e293b;
}

QPushButton#btnDanger {
    background-color: #ef4444;
}

QPushButton#btnDanger:hover {
    background-color: #dc2626;
}

QPushButton#btnDanger:pressed {
    background-color: #b91c1c;
}

QPushButton#btnDanger:disabled {
    background-color: #1e293b;
    color: #475569;
    border: 1px solid #334155;
}

QPushButton#btnSuccess {
    background-color: #10b981;
}

QPushButton#btnSuccess:hover {
    background-color: #059669;
}

/* Combobox (Dropdown) */
QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 10px;
    min-width: 60px;
    color: #f1f5f9;
}

QComboBox:hover {
    border-color: #475569;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    color: #f1f5f9;
    outline: 0px;
    padding: 4px;
}


/* Table Widget */
QTableWidget {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    gridline-color: #1f2937;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #1f2937;
}

QTableWidget::item:selected {
    background-color: #1e293b;
    color: #f1f5f9;
}

QHeaderView::section {
    background-color: #1f2937;
    color: #94a3b8;
    padding: 8px;
    font-weight: bold;
    border: none;
    border-bottom: 2px solid #374151;
}

QHeaderView::section:horizontal {
    border-right: 1px solid #1f2937;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #111827;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #374151;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4b5563;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #111827;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #374151;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #4b5563;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Log Console (Plain Text Edit) */
QPlainTextEdit#logConsole {
    background-color: #020617;
    border: 1px solid #1e293b;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    color: #e2e8f0;
    padding: 8px;
}

/* Checkbox */
QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #334155;
    border-radius: 4px;
    background-color: #1e293b;
}

QCheckBox::indicator:hover {
    border-color: #475569;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* Status Indicator Dot */
QLabel#statusDotGreen {
    background-color: #10b981;
    border-radius: 5px;
    max-width: 10px;
    max-height: 10px;
}

QLabel#statusDotRed {
    background-color: #ef4444;
    border-radius: 5px;
    max-width: 10px;
    max-height: 10px;
}

/* Warning Dialog */
QDialog {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

QLineEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 10px;
    color: #f1f5f9;
}

QLineEdit:hover {
    border-color: #475569;
}

QLineEdit:focus {
    border-color: #3b82f6;
}
"""
