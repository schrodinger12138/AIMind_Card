# 文件路径: ai_reader_cards\ui_components\mindmap_panel.py
"""思维导图面板组件"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSpinBox, QColorDialog)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

# 修复导入路径
from ai_reader_cards.card import MindMapScene, MindMapView, KnowledgeCard


class MindMapPanel(QWidget):
    """思维导图面板"""

    link_cards_requested = pyqtSignal()
    unlink_card_requested = pyqtSignal()
    connection_mode_toggled = pyqtSignal(bool)
    delete_connection_requested = pyqtSignal()
    load_cards_requested = pyqtSignal()
    drawing_mode_toggled = pyqtSignal(bool)
    pen_color_changed = pyqtSignal(QColor)
    pen_width_changed = pyqtSignal(int)
    clear_drawings_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mindmap_scene = None
        self.mindmap_view = None
        self.connection_mode_btn = None
        self.drawing_btn = None
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel("🧠 思维导图画布")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        title_layout.addWidget(title)

        hint = QLabel("提示: Ctrl+滚轮缩放 | 中键拖动平移 | 拖动连接点创建连线 | 一个点可连接多个子节点")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        title_layout.addWidget(hint)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 画布上方工具栏：绘画功能和加载卡片
        canvas_toolbar = QHBoxLayout()
        
        # 加载卡片按钮
        load_btn = QPushButton("📁 加载卡片")
        load_btn.clicked.connect(self.load_cards_requested.emit)
        canvas_toolbar.addWidget(load_btn)
        
        # QHBoxLayout没有addSeparator，使用空白标签代替
        spacer_label = QLabel("|")
        spacer_label.setStyleSheet("color: #ccc; padding: 0 5px;")
        canvas_toolbar.addWidget(spacer_label)
        
        # 绘画模式开关
        self.drawing_btn = QPushButton("🎨 绘画模式")
        self.drawing_btn.setCheckable(True)
        self.drawing_btn.toggled.connect(self.drawing_mode_toggled.emit)
        canvas_toolbar.addWidget(self.drawing_btn)

        # 颜色选择
        color_btn = QPushButton("颜色")
        color_btn.clicked.connect(self._choose_pen_color)
        color_btn.setStyleSheet(f"background-color: {self.pen_color.name()};")
        self.color_btn = color_btn
        canvas_toolbar.addWidget(color_btn)

        # 画笔粗细
        canvas_toolbar.addWidget(QLabel("画笔粗细:"))
        self.pen_size_spin = QSpinBox()
        self.pen_size_spin.setRange(1, 20)
        self.pen_size_spin.setValue(self.pen_width)
        self.pen_size_spin.valueChanged.connect(self.pen_width_changed.emit)
        canvas_toolbar.addWidget(self.pen_size_spin)

        # 清除绘画
        clear_drawing_btn = QPushButton("🧹 清除绘画")
        clear_drawing_btn.clicked.connect(self.clear_drawings_requested.emit)
        canvas_toolbar.addWidget(clear_drawing_btn)
        
        canvas_toolbar.addStretch()
        
        layout.addLayout(canvas_toolbar)

        # 思维导图视图
        self.mindmap_scene = MindMapScene()
        self.mindmap_view = MindMapView(self.mindmap_scene)
        layout.addWidget(self.mindmap_view)

        # 画布操作按钮
        canvas_controls = QHBoxLayout()

        # 连接模式切换按钮
        self.connection_mode_btn = QPushButton("🔗 连接模式")
        self.connection_mode_btn.setCheckable(True)
        self.connection_mode_btn.toggled.connect(self.connection_mode_toggled.emit)
        canvas_controls.addWidget(self.connection_mode_btn)

        link_btn = QPushButton("🔗 连接选中卡片")
        link_btn.clicked.connect(self.link_cards_requested.emit)
        canvas_controls.addWidget(link_btn)

        unlink_btn = QPushButton("❌ 取消连接")
        unlink_btn.clicked.connect(self.unlink_card_requested.emit)
        canvas_controls.addWidget(unlink_btn)

        delete_connection_btn = QPushButton("🗑️ 删除连接")
        delete_connection_btn.clicked.connect(self.delete_connection_requested.emit)
        canvas_controls.addWidget(delete_connection_btn)

        canvas_controls.addStretch()
        layout.addLayout(canvas_controls)

    def set_connection_mode(self, enabled):
        """设置连接模式"""
        self.connection_mode_btn.setChecked(enabled)

    def add_card(self, card):
        """添加卡片到场景"""
        self.mindmap_scene.add_card(card)

    def remove_card(self, card):
        """从场景移除卡片"""
        self.mindmap_scene.remove_card(card)

    def get_all_cards(self):
        """获取所有卡片"""
        return self.mindmap_scene.get_all_cards()

    def get_selected_cards(self):
        """获取选中的卡片"""
        selected_items = self.mindmap_scene.selectedItems()
        return [item for item in selected_items if isinstance(item, KnowledgeCard)]

    def clear_canvas(self):
        """清空画布"""
        for card in self.mindmap_scene.get_all_cards()[:]:
            self.mindmap_scene.remove_card(card)

    def update_scene(self):
        """更新场景"""
        self.mindmap_scene.update()

    def set_drawing_mode(self, enabled):
        """设置绘画模式"""
        self.mindmap_scene.set_drawing_mode(enabled)

    def set_pen_color(self, color):
        """设置画笔颜色"""
        self.mindmap_scene.set_pen_color(color)

    def set_pen_width(self, width):
        """设置画笔宽度"""
        self.mindmap_scene.set_pen_width(width)

    def clear_drawings(self):
        """清除所有绘画"""
        self.mindmap_scene.clear_drawings()
    
    def _choose_pen_color(self):
        """选择画笔颜色"""
        color = QColorDialog.getColor(self.pen_color, self, "选择画笔颜色")
        if color.isValid():
            self.pen_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.pen_color_changed.emit(color)
    
    def set_drawing_mode_ui(self, enabled):
        """设置绘画模式UI状态"""
        if self.drawing_btn:
            self.drawing_btn.setChecked(enabled)
    
    def apply_layout(self, layout_name):
        """应用布局算法"""
        from ai_reader_cards.card import LayoutEngine, TreeNode
        
        cards = self.get_all_cards()
        if not cards:
            return
        
        # 找到根节点（没有父节点的卡片）
        root_cards = [card for card in cards if not hasattr(card, 'parent_card') or card.parent_card is None]
        if not root_cards:
            # 如果没有根节点，使用第一个卡片作为根节点
            root_card = cards[0]
        else:
            root_card = root_cards[0]
        
        # 将卡片结构转换为树结构
        def card_to_tree(card, visited=None):
            if visited is None:
                visited = set()
            if card in visited:
                return None
            visited.add(card)
            
            tree_node = TreeNode(card.title_text, card.pos().x(), card.pos().y())
            tree_node.card_ref = card  # 保存卡片引用
            
            # 处理子卡片
            if hasattr(card, 'child_cards') and card.child_cards:
                for child_card in card.child_cards:
                    child_tree = card_to_tree(child_card, visited)
                    if child_tree:
                        tree_node.add_child(child_tree)
            
            return tree_node
        
        root_tree = card_to_tree(root_card)
        if not root_tree:
            return
        
        # 应用布局算法
        engine = LayoutEngine
        layout_func = getattr(engine, layout_name, None)
        if layout_func:
            layout_func(root_tree)
            
            # 如果支持防重叠，应用防重叠算法
            try:
                from ai_reader_cards.card import EnhancedLayoutEngine
                if layout_name == "mind_map":
                    EnhancedLayoutEngine.mind_map_with_overlap_prevention(root_tree)
                elif layout_name == "logical":
                    EnhancedLayoutEngine.logical_with_overlap_prevention(root_tree)
            except ImportError:
                pass  # 如果增强布局不可用，使用基本布局
            
            # 将布局结果应用回卡片
            def apply_tree_to_cards(tree_node):
                if hasattr(tree_node, 'card_ref'):
                    card = tree_node.card_ref
                    card.setPos(tree_node.x, tree_node.y)
                    # 更新卡片的层级信息
                    if hasattr(card, 'level'):
                        card.level = tree_node.level
                for child in tree_node.children:
                    apply_tree_to_cards(child)
            
            apply_tree_to_cards(root_tree)
            
            # 保存状态用于撤销
            if hasattr(self.mindmap_scene, '_save_state_for_undo'):
                self.mindmap_scene._save_state_for_undo(f"应用布局: {layout_name}")
            
            self.update_scene()