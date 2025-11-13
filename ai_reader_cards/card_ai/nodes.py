"""可视化节点定义 - 基于madmap，添加问题和答案显示"""
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, 
    QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDialogButtonBox, QPushButton
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QLinearGradient
from .models import TreeNode


class CardEditDialog(QDialog):
    """卡片编辑对话框 - 支持编辑标题、问题和答案"""
    
    def __init__(self, tree_node: TreeNode, parent=None):
        super().__init__(parent)
        self.tree_node = tree_node
        self.setWindowTitle("编辑卡片")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("标题:")
        self.title_edit = QLineEdit(self.tree_node.title)
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)
        
        # 问题
        question_label = QLabel("问题:")
        self.question_edit = QTextEdit(self.tree_node.question)
        self.question_edit.setMaximumHeight(100)
        layout.addWidget(question_label)
        layout.addWidget(self.question_edit)
        
        # 答案
        answer_label = QLabel("答案:")
        self.answer_edit = QTextEdit(self.tree_node.answer)
        self.answer_edit.setMaximumHeight(150)
        layout.addWidget(answer_label)
        layout.addWidget(self.answer_edit)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self):
        """获取编辑后的数据"""
        return {
            "title": self.title_edit.text(),
            "question": self.question_edit.toPlainText(),
            "answer": self.answer_edit.toPlainText()
        }


class VisualNode(QGraphicsRectItem):
    """可视化节点 - 显示标题、问题和答案"""
    WIDTH = 280
    HEIGHT = 200  # 增加高度以容纳问题和答案
    
    # 定义信号
    request_edit = pyqtSignal(object)  # 请求编辑卡片
    request_add_child = pyqtSignal(object)  # 请求添加子节点
    jump_to_source_requested = pyqtSignal(object)  # 请求跳转到源文本

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

        # 创建文本项
        self.create_text_items()

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

    def create_text_items(self):
        """创建文本显示项"""
        text_color = self.get_text_color()
        
        # 标题
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(self._truncate_text(self.tree_node.title, 30))
        self.title_item.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.title_item.setDefaultTextColor(text_color)
        self.title_item.setTextWidth(self.WIDTH - 20)
        self.title_item.setPos(10, 10)
        
        # 问题（如果有）
        y_offset = 40
        if self.tree_node.question:
            question_label = QGraphicsTextItem("问题:", self)
            question_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            question_label.setDefaultTextColor(text_color.darker(150))
            question_label.setPos(10, y_offset)
            
            self.question_item = QGraphicsTextItem(self)
            self.question_item.setPlainText(self._truncate_text(self.tree_node.question, 50))
            self.question_item.setFont(QFont("Microsoft YaHei", 9))
            self.question_item.setDefaultTextColor(text_color)
            self.question_item.setTextWidth(self.WIDTH - 20)
            self.question_item.setPos(10, y_offset + 15)
            y_offset += 50
        else:
            self.question_item = None
        
        # 答案（如果有）
        if self.tree_node.answer:
            answer_label = QGraphicsTextItem("答案:", self)
            answer_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            answer_label.setDefaultTextColor(text_color.darker(150))
            answer_label.setPos(10, y_offset)
            
            self.answer_item = QGraphicsTextItem(self)
            self.answer_item.setPlainText(self._truncate_text(self.tree_node.answer, 80))
            self.answer_item.setFont(QFont("Microsoft YaHei", 9))
            self.answer_item.setDefaultTextColor(text_color)
            self.answer_item.setTextWidth(self.WIDTH - 20)
            self.answer_item.setPos(10, y_offset + 15)
        else:
            self.answer_item = None
    
    def _truncate_text(self, text, max_length):
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

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
            # 左键双击编辑节点
            self.edit_node()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键双击删除节点
            self.delete_node()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 左键点击：请求跳转到源文本（如果有）
            if self.tree_node.source_text:
                self.jump_to_source_requested.emit(self)
        super().mousePressEvent(event)

    def delete_node(self):
        """删除节点"""
        if self.scene():
            self.scene().delete_node(self)

    def edit_node(self):
        """编辑节点"""
        dialog = CardEditDialog(self.tree_node, self.scene().views()[0] if self.scene() else None)
        if dialog.exec():
            data = dialog.get_data()
            self.tree_node.title = data["title"]
            self.tree_node.question = data["question"]
            self.tree_node.answer = data["answer"]
            self.create_text_items()  # 重新创建文本项
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
        child_node = TreeNode("新子节点", "", "")
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
            sibling_node = TreeNode("新同级节点", "", "")
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

