# 文件路径: ai_reader_cards\ui_components\control_panel.py
"""控制面板组件"""

from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QLabel,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import QObject, pyqtSignal


class ControlPanel(QObject):
    """顶部控制面板

    设计为信号/布局提供者：
    - 调用 `create_panel()` 返回一个 QLayout，主窗口负责把它加入主布局。
    - 这样避免将 ControlPanel 实现成 QWidget，但仍可复用布局与信号。
    """

    # 在类级别定义信号
    ai_connected = pyqtSignal()
    model_changed = pyqtSignal(str)
    clipboard_monitor_toggled = pyqtSignal(bool)
    save_requested = pyqtSignal()
    load_requested = pyqtSignal()
    export_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    # XMind相关信号
    import_xmind_requested = pyqtSignal()
    export_xmind_requested = pyqtSignal()
    # 新增：Anki导出信号
    export_anki_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.model_combo = None
        self.connect_btn = None
        self.monitor_btn = None
        self.import_xmind_btn = None
        self.export_xmind_btn = None

    def create_panel(self):
        """创建控制面板并返回布局（QLayout）。"""
        # 模型选择
        self.layout.addWidget(QLabel("AI模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        self.layout.addWidget(self.model_combo)

        # 连接AI按钮
        self.connect_btn = QPushButton("🔌 连接AI")
        self.connect_btn.clicked.connect(self._connect_ai)
        self.layout.addWidget(self.connect_btn)

        self.layout.addStretch()

        # 剪贴板监控开关
        self.monitor_btn = QPushButton("📋 启用剪贴板监控")
        self.monitor_btn.setCheckable(True)
        # 使用 lambda 包装 emit 以避免在连接时立即执行
        self.monitor_btn.toggled.connect(lambda checked: self.clipboard_monitor_toggled.emit(checked))
        self.layout.addWidget(self.monitor_btn)

        # XMind导入导出按钮
        self.import_xmind_btn = QPushButton("📥 导入XMind")
        self.import_xmind_btn.clicked.connect(lambda: self.import_xmind_requested.emit())
        self.layout.addWidget(self.import_xmind_btn)

        self.export_xmind_btn = QPushButton("📤 导出XMind")
        self.export_xmind_btn.clicked.connect(lambda: self.export_xmind_requested.emit())
        self.layout.addWidget(self.export_xmind_btn)

        # 保存按钮
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(lambda: self.save_requested.emit())
        self.layout.addWidget(save_btn)

        # 加载按钮
        load_btn = QPushButton("📁 加载")
        load_btn.clicked.connect(lambda: self.load_requested.emit())
        self.layout.addWidget(load_btn)

        # 导出按钮
        export_btn = QPushButton("📤 导出Markdown")
        export_btn.clicked.connect(lambda: self.export_requested.emit())
        self.layout.addWidget(export_btn)

        # 新增：导出到Anki按钮
        export_anki_btn = QPushButton("📚 导出到Anki")
        export_anki_btn.clicked.connect(self.export_anki_requested.emit)  # 确保这里是正确的信号
        self.layout.addWidget(export_anki_btn)

        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空画布")
        clear_btn.clicked.connect(lambda: self.clear_requested.emit())
        self.layout.addWidget(clear_btn)

        return self.layout

    def _on_model_changed(self, model):
        """模型改变回调"""
        self.model_changed.emit(model)

    def _connect_ai(self):
        """连接AI服务"""
        self.ai_connected.emit()

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

    def set_clipboard_monitor_status(self, monitoring):
        """设置剪贴板监控状态"""
        if monitoring:
            self.monitor_btn.setText("📋 剪贴板监控中...")
        else:
            self.monitor_btn.setText("📋 启用剪贴板监控")