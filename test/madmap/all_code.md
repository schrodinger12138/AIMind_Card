# 合并的 Python 代码文件

# 文件路径: connections.py
```python
"""专业连线管理器"""
import math
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath, QPainter, QPen, QBrush, QColor, QLinearGradient, QRadialGradient
from PyQt6.QtCore import Qt

class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.animation_enabled = True

    def create_connection(self, parent_node, child_node, connection_type="bezier"):
        """创建专业连线"""
        if connection_type == "bezier":
            return BezierConnection(parent_node, child_node)
        elif connection_type == "smart":
            return SmartConnection(parent_node, child_node)
        elif connection_type == "gradient":
            return GradientConnection(parent_node, child_node)
        else:
            return BezierConnection(parent_node, child_node)

    def update_all_connections(self):
        """更新所有连线"""
        for connection in self.connections:
            connection.update_path()


class ProfessionalConnection:
    """专业连线基类"""
    def __init__(self, parent_node, child_node):
        self.parent_node = parent_node
        self.child_node = child_node
        self.path = QPainterPath()
        self.animation = None

    def get_connection_points(self):
        """计算连接点位置"""
        parent_center = self.parent_node.center_pos() if hasattr(self.parent_node, "center_pos") else QPointF(
            self.parent_node.pos().x(), self.parent_node.pos().y()
        )
        child_center = self.child_node.center_pos() if hasattr(self.child_node, "center_pos") else QPointF(
            self.child_node.pos().x(), self.child_node.pos().y()
        )

        # 获取宽高
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

        # 计算连接点
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

    def get_connection_points_with_offset(self, start_offset=0, end_offset=0):
        """获取带偏移的连接点位置，用于临时连线"""
        start, end = self.get_connection_points()

        # 计算方向向量
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.sqrt(dx * dx + dy * dy)

        if length > 0:
            # 标准化方向向量
            dx /= length
            dy /= length

            # 应用偏移
            start = QPointF(start.x() + dx * start_offset, start.y() + dy * start_offset)
            end = QPointF(end.x() - dx * end_offset, end.y() - dy * end_offset)

        return start, end

    def update_path(self):
        """更新连线路径 - 子类实现"""
        raise NotImplementedError

    def draw(self, painter: QPainter):
        """绘制连线 - 子类实现"""
        raise NotImplementedError


class BezierConnection(ProfessionalConnection):
    """贝塞尔曲线连线"""
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
        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
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


class SmartConnection(ProfessionalConnection):
    """智能连线（自动避让）"""
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 智能路径：避免直线交叉，添加中间控制点
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2

        # 根据节点层级调整曲线
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
        # 根据层级设置不同颜色
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
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
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


class GradientConnection(ProfessionalConnection):
    """渐变连线"""
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
```

---

# 文件路径: hh.py
```python
import os
import re


def merge_py_to_markdown(root_dir=None, output_filename="all_code.md"):
    """
    合并指定目录及其子目录下的所有 .py 文件为一个 Markdown 文件。
    忽略 test 文件夹及其子目录。
    每个文件会带有路径标识，并以 Markdown 代码块格式包裹。
    """

    if root_dir is None:
        root_dir = os.getcwd()

    output_file = os.path.join(root_dir, output_filename)

    # 检查输出文件是否已存在
    if os.path.exists(output_file):
        print(f"检测到已存在的输出文件: {output_file}")
        choice = input("是否要从该文件回滚到原始文件? (y/N): ").strip().lower()

        if choice in ['y', 'yes']:
            rollback_from_markdown(output_file, root_dir)
            return

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# 合并的 Python 代码文件\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # 过滤掉 test 目录
            if "test111" in dirpath.split(os.sep):
                continue

            for file in filenames:
                if file.endswith(".py"):
                    filepath = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(filepath, root_dir)

                    # 跳过输出文件自身
                    if os.path.abspath(filepath) == os.path.abspath(output_file):
                        continue

                    out.write(f"# 文件路径: {rel_path}\n")
                    out.write("```python\n")
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"# 无法读取文件: {e}\n")
                    out.write("\n```\n\n---\n\n")

    print(f"✅ 所有 .py 文件内容已合并到: {output_file}")


def rollback_from_markdown(markdown_file, root_dir=None):
    """
    从 Markdown 文件回滚到原始 Python 文件
    """
    if root_dir is None:
        root_dir = os.getcwd()

    if not os.path.exists(markdown_file):
        print(f"❌ Markdown 文件不存在: {markdown_file}")
        return

    try:
        with open(markdown_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取 Markdown 文件失败: {e}")
        return

    # 使用正则表达式匹配文件块
    # 模式：以 "# 文件路径: " 开头，然后是代码块
    pattern = r'# 文件路径: (.+?)\n```python\n(.*?)\n```\n\n---\n\n'
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        print("❌ 未找到有效的文件内容")
        return

    restored_count = 0
    for file_path, file_content in matches:
        full_path = os.path.join(root_dir, file_path)

        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file_content.rstrip())  # 移除末尾多余的空行
            print(f"✅ 已恢复: {file_path}")
            restored_count += 1
        except Exception as e:
            print(f"❌ 恢复文件失败 {file_path}: {e}")

    print(f"\n🎉 回滚完成! 共恢复了 {restored_count} 个文件")


