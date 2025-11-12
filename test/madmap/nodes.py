"""可视化节点定义"""
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QInputDialog
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QLinearGradient
from models import TreeNode

class VisualNode(QGraphicsRectItem):
    WIDTH = 160
    HEIGHT = 90

    def __init__(self, tree_node: TreeNode):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # 根据层级设置不同样式
        self.setup_style()

        # 文本
        self.text_item = QGraphicsTextItem(self.tree_node.title, self)
        self.text_item.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.text_item.setDefaultTextColor(self.get_text_color())
        self.text_item.setTextWidth(self.WIDTH - 20)
        self.text_item.setPos(10, 10)

    def setup_style(self):
        """根据节点层级设置样式"""
        level_styles = [
            (QColor(74, 124, 89), QColor(173, 223, 173), 2.5),  # 根节点
            (QColor(49, 99, 149), QColor(173, 216, 230), 2.0),  # 第1级
            (QColor(149, 99, 49), QColor(255, 218, 185), 1.5),  # 第2级
            (QColor(99, 99, 99), QColor(240, 240, 240), 1.0)  # 其他级别
        ]

        level_index = min(self.tree_node.level, len(level_styles) - 1)
        border_color, fill_color, border_width = level_styles[level_index]

        # 设置渐变填充
        gradient = QLinearGradient(0, 0, 0, self.HEIGHT)
        gradient.setColorAt(0, fill_color.lighter(120))
        gradient.setColorAt(1, fill_color.darker(110))

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(border_color, border_width))
        self.setRect(0, 0, self.WIDTH, self.HEIGHT)

    def get_text_color(self):
        """根据背景色返回合适的文字颜色"""
        level_colors = [
            QColor(255, 255, 255),  # 根节点 - 白色文字
            QColor(0, 0, 0),  # 第1级 - 黑色文字
            QColor(0, 0, 0),  # 第2级 - 黑色文字
            QColor(80, 80, 80)  # 其他级别 - 深灰色
        ]
        return level_colors[min(self.tree_node.level, len(level_colors) - 1)]

    def itemChange(self, change, value):
        # 当节点位置改变时，同步 TreeNode 的 x,y 并让场景更新连线
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x() + self.WIDTH / 2, self.pos().y() + self.HEIGHT / 2)

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 左键双击编辑节点标题
            self.edit_title()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键双击删除节点
            self.delete_node()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def delete_node(self):
        """删除节点"""
        if self.scene():
            self.scene().delete_node(self)

    def edit_title(self):
        """编辑节点标题"""
        new_title, ok = QInputDialog.getText(
            None,
            "编辑节点标题",
            "请输入新标题:",
            text=self.tree_node.title
        )
        if ok and new_title:
            self.tree_node.title = new_title
            self.text_item.setPlainText(new_title)
            if self.scene():
                self.scene().update()

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 回车键 - 添加子节点
            self.add_child_node()
            event.accept()
        elif event.key() == Qt.Key.Key_Tab:
            # Tab键 - 添加同级节点
            self.add_sibling_node()
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            # Delete键 - 删除节点
            self.delete_node()
            event.accept()
        else:
            super().keyPressEvent(event)

    def add_child_node(self):
        """添加子节点"""
        child_node = TreeNode("新子节点")
        self.tree_node.add_child(child_node)

        # 计算新节点位置（避免重叠）
        new_x = self.tree_node.x + 200
        new_y = self.tree_node.y + len(self.tree_node.children) * 120

        child_node.x = new_x
        child_node.y = new_y

        # 添加到场景
        if self.scene():
            visual_child = VisualNode(child_node)
            self.scene().add_visual_node(visual_child)
            self.scene().update()

            # 设置新节点为选中状态
            self.scene().clearSelection()
            visual_child.setSelected(True)
            visual_child.setFocus()

    def add_sibling_node(self):
        """添加同级节点"""
        if self.tree_node.parent:
            sibling_node = TreeNode("新同级节点")
            self.tree_node.parent.add_child(sibling_node)

            # 计算新节点位置
            siblings = self.tree_node.parent.children
            index = siblings.index(self.tree_node)

            # 放在当前节点右侧
            sibling_node.x = self.tree_node.x + 200
            sibling_node.y = self.tree_node.y

            # 添加到场景
            if self.scene():
                visual_sibling = VisualNode(sibling_node)
                self.scene().add_visual_node(visual_sibling)
                self.scene().update()

                # 设置新节点为选中状态
                self.scene().clearSelection()
                visual_sibling.setSelected(True)
                visual_sibling.setFocus()
        else:
            # 如果是根节点，不能添加同级节点
            print("根节点不能添加同级节点")