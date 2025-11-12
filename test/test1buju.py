#!/usr/bin/env python3
"""
MindMap/Tree布局演示
支持：
- 节点树数据模型，可序列化 JSON
- 多布局算法: mindMap, logical, timeline, fishbone
- 父子连线绘制
- 节点拖拽 + 自动排列
- 保存/加载 JSON
"""

import sys, json, random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QFileDialog, QComboBox
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QPainter


# -------------------------
# 数据模型
# -------------------------
class TreeNode:
    def __init__(self, title, x=0, y=0):
        self.id = id(self)
        self.title = title
        self.parent = None
        self.children = []
        self.x = x
        self.y = y

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def to_dict(self):
        return {
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["title"], data.get("x",0), data.get("y",0))
        for child_data in data.get("children", []):
            child_node = TreeNode.from_dict(child_data)
            node.add_child(child_node)
        return node


# -------------------------
# 可视化节点
# -------------------------
class VisualNode(QGraphicsRectItem):
    WIDTH = 150
    HEIGHT = 80

    def __init__(self, tree_node: TreeNode):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setBrush(QBrush(QColor(255,255,255)))
        self.setPen(QPen(QColor(100,100,100), 2))

        # 文本
        self.text_item = QGraphicsTextItem(self.tree_node.title, self)
        self.text_item.setFont(QFont("Arial", 10))
        self.text_item.setDefaultTextColor(QColor(0,0,0))
        self.text_item.setPos(10,10)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x() + self.WIDTH/2, self.pos().y() + self.HEIGHT/2)


# -------------------------
# 布局算法
# -------------------------
class LayoutEngine:
    @staticmethod
    def mind_map(root: TreeNode, h_spacing=200, v_spacing=100):
        """左右树形布局"""
        def layout(node, depth=0, y_offset=0):
            node.x = depth * h_spacing
            node.y = y_offset
            child_y = y_offset - v_spacing*(len(node.children)-1)/2
            for c in node.children:
                layout(c, depth+1, child_y)
                child_y += v_spacing
        layout(root)

    @staticmethod
    def logical(root: TreeNode, h_spacing=200, v_spacing=120):
        """自上而下逻辑结构布局"""
        def layout(node, depth=0, x_offset=0):
            node.x = x_offset
            node.y = depth * v_spacing
            child_x = x_offset - (len(node.children)-1)*h_spacing/2
            for c in node.children:
                layout(c, depth+1, child_x)
                child_x += h_spacing
        layout(root)

    @staticmethod
    def timeline(root: TreeNode, h_spacing=200):
        """时间轴布局，横向排列"""
        def layout(node, x_offset=0):
            node.x = x_offset
            node.y = 0
            child_x = x_offset + h_spacing
            for c in node.children:
                layout(c, child_x)
                child_x += h_spacing
        layout(root)

    @staticmethod
    def fishbone(root: TreeNode, h_spacing=200, v_spacing=100):
        """鱼骨图布局"""
        def layout(node, depth=0, y_offset=0):
            node.x = depth*h_spacing
            node.y = y_offset
            for i, c in enumerate(node.children):
                layout(c, depth+1, y_offset + (i - len(node.children)//2)*v_spacing)
        layout(root)


# -------------------------
# 场景 + 绘制连线
# -------------------------
class MindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-1000,-1000,2000,2000)
        self.visual_nodes = []

    def add_visual_node(self, visual_node: VisualNode):
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)

    def drawForeground(self, painter: QPainter, rect):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(70,130,180), 2)
        painter.setPen(pen)
        for vn in self.visual_nodes:
            node = vn.tree_node
            for c in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node==c), None)
                if child_vn:
                    MindMapScene.draw_connection(painter, vn.center_pos(), child_vn.center_pos())

    @staticmethod
    def draw_connection(painter, start, end):
        path = QPainterPath()
        mid_x = (start.x() + end.x())/2
        path.moveTo(start)
        path.lineTo(mid_x, start.y())
        path.lineTo(mid_x, end.y())
        path.lineTo(end)
        painter.drawPath(path)


# -------------------------
# 主窗口
# -------------------------
class MindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python MindMap Demo")
        self.resize(1200, 800)
        self.root_node = None
        self.scene = MindMapScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        control = QHBoxLayout()
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["mind_map","logical","timeline","fishbone"])
        control.addWidget(self.layout_combo)

        add_btn = QPushButton("生成示例树")
        add_btn.clicked.connect(self.create_sample_tree)
        control.addWidget(add_btn)

        save_btn = QPushButton("保存 JSON")
        save_btn.clicked.connect(self.save_json)
        control.addWidget(save_btn)

        load_btn = QPushButton("加载 JSON")
        load_btn.clicked.connect(self.load_json)
        control.addWidget(load_btn)

        layout.addLayout(control)
        layout.addWidget(self.view)

    def create_sample_tree(self):
        # 创建示例树
        self.root_node = TreeNode("根节点")
        for i in range(3):
            child = TreeNode(f"子节点{i+1}")
            self.root_node.add_child(child)
            for j in range(2):
                child.add_child(TreeNode(f"孙节点{i+1}-{j+1}"))
        self.apply_layout()
        self.refresh_scene()

    def apply_layout(self):
        if not self.root_node:
            return
        layout_name = self.layout_combo.currentText()
        engine = LayoutEngine
        getattr(engine, layout_name)(self.root_node)

    def refresh_scene(self):
        self.scene.clear()
        self.scene.visual_nodes.clear()
        def add_visual(node):
            vn = VisualNode(node)
            self.scene.add_visual_node(vn)
            for c in node.children:
                add_visual(c)
        add_visual(self.root_node)

    def save_json(self):
        if not self.root_node:
            return
        path,_ = QFileDialog.getSaveFileName(self,"保存 JSON","","JSON Files (*.json)")
        if path:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(self.root_node.to_dict(), f, ensure_ascii=False, indent=2)

    def load_json(self):
        path,_ = QFileDialog.getOpenFileName(self,"加载 JSON","","JSON Files (*.json)")
        if path:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
            self.root_node = TreeNode.from_dict(data)
            self.apply_layout()
            self.refresh_scene()


# -------------------------
# 主函数
# -------------------------
def main():
    app = QApplication(sys.argv)
    win = MindMapWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
