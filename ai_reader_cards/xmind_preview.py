"""
xmind_preview.py

功能：
- 使用 xmind 库生成一个 sample.xmind（示例结构）
- 从 .xmind 加载并解析树结构
- 在 PyQt6 窗口中用 QGraphicsView 绘制简单树状预览

注意：
- 这只是一个轻量的可视化预览；不是完整 WYSIWYG 编辑器。
- 如果你的环境是 Windows，也可以替换掉打开文件的方式（示例中已做跨平台处理）。
"""

import sys
import os
from collections import defaultdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem
)
from PyQt6.QtCore import QRectF, Qt, QPointF, QUrl
from PyQt6.QtGui import QBrush, QColor, QDesktopServices
import xmind

# ---------- xmind helper functions ----------

def create_sample_xmind(path="sample.xmind"):
    """生成一个简单的 xmind 文件用于演示"""
    wb = xmind.load(path)  # 如果不存在，会创建
    sheet = wb.getPrimarySheet()
    sheet.setTitle("Demo Sheet")
    root = sheet.getRootTopic()
    root.setTitle("Root Node")

    # 添加一些子节点（示例）
    for i in range(3):
        t = root.addSubTopic()
        t.setTitle(f"Branch {i+1}")
        # 每个分支添加子节点
        for j in range(2):
            s = t.addSubTopic()
            s.setTitle(f"Item {i+1}.{j+1}")
    xmind.save(wb, path)
    return path

def topic_get_children(topic):
    """安全地获取子节点（不同 xmind 包可能方法名或返回结构不同，做兼容）"""
    # 常见 API：getSubTopics() / getSubTopic() / getChildren()
    for meth in ("getSubTopics", "getSubTopic", "getChildren", "get_sub_topics"):
        if hasattr(topic, meth):
            children = getattr(topic, meth)()
            # 有的实现返回 dict 或 None，统一为 list
            if children is None:
                return []
            if isinstance(children, dict):
                # dict -> values
                return list(children.values())
            if isinstance(children, (list, tuple)):
                return list(children)
            # else try to iterate
            try:
                return list(children)
            except Exception:
                return []
    # 有的实现用 topic.subTopics
    if hasattr(topic, "subTopics"):
        st = getattr(topic, "subTopics")
        return list(st) if st else []
    return []

def topic_get_title(topic):
    """兼容取 title 的方法名"""
    for meth in ("getTitle", "get_title", "getTopicTitle", "title"):
        if hasattr(topic, meth):
            val = getattr(topic, meth)
            return val() if callable(val) else val
    # 直接访问属性 name/text
    for attr in ("title", "text", "name"):
        if hasattr(topic, attr):
            val = getattr(topic, attr)
            return val() if callable(val) else val
    return "Untitled"

def build_tree_from_topic(topic):
    """把 xmind 的 topic 转成 dict 树结构"""
    node = {"title": topic_get_title(topic), "obj": topic, "children": []}
    for c in topic_get_children(topic):
        node["children"].append(build_tree_from_topic(c))
    return node

# ---------- simple tree layout ----------

def layout_tree(root_node, x_spacing=150, y_spacing=80):
    """
    为每个节点分配 (x, y) 坐标
    简单策略：按层分配 y，横向均匀分布
    返回： dict: node -> QPointF
    """
    levels = defaultdict(list)
    def dfs(n, depth=0):
        levels[depth].append(n)
        for ch in n["children"]:
            dfs(ch, depth+1)
    dfs(root_node, 0)

    positions = {}
    # 对每一层，横向安排
    for depth, nodes in levels.items():
        count = len(nodes)
        # 中心对齐：将 x 从 -w ... +w
        total_width = (count - 1) * x_spacing
        for i, node in enumerate(nodes):
            x = i * x_spacing - total_width / 2
            y = depth * y_spacing
            positions[id(node)] = QPointF(x, y)
    return positions

# ---------- PyQt Graphics ----------

class XMindPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints())  # basic
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.node_items = {}  # id(node) -> rect/text

    def draw_tree(self, root_node):
        self.scene.clear()
        positions = layout_tree(root_node)
        # draw nodes
        for node in collect_nodes(root_node):
            pos = positions.get(id(node), QPointF(0,0))
            # rectangle
            rect = QGraphicsRectItem(QRectF(pos.x()-60, pos.y()-20, 120, 40))
            rect.setBrush(QBrush(QColor(240, 248, 255)))
            rect.setPen(Qt.GlobalColor.black)
            text = QGraphicsTextItem(node["title"])
            text.setTextWidth(110)
            text.setPos(pos.x()-55, pos.y()-18)
            self.scene.addItem(rect)
            self.scene.addItem(text)
            self.node_items[id(node)] = (rect, text)
        # draw lines
        def draw_lines(parent):
            for ch in parent["children"]:
                p = positions.get(id(parent), QPointF(0,0))
                c = positions.get(id(ch), QPointF(0,0))
                # simple straight line
                self.scene.addLine(p.x(), p.y()+20, c.x(), c.y()-20)
                draw_lines(ch)
        draw_lines(root_node)
        # adjust scene rect
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

def collect_nodes(root):
    out = []
    def dfs(n):
        out.append(n)
        for ch in n["children"]:
            dfs(ch)
    dfs(root)
    return out

# ---------- Main Window ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XMind PyQt Preview Demo")
        self.resize(900, 600)

        central = QWidget()
        vbox = QVBoxLayout()

        btn_create = QPushButton("Create sample.xmind")
        btn_create.clicked.connect(self.on_create)
        btn_load = QPushButton("Load .xmind and Preview")
        btn_load.clicked.connect(self.on_load)
        btn_open = QPushButton("Open sample.xmind with system default app")
        btn_open.clicked.connect(self.on_open_file)

        vbox.addWidget(btn_create)
        vbox.addWidget(btn_load)
        vbox.addWidget(btn_open)

        self.preview = XMindPreviewWidget()
        vbox.addWidget(self.preview)

        central.setLayout(vbox)
        self.setCentralWidget(central)

        # default path
        self.xmind_path = os.path.abspath("sample.xmind")

    def on_create(self):
        path = create_sample_xmind(self.xmind_path)
        self.statusBar().showMessage(f"Created: {path}")

    def on_load(self):
        # allow user to choose file
        p, _ = QFileDialog.getOpenFileName(self, "Open .xmind", os.getcwd(), "XMind files (*.xmind)")
        if not p:
            return
        try:
            wb = xmind.load(p)
            sheet = wb.getPrimarySheet()
            root = sheet.getRootTopic()
            tree = build_tree_from_topic(root)
            self.preview.draw_tree(tree)
            self.statusBar().showMessage(f"Loaded and rendered: {p}")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading xmind: {e}")

    def on_open_file(self):
        if os.path.exists(self.xmind_path):
            url = QUrl.fromLocalFile(self.xmind_path)
            QDesktopServices.openUrl(url)  # cross platform open with default app
        else:
            self.statusBar().showMessage("sample.xmind not found. Create it first.")

# ---------- run ----------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
