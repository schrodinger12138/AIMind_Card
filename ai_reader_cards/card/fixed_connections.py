"""固定长度连线系统 - 参考思维导图连线方式"""
import math
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath, QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt


class FixedLengthConnection:
    """固定长度连线 - 思维导图风格"""
    
    def __init__(self, parent_node, child_node, layout_type="mind_map"):
        self.parent_node = parent_node
        self.child_node = child_node
        self.layout_type = layout_type
        self.path = QPainterPath()
        
        # 固定长度参数（不可变，参考madmap要求）
        self.base_horizontal_length = 80  # 固定水平线段长度（不可变）
        self.base_vertical_length = 60     # 固定垂直线段长度（不可变）
        self.auto_calculate_length = False  # 不使用自动计算，使用固定长度
        
    def update_path(self):
        """更新连线路径 - 根据布局类型自动计算连线长度"""
        parent_center = self.parent_node.get_center_pos() if hasattr(self.parent_node, "get_center_pos") else (
            self.parent_node.center_pos() if hasattr(self.parent_node, "center_pos") else QPointF(
                self.parent_node.pos().x(), self.parent_node.pos().y()
            )
        )
        child_center = self.child_node.get_center_pos() if hasattr(self.child_node, "get_center_pos") else (
            self.child_node.center_pos() if hasattr(self.child_node, "center_pos") else QPointF(
                self.child_node.pos().x(), self.child_node.pos().y()
            )
        )
        
        # 获取卡片尺寸
        try:
            pw = self.parent_node.CARD_WIDTH
            ph = self.parent_node.CARD_HEIGHT
        except:
            try:
                br = self.parent_node.boundingRect()
                pw, ph = br.width(), br.height()
            except:
                pw, ph = 280, 180
        
        try:
            cw = self.child_node.CARD_WIDTH
            ch = self.child_node.CARD_HEIGHT
        except:
            try:
                br2 = self.child_node.boundingRect()
                cw, ch = br2.width(), br2.height()
            except:
                cw, ch = 280, 180
        
        # 根据布局类型选择连线方式
        if self.layout_type == "mind_map" or self.layout_type == "logical":
            # 左右或上下布局：使用L型连线（固定长度）
            self._create_l_shape_connection(parent_center, child_center, pw, ph, cw, ch)
        elif self.layout_type == "timeline":
            # 时间轴布局：水平连线
            self._create_horizontal_connection(parent_center, child_center, pw, ph, cw, ch)
        else:
            # 默认：L型连线
            self._create_l_shape_connection(parent_center, child_center, pw, ph, cw, ch)
    
    def _create_l_shape_connection(self, parent_center, child_center, pw, ph, cw, ch):
        """创建L型连线（自动计算长度）"""
        dx = child_center.x() - parent_center.x()
        dy = child_center.y() - parent_center.y()
        
        # 使用固定长度（不可变，参考madmap要求）
        self.horizontal_length = self.base_horizontal_length
        self.vertical_length = self.base_vertical_length
        
        # 判断主要方向
        if abs(dx) > abs(dy):
            # 水平方向为主
            if dx > 0:
                # 子在父右侧
                start = QPointF(parent_center.x() + pw / 2, parent_center.y())
                end = QPointF(child_center.x() - cw / 2, child_center.y())
                
                # L型：先水平（固定长度），后垂直
                # 使用固定长度（不可变）
                mid_x = start.x() + self.horizontal_length
                mid_y = end.y()
                
                self.path = QPainterPath()
                self.path.moveTo(start)
                self.path.lineTo(mid_x, start.y())  # 水平线段（固定长度）
                self.path.lineTo(mid_x, mid_y)     # 垂直线段
                self.path.lineTo(end)               # 水平线段到终点
            else:
                # 子在父左侧
                start = QPointF(parent_center.x() - pw / 2, parent_center.y())
                end = QPointF(child_center.x() + cw / 2, child_center.y())
                
                # 使用固定长度（不可变）
                mid_x = start.x() - self.horizontal_length
                mid_y = end.y()
                
                self.path = QPainterPath()
                self.path.moveTo(start)
                self.path.lineTo(mid_x, start.y())  # 水平线段（固定长度）
                self.path.lineTo(mid_x, mid_y)     # 垂直线段
                self.path.lineTo(end)               # 水平线段到终点
        else:
            # 垂直方向为主
            if dy > 0:
                # 子在父下方
                start = QPointF(parent_center.x(), parent_center.y() + ph / 2)
                end = QPointF(child_center.x(), child_center.y() - ch / 2)
                
                # L型：先垂直（固定长度），后水平
                # 使用固定长度（不可变）
                mid_x = end.x()
                mid_y = start.y() + self.vertical_length
                
                self.path = QPainterPath()
                self.path.moveTo(start)
                self.path.lineTo(start.x(), mid_y)  # 垂直线段（固定长度）
                self.path.lineTo(mid_x, mid_y)     # 水平线段
                self.path.lineTo(end)               # 垂直线段到终点
            else:
                # 子在父上方
                start = QPointF(parent_center.x(), parent_center.y() - ph / 2)
                end = QPointF(child_center.x(), child_center.y() + ch / 2)
                
                # 使用固定长度（不可变）
                mid_x = end.x()
                mid_y = start.y() - self.vertical_length
                
                self.path = QPainterPath()
                self.path.moveTo(start)
                self.path.lineTo(start.x(), mid_y)  # 垂直线段（固定长度）
                self.path.lineTo(mid_x, mid_y)     # 水平线段
                self.path.lineTo(end)               # 垂直线段到终点
    
    def _create_horizontal_connection(self, parent_center, child_center, pw, ph, cw, ch):
        """创建水平连线（时间轴布局）- 使用固定长度"""
        start = QPointF(parent_center.x() + pw / 2, parent_center.y())
        # 使用固定长度，而不是直接连接到终点
        end = QPointF(start.x() + self.horizontal_length, start.y())
        
        self.path = QPainterPath()
        self.path.moveTo(start)
        self.path.lineTo(end)  # 固定长度水平线
    
    def draw(self, painter: QPainter):
        """绘制连线"""
        # 根据层级设置颜色
        level = 1
        if hasattr(self.child_node, "level"):
            level = max(1, self.child_node.level)
        
        level_colors = [
            QColor(70, 130, 180),   # 第1级 - 蓝色
            QColor(65, 105, 225),   # 第2级 - 深蓝色
            QColor(135, 206, 250),  # 第3级 - 浅蓝色
            QColor(173, 216, 230)   # 第4级 - 更浅的蓝色
        ]
        
        color_index = min(level - 1, len(level_colors) - 1)
        pen_color = level_colors[color_index]
        
        pen = QPen(pen_color, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        
        # 绘制箭头
        self.draw_arrow(painter)
    
    def draw_arrow(self, painter: QPainter):
        """绘制箭头"""
        # 获取路径的最后一个点作为箭头位置
        if self.path.elementCount() > 0:
            # 获取最后两个点来确定方向
            last_point = QPointF(
                self.path.elementAt(self.path.elementCount() - 1).x,
                self.path.elementAt(self.path.elementCount() - 1).y
            )
            
            if self.path.elementCount() >= 2:
                prev_point = QPointF(
                    self.path.elementAt(self.path.elementCount() - 2).x,
                    self.path.elementAt(self.path.elementCount() - 2).y
                )
                
                direction = last_point - prev_point
                if direction.manhattanLength() > 0:
                    arrow_size = 10
                    angle = math.atan2(direction.y(), direction.x())
                    
                    arrow_p1 = QPointF(
                        last_point.x() - arrow_size * math.cos(angle - math.pi / 6),
                        last_point.y() - arrow_size * math.sin(angle - math.pi / 6)
                    )
                    arrow_p2 = QPointF(
                        last_point.x() - arrow_size * math.cos(angle + math.pi / 6),
                        last_point.y() - arrow_size * math.sin(angle + math.pi / 6)
                    )
                    
                    arrow_path = QPainterPath()
                    arrow_path.moveTo(last_point)
                    arrow_path.lineTo(arrow_p1)
                    arrow_path.lineTo(arrow_p2)
                    arrow_path.closeSubpath()
                    
                    painter.setBrush(QBrush(QColor(70, 130, 180)))
                    painter.setPen(QPen(Qt.PenStyle.NoPen))
                    painter.drawPath(arrow_path)


class FixedConnectionManager:
    """固定长度连线管理器"""
    
    def __init__(self):
        self.layout_type = "mind_map"
    
    def set_layout_type(self, layout_type):
        """设置布局类型"""
        self.layout_type = layout_type
    
    def create_connection(self, parent_node, child_node):
        """创建固定长度连线"""
        return FixedLengthConnection(parent_node, child_node, self.layout_type)

