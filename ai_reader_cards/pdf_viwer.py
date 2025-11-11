# 文件路径: ai_reader_cards\pdf_viewer.py
"""PDF阅读器模块 - 独立的PDF查看功能"""

import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QScrollArea, QTextEdit,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage


class PDFViewer(QWidget):
    """独立的PDF阅读器组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 200
        self.current_filepath = ""

        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 控制栏
        control_layout = QHBoxLayout()

        self.open_btn = QPushButton("📄 打开PDF")
        self.open_btn.clicked.connect(self.open_pdf)
        control_layout.addWidget(self.open_btn)

        control_layout.addWidget(QLabel("页码:"))
        self.page_spin = QComboBox()
        self.page_spin.currentTextChanged.connect(self.on_page_changed)
        control_layout.addWidget(self.page_spin)

        control_layout.addWidget(QLabel("缩放:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["100%", "150%", "200%", "250%", "300%"])
        self.zoom_combo.setCurrentText("200%")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_changed)
        control_layout.addWidget(self.zoom_combo)

        self.prev_btn = QPushButton("◀ 上一页")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        control_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("下一页 ▶")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        control_layout.addWidget(self.next_btn)

        # 文件信息标签
        self.file_info_label = QLabel("未打开文件")
        self.file_info_label.setStyleSheet("color: gray; font-size: 11px;")
        control_layout.addWidget(self.file_info_label)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # PDF显示区域
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setMinimumSize(600, 800)
        self.pdf_label.setText("请打开PDF文件\n\n支持拖放PDF文件到此区域")
        self.pdf_label.setStyleSheet("""
            border: 2px dashed #ccc; 
            background-color: #f5f5f5; 
            padding: 20px; 
            color: #666;
            font-size: 14px;
        """)
        self.pdf_label.setAcceptDrops(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.pdf_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 文本提取区域
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("提取的文本:"))

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("PDF文本内容将显示在这里...")
        self.text_area.setMaximumHeight(150)
        text_layout.addWidget(self.text_area)

        layout.addLayout(text_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.create_card_btn = QPushButton("📝 从选中文本创建卡片")
        self.create_card_btn.clicked.connect(self.create_card_from_text)
        self.create_card_btn.setEnabled(False)
        button_layout.addWidget(self.create_card_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def dragEnterEvent(self, event):
        """拖放进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()
                self.pdf_label.setStyleSheet("""
                    border: 2px dashed #0078d7; 
                    background-color: #e3f2fd; 
                    padding: 20px; 
                    color: #666;
                    font-size: 14px;
                """)

    def dragLeaveEvent(self, event):
        """拖放离开事件"""
        self.pdf_label.setStyleSheet("""
            border: 2px dashed #ccc; 
            background-color: #f5f5f5; 
            padding: 20px; 
            color: #666;
            font-size: 14px;
        """)

    def dropEvent(self, event):
        """拖放释放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            filepath = urls[0].toLocalFile()
            if filepath.lower().endswith('.pdf'):
                self.open_pdf_file(filepath)
                self.pdf_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
                event.acceptProposedAction()

    def open_pdf(self):
        """打开PDF文件"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "打开PDF文件", "", "PDF文件 (*.pdf)"
        )

        if filepath:
            self.open_pdf_file(filepath)

    def open_pdf_file(self, filepath):
        """打开PDF文件的具体实现"""
        try:
            # 关闭之前打开的文档
            self.close_document()

            self.doc = fitz.open(filepath)
            self.current_filepath = filepath
            self.total_pages = len(self.doc)
            self.current_page = 0

            # 更新页码选择
            self.page_spin.clear()
            self.page_spin.addItems([str(i + 1) for i in range(self.total_pages)])

            # 启用控件
            self.prev_btn.setEnabled(self.total_pages > 1)
            self.next_btn.setEnabled(self.total_pages > 1)
            self.create_card_btn.setEnabled(True)

            # 更新文件信息
            filename = os.path.basename(filepath)
            self.file_info_label.setText(f"{filename} (共{self.total_pages}页)")

            # 显示第一页
            self.display_page(0)

            # 发送打开成功信号
            if hasattr(self.parent(), 'on_pdf_opened'):
                self.parent().on_pdf_opened(filepath)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开PDF文件:\n{str(e)}")

    def display_page(self, page_num):
        """显示指定页面"""
        if not self.doc:
            return

        if page_num < 0 or page_num >= self.total_pages:
            return

        self.current_page = page_num

        try:
            page = self.doc.load_page(page_num)

            # 渲染页面为图像
            zoom = self.zoom_level / 100
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # 转换为QImage
            img_data = pix.tobytes("ppm")
            qimage = QImage()
            qimage.loadFromData(img_data, "PPM")

            # 显示图像
            pixmap = QPixmap.fromImage(qimage)
            self.pdf_label.setPixmap(pixmap)
            self.pdf_label.setText("")
            self.pdf_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")

        except Exception as e:
            self.pdf_label.setText(f"无法显示页面: {str(e)}")
            self.pdf_label.setStyleSheet("border: 1px solid #ccc; background-color: #fff0f0;")
            return

        # 更新页码
        self.page_spin.setCurrentText(str(page_num + 1))

        # 提取文本
        try:
            page = self.doc.load_page(page_num)
            text = page.get_text()
            self.text_area.setPlainText(text)
        except Exception as e:
            self.text_area.setPlainText(f"无法提取文本: {str(e)}")

    def on_page_changed(self, page_text):
        """页码改变"""
        if page_text and self.doc:
            try:
                page_num = int(page_text) - 1
                if 0 <= page_num < self.total_pages:
                    self.display_page(page_num)
            except ValueError:
                pass

    def on_zoom_changed(self, zoom_text):
        """缩放改变"""
        try:
            self.zoom_level = int(zoom_text.replace('%', ''))
            if self.doc:
                self.display_page(self.current_page)
        except ValueError:
            pass

    def prev_page(self):
        """上一页"""
        if self.current_page > 0 and self.doc:
            self.display_page(self.current_page - 1)

    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages - 1 and self.doc:
            self.display_page(self.current_page + 1)

    def create_card_from_text(self):
        """从选中文本创建卡片"""
        selected_text = self.text_area.textCursor().selectedText()
        if not selected_text:
            selected_text = self.text_area.toPlainText()[:500]

        if selected_text.strip():
            # 发送创建卡片信号
            if hasattr(self.parent(), 'create_card_from_text'):
                self.parent().create_card_from_text(selected_text, self.current_page + 1)

    def close_document(self):
        """安全关闭文档"""
        if self.doc:
            try:
                self.doc.close()
            except:
                pass
            self.doc = None

    def get_current_text(self):
        """获取当前文本内容"""
        return self.text_area.toPlainText()

    def get_selected_text(self):
        """获取选中的文本"""
        return self.text_area.textCursor().selectedText()

    def is_pdf_loaded(self):
        """检查是否有PDF加载"""
        return self.doc is not None and not self.doc.is_closed


class PDFTabWidget(QWidget):
    """PDF标签页组件 - 整合PDF阅读器和相关功能"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_viewer = PDFViewer(self)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.addWidget(self.pdf_viewer)

    def open_pdf_file(self, filepath):
        """打开PDF文件"""
        self.pdf_viewer.open_pdf_file(filepath)

    def close_document(self):
        """关闭文档"""
        self.pdf_viewer.close_document()

    def on_pdf_opened(self, filepath):
        """PDF打开成功回调"""
        # 可以在这里添加额外的处理逻辑
        pass

    def create_card_from_text(self, text, page_num):
        """创建卡片回调"""
        # 转发到父窗口
        if hasattr(self.parent(), 'create_card_from_pdf_text'):
            self.parent().create_card_from_pdf_text(text, page_num)