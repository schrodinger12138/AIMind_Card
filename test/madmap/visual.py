from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QPointF

class VisualNode(QGraphicsRectItem):
    WIDTH = 160
    HEIGHT = 90

    def __init__(self, tree_node):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.text_item = QGraphicsTextItem(tree_node.title, self)
        self.text_item.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.text_item.setTextWidth(self.WIDTH - 20)
        self.text_item.setPos(10, 10)
        self.update_style()

    def update_style(self):
        """根据层级设置样式"""
        color_map = [QColor(74,124,89), QColor(49,99,149), QColor(149,99,49), QColor(99,99,99)]
        fill = color_map[min(self.tree_node.level, len(color_map)-1)]
        gradient = QBrush(fill)
        self.setBrush(gradient)
        self.setPen(QPen(QColor(0,0,0), 2))

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update_connections()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x()+self.WIDTH/2, self.pos().y()+self.HEIGHT/2)
