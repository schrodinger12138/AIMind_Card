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
        """初始化UI"""
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

        # 文件操作
        open_btn = QPushButton("📂 打开")
        open_btn.clicked.connect(self.open_requested.emit)
        self.addWidget(open_btn)

        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_requested.emit)
        self.addWidget(save_btn)

        load_btn = QPushButton("📁 加载")
        load_btn.clicked.connect(self.load_requested.emit)
        self.addWidget(load_btn)

        self.addSeparator()

        # 剪贴板监控
        self.monitor_btn = QPushButton("📋 监控剪贴板")
        self.monitor_btn.setCheckable(True)
        self.monitor_btn.toggled.connect(self.toggle_clipboard_monitor_requested.emit)
        self.addWidget(self.monitor_btn)

        # 清空画布
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_canvas_requested.emit)
        self.addWidget(clear_btn)

        self.addSeparator()

        # 导出按钮
        export_markdown_btn = QPushButton("📝 导出MD")
        export_markdown_btn.clicked.connect(self.export_markdown_requested.emit)
        self.addWidget(export_markdown_btn)

        export_xmind_btn = QPushButton("🧠 导出XMind")
        export_xmind_btn.clicked.connect(self.export_xmind_requested.emit)
        self.addWidget(export_xmind_btn)

        export_anki_btn = QPushButton("📚 导出Anki")
        export_anki_btn.clicked.connect(self.export_anki_requested.emit)
        self.addWidget(export_anki_btn)

    def set_ai_connected(self, model):
        """设置AI连接状态"""
        if self.connect_btn:
            self.connect_btn.setText("✅ AI已连接")
            self.connect_btn.setEnabled(False)
        if self.model_combo:
            self.model_combo.setEnabled(False)

    def set_clipboard_monitor_status(self, monitoring):
        """设置剪贴板监控状态"""
        if monitoring:
            self.monitor_btn.setText("📋 监控中...")
        else:
            self.monitor_btn.setText("📋 监控剪贴板")

    def get_selected_model(self):
        """获取选中的模型"""
        return self.model_combo.currentText() if self.model_combo else None