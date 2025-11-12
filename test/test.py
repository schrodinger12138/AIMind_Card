#!/usr/bin/env python3
"""
MindMap/Tree布局演示 - 专业版连线功能（修正版）
功能：
- 节点树数据模型，可序列化 JSON
- 多布局算法: mind_map, logical, timeline, fishbone
- 专业连线绘制：贝塞尔曲线、渐变色彩、智能避让
- 节点拖拽 + 自动排列
- 保存/加载 JSON
"""

import sys
import json
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QFileDialog, QComboBox, QLabel, QSlider, QGraphicsItem
)
from PyQt6.QtCore import Qt, QPointF, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainterPath, QPainter, QLinearGradient, QRadialGradient
)


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
        self.level = 0  # 节点层级

    def add_child(self, node):
        node.parent = self
        node.level = self.level + 1
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
        node = TreeNode(data["title"], data.get("x", 0), data.get("y", 0))
        for child_data in data.get("children", []):
            child_node = TreeNode.from_dict(child_data)
            node.add_child(child_node)
        return node


# -------------------------
# 专业连线管理器
# -------------------------
class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.animation_enabled = True

    def create_connection(self, parent_node, child_node, connection_type="bezier"):
        """创建专业连线（parent_node / child_node 应为 VisualNode 实例）"""
        if connection_type == "bezier":
            return BezierConnection(parent_node, child_node)
        elif connection_type == "smart":
            return SmartConnection(parent_node, child_node)
        elif connection_type == "gradient":
            return GradientConnection(parent_node, child_node)
        else:
            return BezierConnection(parent_node, child_node)

    def update_all_connections(self):
        """更新所有连线（若需要缓存可用）"""
        for connection in self.connections:
            connection.update_path()


# -------------------------
# 专业连线基类
# -------------------------
class ProfessionalConnection:
    def __init__(self, parent_node: QGraphicsRectItem, child_node: QGraphicsRectItem):
        self.parent_node = parent_node
        self.child_node = child_node
        self.path = QPainterPath()
        self.animation = None

    def get_connection_points(self):
        """计算连接点位置（基于 visual node 的 center 与矩形边界）"""
        # 使用 VisualNode 的 center_pos() 方法（若传入的是 VisualNode）
        parent_center = self.parent_node.center_pos() if hasattr(self.parent_node, "center_pos") else QPointF(
            self.parent_node.pos().x(), self.parent_node.pos().y()
        )
        child_center = self.child_node.center_pos() if hasattr(self.child_node, "center_pos") else QPointF(
            self.child_node.pos().x(), self.child_node.pos().y()
        )

        # 获取宽高（支持 VisualNode 常量或取 boundingRect）
        try:
            pw = self.parent_node.WIDTH
            ph = self.parent_node.HEIGHT
        except Exception:
            br = self.parent_node.boundingRect()
            pw, ph = br.width(), br.height()

        try:
            cw = self.child_node.WIDTH
            ch = self.child_node.HEIGHT
        except Exception:
            br2 = self.child_node.boundingRect()
            cw, ch = br2.width(), br2.height()

        dx = child_center.x() - parent_center.x()
        dy = child_center.y() - parent_center.y()

        # 计算连接点（在矩形边界上，简化为水平或垂直方向连接）
        if abs(dx) > abs(dy):  # 水平方向为主
            if dx > 0:  # 子在父右侧
                start = QPointF(parent_center.x() + pw / 2, parent_center.y())
                end = QPointF(child_center.x() - cw / 2, child_center.y())
            else:  # 子在父左侧
                start = QPointF(parent_center.x() - pw / 2, parent_center.y())
                end = QPointF(child_center.x() + cw / 2, child_center.y())
        else:  # 垂直方向为主
            if dy > 0:  # 子在父下方
                start = QPointF(parent_center.x(), parent_center.y() + ph / 2)
                end = QPointF(child_center.x(), child_center.y() - ch / 2)
            else:  # 子在父上方
                start = QPointF(parent_center.x(), parent_center.y() - ph / 2)
                end = QPointF(child_center.x(), child_center.y() + ch / 2)

        return start, end

    def update_path(self):
        """更新连线路径 - 子类实现"""
        raise NotImplementedError

    def draw(self, painter: QPainter):
        """绘制连线 - 子类实现"""
        raise NotImplementedError


