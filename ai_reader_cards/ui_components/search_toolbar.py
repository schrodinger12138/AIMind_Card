# 文件路径: ai_reader_cards\ui_components\search_toolbar.py
"""搜索工具栏组件"""

from PyQt6.QtWidgets import (QToolBar, QLineEdit, QPushButton, QLabel,
                             QComboBox, QCheckBox, QHBoxLayout, QWidget)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence


class SearchToolbar(QToolBar):
    """搜索工具栏"""

    search_requested = pyqtSignal(str, list)  # keyword, fields
    navigate_next_requested = pyqtSignal()
    navigate_previous_requested = pyqtSignal()
    clear_search_requested = pyqtSignal()

    def __init__(self):
        super().__init__("搜索工具")
        self.search_input = None
        self.fields_combo = None
        self.case_sensitive_check = None
        self.status_label = None

        self.setMovable(False)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 搜索输入框
        self.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索卡片...")
        self.search_input.setMaximumWidth(200)
        self.search_input.returnPressed.connect(self._on_search)
        self.addWidget(self.search_input)

        # 搜索字段选择
        self.addWidget(QLabel("搜索字段:"))
        self.fields_combo = QComboBox()
        self.fields_combo.addItems(["全部", "标题", "问题", "答案", "标题+问题", "问题+答案"])
        self.addWidget(self.fields_combo)

        # 搜索按钮
        search_btn = QPushButton("🔍 搜索")
        search_btn.clicked.connect(self._on_search)
        self.addWidget(search_btn)

        self.addSeparator()

        # 导航按钮
        prev_btn = QPushButton("◀ 上一个")
        prev_btn.clicked.connect(self.navigate_previous_requested.emit)
        self.addWidget(prev_btn)

        next_btn = QPushButton("下一个 ▶")
        next_btn.clicked.connect(self.navigate_next_requested.emit)
        self.addWidget(next_btn)

        self.addSeparator()

        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.addWidget(self.status_label)

        self.addSeparator()

        # 清除搜索按钮
        clear_btn = QPushButton("清除搜索")
        clear_btn.clicked.connect(self.clear_search_requested.emit)
        self.addWidget(clear_btn)

    def _on_search(self):
        """执行搜索"""
        keyword = self.search_input.text().strip()
        if not keyword:
            return

        # 解析搜索字段
        fields_option = self.fields_combo.currentText()
        if fields_option == "全部":
            search_fields = ['title', 'question', 'answer']
        elif fields_option == "标题":
            search_fields = ['title']
        elif fields_option == "问题":
            search_fields = ['question']
        elif fields_option == "答案":
            search_fields = ['answer']
        elif fields_option == "标题+问题":
            search_fields = ['title', 'question']
        elif fields_option == "问题+答案":
            search_fields = ['question', 'answer']
        else:
            search_fields = ['title', 'question', 'answer']

        self.search_requested.emit(keyword, search_fields)

    def update_status(self, current_index, total_results, keyword):
        """更新搜索状态"""
        if total_results == 0:
            self.status_label.setText(f"未找到 '{keyword}'")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
        else:
            self.status_label.setText(f"找到 {total_results} 个结果 - 当前: {current_index}/{total_results}")
            self.status_label.setStyleSheet("color: green; font-size: 11px;")

    def clear_status(self):
        """清除状态"""
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.search_input.clear()

    def set_search_text(self, text):
        """设置搜索文本"""
        self.search_input.setText(text)