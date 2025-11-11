# 文件路径: ai_reader_cards\ui_components\input_panel.py
"""输入面板组件"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QMessageBox)
from PyQt6.QtCore import pyqtSignal


class InputPanel(QWidget):
    """文件输入面板"""

    file_opened = pyqtSignal(str, str)  # filepath, file_type
    generate_card_requested = pyqtSignal(str)
    text_operation_requested = pyqtSignal(str)  # copy, paste, cut, select_all

    def __init__(self):
        super().__init__()
        self.text_input = None
        self.file_info_label = None
        self.generate_btn = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题和文件控制栏
        title_layout = QHBoxLayout()
        title = QLabel("📚 文件阅读区")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        title_layout.addWidget(title)

        # 文件操作按钮
        open_file_btn = QPushButton("📂 打开文件")
        open_file_btn.clicked.connect(self._open_file)
        title_layout.addWidget(open_file_btn)

        clear_file_btn = QPushButton("🗑️ 清空")
        clear_file_btn.clicked.connect(self._clear_content)
        title_layout.addWidget(clear_file_btn)

        title_layout.addStretch()

        # 文件信息标签
        self.file_info_label = QLabel("未打开文件")
        self.file_info_label.setStyleSheet("color: gray; font-size: 11px;")
        title_layout.addWidget(self.file_info_label)

        layout.addLayout(title_layout)

        # 文本显示和编辑区域
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "文件内容将显示在这里...\n\n"
            "支持的操作：\n"
            "1. 打开文本文件(.txt)、PDF文件(.pdf)\n"
            "2. 支持复制(Ctrl+C)、粘贴(Ctrl+V)、剪切(Ctrl+X)\n"
            "3. 选中文本后按空格键快速生成卡片\n"
            "4. 支持查找(Ctrl+F)、全选(Ctrl+A)"
        )
        layout.addWidget(self.text_input)

        # 文本操作工具栏
        text_toolbar = QHBoxLayout()

        copy_btn = QPushButton("📋 复制")
        copy_btn.clicked.connect(lambda: self.text_operation_requested.emit("copy"))
        text_toolbar.addWidget(copy_btn)

        paste_btn = QPushButton("📄 粘贴")
        paste_btn.clicked.connect(lambda: self.text_operation_requested.emit("paste"))
        text_toolbar.addWidget(paste_btn)

        cut_btn = QPushButton("✂️ 剪切")
        cut_btn.clicked.connect(lambda: self.text_operation_requested.emit("cut"))
        text_toolbar.addWidget(cut_btn)

        select_all_btn = QPushButton("🔍 全选")
        select_all_btn.clicked.connect(lambda: self.text_operation_requested.emit("select_all"))
        text_toolbar.addWidget(select_all_btn)

        text_toolbar.addStretch()
        layout.addLayout(text_toolbar)

        # 生成卡片按钮
        self.generate_btn = QPushButton("✨ 从选中文本生成卡片 (Space)")
        self.generate_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        self.generate_btn.clicked.connect(self._generate_card_from_selection)
        self.generate_btn.setEnabled(False)
        layout.addWidget(self.generate_btn)

    def _open_file(self):
        """打开文件"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            "",
            "文本文件 (*.txt);;PDF文件 (*.pdf);;所有文件 (*.*)"
        )

        if filepath:
            if filepath.lower().endswith('.pdf'):
                self.file_opened.emit(filepath, 'pdf')
            else:
                self.file_opened.emit(filepath, 'text')

    def _clear_content(self):
        """清空内容"""
        self.text_input.clear()
        self.file_info_label.setText("未打开文件")
        self.generate_btn.setEnabled(False)

    def _generate_card_from_selection(self):
        """从选中文本生成卡片"""
        cursor = self.text_input.textCursor()
        if cursor.hasSelection():
            # 使用选中文本
            text = cursor.selectedText()
        else:
            # 如果没有选中文本，使用全部文本（限制长度）
            text = self.text_input.toPlainText()[:1000]
            if not text:
                QMessageBox.warning(self, "提示", "请先打开文件或输入文本内容")
                return

        if len(text) < 10:
            QMessageBox.warning(self, "提示", "文本过短，请输入至少10个字符")
            return

        self.generate_card_requested.emit(text)

    def set_file_content(self, content, filename, file_type):
        """设置文件内容"""
        self.text_input.setPlainText(content)
        if file_type == 'pdf':
            self.file_info_label.setText(f"PDF文件: {filename}")
        else:
            self.file_info_label.setText(f"文本文件: {filename}")
        self.generate_btn.setEnabled(True)

    def enable_generate_button(self, enabled):
        """启用/禁用生成按钮"""
        self.generate_btn.setEnabled(enabled)

    def get_text_input(self):
        """获取文本输入框"""
        return self.text_input