# -------------------------
# 贝塞尔曲线连线
# -------------------------
class BezierConnection(ProfessionalConnection):
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)
        self.curve_strength = 0.3

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 计算控制点
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        control1 = QPointF(start.x() + dx * self.curve_strength, start.y())
        control2 = QPointF(end.x() - dx * self.curve_strength, end.y())

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        pen = QPen(QColor(70, 130, 180), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)

        # 绘制箭头
        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            # 计算箭头位置（在路径的末端）
            arrow_size = 12
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            painter.setBrush(QBrush(QColor(70, 130, 180)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


# -------------------------
# 智能连线（自动避让）
# -------------------------
class SmartConnection(ProfessionalConnection):
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 智能路径：避免直线交叉，添加中间控制点
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2

        # 根据节点层级调整曲线（尝试读取 child_node 的 TreeNode 层级）
        curve_offset = 0
        if hasattr(self.child_node, "tree_node"):
            curve_offset = 50 * max(0, (self.child_node.tree_node.level - 1))
        else:
            curve_offset = 50

        control1 = QPointF(mid_x, start.y())
        control2 = QPointF(mid_x, end.y())

        # 如果节点在同一侧，添加偏移避免重叠
        if abs(start.x() - end.x()) < 100:
            control1.setX(control1.x() + curve_offset)
            control2.setX(control2.x() + curve_offset)

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        # 根据层级设置不同颜色（尝试读取 child_node 层级）
        level = 1
        if hasattr(self.child_node, "tree_node"):
            level = max(1, self.child_node.tree_node.level)

        level_colors = [
            QColor(70, 130, 180),  # 第1级
            QColor(65, 105, 225),  # 第2级
            QColor(135, 206, 250),  # 第3级
            QColor(173, 216, 230)  # 第4级
        ]

        color_index = min(level - 1, len(level_colors) - 1)
        pen_color = level_colors[color_index]

        pen = QPen(pen_color, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        # pen.setDashPattern([3.0, 2.0])  # PyQt6 支持 setDashPattern，但也可使用样式
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)

        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        # 复用 Bezier 箭头实现（简化）
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 10
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            painter.setBrush(QBrush(QColor(65, 105, 225)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


# -------------------------
# 渐变连线
# -------------------------
class GradientConnection(ProfessionalConnection):
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 创建平滑的贝塞尔曲线
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        control1 = QPointF(start.x() + dx * 0.5, start.y())
        control2 = QPointF(end.x() - dx * 0.5, end.y())

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        start, end = self.get_connection_points()

        # 创建渐变画笔
        gradient = QLinearGradient(start, end)
        gradient.setColorAt(0, QColor(255, 105, 97))  # 珊瑚红
        gradient.setColorAt(0.5, QColor(255, 180, 128))  # 浅橙色
        gradient.setColorAt(1, QColor(119, 221, 119))  # 浅绿色

        pen = QPen(QBrush(gradient), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)

        # 渐变箭头
        self.draw_gradient_arrow(painter)

    def draw_gradient_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 14
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            # 箭头渐变
            arrow_gradient = QRadialGradient(end, arrow_size)
            arrow_gradient.setColorAt(0, QColor(119, 221, 119))
            arrow_gradient.setColorAt(1, QColor(255, 105, 97))

            painter.setBrush(QBrush(arrow_gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
            painter.drawPath(arrow_path)


# -------------------------
# 场景 + 专业连线绘制
# -------------------------
class ProfessionalMindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-2000, -2000, 4000, 4000)
        self.visual_nodes = []
        self.connection_manager = ConnectionManager()
        self.connection_style = "bezier"  # 默认连线样式

    def add_visual_node(self, visual_node: 'VisualNode'):
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)

    def set_connection_style(self, style):
        """设置连线样式"""
        self.connection_style = style
        self.update()

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """绘制专业连线"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        connections = []
        for vn in self.visual_nodes:
            node = vn.tree_node
            for child in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node == child), None)
                if child_vn:
                    connection = self.connection_manager.create_connection(vn, child_vn, self.connection_style)
                    connection.update_path()
                    connections.append(connection)

        # 绘制所有连线（在前景层）
        for connection in connections:
            connection.draw(painter)


# -------------------------
# 增强的可视化节点
# -------------------------
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

        # 圆角效果（这里仍使用矩形，但可扩展为绘制圆角）
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


# -------------------------
# 布局算法
# -------------------------
class LayoutEngine:
    @staticmethod
    def mind_map(root: TreeNode, h_spacing=200, v_spacing=100):
        """左右树形布局"""

        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            child_y = y_offset - v_spacing * (len(node.children) - 1) / 2
            for c in node.children:
                layout(c, depth + 1, child_y, direction)
                child_y += v_spacing

        # 根节点在中间，左右分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        root.x = 0
        root.y = 0

        # 布局左侧子节点
        left_y = -v_spacing * (len(left_children) - 1) / 2
        for c in left_children:
            layout(c, 1, left_y, -1)  # 向左
            left_y += v_spacing

        # 布局右侧子节点
        right_y = -v_spacing * (len(right_children) - 1) / 2
        for c in right_children:
            layout(c, 1, right_y, 1)  # 向右
            right_y += v_spacing

    @staticmethod
    def logical(root: TreeNode, h_spacing=200, v_spacing=120):
        """自上而下逻辑结构布局"""

        def layout(node, depth=0, x_offset=0):
            node.x = x_offset
            node.y = depth * v_spacing
            if node.children:
                child_x = x_offset - (len(node.children) - 1) * h_spacing / 2
                for c in node.children:
                    layout(c, depth + 1, child_x)
                    child_x += h_spacing

        layout(root)

    @staticmethod
    def timeline(root: TreeNode, h_spacing=200):
        """时间轴布局，横向排列"""

        def layout(node, x_offset=0, y_offset=0):
            node.x = x_offset
            node.y = y_offset
            child_x = x_offset + h_spacing
            for i, c in enumerate(node.children):
                layout(c, child_x, y_offset + (i - len(node.children) // 2) * 100)
                child_x += h_spacing

        layout(root)

    @staticmethod
    def fishbone(root: TreeNode, h_spacing=200, v_spacing=100):
        """鱼骨图布局"""

        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            for i, c in enumerate(node.children):
                layout(c, depth + 1, y_offset + (i - len(node.children) // 2) * v_spacing, direction)

        # 左右对称分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        for c in left_children:
            layout(c, 1, 0, -1)
        for c in right_children:
            layout(c, 1, 0, 1)


# -------------------------
# 主窗口
# -------------------------
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
        self.layout_combo.addItems(["mind_map", "logical", "timeline", "fishbone"])
        control.addWidget(self.layout_combo)

        # 连线样式选择
        control.addWidget(QLabel("连线样式:"))
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["bezier", "smart", "gradient"])
        self.connection_combo.currentTextChanged.connect(self.change_connection_style)
        control.addWidget(self.connection_combo)

        # 功能按钮
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

        layout.addLayout(control)
        layout.addWidget(self.view)

        # 设置视图属性
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def change_connection_style(self, style):
        """切换连线样式"""
        self.scene.set_connection_style(style)
        self.scene.update()

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
                    for detail in details[:2]:  # 只添加前两个细节
                        detail_node = TreeNode(detail)
                        sub_child.add_child(detail_node)

        self.apply_layout()
        self.refresh_scene()

    def apply_layout(self):
        if not self.root_node:
            return
        layout_name = self.layout_combo.currentText()
        engine = LayoutEngine
        # 动态调用布局函数
        func = getattr(engine, layout_name, None)
        if func:
            func(self.root_node)

    def refresh_scene(self):
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
        if not self.root_node:
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.root_node.to_dict(), f, ensure_ascii=False, indent=2)

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "加载 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.root_node = TreeNode.from_dict(data)
            # 重新计算层级
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


# -------------------------
# 主函数
# -------------------------
def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    win = ProfessionalMindMapWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
