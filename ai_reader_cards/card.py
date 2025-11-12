"""卡片模块 - 定义可视化知识卡片"""

from PyQt6.QtWidgets import (QGraphicsRectItem, QGraphicsTextItem,
                              QGraphicsItem, QGraphicsSceneMouseEvent,
                              QInputDialog, QMessageBox, QMenu,
                              QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QTextEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (QPen, QBrush, QColor, QFont, QPainterPath,
                         QCursor, QAction, QPainter)
class ConnectionPoint(QGraphicsRectItem):
    """连接点图形项"""

    def __init__(self, parent_card, direction):
        super().__init__(-4, -4, 8, 8)  # 8x8像素的连接点
        self.parent_card = parent_card
        self.direction = direction
        self.setBrush(QBrush(QColor(70, 130, 180)))
        self.setPen(QPen(QColor(255, 255, 255), 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.setZValue(100)  # 确保连接点在最上层

    def hoverEnterEvent(self, event):
        """鼠标悬停时改变颜色"""
        self.setBrush(QBrush(QColor(255, 140, 0)))  # 悬停时橙色
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """鼠标离开时恢复颜色"""
        self.setBrush(QBrush(QColor(70, 130, 180)))  # 正常时蓝色
        super().hoverLeaveEvent(event)


"""卡片模块 - 定义可视化知识卡片"""


class CardEditDialog(QDialog):
    """卡片编辑对话框"""
    # ... 保持原有代码不变 ...
    pass

class KnowledgeCard(QGraphicsRectItem):
    """知识卡片 - 可拖动、可编辑的卡片"""

    CARD_WIDTH = 280
    CARD_HEIGHT = 180
    HEADER_HEIGHT = 35
    BORDER_RADIUS = 8

    # 定义信号
    request_edit = pyqtSignal(object)  # 请求编辑卡片
    request_add_child = pyqtSignal(object)  # 请求添加子节点
    content_changed = pyqtSignal(object)  # 内容改变信号
    connection_started = pyqtSignal(object, str, QPointF)  # 开始连接信号

    def __init__(self, card_id, title, question, answer, x=0, y=0):
        """初始化卡片"""
        super().__init__(0, 0, self.CARD_WIDTH, self.CARD_HEIGHT)

        self.card_id = card_id
        self.title_text = title
        self.question_text = question
        self.answer_text = answer
        self.parent_card = None
        self.child_cards = []
        self.connections = []  # 存储连接信息
        self.level = 0  # 层级属性，第一个卡片为0
        # 修复：添加 connection_points 初始化
        self.connection_points = {}

        # 设置卡片属性
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # 设置卡片样式
        self.setPen(QPen(QColor(100, 100, 100), 2))
        self.setBrush(QBrush(QColor(255, 255, 255)))

        # 创建文本显示项
        self.create_text_items()

        # 计算连接点位置
        self.update_connection_points()

    def create_text_items(self):
        """创建文本显示项"""
        # 创建标题文本
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(self._truncate_text(self.title_text, 30))
        self.title_item.setPos(10, 5)
        title_font = QFont("Arial", 11, QFont.Weight.Bold)
        self.title_item.setFont(title_font)
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))
        self.title_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # 创建问题文本
        self.question_item = QGraphicsTextItem(self)
        self.question_item.setPlainText("Q: " + self._truncate_text(self.question_text, 60))
        self.question_item.setPos(10, self.HEADER_HEIGHT + 5)
        question_font = QFont("Arial", 9, QFont.Weight.Bold)
        self.question_item.setFont(question_font)
        self.question_item.setDefaultTextColor(QColor(70, 130, 180))
        self.question_item.setTextWidth(self.CARD_WIDTH - 20)
        self.question_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # 创建答案文本
        self.answer_item = QGraphicsTextItem(self)
        self.answer_item.setPlainText("A: " + self._truncate_text(self.answer_text, 120))
        self.answer_item.setPos(10, self.HEADER_HEIGHT + 50)
        answer_font = QFont("Arial", 8)
        self.answer_item.setFont(answer_font)
        self.answer_item.setDefaultTextColor(QColor(60, 60, 60))
        self.answer_item.setTextWidth(self.CARD_WIDTH - 20)
        self.answer_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    # 修复：添加缺失的连接点方法
    def update_connection_points(self):
        """更新连接点位置"""
        self.connection_points = {
            'top': QPointF(self.CARD_WIDTH / 2, 0),
            'right': QPointF(self.CARD_WIDTH, self.CARD_HEIGHT / 2),
            'bottom': QPointF(self.CARD_WIDTH / 2, self.CARD_HEIGHT),
            'left': QPointF(0, self.CARD_HEIGHT / 2)
        }

    def get_connection_point(self, direction):
        """获取指定方向的连接点"""
        if direction in self.connection_points:
            return self.mapToScene(self.connection_points[direction])
        return self.get_center_pos()

    def get_nearest_connection_point(self, target_point):
        """获取距离目标点最近的连接点"""
        local_target = self.mapFromScene(target_point)

        min_distance = float('inf')
        nearest_direction = 'bottom'

        for direction, point in self.connection_points.items():
            distance = (point - local_target).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                nearest_direction = direction

        return nearest_direction, self.get_connection_point(nearest_direction)

    def add_connection(self, from_direction, to_card, to_direction):
        """添加连接关系"""
        connection = {
            'from_direction': from_direction,
            'to_card': to_card,
            'to_direction': to_direction
        }
        self.connections.append(connection)
        to_card.set_parent_card(self)

    def remove_connection(self, to_card):
        """移除连接"""
        self.connections = [conn for conn in self.connections if conn['to_card'] != to_card]
        if to_card in self.child_cards:
            self.child_cards.remove(to_card)
        to_card.set_parent_card(None)

    def get_connections(self):
        """获取所有连接"""
        return self.connections

    # 修复：添加缺失的鼠标事件方法
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在连接点附近
            click_pos = event.pos()
            for direction, point in self.connection_points.items():
                if (point - click_pos).manhattanLength() < 20:  # 点击在连接点附近
                    scene_point = self.mapToScene(point)
                    self.connection_started.emit(self, direction, scene_point)
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """双击事件处理"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 左键双击编辑卡片
            self.edit_card()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键双击删除卡片
            if self.scene() and hasattr(self.scene(), '_save_state_for_undo'):
                self.scene()._save_state_for_undo("删除卡片")
                self.scene().remove_card(self)
                self.scene().update()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def edit_card(self):
        """编辑卡片内容"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox
        
        dialog = QDialog(None)
        dialog.setWindowTitle("编辑卡片")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # 标题输入
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        title_edit = QLineEdit(self.title_text)
        title_layout.addWidget(title_edit)
        layout.addLayout(title_layout)
        
        # 问题输入
        question_label = QLabel("问题:")
        layout.addWidget(question_label)
        question_edit = QTextEdit(self.question_text)
        question_edit.setMaximumHeight(100)
        layout.addWidget(question_edit)
        
        # 答案输入
        answer_label = QLabel("答案:")
        layout.addWidget(answer_label)
        answer_edit = QTextEdit(self.answer_text)
        answer_edit.setMaximumHeight(150)
        layout.addWidget(answer_edit)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.title_text = title_edit.text()
            self.question_text = question_edit.toPlainText()
            self.answer_text = answer_edit.toPlainText()
            
            # 更新显示
            self.title_item.setPlainText(self._truncate_text(self.title_text, 30))
            self.question_item.setPlainText("Q: " + self._truncate_text(self.question_text, 60))
            self.answer_item.setPlainText("A: " + self._truncate_text(self.answer_text, 120))
            
            # 发送内容改变信号
            self.content_changed.emit(self)
            
            if self.scene():
                self.scene().update()

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Enter键 - 添加子节点
            self.add_child_card()
            event.accept()
        elif event.key() == Qt.Key.Key_Tab:
            # Tab键 - 添加同级节点
            self.add_sibling_card()
            event.accept()
        else:
            super().keyPressEvent(event)

    def add_child_card(self):
        """添加子卡片"""
        from ai_reader_cards.card import KnowledgeCard
        import uuid
        
        # 创建新卡片
        child_card = KnowledgeCard(
            str(uuid.uuid4()),
            "新子卡片",
            "问题内容",
            "答案内容",
            self.pos().x() + 200,
            self.pos().y() + len(self.child_cards) * 200
        )
        
        # 添加到场景
        if self.scene():
            self.scene().add_card(child_card)
            child_card.set_parent_card(self)
            self.scene().update()
            
            # 设置新卡片为选中状态
            self.scene().clearSelection()
            child_card.setSelected(True)
            child_card.setFocus()

    def add_sibling_card(self):
        """添加同级卡片 - Tab键"""
        from ai_reader_cards.card import KnowledgeCard
        import uuid
        
        # 创建新卡片，与当前卡片同级
        sibling_card = KnowledgeCard(
            str(uuid.uuid4()),
            "新同级卡片",
            "问题内容",
            "答案内容",
            self.pos().x() + 200,
            self.pos().y()
        )
        
        # 设置相同的父节点和层级
        if self.parent_card:
            sibling_card.set_parent_card(self.parent_card)
        else:
            # 如果没有父节点，说明是根节点，新卡片也是根节点（层级0）
            sibling_card.level = 0
        
        # 添加到场景
        if self.scene():
            self.scene().add_card(sibling_card)
            self.scene().update()
            
            # 设置新卡片为选中状态
            self.scene().clearSelection()
            sibling_card.setSelected(True)
            sibling_card.setFocus()

    def _truncate_text(self, text, max_length):
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def set_parent_card(self, parent):
        """设置父卡片并更新层级"""
        if self.parent_card:
            self.parent_card.child_cards.remove(self)
        self.parent_card = parent
        if parent:
            if self not in parent.child_cards:
                parent.child_cards.append(self)
            # 更新层级：父节点的层级+1
            self.level = parent.level + 1
            # 递归更新所有子节点的层级
            self._update_children_levels()
        else:
            # 如果没有父节点，层级为0
            self.level = 0
            self._update_children_levels()
    
    def _update_children_levels(self):
        """递归更新所有子节点的层级"""
        for child in self.child_cards:
            child.level = self.level + 1
            child._update_children_levels()

    def get_center_pos(self):
        """获取卡片中心位置"""
        return QPointF(
            self.pos().x() + self.CARD_WIDTH / 2,
            self.pos().y() + self.CARD_HEIGHT / 2
        )
    
    def center_pos(self):
        """获取卡片中心位置（用于连线系统）"""
        return self.get_center_pos()

    def to_dict(self):
        """转换为字典格式用于保存"""
        return {
            "id": self.card_id,
            "title": self.title_text,
            "question": self.question_text,
            "answer": self.answer_text,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "level": self.level,  # 保存层级
            "parent_id": self.parent_card.card_id if self.parent_card else None
        }

    def paint(self, painter, option, widget=None):
        """自定义绘制卡片"""
        # 绘制阴影效果
        shadow_rect = QRectF(3, 3, self.CARD_WIDTH, self.CARD_HEIGHT)
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # 绘制主卡片背景
        card_rect = QRectF(0, 0, self.CARD_WIDTH, self.CARD_HEIGHT)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRoundedRect(card_rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # 绘制标题栏背景
        header_rect = QRectF(0, 0, self.CARD_WIDTH, self.HEADER_HEIGHT)
        if self.isSelected():
            painter.setBrush(QBrush(QColor(255, 140, 0)))  # 选中时橙色
        else:
            painter.setBrush(QBrush(QColor(70, 130, 180)))  # 默认蓝色
        painter.setPen(Qt.PenStyle.NoPen)

        # 绘制圆角标题栏
        path = QPainterPath()
        path.moveTo(0, self.HEADER_HEIGHT)
        path.lineTo(0, self.BORDER_RADIUS)
        path.quadTo(0, 0, self.BORDER_RADIUS, 0)
        path.lineTo(self.CARD_WIDTH - self.BORDER_RADIUS, 0)
        path.quadTo(self.CARD_WIDTH, 0, self.CARD_WIDTH, self.BORDER_RADIUS)
        path.lineTo(self.CARD_WIDTH, self.HEADER_HEIGHT)
        path.closeSubpath()
        painter.drawPath(path)

        # 绘制连接点（仅在选中时显示）
        # 绘制连接点（仅在选中时显示）
        if self.isSelected():
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(70, 130, 180), 2))

            for point in self.connection_points.values():
                # 使用QRectF来绘制椭圆
                painter.drawEllipse(QRectF(point.x() - 4, point.y() - 4, 8, 8))


    def itemChange(self, change, value):
        """卡片位置改变时的回调"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # 更新连接点位置
            self.update_connection_points()
            # 自动检测并建立父子关系
            if self.scene() and hasattr(self.scene(), 'check_auto_connect'):
                self.scene().check_auto_connect(self)
            # 通知场景更新连线
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)

    def get_bottom_center(self):
        """获取卡片底部中心位置"""
        return QPointF(
            self.pos().x() + self.CARD_WIDTH / 2,
            self.pos().y() + self.CARD_HEIGHT
        )

    def get_top_center(self):
        """获取卡片顶部中心位置"""
        return QPointF(
            self.pos().x() + self.CARD_WIDTH / 2,
            self.pos().y()
        )