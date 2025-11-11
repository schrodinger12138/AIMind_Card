# 文件路径: ai_reader_cards\ui_components\alignment_toolbar.py
"""对齐工具栏组件"""

from PyQt6.QtWidgets import QToolBar, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal


class AlignmentToolbar(QToolBar):
    """对齐工具栏"""

    alignment_requested = pyqtSignal(str)  # align_type
    arrange_hierarchy_requested = pyqtSignal()

    def __init__(self):
        super().__init__("对齐工具")
        self.setMovable(False)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 对齐按钮
        self.addWidget(QLabel("对齐:"))

        left_btn = QPushButton("左对齐")
        left_btn.clicked.connect(lambda: self.alignment_requested.emit("left"))
        self.addWidget(left_btn)

        right_btn = QPushButton("右对齐")
        right_btn.clicked.connect(lambda: self.alignment_requested.emit("right"))
        self.addWidget(right_btn)

        top_btn = QPushButton("顶对齐")
        top_btn.clicked.connect(lambda: self.alignment_requested.emit("top"))
        self.addWidget(top_btn)

        bottom_btn = QPushButton("底对齐")
        bottom_btn.clicked.connect(lambda: self.alignment_requested.emit("bottom"))
        self.addWidget(bottom_btn)

        self.addSeparator()

        center_h_btn = QPushButton("水平居中")
        center_h_btn.clicked.connect(lambda: self.alignment_requested.emit("center_h"))
        self.addWidget(center_h_btn)

        center_v_btn = QPushButton("垂直居中")
        center_v_btn.clicked.connect(lambda: self.alignment_requested.emit("center_v"))
        self.addWidget(center_v_btn)

        self.addSeparator()

        distribute_h_btn = QPushButton("水平分布")
        distribute_h_btn.clicked.connect(lambda: self.alignment_requested.emit("distribute_h"))
        self.addWidget(distribute_h_btn)

        distribute_v_btn = QPushButton("垂直分布")
        distribute_v_btn.clicked.connect(lambda: self.alignment_requested.emit("distribute_v"))
        self.addWidget(distribute_v_btn)

        self.addSeparator()

        # 层次排列
        hierarchy_btn = QPushButton("层次排列")
        hierarchy_btn.clicked.connect(self.arrange_hierarchy_requested.emit)
        self.addWidget(hierarchy_btn)