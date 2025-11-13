# 文件路径: ai_reader_cards\ui_components\main_toolbar.py
"""主工具栏组件"""

from PyQt6.QtWidgets import QToolBar, QPushButton, QComboBox, QLabel
from PyQt6.QtCore import pyqtSignal


class MainToolbar(QToolBar):
    """主工具栏 - 包含最常用的功能"""

    # AI相关信号
    connect_ai_requested = pyqtSignal()
    model_changed = pyqtSignal(str)

    # 文件操作信号
    open_requested = pyqtSignal()
    save_requested = pyqtSignal()
    load_requested = pyqtSignal()

    # 工具信号
    toggle_clipboard_monitor_requested = pyqtSignal(bool)
    clear_canvas_requested = pyqtSignal()
    
    # 布局相关信号
    layout_changed = pyqtSignal(str)
    apply_layout_requested = pyqtSignal()
    
    # 连线样式信号
    connection_style_changed = pyqtSignal(str)

    # 导出信号
    export_markdown_requested = pyqtSignal()
    export_xmind_requested = pyqtSignal()
    export_anki_requested = pyqtSignal()

    def __init__(self):
        super().__init__("主工具栏")
        self.setMovable(False)
        self.model_combo = None
        self.connect_btn = None
        self.monitor_btn = None
        self.init_ui()

    def init_ui(self):
        """初始化UI - 简化版，只保留核心功能"""
        # AI模型选择
        self.addWidget(QLabel("AI模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        self.model_combo.currentTextChanged.connect(self.model_changed.emit)
        self.addWidget(self.model_combo)

        # 连接AI按钮
        self.connect_btn = QPushButton("🔌 连接AI")
        self.connect_btn.clicked.connect(self.connect_ai_requested.emit)
        self.addWidget(self.connect_btn)

        self.addSeparator()

        # 布局选择
        self.addWidget(QLabel("布局:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["mind_map", "logical", "timeline", "fishbone", "auto_arrange"])
        self.layout_combo.currentTextChanged.connect(self.layout_changed.emit)
        self.addWidget(self.layout_combo)
        
        apply_layout_btn = QPushButton("📐 应用布局")
        apply_layout_btn.clicked.connect(self.apply_layout_requested.emit)
        self.addWidget(apply_layout_btn)
        
        # 连线样式选择
        self.addWidget(QLabel("连线:"))
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["fixed", "bezier", "smart", "gradient", "default"])
        self.connection_combo.setCurrentText("fixed")  # 默认固定长度
        self.connection_combo.currentTextChanged.connect(self.connection_style_changed.emit)
        self.addWidget(self.connection_combo)

    def set_ai_connected(self, model):
        """设置AI连接状态"""
        if self.connect_btn:
            self.connect_btn.setText("✅ AI已连接")
            self.connect_btn.setEnabled(False)
        if self.model_combo:
            self.model_combo.setEnabled(False)

    def get_selected_model(self):
        """获取选中的模型"""
        return self.model_combo.currentText() if self.model_combo else None