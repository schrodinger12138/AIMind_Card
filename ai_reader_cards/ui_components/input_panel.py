# 文件路径: ai_reader_cards\ui_components\input_panel.py
"""输入面板组件"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QMessageBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class InputPanel(QWidget):
    """文件输入面板"""

    file_opened = pyqtSignal(str, str)  # filepath, file_type
    generate_card_requested = pyqtSignal(str)
    text_operation_requested = pyqtSignal(str)  # copy, paste, cut, select_all
    pdf_dropped = pyqtSignal(str)  # PDF文件路径

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

        # 文本显示和编辑区域 - 使用Markdown查看器
        try:
            from ai_reader_cards.markdown_viewer import MarkdownViewer
            self.text_input = MarkdownViewer()
            self.is_markdown_mode = True
        except ImportError:
            # 如果导入失败，使用普通QTextEdit
            self.text_input = QTextEdit()
            self.is_markdown_mode = False
        
        self.text_input.setPlaceholderText(
            "文件内容将显示在这里...\n\n"
            "支持的操作：\n"
            "1. 拖拽PDF文件到此处，可选择转换为Markdown\n"
            "2. 打开文本文件(.txt)、PDF文件(.pdf)\n"
            "3. 支持复制(Ctrl+C)、粘贴(Ctrl+V)、剪切(Ctrl+X)\n"
            "4. 选中文本后按空格键快速生成卡片\n"
            "5. 支持查找(Ctrl+F)、全选(Ctrl+A)\n"
            "6. 支持Markdown格式和数学公式显示"
        )
        
        # 启用拖拽
        self.setAcceptDrops(True)
        self.text_input.setAcceptDrops(True)
        
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
        # 获取选中文本或全部文本
        if hasattr(self.text_input, 'textCursor'):
            cursor = self.text_input.textCursor()
            if cursor.hasSelection():
                text = cursor.selectedText()
            else:
                text = self.get_plain_text()[:1000]
        else:
            text = self.get_plain_text()[:1000]
        
        if not text:
            QMessageBox.warning(self, "提示", "请先打开文件或输入文本内容")
            return

        if len(text) < 10:
            QMessageBox.warning(self, "提示", "文本过短，请输入至少10个字符")
            return

        self.generate_card_requested.emit(text)

    def enable_generate_button(self, enabled):
        """启用/禁用生成按钮"""
        self.generate_btn.setEnabled(enabled)

    def get_text_input(self):
        """获取文本输入框"""
        return self.text_input
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()
                self.setStyleSheet("border: 2px dashed #0078d7; background-color: #e3f2fd;")
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.setStyleSheet("")
    
    def dropEvent(self, event: QDropEvent):
        """拖拽释放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            filepath = urls[0].toLocalFile()
            if filepath.lower().endswith('.pdf'):
                self.setStyleSheet("")
                self.pdf_dropped.emit(filepath)
                event.acceptProposedAction()
            else:
                event.ignore()
    
    def set_file_content(self, content, filename, file_type):
        """设置文件内容"""
        if self.is_markdown_mode and hasattr(self.text_input, 'set_markdown_content'):
            self.text_input.set_markdown_content(content)
        else:
            self.text_input.setPlainText(content)
        
        if file_type == 'pdf':
            self.file_info_label.setText(f"PDF文件: {filename}")
        elif file_type == 'markdown':
            self.file_info_label.setText(f"Markdown文件: {filename}")
        else:
            self.file_info_label.setText(f"文本文件: {filename}")
        self.generate_btn.setEnabled(True)
    
    def get_plain_text(self):
        """获取纯文本内容（用于生成卡片）"""
        if hasattr(self.text_input, 'toPlainText'):
            return self.text_input.toPlainText()
        elif hasattr(self.text_input, 'document'):
            return self.text_input.document().toPlainText()
        else:
            return ""