"""
文本选择操作栏 - 显示在选中文本上方
支持：复制、翻译、制卡、划线、高亮等功能
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QComboBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush


class TextSelectionToolbar(QWidget):
    """文本选择操作栏"""
    
    # 信号定义
    copy_requested = pyqtSignal()
    translate_requested = pyqtSignal()
    create_card_requested = pyqtSignal()
    underline_requested = pyqtSignal(str)  # 颜色
    highlight_requested = pyqtSignal(str)  # 颜色
    
    # 预定义颜色
    COLORS = {
        "黄色": QColor(255, 255, 0),
        "绿色": QColor(144, 238, 144),
        "蓝色": QColor(173, 216, 230),
        "红色": QColor(255, 182, 193),
        "橙色": QColor(255, 165, 0),
        "紫色": QColor(221, 160, 221),
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 复制按钮
        copy_btn = QPushButton("📋 复制")
        copy_btn.setStyleSheet("padding: 5px 10px; border-radius: 3px;")
        copy_btn.clicked.connect(self.copy_requested.emit)
        layout.addWidget(copy_btn)
        
        # 翻译按钮
        translate_btn = QPushButton("🌐 翻译")
        translate_btn.setStyleSheet("padding: 5px 10px; border-radius: 3px;")
        translate_btn.clicked.connect(self.translate_requested.emit)
        layout.addWidget(translate_btn)
        
        # 制卡按钮
        card_btn = QPushButton("✨ 制卡")
        card_btn.setStyleSheet("padding: 5px 10px; border-radius: 3px;")
        card_btn.clicked.connect(self.create_card_requested.emit)
        layout.addWidget(card_btn)
        
        # 划线颜色选择
        underline_label = QPushButton("下划线")
        underline_label.setStyleSheet("padding: 5px 10px; border-radius: 3px;")
        underline_combo = QComboBox()
        underline_combo.addItems(["黄色", "绿色", "蓝色", "红色", "橙色", "紫色", "自定义..."])
        underline_combo.currentTextChanged.connect(self._on_underline_color_changed)
        layout.addWidget(underline_label)
        layout.addWidget(underline_combo)
        self.underline_combo = underline_combo
        
        # 高亮颜色选择
        highlight_label = QPushButton("高亮")
        highlight_label.setStyleSheet("padding: 5px 10px; border-radius: 3px;")
        highlight_combo = QComboBox()
        highlight_combo.addItems(["黄色", "绿色", "蓝色", "红色", "橙色", "紫色", "自定义..."])
        highlight_combo.currentTextChanged.connect(self._on_highlight_color_changed)
        layout.addWidget(highlight_label)
        layout.addWidget(highlight_combo)
        self.highlight_combo = highlight_combo
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 240);
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QComboBox {
                padding: 3px 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
    
    def _on_underline_color_changed(self, color_text):
        """划线颜色改变"""
        if color_text == "自定义...":
            color = QColorDialog.getColor(QColor(255, 255, 0), self, "选择划线颜色")
            if color.isValid():
                color_name = color.name()
                self.underline_requested.emit(color_name)
        else:
            color = self.COLORS.get(color_text, QColor(255, 255, 0))
            self.underline_requested.emit(color.name())
    
    def _on_highlight_color_changed(self, color_text):
        """高亮颜色改变"""
        if color_text == "自定义...":
            color = QColorDialog.getColor(QColor(255, 255, 0), self, "选择高亮颜色")
            if color.isValid():
                color_name = color.name()
                self.highlight_requested.emit(color_name)
        else:
            color = self.COLORS.get(color_text, QColor(255, 255, 0))
            self.highlight_requested.emit(color.name())
    
    def show_at_position(self, position: QPoint):
        """在指定位置显示工具栏"""
        self.move(position)
        self.show()
        self.raise_()
    
    def paintEvent(self, event):
        """绘制圆角背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形背景
        rect = self.rect()
        painter.setBrush(QBrush(QColor(240, 240, 240, 240)))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRoundedRect(rect, 5, 5)
        
        super().paintEvent(event)





