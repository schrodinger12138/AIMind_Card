"""
节点标签支持 - 多标签、标签样式
参考 Simple Mind Map 的标签功能
"""

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem


class TagItem(QGraphicsRectItem):
    """标签项"""
    
    def __init__(self, text, color=None, parent=None):
        super().__init__(parent)
        self.text = text
        self.color = color or QColor(100, 150, 200)
        self.text_item = None
        
        # 计算标签大小
        font = QFont("Microsoft YaHei", 8)
        metrics = QPainter.fontMetrics(font)
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # 设置标签矩形（带内边距）
        padding = 6
        self.setRect(0, 0, text_width + padding * 2, text_height + padding * 2)
        
        # 创建文字项
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(QColor(255, 255, 255))
        self.text_item.setFont(font)
        self.text_item.setPos(padding, padding)
        
        # 设置样式
        self.setBrush(QBrush(self.color))
        self.setPen(QPen(self.color.darker(120), 1))
        
        # 设置标志
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
    
    def paint(self, painter, option, widget):
        """绘制圆角标签"""
        rect = self.rect()
        radius = 4
        
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, self.brush())
        painter.strokePath(path, self.pen())


class TagManager:
    """标签管理器"""
    
    # 预设标签颜色
    PRESET_COLORS = [
        QColor(100, 150, 200),  # 蓝色
        QColor(150, 100, 200),  # 紫色
        QColor(200, 100, 150),  # 粉色
        QColor(100, 200, 150),  # 绿色
        QColor(200, 150, 100),  # 橙色
        QColor(200, 100, 100),  # 红色
        QColor(100, 200, 200),  # 青色
        QColor(200, 200, 100),  # 黄色
    ]
    
    @classmethod
    def create_tag(cls, text, color_index=0):
        """创建标签"""
        color = cls.PRESET_COLORS[color_index % len(cls.PRESET_COLORS)]
        return TagItem(text, color)
    
    @classmethod
    def create_tags(cls, tag_list, color_indices=None):
        """创建多个标签"""
        tags = []
        for i, tag_text in enumerate(tag_list):
            color_idx = color_indices[i] if color_indices and i < len(color_indices) else i
            tags.append(cls.create_tag(tag_text, color_idx))
        return tags

