"""
节点形状扩展 - 支持多种节点形状
参考 Simple Mind Map 的 Shape.js
"""

from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush


class NodeShapeFactory:
    """节点形状工厂"""
    
    SHAPE_RECTANGLE = "rectangle"
    SHAPE_ROUNDED_RECTANGLE = "rounded_rectangle"
    SHAPE_ELLIPSE = "ellipse"
    SHAPE_CIRCLE = "circle"
    SHAPE_DIAMOND = "diamond"
    
    @staticmethod
    def create_shape(shape_type, rect: QRectF, parent=None):
        """创建形状"""
        if shape_type == NodeShapeFactory.SHAPE_RECTANGLE:
            return QGraphicsRectItem(rect, parent)
        elif shape_type == NodeShapeFactory.SHAPE_ROUNDED_RECTANGLE:
            return RoundedRectangleItem(rect, parent)
        elif shape_type == NodeShapeFactory.SHAPE_ELLIPSE:
            return QGraphicsEllipseItem(rect, parent)
        elif shape_type == NodeShapeFactory.SHAPE_CIRCLE:
            # 圆形：使用较大的边作为直径
            size = min(rect.width(), rect.height())
            circle_rect = QRectF(
                rect.x() + (rect.width() - size) / 2,
                rect.y() + (rect.height() - size) / 2,
                size, size
            )
            return QGraphicsEllipseItem(circle_rect, parent)
        elif shape_type == NodeShapeFactory.SHAPE_DIAMOND:
            return DiamondItem(rect, parent)
        else:
            return QGraphicsRectItem(rect, parent)


class RoundedRectangleItem(QGraphicsRectItem):
    """圆角矩形"""
    
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.radius = 10
    
    def paint(self, painter, option, widget):
        """绘制圆角矩形"""
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        painter.fillPath(path, self.brush())
        painter.strokePath(path, self.pen())


class DiamondItem(QGraphicsRectItem):
    """菱形"""
    
    def paint(self, painter, option, widget):
        """绘制菱形"""
        rect = self.rect()
        center_x = rect.center().x()
        center_y = rect.center().y()
        half_width = rect.width() / 2
        half_height = rect.height() / 2
        
        path = QPainterPath()
        path.moveTo(center_x, rect.top())
        path.lineTo(rect.right(), center_y)
        path.lineTo(center_x, rect.bottom())
        path.lineTo(rect.left(), center_y)
        path.closeSubpath()
        
        painter.fillPath(path, self.brush())
        painter.strokePath(path, self.pen())

