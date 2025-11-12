"""专业连线管理器 - 从 madmap 集成"""
import math
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath, QPainter, QPen, QBrush, QColor, QLinearGradient, QRadialGradient
from PyQt6.QtCore import Qt


class ConnectionManager:
    """连线管理器"""
    
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
            try:
                pw = self.parent_node.CARD_WIDTH
                ph = self.parent_node.CARD_HEIGHT
            except Exception:
                try:
                    br = self.parent_node.boundingRect()
                    pw, ph = br.width(), br.height()
                except:
                    pw, ph = 280, 180  # KnowledgeCard 默认尺寸

        try:
            cw = self.child_node.WIDTH
            ch = self.child_node.HEIGHT
        except Exception:
            try:
                cw = self.child_node.CARD_WIDTH
                ch = self.child_node.CARD_HEIGHT
            except Exception:
                try:
                    br2 = self.child_node.boundingRect()
                    cw, ch = br2.width(), br2.height()
                except:
                    cw, ch = 280, 180  # KnowledgeCard 默认尺寸

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

