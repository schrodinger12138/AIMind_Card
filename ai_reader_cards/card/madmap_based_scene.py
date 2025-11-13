"""
基于 madmap 的场景 - 整合 AI 生成等功能
参考 test/madmap/scene.py
"""

from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtCore import QRectF, Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor

from .madmap_based_connections import CardConnectionManager
from .madmap_based_nodes import CardVisualNode
from .madmap_based_models import CardTreeNode
from .madmap_based_layout import CardLayoutEngine
from .associative_line_manager import AssociativeLineManager


class CardMindMapScene(QGraphicsScene):
    """
    卡片思维导图场景 - 基于 madmap 的 ProfessionalMindMapScene
    整合 AI 生成、布局等功能
    """
    
    # 定义信号
    card_clicked = pyqtSignal(object)  # 卡片被点击
    jump_to_source_requested = pyqtSignal(object)  # 请求跳转到源文本
    jump_to_note_requested = pyqtSignal(object)  # 请求跳转到笔记
    jump_to_card_requested = pyqtSignal(str)  # 请求跳转到卡片（通过卡片ID）
    
    def __init__(self):
        super().__init__(-2000, -2000, 4000, 4000)
        self.visual_nodes = []
        self.connection_manager = CardConnectionManager()
        self.connection_style = "bezier"  # 默认连线样式
        self.layout_engine = CardLayoutEngine()
        self.current_layout_type = "mind_map"  # 当前布局类型
        self.associative_line_manager = AssociativeLineManager(self)  # 关联线管理器

        # 复制粘贴相关
        self.copied_nodes = []
        
        # 关联线创建模式
        self.is_creating_associative_line = False
        self.associative_line_start_node = None

    def add_visual_node(self, visual_node: CardVisualNode):
        """添加可视化节点"""
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)
        
        # 连接信号
        visual_node.jump_to_source_requested.connect(self._on_jump_to_source_requested)
        visual_node.jump_to_note_requested.connect(self._on_jump_to_note_requested)
        
        # 渲染关联线（如果节点有关联线数据）
        self.associative_line_manager.render_all_lines()

    def set_connection_style(self, style):
        """设置连线样式"""
        self.connection_style = style
        self.update()

    def set_layout_type(self, layout_type):
        """设置布局类型"""
        self.current_layout_type = layout_type
        # 不自动应用布局，需要手动调用 apply_layout()

    def apply_layout(self):
        """应用布局算法（参考 madmap 的 apply_layout）"""
        root_node = self.get_root_node()
        if not root_node:
            return
        
        # 应用布局
        layout_func = getattr(self.layout_engine, self.current_layout_type, None)
        if layout_func:
            layout_func(root_node)
            self.refresh_positions()
            self.update()

    def get_root_node(self):
        """获取根节点"""
        for vn in self.visual_nodes:
            if vn.tree_node.level == 0:
                return vn.tree_node
        if self.visual_nodes:
            return self.visual_nodes[0].tree_node
        return None

    def refresh_positions(self):
        """刷新节点位置"""
        for vn in self.visual_nodes:
            vn.setPos(vn.tree_node.x, vn.tree_node.y)
        # 更新关联线位置
        self.associative_line_manager.update_all_lines()

    def keyPressEvent(self, event):
        """处理键盘事件（参考 madmap）"""
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
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, CardVisualNode)]
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
            visual_node = CardVisualNode(copied_node)
            self.add_visual_node(visual_node)

            # 递归添加子节点
            def add_children(parent_node, parent_visual):
                for child in parent_node.children:
                    child_visual = CardVisualNode(child)
                    self.add_visual_node(child_visual)
                    add_children(child, child_visual)

            add_children(copied_node, visual_node)

        self.update()
        print(f"已粘贴 {len(self.copied_nodes)} 个节点")

    def delete_selected_nodes(self):
        """删除选中的节点"""
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, CardVisualNode)]
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
        """绘制专业连线（参考 madmap）"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制永久连线
        connections = []
        for vn in self.visual_nodes:
            node = vn.tree_node
            for child in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node == child), None)
                if child_vn:
                    connection = self.connection_manager.create_connection(
                        vn, child_vn, self.connection_style
                    )
                    connection.update_path()
                    connections.append(connection)

        # 绘制所有永久连线
        for connection in connections:
            connection.draw(painter)
        
        # 更新关联线（关联线由 AssociativeLineItem 自己绘制）
        self.associative_line_manager.update_all_lines()

    def mouseDoubleClickEvent(self, event):
        """空白处双击创建新节点（参考 madmap）"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取点击位置
            scene_pos = event.scenePos()

            # 创建新节点
            new_node = CardTreeNode("新节点", "问题内容", "答案内容", scene_pos.x(), scene_pos.y())

            # 添加到场景
            visual_node = CardVisualNode(new_node)
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
    
    def _on_jump_to_source_requested(self, visual_node):
        """处理跳转到源文本请求"""
        self.jump_to_source_requested.emit(visual_node.tree_node)
    
    def _on_jump_to_note_requested(self, visual_node):
        """处理跳转到笔记请求"""
        self.jump_to_note_requested.emit(visual_node.tree_node)
    
    def find_node_by_id(self, node_id):
        """根据节点ID查找可视化节点"""
        for vn in self.visual_nodes:
            if vn.tree_node.id == node_id:
                return vn
        return None
    
    def jump_to_card(self, node_id):
        """跳转到指定卡片并高亮显示"""
        visual_node = self.find_node_by_id(node_id)
        if visual_node:
            # 清除之前的选择
            self.clearSelection()
            # 选中目标节点
            visual_node.setSelected(True)
            visual_node.setFocus()
            # 如果场景有视图，居中显示
            views = self.views()
            if views:
                views[0].centerOn(visual_node)
            self.update()
            return True
        return False
    
    def add_card_from_ai(self, title, question, answer, source_text="", source_start=-1, source_end=-1):
        """
        从 AI 生成添加卡片
        Args:
            title: 卡片标题
            question: 问题
            answer: 答案
            source_text: 源文本
            source_start: 源文本起始位置
            source_end: 源文本结束位置
        """
        # 创建新节点
        new_node = CardTreeNode(title, question, answer)
        new_node.source_text = source_text
        new_node.source_text_start = source_start
        new_node.source_text_end = source_end
        
        # 如果没有根节点，设置为根节点
        if not any(vn.tree_node.level == 0 for vn in self.visual_nodes):
            new_node.level = 0
            new_node.x = 400
            new_node.y = 300
        else:
            # 添加到根节点下
            root_node = self.get_root_node()
            if root_node:
                root_node.add_child(new_node)
                # 计算位置（临时，布局会调整）
                new_node.x = root_node.x + 300
                new_node.y = root_node.y + len(root_node.children) * 200
        
        # 添加到场景
        visual_node = CardVisualNode(new_node)
        self.add_visual_node(visual_node)
        
        # 应用布局
        self.apply_layout()
        
        # 设置新节点为选中状态
        self.clearSelection()
        visual_node.setSelected(True)
        visual_node.setFocus()
        
        self.update()
        return visual_node

