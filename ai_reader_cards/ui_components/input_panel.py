# 文件路径: ai_reader_cards\ui_components\input_panel.py
"""输入面板组件"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QMessageBox, QCheckBox,
                             QDialog, QComboBox, QSplitter, QPlainTextEdit)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class InputPanel(QWidget):
    """文件输入面板"""

    file_opened = pyqtSignal(str, str)  # filepath, file_type
    generate_card_requested = pyqtSignal(str)
    text_operation_requested = pyqtSignal(str)  # copy, paste, cut, select_all
    pdf_dropped = pyqtSignal(str)  # PDF文件路径
    markdown_dropped = pyqtSignal(str)  # Markdown文件路径
    translate_requested = pyqtSignal(str)  # target_language
    highlight_text_requested = pyqtSignal(str, int, int)  # text, start_pos, end_pos
    export_html_requested = pyqtSignal(str)  # filepath
    export_pdf_requested = pyqtSignal(str)  # filepath

    def __init__(self):
        super().__init__()
        self.text_input = None
        self.file_info_label = None
        self.generate_btn = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(2)  # 最小间距
        layout.setContentsMargins(2, 2, 2, 2)  # 最小边距

        # 标题和文件控制栏（超紧凑布局）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(2)  # 最小间距
        title_layout.setContentsMargins(2, 1, 2, 1)  # 最小边距（上下1px）
        
        title = QLabel("文件")
        title.setStyleSheet("font-size: 10px; font-weight: bold; padding: 0px; margin: 0px;")
        title.setMaximumHeight(22)  # 限制高度
        title_layout.addWidget(title)

        # 文件操作按钮（超紧凑）
        open_file_btn = QPushButton("打开")
        open_file_btn.setMaximumHeight(22)  # 更小的高度
        open_file_btn.setMinimumHeight(22)
        open_file_btn.setStyleSheet("font-size: 9px; padding: 1px 4px; margin: 0px;")
        open_file_btn.clicked.connect(self._open_file)
        title_layout.addWidget(open_file_btn)

        clear_file_btn = QPushButton("清空")
        clear_file_btn.setMaximumHeight(22)
        clear_file_btn.setMinimumHeight(22)
        clear_file_btn.setStyleSheet("font-size: 9px; padding: 1px 4px; margin: 0px;")
        clear_file_btn.clicked.connect(self._clear_content)
        title_layout.addWidget(clear_file_btn)

        title_layout.addStretch()

        # 文件信息标签（超紧凑）
        self.file_info_label = QLabel("未打开文件")
        self.file_info_label.setStyleSheet("color: gray; font-size: 8px; padding: 0px; margin: 0px;")
        self.file_info_label.setMaximumHeight(22)
        title_layout.addWidget(self.file_info_label)

        layout.addLayout(title_layout)

        # 文本显示和编辑区域 - 使用Markdown查看器
        # 优先使用ReText方式的预览（如果可用）
        try:
            from ai_reader_cards.markdown.markdown_preview_retext import MarkdownPreviewReText
            from PyQt6.QtCore import Qt as QtCore
            
            # 创建分割器：左侧编辑，右侧预览
            splitter = QSplitter(QtCore.Orientation.Horizontal)
            
            # 左侧：文本编辑区
            self.text_input = QPlainTextEdit()
            self.text_input.setPlaceholderText(
                "在此输入Markdown内容...\n\n"
                "支持的功能：\n"
                "1. Markdown语法（标题、列表、表格等）\n"
                "2. LaTeX公式：$E=mc^2$ 或 $$\\int_0^\\infty e^{-x^2}dx$$\n"
                "3. 代码高亮：```python\ncode\n```\n"
                "4. 图片：![alt](path/to/image.png)\n"
                "5. Obsidian特性：[[链接]]、#标签、- [ ]任务列表\n"
                "6. 实时预览在右侧显示（使用ReText渲染引擎）"
            )
            
            # 只添加编辑区，预览区将在主窗口中单独管理
            layout.addWidget(self.text_input)
            
            # 创建预览区但不添加到布局中（将在主窗口中单独管理）
            self.preview = MarkdownPreviewReText()
            
            # 创建生成卡片和翻译按钮（将在主窗口中添加到预览区上方）
            self.generate_btn = QPushButton("生成卡片")
            self.generate_btn.clicked.connect(self._generate_card_from_selection)
            self.generate_btn.setEnabled(False)
            
            self.translate_btn = QPushButton("翻译")
            self.translate_btn.setEnabled(False)
            self.translate_btn.clicked.connect(self._show_translate_dialog)
            
            # 连接文本变化信号到预览更新
            self.text_input.textChanged.connect(self._update_preview)
            self.is_markdown_mode = True
            self.use_preview = True
            self.preview_type = "retext"  # 标记使用ReText方式
        except ImportError:
            # 如果QWebEngineView不可用，使用MarkdownViewer
            try:
                from ai_reader_cards.markdown import MarkdownViewer
                self.text_input = MarkdownViewer()
                self.is_markdown_mode = True
                self.use_preview = False
                layout.addWidget(self.text_input)
            except ImportError:
                # 如果都不可用，使用普通QTextEdit
                self.text_input = QTextEdit()
                self.is_markdown_mode = False
                self.use_preview = False
                layout.addWidget(self.text_input)
        
        self.text_input.setPlaceholderText(
            "文件内容将显示在这里...\n\n"
            "支持的操作：\n"
            "1. 拖拽PDF文件到此处，可选择转换为Markdown\n"
            "2. 拖拽Markdown文件(.md/.markdown)到此处直接打开\n"
            "3. 打开文本文件(.txt)、PDF文件(.pdf)、Markdown文件(.md)\n"
            "4. 支持复制(Ctrl+C)、粘贴(Ctrl+V)、剪切(Ctrl+X)\n"
            "5. 选中文本后按空格键快速生成卡片\n"
            "6. 支持查找(Ctrl+F)、全选(Ctrl+A)\n"
            "7. 支持Markdown格式和数学公式显示"
        )
        
        # 启用拖拽
        self.setAcceptDrops(True)
        if hasattr(self, 'text_input'):
            self.text_input.setAcceptDrops(True)
        
        # 注意：按钮已经移到预览区域上方（在 Markdown 预览模式中）
        # 如果没有预览模式，需要在这里添加按钮（但通常不会进入这个分支）

    def _open_file(self):
        """打开文件"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            "",
            "Markdown文件 (*.md *.markdown);;文本文件 (*.txt);;PDF文件 (*.pdf);;所有文件 (*.*)"
        )

        if filepath:
            if filepath.lower().endswith('.pdf'):
                self.file_opened.emit(filepath, 'pdf')
            elif filepath.lower().endswith(('.md', '.markdown')):
                self.file_opened.emit(filepath, 'markdown')
            else:
                self.file_opened.emit(filepath, 'text')

    def _clear_content(self):
        """清空内容"""
        self.text_input.clear()
        self.file_info_label.setText("未打开文件")
        self.generate_btn.setEnabled(False)

    def _update_preview(self):
        """更新预览"""
        if hasattr(self, 'preview') and hasattr(self, 'text_input'):
            content = self.text_input.toPlainText()
            # 获取当前文件路径（如果有）
            base_path = getattr(self, '_current_file_path', None)
            
            # 使用ReText方式更新预览
            if hasattr(self, 'preview_type') and self.preview_type == "retext":
                # ReText方式：使用 set_markdown 方法
                self.preview.set_markdown(content, base_path)
            else:
                # 兼容旧方式
                if hasattr(self.preview, 'set_markdown'):
                    self.preview.set_markdown(content, base_path)
                elif hasattr(self.preview, 'set_markdown_content'):
                    self.preview.set_markdown_content(content)
    
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
            if urls:
                filepath = urls[0].toLocalFile().lower()
                if filepath.endswith(('.pdf', '.md', '.markdown')):
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
            filepath_lower = filepath.lower()
            
            self.setStyleSheet("")
            
            if filepath_lower.endswith('.pdf'):
                # PDF文件
                self.pdf_dropped.emit(filepath)
                event.acceptProposedAction()
            elif filepath_lower.endswith(('.md', '.markdown')):
                # Markdown文件
                self.markdown_dropped.emit(filepath)
                event.acceptProposedAction()
            else:
                event.ignore()
    
    def set_file_content(self, content, filename, file_type):
        """设置文件内容"""
        # 保存当前文件路径（用于预览）
        self._current_file_path = filename if file_type in ['markdown', 'pdf'] else None
        
        if self.is_markdown_mode:
            # Markdown模式
            if hasattr(self, 'preview') and self.use_preview:
                # 有预览模式：设置编辑器内容，预览会自动更新
                if hasattr(self.text_input, 'setPlainText'):
                    self.text_input.setPlainText(content)
                else:
                    self.text_input.setText(content)
                
                # 设置预览的文件路径（ReText方式需要）
                if hasattr(self, 'preview_type') and self.preview_type == "retext":
                    if filename and file_type == 'markdown':
                        self.preview.set_file_path(filename)
                
                # 触发预览更新
                self._update_preview()
            elif hasattr(self.text_input, 'set_markdown_content'):
                # 使用MarkdownViewer
                self.text_input.set_markdown_content(content)
            else:
                self.text_input.setPlainText(content)
        else:
            # 普通文本模式
            if hasattr(self.text_input, 'setPlainText'):
                self.text_input.setPlainText(content)
            else:
                self.text_input.setText(content)
        
        if file_type == 'pdf':
            self.file_info_label.setText(f"PDF文件: {filename}")
        elif file_type == 'markdown':
            self.file_info_label.setText(f"Markdown文件: {filename}")
        else:
            self.file_info_label.setText(f"文本文件: {filename}")
        self.generate_btn.setEnabled(True)
        self.translate_btn.setEnabled(True)
    
    def get_plain_text(self):
        """获取纯文本内容（用于生成卡片）"""
        if hasattr(self.text_input, 'toPlainText'):
            return self.text_input.toPlainText()
        elif hasattr(self.text_input, 'document'):
            return self.text_input.document().toPlainText()
        else:
            return ""
    
    def _export_html(self):
        """导出为HTML"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出HTML", "", "HTML文件 (*.html)"
        )
        if filepath and hasattr(self, 'preview'):
            if self.preview.export_to_html(filepath):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "成功", f"已导出到: {filepath}")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "失败", "导出HTML失败")
    
    def _export_pdf(self):
        """导出为PDF"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出PDF", "", "PDF文件 (*.pdf)"
        )
        if filepath and hasattr(self, 'preview'):
            if self.preview.export_to_pdf(filepath):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "成功", f"已导出到: {filepath}")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "失败", "导出PDF失败，请确保已安装weasyprint或pypandoc")
    
    def _show_translate_dialog(self):
        """显示翻译对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("翻译Markdown")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # 目标语言选择
        layout.addWidget(QLabel("选择目标语言:"))
        language_combo = QComboBox()
        language_combo.addItems([
            "中文 (zh)",
            "英文 (en)",
            "日文 (ja)",
            "韩文 (ko)",
            "法文 (fr)",
            "德文 (de)",
            "西班牙文 (es)"
        ])
        layout.addWidget(language_combo)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = language_combo.currentText()
            # 提取语言代码
            if "(" in selected and ")" in selected:
                lang_code = selected.split("(")[1].split(")")[0]
            else:
                lang_code = "zh"
            self.translate_requested.emit(lang_code)