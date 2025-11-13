"""
基于 madmap 的可视化节点 - 添加问题和答案显示
参考 test/madmap/nodes.py
"""

from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, 
    QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QPushButton, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QObject
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QLinearGradient, QPixmap

from .madmap_based_models import CardTreeNode
from PyQt6.QtWidgets import QGraphicsPixmapItem


class CardEditDialog(QDialog):
    """卡片编辑对话框 - 支持问题、答案、笔记和图片编辑"""
    
    def __init__(self, parent=None, title="", question="", answer="", note="", image_path="", image_placement="top"):
        super().__init__(parent)
        self.setWindowTitle("编辑卡片")
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # 标题
        layout.addWidget(QLabel("标题:"))
        self.title_edit = QLineEdit(title)
        layout.addWidget(self.title_edit)
        
        # 问题
        layout.addWidget(QLabel("问题:"))
        self.question_edit = QTextEdit(question)
        self.question_edit.setMaximumHeight(100)
        layout.addWidget(self.question_edit)
        
        # 答案
        layout.addWidget(QLabel("答案:"))
        self.answer_edit = QTextEdit(answer)
        self.answer_edit.setMaximumHeight(150)
        layout.addWidget(self.answer_edit)
        
        # 笔记
        layout.addWidget(QLabel("笔记:"))
        self.note_edit = QTextEdit(note)
        self.note_edit.setPlaceholderText("在此输入笔记内容...")
        layout.addWidget(self.note_edit)
        
        # 图片
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("图片:"))
        self.image_path_edit = QLineEdit(image_path)
        image_layout.addWidget(self.image_path_edit)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_image)
        image_layout.addWidget(browse_btn)
        layout.addLayout(image_layout)
        
        # 图片位置
        placement_layout = QHBoxLayout()
        placement_layout.addWidget(QLabel("图片位置:"))
        self.placement_combo = QComboBox()
        self.placement_combo.addItems(["top", "bottom", "left", "right"])
        self.placement_combo.setCurrentText(image_placement)
        placement_layout.addWidget(self.placement_combo)
        layout.addLayout(placement_layout)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_image(self):
        """浏览图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_path:
            self.image_path_edit.setText(file_path)
    
    def get_data(self):
        """获取编辑后的数据"""
        return {
            "title": self.title_edit.text(),
            "question": self.question_edit.toPlainText(),
            "answer": self.answer_edit.toPlainText(),
            "note": self.note_edit.toPlainText(),
            "image_path": self.image_path_edit.text(),
            "image_placement": self.placement_combo.currentText()
        }


class CardVisualNode(QObject, QGraphicsRectItem):
    """
    卡片可视化节点 - 基于 madmap 的 VisualNode，添加问题和答案显示
    参考 test/madmap/nodes.py
    注意：需要同时继承 QObject 和 QGraphicsRectItem 以支持信号
    """
    
    WIDTH = 280
    HEIGHT = 180
    HEADER_HEIGHT = 35

    # 定义信号
    jump_to_source_requested = pyqtSignal(object)  # 请求跳转到源文本
    jump_to_note_requested = pyqtSignal(object)  # 请求跳转到笔记
    show_note_requested = pyqtSignal(object)  # 请求显示笔记

    def __init__(self, tree_node: CardTreeNode):
        # 先初始化 QObject，再初始化 QGraphicsRectItem
        QObject.__init__(self)
        QGraphicsRectItem.__init__(self, 0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # 根据层级设置不同样式
        self.setup_style()

        # 创建文本显示项
        self.create_text_items()
        
        # 创建图片显示项（如果有）
        self.image_item = None
        if tree_node.image_path:
            self.add_image(tree_node.image_path, tree_node.image_placement)

    def setup_style(self):
        """根据节点层级设置样式（参考 madmap）"""
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
        """创建文本显示项（标题、问题、答案）"""
        text_color = self.get_text_color()
        
        # 标题文本
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(self._truncate_text(self.tree_node.title, 30))
        self.title_item.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.title_item.setDefaultTextColor(text_color)
        self.title_item.setTextWidth(self.WIDTH - 20)
        self.title_item.setPos(10, 5)
        
        # 问题文本（如果有）
        if self.tree_node.question:
            self.question_item = QGraphicsTextItem(self)
            self.question_item.setPlainText(self._truncate_text(self.tree_node.question, 50))
            self.question_item.setFont(QFont("Microsoft YaHei", 9))
            self.question_item.setDefaultTextColor(text_color)
            self.question_item.setTextWidth(self.WIDTH - 20)
            self.question_item.setPos(10, self.HEADER_HEIGHT)
        else:
            self.question_item = None
        
        # 答案文本（如果有）
        if self.tree_node.answer:
            answer_y = self.HEADER_HEIGHT + (30 if self.question_item else 0)
            self.answer_item = QGraphicsTextItem(self)
            self.answer_item.setPlainText(self._truncate_text(self.tree_node.answer, 80))
            self.answer_item.setFont(QFont("Microsoft YaHei", 9))
            self.answer_item.setDefaultTextColor(text_color)
            self.answer_item.setTextWidth(self.WIDTH - 20)
            self.answer_item.setPos(10, answer_y)
        else:
            self.answer_item = None
        
        # 笔记图标（如果有笔记）
        if self.tree_node.note_text:
            # 如果已存在，先删除
            if hasattr(self, 'note_indicator') and self.note_indicator:
                self.scene().removeItem(self.note_indicator) if self.scene() else None
            self.note_indicator = QGraphicsTextItem("📝", self)
            self.note_indicator.setFont(QFont("Microsoft YaHei", 10))
            self.note_indicator.setDefaultTextColor(text_color)
            # 放在右上角
            self.note_indicator.setPos(self.WIDTH - 25, 5)
        else:
            # 如果没有笔记，删除图标
            if hasattr(self, 'note_indicator') and self.note_indicator:
                if self.scene():
                    self.scene().removeItem(self.note_indicator)
                self.note_indicator = None

    def _truncate_text(self, text, max_length):
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def itemChange(self, change, value):
        # 当节点位置改变时，同步 CardTreeNode 的 x,y 并让场景更新连线
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update()
        # 多重继承时，明确调用 QGraphicsRectItem 的 itemChange
        return QGraphicsRectItem.itemChange(self, change, value)

    def center_pos(self):
        """获取节点中心位置"""
        return QPointF(self.pos().x() + self.WIDTH / 2, self.pos().y() + self.HEIGHT / 2)

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 左键双击编辑节点
            self.edit_card()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键双击删除节点
            self.delete_node()
            event.accept()
        else:
            QGraphicsRectItem.mouseDoubleClickEvent(self, event)

    def mousePressEvent(self, event):
        """鼠标点击事件 - 支持跳转到源文本或笔记，以及创建关联线"""
        scene = self.scene()
        if scene and hasattr(scene, 'is_creating_associative_line'):
            # 如果正在创建关联线
            if scene.is_creating_associative_line:
                if scene.associative_line_start_node != self:
                    # 完成关联线创建
                    scene.associative_line_manager.complete_creating_line(self)
                    scene.is_creating_associative_line = False
                    scene.associative_line_start_node = None
                    event.accept()
                    return
                else:
                    # 不能连接到自身
                    scene.is_creating_associative_line = False
                    scene.associative_line_start_node = None
                    event.accept()
                    return
        
        if event.button() == Qt.MouseButton.LeftButton:
            # 左键点击：优先跳转到笔记，如果没有笔记则跳转到源文本
            if self.tree_node.note_text:
                # 如果有笔记，跳转到笔记
                self.jump_to_note_requested.emit(self)
            elif self.tree_node.source_text:
                # 如果有源文本，跳转到源文本
                self.jump_to_source_requested.emit(self)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键点击：开始创建关联线
            if scene and hasattr(scene, 'associative_line_manager'):
                scene.is_creating_associative_line = True
                scene.associative_line_start_node = self
                # 可以在这里显示提示
                print(f"开始创建关联线，请点击目标节点")
                event.accept()
                return
        QGraphicsRectItem.mousePressEvent(self, event)

    def delete_node(self):
        """删除节点"""
        if self.scene():
            self.scene().delete_node(self)

    def edit_card(self):
        """编辑卡片（标题、问题、答案、笔记、图片）"""
        dialog = CardEditDialog(
            None,
            self.tree_node.title,
            self.tree_node.question,
            self.tree_node.answer,
            self.tree_node.note_text,
            getattr(self.tree_node, 'image_path', ''),
            getattr(self.tree_node, 'image_placement', 'top')
        )
        if dialog.exec():
            data = dialog.get_data()
            self.tree_node.title = data["title"]
            self.tree_node.question = data["question"]
            self.tree_node.answer = data["answer"]
            self.tree_node.note_text = data.get("note", "")
            self.tree_node.image_path = data.get("image_path", "")
            self.tree_node.image_placement = data.get("image_placement", "top")
            
            # 更新显示（包括笔记图标）
            self.create_text_items()
            # 更新图片（如果有）
            if data.get("image_path"):
                self.add_image(data.get("image_path"), data.get("image_placement", "top"))
            elif self.image_item:
                # 如果删除了图片
                if self.scene():
                    self.scene().removeItem(self.image_item)
                self.image_item = None
            if self.scene():
                self.scene().update()
    
    def add_image(self, image_path, placement='top'):
        """添加图片到节点"""
        if not image_path:
            return
        
        # 如果已有图片，先删除
        if self.image_item:
            if self.scene():
                self.scene().removeItem(self.image_item)
            self.image_item = None
        
        # 加载图片
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"无法加载图片: {image_path}")
            return
        
        # 调整图片大小以适应节点
        max_width = self.WIDTH - 20
        max_height = 100
        
        scaled_pixmap = pixmap.scaled(
            max_width, max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 创建图片项
        self.image_item = QGraphicsPixmapItem(scaled_pixmap, self)
        
        # 根据placement设置位置
        if placement == 'top':
            self.image_item.setPos(10, 5)
        elif placement == 'bottom':
            self.image_item.setPos(10, self.HEIGHT - scaled_pixmap.height() - 5)
        elif placement == 'left':
            self.image_item.setPos(5, 10)
        elif placement == 'right':
            self.image_item.setPos(self.WIDTH - scaled_pixmap.width() - 5, 10)
        
        # 更新文本位置以适应图片
        self._adjust_text_for_image(placement)
    
    def _adjust_text_for_image(self, placement):
        """调整文本位置以适应图片"""
        if not self.image_item:
            return
        
        image_height = self.image_item.boundingRect().height()
        image_width = self.image_item.boundingRect().width()
        
        if placement == 'top':
            # 图片在上方，文本向下移动
            if self.title_item:
                self.title_item.setPos(10, 5 + image_height + 5)
            if self.question_item:
                self.question_item.setPos(10, self.HEADER_HEIGHT + image_height + 5)
            if self.answer_item:
                answer_y = self.HEADER_HEIGHT + (30 if self.question_item else 0) + image_height + 5
                self.answer_item.setPos(10, answer_y)
        elif placement == 'left':
            # 图片在左侧，文本向右移动
            offset_x = image_width + 10
            if self.title_item:
                self.title_item.setPos(offset_x, 5)
            if self.question_item:
                self.question_item.setPos(offset_x, self.HEADER_HEIGHT)
            if self.answer_item:
                answer_y = self.HEADER_HEIGHT + (30 if self.question_item else 0)
                self.answer_item.setPos(offset_x, answer_y)

    def keyPressEvent(self, event):
        """键盘事件处理（参考 madmap）"""
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
            QGraphicsRectItem.keyPressEvent(self, event)

    def add_child_node(self):
        """添加子节点（参考 madmap）"""
        child_node = CardTreeNode("新子节点", "问题内容", "答案内容")
        self.tree_node.add_child(child_node)

        # 计算新节点位置（避免重叠）
        new_x = self.tree_node.x + 300
        new_y = self.tree_node.y + len(self.tree_node.children) * 200

        child_node.x = new_x
        child_node.y = new_y

        # 添加到场景
        if self.scene():
            visual_child = CardVisualNode(child_node)
            self.scene().add_visual_node(visual_child)
            # 应用布局
            if hasattr(self.scene(), 'apply_layout'):
                self.scene().apply_layout()
            self.scene().update()

            # 设置新节点为选中状态
            self.scene().clearSelection()
            visual_child.setSelected(True)
            visual_child.setFocus()

    def add_sibling_node(self):
        """添加同级节点（参考 madmap）"""
        if self.tree_node.parent:
            sibling_node = CardTreeNode("新同级节点", "问题内容", "答案内容")
            self.tree_node.parent.add_child(sibling_node)

            # 计算新节点位置
            siblings = self.tree_node.parent.children
            index = siblings.index(self.tree_node)

            # 放在当前节点右侧
            sibling_node.x = self.tree_node.x + 300
            sibling_node.y = self.tree_node.y

            # 添加到场景
            if self.scene():
                visual_sibling = CardVisualNode(sibling_node)
                self.scene().add_visual_node(visual_sibling)
                # 应用布局
                if hasattr(self.scene(), 'apply_layout'):
                    self.scene().apply_layout()
                self.scene().update()

                # 设置新节点为选中状态
                self.scene().clearSelection()
                visual_sibling.setSelected(True)
                visual_sibling.setFocus()
        else:
            # 如果是根节点，不能添加同级节点
            print("根节点不能添加同级节点")

