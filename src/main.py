import os
import sys
import html
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QComboBox, QFrame, QPlainTextEdit, QCheckBox,
    QLineEdit, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QColor, QFont

# Internal imports
from utils import find_pandoc
from styles import APP_STYLE
from converter import ConversionWorker

def get_icon_path():
    """Get absolute path to icon, works in dev mode and PyInstaller."""
    # 1. Try relative to this file's folder (works in dev/run from source)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default.ico")
    if os.path.exists(path):
        return path
    # 2. Try PyInstaller unpack directory
    if getattr(sys, 'frozen', False):
        path = os.path.join(sys._MEIPASS, "src", "default.ico")
        if os.path.exists(path):
            return path
        path = os.path.join(sys._MEIPASS, "default.ico")
        if os.path.exists(path):
            return path
    return None

def format_size(size_bytes):
    """Format file size in human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

class DragDropZone(QFrame):
    """Custom Drag and Drop Frame."""
    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dragDropZone")
        self.setAcceptDrops(True)
        self.setProperty("dragActive", "false")
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        self.iconLabel = QLabel("📥", self)
        self.iconLabel.setStyleSheet("font-size: 32px; background: transparent;")
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.textLabel = QLabel("拖拽文件或文件夹到此处导入", self)
        self.textLabel.setObjectName("dragDropText")
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hintLabel = QLabel("支持 .md, .docx, .html, .txt 等常见格式", self)
        self.hintLabel.setObjectName("dragDropHint")
        self.hintLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.iconLabel)
        layout.addWidget(self.textLabel)
        layout.addWidget(self.hintLabel)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", "true")
            self.style().polish(self)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", "false")
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", "false")
        self.style().polish(self)

        urls = event.mimeData().urls()
        files = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.exists(path):
                # If directory is dropped, we can find all files inside
                if os.path.isdir(path):
                    for root, _, filenames in os.walk(path):
                        for name in filenames:
                            files.append(os.path.join(root, name))
                else:
                    files.append(path)
        if files:
            self.filesDropped.emit(files)


class PandocMissingDialog(QDialog):
    """Dialog displayed when Pandoc is missing on startup."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统提示")
        self.setFixedSize(500, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("⚠️ 未检测到 Pandoc 环境", self)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ef4444;")

        desc = QLabel(
            "文档格式转换的核心引擎为 Pandoc。系统当前未检测到 Pandoc。\n"
            "您可以通过以下命令行（PowerShell）命令进行快速安装：",
            self
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.5;")

        # Command Box
        cmd_box = QHBoxLayout()
        self.cmd_line = QLineEdit("winget install jgm.pandoc", self)
        self.cmd_line.setReadOnly(True)
        self.cmd_line.setStyleSheet("font-family: Consolas; font-size: 12px; padding: 8px; background-color: #1e293b; border: 1px solid #334155; color: #38bdf8;")
        
        copy_btn = QPushButton("复制", self)
        copy_btn.setObjectName("btnSecondary")
        copy_btn.setFixedWidth(60)
        copy_btn.clicked.connect(self.copy_cmd)
        
        cmd_box.addWidget(self.cmd_line)
        cmd_box.addWidget(copy_btn)

        note = QLabel(
            "提示：安装完成后，需要点击【重新检测】按钮。如果命令行安装失败，请访问官网下载安装包手动安装（安装后需重启终端或本程序以更新环境变量）。", 
            self
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #94a3b8; font-size: 11px; line-height: 1.4;")

        # Buttons
        btn_layout = QHBoxLayout()
        
        web_btn = QPushButton("访问官网", self)
        web_btn.setObjectName("btnSecondary")
        web_btn.clicked.connect(self.open_website)

        exit_btn = QPushButton("退出程序", self)
        exit_btn.setObjectName("btnDanger")
        exit_btn.clicked.connect(self.reject)

        recheck_btn = QPushButton("重新检测", self)
        recheck_btn.setObjectName("btnSuccess")
        recheck_btn.clicked.connect(self.accept)

        btn_layout.addWidget(web_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(exit_btn)
        btn_layout.addWidget(recheck_btn)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(cmd_box)
        layout.addWidget(note)
        layout.addStretch()
        layout.addLayout(btn_layout)

    def copy_cmd(self):
        QApplication.clipboard().setText(self.cmd_line.text())
        self.cmd_line.selectAll()
        QMessageBox.information(self, "成功", "安装命令已复制到剪贴板！\n请打开 PowerShell 运行此命令。")

    def open_website(self):
        import webbrowser
        webbrowser.open("https://pandoc.org/installing.html")


class PandocFlowApp(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.pandoc_path = None
        self.pandoc_version = None
        self.added_files = set() # Store paths to prevent duplicate entries
        self.active_workers = []
        self.queue_tasks = []
        self.total_queue_count = 0
        self.completed_queue_count = 0

        # Setup process App ID for Windows taskbar icon integration
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.pandocflow.1.0")
            except Exception:
                pass

        self.setWindowTitle("PandocFlow 中文独立版 - 文档格式转换工具")
        self.setMinimumSize(850, 650)
        self.setStyleSheet(APP_STYLE)

        # Set window icon
        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()
        self.check_environment()

    def init_ui(self):
        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # ---------------- Header Section ----------------
        header_layout = QHBoxLayout()
        
        title_vbox = QVBoxLayout()
        app_title = QLabel("PandocFlow 中文独立版", self)
        app_title.setObjectName("appTitle")
        app_sub = QLabel("基于 Pandoc 的多格式文档批量转换小工具", self)
        app_sub.setObjectName("appSubtitle")
        title_vbox.addWidget(app_title)
        title_vbox.addWidget(app_sub)
        
        # Pandoc status badge
        self.status_frame = QFrame(self)
        self.status_frame.setObjectName("statusFrame")
        status_hbox = QHBoxLayout(self.status_frame)
        status_hbox.setContentsMargins(10, 6, 10, 6)
        status_hbox.setSpacing(8)
        
        self.status_dot = QLabel(self)
        self.status_dot.setObjectName("statusDotRed")
        self.status_text = QLabel("正在检测 Pandoc...", self)
        self.status_text.setObjectName("statusText")
        
        status_hbox.addWidget(self.status_dot)
        status_hbox.addWidget(self.status_text)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        header_layout.addWidget(self.status_frame)
        main_layout.addLayout(header_layout)

        # ---------------- Drag & Drop Zone ----------------
        drag_drop_layout = QHBoxLayout()
        self.drag_zone = DragDropZone(self)
        self.drag_zone.filesDropped.connect(self.handle_files_dropped)
        
        # Quick add buttons
        btn_vbox = QVBoxLayout()
        btn_vbox.setSpacing(8)
        
        self.btn_add_files = QPushButton("📥 选择文件...", self)
        self.btn_add_files.setObjectName("btnSecondary")
        self.btn_add_files.clicked.connect(self.open_file_dialog)
        
        self.btn_add_dir = QPushButton("📂 选择文件夹...", self)
        self.btn_add_dir.setObjectName("btnSecondary")
        self.btn_add_dir.clicked.connect(self.open_dir_dialog)
        
        self.btn_clear_list = QPushButton("🗑️ 清空列表", self)
        self.btn_clear_list.setObjectName("btnDanger")
        self.btn_clear_list.clicked.connect(self.clear_queue)
        
        btn_vbox.addWidget(self.btn_add_files)
        btn_vbox.addWidget(self.btn_add_dir)
        btn_vbox.addStretch()
        btn_vbox.addWidget(self.btn_clear_list)
        
        drag_drop_layout.addWidget(self.drag_zone, 4)
        drag_drop_layout.addLayout(btn_vbox, 1)
        main_layout.addLayout(drag_drop_layout)

        # ---------------- Configurations Pane ----------------
        config_frame = QFrame(self)
        config_frame.setObjectName("cardFrame")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(14, 12, 14, 12)
        config_layout.setSpacing(10)

        config_title = QLabel("⚙️ 转换设置 (全局)", self)
        config_title.setObjectName("sectionTitle")
        config_layout.addWidget(config_title)

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(20)

        # Target format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("全局目标格式:", self))
        self.combo_global_format = QComboBox(self)
        self.combo_global_format.addItems([
            "docx", "md", "html", "epub", "odt", "rtf", "txt", "rst", "pdf"
        ])
        self.combo_global_format.currentTextChanged.connect(self.global_format_changed)
        format_layout.addWidget(self.combo_global_format)
        
        # Output directory
        output_layout = QHBoxLayout()
        self.chk_same_dir = QCheckBox("输出到原文件同目录", self)
        self.chk_same_dir.setChecked(True)
        self.chk_same_dir.stateChanged.connect(self.same_dir_checkbox_changed)
        
        self.txt_output_dir = QLineEdit(self)
        self.txt_output_dir.setPlaceholderText("选择自定义输出目录...")
        self.txt_output_dir.setEnabled(False)
        
        self.btn_browse_output = QPushButton("浏览...", self)
        self.btn_browse_output.setObjectName("btnSecondary")
        self.btn_browse_output.setEnabled(False)
        self.btn_browse_output.clicked.connect(self.browse_output_dir)
        
        output_layout.addWidget(self.chk_same_dir)
        output_layout.addWidget(self.txt_output_dir)
        output_layout.addWidget(self.btn_browse_output)

        inputs_layout.addLayout(format_layout, 1)
        inputs_layout.addLayout(output_layout, 2)
        config_layout.addLayout(inputs_layout)
        
        main_layout.addWidget(config_frame)

        # ---------------- Queue Table ----------------
        table_title_layout = QHBoxLayout()
        queue_label = QLabel("📋 待处理队列", self)
        queue_label.setObjectName("sectionTitle")
        table_title_layout.addWidget(queue_label)
        table_title_layout.addStretch()
        
        self.lbl_queue_stats = QLabel("共 0 个文件", self)
        self.lbl_queue_stats.setStyleSheet("color: #94a3b8; font-size: 12px;")
        table_title_layout.addWidget(self.lbl_queue_stats)
        main_layout.addLayout(table_title_layout)

        self.table_queue = QTableWidget(self)
        self.table_queue.setColumnCount(6)
        self.table_queue.setHorizontalHeaderLabels(["文件名", "大小", "原格式", "目标格式", "状态", "操作"])
        self.table_queue.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_queue.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_queue.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_queue.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_queue.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_queue.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table_queue.setColumnWidth(1, 80)
        self.table_queue.setColumnWidth(2, 60)
        self.table_queue.setColumnWidth(3, 100)
        self.table_queue.setColumnWidth(5, 70)
        main_layout.addWidget(self.table_queue)

        # ---------------- Log Console ----------------
        log_label_layout = QHBoxLayout()
        log_lbl = QLabel("💻 运行日志", self)
        log_lbl.setObjectName("sectionTitle")
        log_label_layout.addWidget(log_lbl)
        main_layout.addLayout(log_label_layout)
        
        self.txt_log = QPlainTextEdit(self)
        self.txt_log.setObjectName("logConsole")
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(100)
        main_layout.addWidget(self.txt_log)

        # ---------------- Bottom Action Bar ----------------
        action_layout = QHBoxLayout()
        
        self.btn_convert = QPushButton("🚀 开始批量转换", self)
        self.btn_convert.setObjectName("btnSuccess") # Success is green themed
        self.btn_convert.setMinimumHeight(40)
        self.btn_convert.clicked.connect(self.start_batch_conversion)
        
        action_layout.addStretch()
        action_layout.addWidget(self.btn_convert, 1)
        main_layout.addLayout(action_layout)

        self.log("程序初始化成功。支持拖拽或选择文件进行操作。")

    # ---------------- Environment Checking ----------------
    def check_environment(self):
        """Check for Pandoc installation and update UI, alert user if missing."""
        path, version = find_pandoc()
        if path:
            self.pandoc_path = path
            self.pandoc_version = version
            self.status_dot.setObjectName("statusDotGreen")
            self.status_dot.style().polish(self.status_dot)
            version_short = version.split('\n')[0] if '\n' in version else version
            self.status_text.setText(f"Pandoc 可用: {version_short}")
            self.log(f"环境检测：找到 Pandoc，路径: {path}，版本信息: {version_short}")
            self.btn_convert.setEnabled(True)
            return True
        else:
            self.pandoc_path = None
            self.pandoc_version = None
            self.status_dot.setObjectName("statusDotRed")
            self.status_dot.style().polish(self.status_dot)
            self.status_text.setText("Pandoc 未检测到")
            self.log("环境检测：未检测到 Pandoc 工具！", "error")
            self.btn_convert.setEnabled(False)
            
            # Popup warning dialog
            dialog = PandocMissingDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # User clicked "Recheck"
                return self.check_environment()
            else:
                # User closed dialog or clicked exit
                sys.exit(0)

    # ---------------- Logging ----------------
    def log(self, message, level="info"):
        """Write formatted message to log screen."""
        prefix = "[INFO] "
        color = "#e2e8f0"
        if level == "error":
            prefix = "[ERROR] "
            color = "#ef4444"
        elif level == "success":
            prefix = "[SUCCESS] "
            color = "#10b981"
        elif level == "warning":
            prefix = "[WARNING] "
            color = "#f59e0b"

        safe_message = html.escape(f"{prefix}{message}")
        self.txt_log.appendHtml(f"<span style='color: {color};'>{safe_message}</span>")
        # Scroll to bottom
        scrollbar = self.txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ---------------- File and Folder Browsing ----------------
    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择要转换的文档", "", 
            "常用文档 (*.md *.markdown *.docx *.html *.htm *.epub *.odt *.rtf *.txt *.rst);;所有文件 (*.*)"
        )
        if file_paths:
            self.handle_files_dropped(file_paths)

    def open_dir_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择文件夹导入")
        if dir_path:
            files = []
            for root, _, filenames in os.walk(dir_path):
                for name in filenames:
                    files.append(os.path.join(root, name))
            if files:
                self.handle_files_dropped(files)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if dir_path:
            self.txt_output_dir.setText(dir_path)

    # ---------------- Event Handlers ----------------
    def same_dir_checkbox_changed(self, state):
        same_dir = (state == 2) # Qt.CheckState.Checked is integer 2
        self.txt_output_dir.setEnabled(not same_dir)
        self.btn_browse_output.setEnabled(not same_dir)

    def global_format_changed(self, format_str):
        """Update all row comboboxes when global format is changed."""
        for row in range(self.table_queue.rowCount()):
            combo = self.table_queue.cellWidget(row, 3)
            if isinstance(combo, QComboBox):
                # Search index of the global format in row format list
                idx = combo.findText(format_str)
                if idx >= 0:
                    combo.setCurrentIndex(idx)

    def handle_files_dropped(self, file_paths):
        """Processes files to add them to the conversion queue."""
        supported_exts = {
            '.md', '.markdown', '.docx', '.html', '.htm', '.epub', '.odt',
            '.rtf', '.txt', '.rst'
        }
        added_count = 0

        for path in file_paths:
            path = os.path.abspath(path)
            # Prevent duplicate files
            if path in self.added_files:
                continue

            _, ext = os.path.splitext(path.lower())
            if ext not in supported_exts:
                # If they select a random file, we can still add it but default warning
                # we only process files with actual content or we warn
                pass

            file_size = os.path.getsize(path)
            self.added_files.add(path)
            self.add_file_to_table(path, file_size, ext)
            added_count += 1

        if added_count > 0:
            self.log(f"成功导入 {added_count} 个新文件。")
            self.update_queue_stats()

    def add_file_to_table(self, file_path, size, ext):
        """Adds a single file to the UI table grid."""
        row = self.table_queue.rowCount()
        self.table_queue.insertRow(row)

        # Col 0: File path (stored hidden or in custom item)
        # Col 0 is file name, with tool tip of full path
        name_item = QTableWidgetItem(os.path.basename(file_path))
        name_item.setToolTip(file_path)
        name_item.setData(Qt.ItemDataRole.UserRole, file_path) # Store full path
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_queue.setItem(row, 0, name_item)

        # Col 1: Size
        size_item = QTableWidgetItem(format_size(size))
        size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_queue.setItem(row, 1, size_item)

        # Col 2: Source format
        src_format = ext.strip(".").upper()
        src_item = QTableWidgetItem(src_format if src_format else "UNKNOWN")
        src_item.setFlags(src_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_queue.setItem(row, 2, src_item)

        # Col 3: Target format dropdown
        combo = QComboBox(self)
        
        # Pandoc supports these output formats for all accepted source formats.
        targets = ["docx", "md", "html", "epub", "odt", "rtf", "txt", "rst", "pdf"]
        source_target = "md" if ext.lower() == ".markdown" else ext.lower().strip(".")
        targets = [target for target in targets if target != source_target]

        combo.addItems(targets)
        
        # Set selection to match global selection if valid
        global_sel = self.combo_global_format.currentText()
        if global_sel in targets:
            combo.setCurrentText(global_sel)
        else:
            # Otherwise default to first
            if targets:
                combo.setCurrentIndex(0)
                
        # Set underlying table item text so that column data is populated
        format_item = QTableWidgetItem(combo.currentText())
        format_item.setFlags(format_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_queue.setItem(row, 3, format_item)
                
        self.table_queue.setCellWidget(row, 3, combo)

        # Connect change event to update the item and reset status
        combo.currentTextChanged.connect(self.sync_combo_text_to_item)

        # Col 4: Status
        status_item = QTableWidgetItem("待处理")
        status_item.setForeground(QColor("#94a3b8")) # Gray
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_queue.setItem(row, 4, status_item)

        # Col 5: Actions (Delete Button)
        del_btn = QPushButton("移除", self)
        del_btn.setObjectName("btnDanger")
        del_btn.setStyleSheet("padding: 2px 6px; font-size: 11px; max-width: 60px;")
        del_btn.setProperty("filePath", file_path)
        del_btn.clicked.connect(self.remove_file_by_button)
        
        # Align center
        cell_widget = QWidget()
        cell_layout = QHBoxLayout(cell_widget)
        cell_layout.setContentsMargins(0, 0, 0, 0)
        cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cell_layout.addWidget(del_btn)
        self.table_queue.setCellWidget(row, 5, cell_widget)

    def sync_combo_text_to_item(self, text):
        """Update the underlying cell item when combobox value changes, and reset status."""
        sender = self.sender()
        if not sender:
            return
            
        for row in range(self.table_queue.rowCount()):
            if self.table_queue.cellWidget(row, 3) == sender:
                item = self.table_queue.item(row, 3)
                if item:
                    item.setText(text)
                
                # Reset conversion status back to pending since the target format was changed
                status_item = self.table_queue.item(row, 4)
                if status_item:
                    status_item.setText("待处理")
                    status_item.setForeground(QColor("#94a3b8"))
                    status_item.setToolTip("")
                break

    def remove_file_by_button(self):
        """Remove single file from the table queue based on the button property."""
        sender = self.sender()
        if not sender:
            return
        
        file_path = sender.property("filePath")
        if not file_path:
            return

        # Find row containing the file path
        for row in range(self.table_queue.rowCount()):
            item = self.table_queue.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == file_path:
                self.table_queue.removeRow(row)
                if file_path in self.added_files:
                    self.added_files.remove(file_path)
                self.log(f"已从队列中移除: {os.path.basename(file_path)}")
                self.update_queue_stats()
                break

    def clear_queue(self):
        self.table_queue.setRowCount(0)
        self.added_files.clear()
        self.log("待处理队列已清空。")
        self.update_queue_stats()

    def update_queue_stats(self):
        count = self.table_queue.rowCount()
        self.lbl_queue_stats.setText(f"共 {count} 个文件")

    # ---------------- Conversion Pipeline ----------------
    def start_batch_conversion(self):
        """Start converting files in queue sequentially."""
        if not self.pandoc_path:
            QMessageBox.critical(self, "错误", "未检测到 Pandoc 环境，无法进行转换。")
            return

        row_count = self.table_queue.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "提示", "待处理队列为空，请先添加文件！")
            return

        # Create tasks
        self.queue_tasks = []
        
        # Output directory config
        same_dir = self.chk_same_dir.isChecked()
        custom_dir = self.txt_output_dir.text().strip() if not same_dir else None
        
        if not same_dir and not custom_dir:
            QMessageBox.warning(self, "提示", "请选择自定义输出目录！")
            return

        # Collect tasks
        for row in range(row_count):
            status_item = self.table_queue.item(row, 4)
            # Only convert items that are not already "成功"
            if status_item and status_item.text() != "转换成功":
                name_item = self.table_queue.item(row, 0)
                file_path = name_item.data(Qt.ItemDataRole.UserRole)
                
                combo_target = self.table_queue.cellWidget(row, 3)
                target_format = combo_target.currentText()
                
                self.queue_tasks.append({
                    'row': row,
                    'file_path': file_path,
                    'target_format': target_format,
                    'output_dir': custom_dir
                })

        if not self.queue_tasks:
            QMessageBox.information(self, "提示", "队列中的所有文件均已转换成功！")
            return

        # Disable main UI widgets during active conversion to prevent interference
        self.set_ui_enabled(False)
        
        self.total_queue_count = len(self.queue_tasks)
        self.completed_queue_count = 0
        self.log(f"开始批量转换队列，共 {self.total_queue_count} 个任务...")
        
        # Execute first task
        self.process_next_task()

    def set_ui_enabled(self, enabled):
        """Enable or disable interactive widgets during active running conversion."""
        self.btn_convert.setEnabled(enabled)
        self.btn_clear_list.setEnabled(enabled)
        self.btn_add_files.setEnabled(enabled)
        self.btn_add_dir.setEnabled(enabled)
        self.drag_zone.setAcceptDrops(enabled)
        self.table_queue.setEnabled(enabled)
        self.combo_global_format.setEnabled(enabled)
        self.chk_same_dir.setEnabled(enabled)
        if not self.chk_same_dir.isChecked():
            self.txt_output_dir.setEnabled(enabled)
            self.btn_browse_output.setEnabled(enabled)

    def process_next_task(self):
        """Retrieves next task from queue and spawns background Worker thread."""
        if not self.queue_tasks:
            # All tasks done!
            self.log(f"批量转换任务结束。成功完成 {self.completed_queue_count}/{self.total_queue_count} 个文件。", "success")
            QMessageBox.information(
                self, "批量转换完成", 
                f"转换任务处理完毕！\n成功完成 {self.completed_queue_count} 个文件，失败 {self.total_queue_count - self.completed_queue_count} 个。"
            )
            self.set_ui_enabled(True)
            return

        task = self.queue_tasks.pop(0)
        row = task['row']
        file_path = task['file_path']
        target_format = task['target_format']
        output_dir = task['output_dir']

        # Update table status in GUI
        status_item = self.table_queue.item(row, 4)
        status_item.setText("转换中...")
        status_item.setForeground(QColor("#38bdf8")) # Blueish

        # Spawn Thread Worker
        worker = ConversionWorker(self.pandoc_path, file_path, target_format, output_dir)
        # Pass row along using lambda or direct attributes to retrieve it later
        worker.finished.connect(lambda f, o, s, m, r=row: self.on_worker_finished(f, o, s, m, r))
        
        # Keep references alive
        self.active_workers.append(worker)
        worker.start()

    def on_worker_finished(self, input_file, output_file, success, message, row):
        """Handles completion of a worker thread."""
        status_item = self.table_queue.item(row, 4)
        file_name = os.path.basename(input_file)

        if success:
            status_item.setText("转换成功")
            status_item.setForeground(QColor("#10b981")) # Green
            status_item.setToolTip(f"输出文件: {output_file}")
            self.log(f"转换成功: {file_name} -> {os.path.basename(output_file)}", "success")
            self.completed_queue_count += 1
        else:
            status_item.setText("转换失败")
            status_item.setForeground(QColor("#ef4444")) # Red
            status_item.setToolTip(message)
            self.log(f"转换失败: {file_name}。原因: {message}", "error")

        # Cleanup worker reference
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)

        # Process next
        self.process_next_task()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PandocFlowApp()
    window.show()
    sys.exit(app.exec())
