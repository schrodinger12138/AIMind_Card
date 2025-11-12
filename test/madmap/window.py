"""主窗口定义"""
import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsView, QFileDialog, QComboBox, QLabel
)
from PyQt6.QtGui import QPainter, QKeyEvent
from PyQt6.QtCore import Qt
from scene import ProfessionalMindMapScene
from layout import LayoutEngine
from nodes import VisualNode
from models import TreeNode

class ProfessionalMindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("专业思维导图 - 高级连线演示")
        self.resize(1400, 900)
        self.root_node = None
        self.scene = ProfessionalMindMapScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 专业控制面板
        control = QHBoxLayout()

        # 布局选择
        control.addWidget(QLabel("布局算法:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["mind_map", "logical", "timeline", "fishbone", "auto_arrange"])
        control.addWidget(self.layout_combo)

        # 连线样式选择
        control.addWidget(QLabel("连线样式:"))
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["bezier", "smart", "gradient"])
        self.connection_combo.currentTextChanged.connect(self.change_connection_style)
        control.addWidget(self.connection_combo)

        # 功能按钮
        layout_btn = QPushButton("应用布局")
        layout_btn.clicked.connect(self.apply_layout)
        control.addWidget(layout_btn)

        add_btn = QPushButton("生成示例树")
        add_btn.clicked.connect(self.create_sample_tree)
        control.addWidget(add_btn)

        save_btn = QPushButton("保存 JSON")
        save_btn.clicked.connect(self.save_json)
        control.addWidget(save_btn)

        load_btn = QPushButton("加载 JSON")
        load_btn.clicked.connect(self.load_json)
        control.addWidget(load_btn)

        clear_btn = QPushButton("清空画布")
        clear_btn.clicked.connect(self.clear_canvas)
        control.addWidget(clear_btn)

        # 添加键盘快捷键说明
        help_label = QLabel("快捷键: Enter-子节点 | Tab-同级节点 | Delete-删除 | 双击右键-删除 | Ctrl+A-全选 | Ctrl+C-复制 | Ctrl+V-粘贴")
        control.addWidget(help_label)

        layout.addLayout(control)
        layout.addWidget(self.view)

        # 设置视图属性
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.view.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        """窗口级别的键盘事件处理"""
        # 将键盘事件传递给场景
        self.scene.keyPressEvent(event)

    def change_connection_style(self, style):
        """切换连线样式"""
        self.scene.set_connection_style(style)
        self.scene.update()

    def apply_layout(self):
        """应用布局算法到所有节点（包括用户创建的）"""
        if not self.get_root_node():
            return

        layout_name = self.layout_combo.currentText()
        engine = LayoutEngine
        func = getattr(engine, layout_name, None)
        if func:
            # 获取根节点并应用布局
            root = self.get_root_node()
            func(root)
            self.refresh_scene()

    def get_root_node(self):
        """获取根节点（如果没有明确的根节点，则使用第一个节点）"""
        if self.root_node:
            return self.root_node

        if self.scene.visual_nodes:
            # 查找层级为0的节点作为根节点
            for vn in self.scene.visual_nodes:
                if vn.tree_node.level == 0:
                    self.root_node = vn.tree_node
                    return self.root_node

            # 如果没有层级为0的节点，使用第一个节点作为根节点
            self.root_node = self.scene.visual_nodes[0].tree_node
            return self.root_node

        return None

    def create_sample_tree(self):
        """创建专业示例树"""
        self.root_node = TreeNode("核心主题")
        self.root_node.level = 0

        # 第一级节点
        topics = ["战略规划", "产品设计", "技术架构", "市场营销", "运营管理"]
        for i, topic in enumerate(topics):
            child = TreeNode(topic)
            self.root_node.add_child(child)

            # 第二级节点
            sub_topics = []
            if topic == "战略规划":
                sub_topics = ["市场分析", "竞争策略", "目标设定", "资源分配"]
            elif topic == "产品设计":
                sub_topics = ["用户研究", "功能规划", "原型设计", "用户体验"]
            elif topic == "技术架构":
                sub_topics = ["前端技术", "后端服务", "数据库设计", "部署方案"]
            elif topic == "市场营销":
                sub_topics = ["品牌建设", "渠道策略", "内容营销", "数据分析"]
            else:
                sub_topics = ["流程优化", "团队管理", "绩效评估", "风险控制"]

            for sub_topic in sub_topics:
                sub_child = TreeNode(sub_topic)
                child.add_child(sub_child)

                # 第三级节点（部分节点）
                if sub_topic in ["用户研究", "功能规划", "前端技术", "后端服务"]:
                    details = ["需求收集", "方案评估", "实施计划", "验收标准"]
                    for detail in details[:2]:
                        detail_node = TreeNode(detail)
                        sub_child.add_child(detail_node)

        self.apply_layout()
        self.refresh_scene()

    def refresh_scene(self):
        """刷新场景"""
        self.scene.clear()
        self.scene.visual_nodes.clear()

        def add_visual(node):
            vn = VisualNode(node)
            self.scene.add_visual_node(vn)
            for c in node.children:
                add_visual(c)

        if self.root_node:
            add_visual(self.root_node)
            self.scene.update()

    def save_json(self):
        """保存为JSON文件"""
        root_node = self.get_root_node()
        if not root_node:
            return

        path, _ = QFileDialog.getSaveFileName(self, "保存 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(root_node.to_dict(), f, ensure_ascii=False, indent=2)

    def load_json(self):
        """从JSON文件加载"""
        path, _ = QFileDialog.getOpenFileName(self, "加载 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.root_node = TreeNode.from_dict(data)
            self.calculate_levels(self.root_node)
            self.apply_layout()
            self.refresh_scene()

    def calculate_levels(self, node, level=0):
        """计算节点层级"""
        node.level = level
        for child in node.children:
            self.calculate_levels(child, level + 1)

    def clear_canvas(self):
        """清空画布"""
        self.root_node = None
        self.scene.clear()
        self.scene.visual_nodes.clear()
        self.scene.copied_nodes.clear()