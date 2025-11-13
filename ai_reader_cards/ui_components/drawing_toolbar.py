# 文件路径: ai_reader_cards\ui_components\drawing_toolbar.py
"""绘画工具栏组件"""

from PyQt6.QtWidgets import QToolBar, QPushButton, QLabel, QSpinBox, QColorDialog
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor


class DrawingToolbar(QToolBar):
    """绘画工具栏"""

    drawing_mode_toggled = pyqtSignal(bool)
    pen_color_changed = pyqtSignal(QColor)
    pen_width_changed = pyqtSignal(int)
    clear_drawings_requested = pyqtSignal()

    def __init__(self):
        super().__init__("绘画工具")
        self.drawing_btn = None
        self.color_btn = None
        self.pen_size_spin = None
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3

        self.setMovable(False)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 绘画模式开关
        self.drawing_btn = QPushButton("🎨 绘画模式")
        self.drawing_btn.setCheckable(True)
        self.drawing_btn.toggled.connect(self.drawing_mode_toggled.emit)
        self.addWidget(self.drawing_btn)

        self.addSeparator()

        # 颜色选择
        self.color_btn = QPushButton("颜色")
        self.color_btn.clicked.connect(self._choose_pen_color)
        self.color_btn.setStyleSheet(f"background-color: {self.pen_color.name()};")
        self.addWidget(self.color_btn)

        # 画笔粗细
        self.addWidget(QLabel("画笔粗细:"))
        self.pen_size_spin = QSpinBox()
        self.pen_size_spin.setRange(1, 20)
        self.pen_size_spin.setValue(self.pen_width)
        self.pen_size_spin.valueChanged.connect(self.pen_width_changed.emit)
        self.addWidget(self.pen_size_spin)

        self.addSeparator()

        # 清除绘画
        clear_drawing_btn = QPushButton("🧹 清除绘画")
        clear_drawing_btn.clicked.connect(self.clear_drawings_requested.emit)
        self.addWidget(clear_drawing_btn)

    def _choose_pen_color(self):
        """选择画笔颜色"""
        color = QColorDialog.getColor(self.pen_color, self, "选择画笔颜色")
        if color.isValid():
            self.pen_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.pen_color_changed.emit(color)

    def toggle_drawing_mode(self):
        """切换绘画模式"""
        self.drawing_btn.toggle()