if __name__ == "__main__":
    merge_py_to_markdown()
```

---

# 文件路径: layout.py
```python
"""布局算法"""


class LayoutEngine:
    @staticmethod
    def mind_map(root, h_spacing=200, v_spacing=100):
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
    def logical(root, h_spacing=200, v_spacing=120):
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
    def timeline(root, h_spacing=200):
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
    def fishbone(root, h_spacing=200, v_spacing=100):
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

    @staticmethod
    def auto_arrange(root, h_spacing=200, v_spacing=120):
        """自动排列避免重叠"""

        def get_all_nodes(node):
            """获取所有节点"""
            nodes = [node]
            for child in node.children:
                nodes.extend(get_all_nodes(child))
            return nodes

        def check_overlap(node1, node2):
            """检查两个节点是否重叠"""
            return (abs(node1.x - node2.x) < h_spacing and
                    abs(node1.y - node2.y) < v_spacing)

        def adjust_position(node, all_nodes):
            """调整节点位置避免重叠"""
            for other_node in all_nodes:
                if node != other_node and check_overlap(node, other_node):
                    # 如果重叠，向右下方移动
                    node.x += h_spacing * 0.7
                    node.y += v_spacing * 0.7
                    # 递归检查是否还会与其他节点重叠
                    adjust_position(node, all_nodes)
                    break

        # 先应用基本布局
        LayoutEngine.mind_map(root, h_spacing, v_spacing)

        # 获取所有节点并检查重叠
        all_nodes = get_all_nodes(root)
        for node in all_nodes:
            adjust_position(node, all_nodes)
```

---

# 文件路径: main.py
```python
#!/usr/bin/env python3
"""
MindMap/Tree布局演示 - 专业版连线功能（重构版）
功能：
- 模块化代码结构
- 节点防重叠自动排列
- 键盘快捷键操作
- 双击编辑节点
- 空白处创建节点
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter
from window import ProfessionalMindMapWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = ProfessionalMindMapWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

# 文件路径: models.py
```python
"""数据模型定义"""
import json
import uuid


class TreeNode:
    def __init__(self, title, x=0, y=0):
        self.id = str(uuid.uuid4())  # 使用UUID确保唯一性
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

    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["title"], data.get("x", 0), data.get("y", 0))
        node.id = data.get("id", str(uuid.uuid4()))
        for child_data in data.get("children", []):
            child_node = TreeNode.from_dict(child_data)
            node.add_child(child_node)
        return node

    def find_node_by_id(self, node_id):
        """根据ID查找节点"""
        if self.id == node_id:
            return self

        for child in self.children:
            found = child.find_node_by_id(node_id)
            if found:
                return found
        return None

    def get_siblings(self):
        """获取同级节点"""
        if self.parent is None:
            return [self]
        return self.parent.children

    def is_descendant_of(self, node):
        """检查当前节点是否是指定节点的后代"""
        current = self
        while current.parent is not None:
            if current.parent == node:
                return True
            current = current.parent
        return False

    def update_levels(self, new_level=0):
        """递归更新节点层级"""
        self.level = new_level
        for child in self.children:
            child.update_levels(new_level + 1)

    def duplicate(self):
        """复制节点及其子树"""
        new_node = TreeNode(self.title, self.x + 20, self.y + 20)
        new_node.level = self.level

        for child in self.children:
            new_child = child.duplicate()
            new_node.add_child(new_child)

        return new_node
```

---

# 文件路径: nodes.py
```python
"""可视化节点定义"""
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QInputDialog
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QLinearGradient
from models import TreeNode

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
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

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

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 左键双击编辑节点标题
            self.edit_title()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键双击删除节点
            self.delete_node()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def delete_node(self):
        """删除节点"""
        if self.scene():
            self.scene().delete_node(self)

    def edit_title(self):
        """编辑节点标题"""
        new_title, ok = QInputDialog.getText(
            None,
            "编辑节点标题",
            "请输入新标题:",
            text=self.tree_node.title
        )
        if ok and new_title:
            self.tree_node.title = new_title
            self.text_item.setPlainText(new_title)
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
        child_node = TreeNode("新子节点")
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
            sibling_node = TreeNode("新同级节点")
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
```

---

# 文件路径: scene.py
```python
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
```

---

# 文件路径: visual.py
```python
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QPointF

class VisualNode(QGraphicsRectItem):
    WIDTH = 160
    HEIGHT = 90

    def __init__(self, tree_node):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.text_item = QGraphicsTextItem(tree_node.title, self)
        self.text_item.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.text_item.setTextWidth(self.WIDTH - 20)
        self.text_item.setPos(10, 10)
        self.update_style()

    def update_style(self):
        """根据层级设置样式"""
        color_map = [QColor(74,124,89), QColor(49,99,149), QColor(149,99,49), QColor(99,99,99)]
        fill = color_map[min(self.tree_node.level, len(color_map)-1)]
        gradient = QBrush(fill)
        self.setBrush(gradient)
        self.setPen(QPen(QColor(0,0,0), 2))

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update_connections()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x()+self.WIDTH/2, self.pos().y()+self.HEIGHT/2)

```

---

# 文件路径: window.py
```python
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
```

---

