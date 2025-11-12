"""图形场景定义"""
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor
from connections import ConnectionManager
from nodes import VisualNode
from models import TreeNode

class ProfessionalMindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-2000, -2000, 4000, 4000)
        self.visual_nodes = []
        self.connection_manager = ConnectionManager()
        self.connection_style = "bezier"  # 默认连线样式

        # 复制粘贴相关
        self.copied_nodes = []

    def add_visual_node(self, visual_node: VisualNode):
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)

    def set_connection_style(self, style):
        """设置连线样式"""
        self.connection_style = style
        self.update()

    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 添加子节点
            selected_items = self.selectedItems()
            if selected_items:
                selected_items[0].add_child_node()
                event.accept()
                return
        elif event.key() == Qt.Key.Key_Tab:
            # 添加同级节点
            selected_items = self.selectedItems()
            if selected_items:
                selected_items[0].add_sibling_node()
                event.accept()
                return
        elif event.key() == Qt.Key.Key_Delete:
            # 删除选中节点
            self.delete_selected_nodes()
            event.accept()
            return
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_A:
                # Ctrl+A 全选
                self.select_all_nodes()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_C:
                # Ctrl+C 复制
                self.copy_selected_nodes()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_V:
                # Ctrl+V 粘贴
                self.paste_nodes()
                event.accept()
                return

        super().keyPressEvent(event)

    def select_all_nodes(self):
        """选择所有节点"""
        for node in self.visual_nodes:
            node.setSelected(True)

    def copy_selected_nodes(self):
        """复制选中的节点"""
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, VisualNode)]
        self.copied_nodes = []

        for node in selected_nodes:
            # 复制节点及其子树
            copied_node = node.tree_node.duplicate()
            self.copied_nodes.append(copied_node)

        print(f"已复制 {len(self.copied_nodes)} 个节点")

    def paste_nodes(self):
        """粘贴节点"""
        if not self.copied_nodes:
            return

        # 计算粘贴位置（稍微偏移）
        paste_offset = 30

        for copied_node in self.copied_nodes:
            # 调整位置
            copied_node.x += paste_offset
            copied_node.y += paste_offset

            # 添加到场景
            visual_node = VisualNode(copied_node)
            self.add_visual_node(visual_node)

            # 递归添加子节点
            def add_children(parent_node, parent_visual):
                for child in parent_node.children:
                    child_visual = VisualNode(child)
                    self.add_visual_node(child_visual)
                    add_children(child, child_visual)

            add_children(copied_node, visual_node)

        self.update()
        print(f"已粘贴 {len(self.copied_nodes)} 个节点")

    def delete_selected_nodes(self):
        """删除选中的节点"""
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, VisualNode)]
        for node in selected_nodes:
            self.delete_node(node)

    def delete_node(self, node):
        """删除指定节点及其子树"""
        if node in self.visual_nodes:
            # 递归删除所有子节点
            def remove_children(tree_node):
                for child in tree_node.children[:]:  # 使用副本遍历
                    child_vn = next((v for v in self.visual_nodes if v.tree_node == child), None)
                    if child_vn:
                        remove_children(child)
                        self.visual_nodes.remove(child_vn)
                        self.removeItem(child_vn)

            # 从父节点中移除
            if node.tree_node.parent:
                node.tree_node.parent.remove_child(node.tree_node)

            # 删除节点及其子树
            remove_children(node.tree_node)
            self.visual_nodes.remove(node)
            self.removeItem(node)

            self.update()
            print(f"已删除节点: {node.tree_node.title}")

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """绘制专业连线"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制永久连线
        connections = []
        for vn in self.visual_nodes:
            node = vn.tree_node
            for child in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node == child), None)
                if child_vn:
                    connection = self.connection_manager.create_connection(vn, child_vn, self.connection_style)
                    connection.update_path()
                    connections.append(connection)

        # 绘制所有永久连线
        for connection in connections:
            connection.draw(painter)

    def mouseDoubleClickEvent(self, event):
        """空白处双击创建新节点"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取点击位置
            scene_pos = event.scenePos()

            # 创建新节点
            new_node = TreeNode("新节点", scene_pos.x(), scene_pos.y())

            # 添加到场景
            visual_node = VisualNode(new_node)
            self.add_visual_node(visual_node)

            # 如果没有根节点，设置为根节点
            if not any(vn.tree_node.level == 0 for vn in self.visual_nodes):
                new_node.level = 0

            self.update()

            # 设置新节点为选中状态
            self.clearSelection()
            visual_node.setSelected(True)
            visual_node.setFocus()

            event.accept()
        else:
            super().mouseDoubleClickEvent(event)