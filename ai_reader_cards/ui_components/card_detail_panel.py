"""
卡片详情显示面板
显示选中卡片的标题、问题、答案和笔记
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class CardDetailPanel(QWidget):
    """卡片详情显示面板"""
    
    edit_requested = pyqtSignal(object)  # 请求编辑卡片
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_card = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("卡片详情")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 编辑按钮
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        self.edit_btn.setEnabled(False)
        title_layout.addWidget(self.edit_btn)
        layout.addLayout(title_layout)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # 标题显示
        title_section = QVBoxLayout()
        title_section.addWidget(QLabel("标题:"))
        self.title_display = QTextEdit()
        self.title_display.setReadOnly(True)
        self.title_display.setMaximumHeight(50)
        self.title_display.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        title_section.addWidget(self.title_display)
        content_layout.addLayout(title_section)
        
        # 问题显示
        question_section = QVBoxLayout()
        question_section.addWidget(QLabel("问题:"))
        self.question_display = QTextEdit()
        self.question_display.setReadOnly(True)
        self.question_display.setMaximumHeight(120)
        self.question_display.setFont(QFont("Microsoft YaHei", 10))
        question_section.addWidget(self.question_display)
        content_layout.addLayout(question_section)
        
        # 答案显示
        answer_section = QVBoxLayout()
        answer_section.addWidget(QLabel("答案:"))
        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)
        self.answer_display.setFont(QFont("Microsoft YaHei", 10))
        answer_section.addWidget(self.answer_display)
        content_layout.addLayout(answer_section)
        
        # 笔记显示
        note_section = QVBoxLayout()
        note_section.addWidget(QLabel("笔记:"))
        self.note_display = QTextEdit()
        self.note_display.setReadOnly(True)
        self.note_display.setFont(QFont("Microsoft YaHei", 10))
        note_section.addWidget(self.note_display)
        content_layout.addLayout(note_section)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 初始状态：显示提示
        self.clear_display()
    
    def display_card(self, card_node):
        """显示卡片内容"""
        self.current_card = card_node
        
        if card_node:
            # 显示标题
            self.title_display.setPlainText(card_node.title if hasattr(card_node, 'title') else "")
            
            # 显示问题
            question = card_node.question if hasattr(card_node, 'question') else ""
            self.question_display.setPlainText(question)
            self.question_display.setVisible(bool(question))
            
            # 显示答案
            answer = card_node.answer if hasattr(card_node, 'answer') else ""
            self.answer_display.setPlainText(answer)
            self.answer_display.setVisible(bool(answer))
            
            # 显示笔记
            note = card_node.note_text if hasattr(card_node, 'note_text') else ""
            self.note_display.setPlainText(note)
            self.note_display.setVisible(bool(note))
            
            # 启用编辑按钮
            self.edit_btn.setEnabled(True)
        else:
            self.clear_display()
    
    def clear_display(self):
        """清空显示"""
        self.current_card = None
        self.title_display.setPlainText("")
        self.question_display.setPlainText("")
        self.answer_display.setPlainText("")
        self.note_display.setPlainText("")
        self.edit_btn.setEnabled(False)
    
    def _on_edit_clicked(self):
        """编辑按钮点击事件"""
        if self.current_card:
            self.edit_requested.emit(self.current_card)

