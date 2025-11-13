"""
增强的连线系统 - 参考 simple-mind-map 实现
支持多种连线风格、自动长度计算、圆角等特性
"""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPen, QColor, QPainter, QPainterPath, QPolygonF, QLinearGradient
from typing import Tuple, Optional, List
import math


class EnhancedConnectionRenderer:
    """增强的连线渲染器 - 参考 simple-mind-map 的实现"""
    
    # 连线风格常量
    LINE_STYLE_STRAIGHT = "straight"  # 直线（折线）
    LINE_STYLE_CURVE = "curve"  # 曲线（贝塞尔）
    LINE_STYLE_DIRECT = "direct"  # 直连（直线）
    LINE_STYLE_BEZIER = "bezier"  # 三次贝塞尔曲线
    
    def __init__(self, line_radius=5, line_width=2.5, line_color=None):
        """
        初始化连线渲染器
        Args:
            line_radius: 连线圆角半径
            line_width: 连线宽度
            line_color: 连线颜色（默认使用渐变）
        """
        self.line_radius = line_radius
        self.line_width = line_width
        self.line_color = line_color or QColor(70, 130, 180, 200)
        self.default_margin_x = 80  # 默认水平间距
        self.default_margin_y = 40  # 默认垂直间距
    
    def render_line(self, painter: QPainter, parent_card, child_card, 
                   style: str = LINE_STYLE_STRAIGHT, 
                   layout_type: str = "mind_map") -> None:
        """
        渲染连线
        Args:
            painter: QPainter对象
            parent_card: 父节点卡片
            child_card: 子节点卡片
            style: 连线风格
            layout_type: 布局类型（mind_map, logical, timeline, fishbone等）
        """
        if style == self.LINE_STYLE_STRAIGHT:
            self._render_straight_line(painter, parent_card, child_card, layout_type)
        elif style == self.LINE_STYLE_CURVE:
            self._render_curve_line(painter, parent_card, child_card, layout_type)
        elif style == self.LINE_STYLE_DIRECT:
            self._render_direct_line(painter, parent_card, child_card)
        elif style == self.LINE_STYLE_BEZIER:
            self._render_bezier_line(painter, parent_card, child_card)
        else:
            # 默认使用直线
            self._render_straight_line(painter, parent_card, child_card, layout_type)
    
    def _render_straight_line(self, painter: QPainter, parent_card, child_card, layout_type: str):
        """渲染直线风格连线（折线，带圆角）"""
        # 获取连接点
        start_point, end_point, direction = self._get_connection_points(
            parent_card, child_card, layout_type
        )
        
        # 创建折线路径（参考 simple-mind-map 的 createFoldLine）
        path_points = self._create_fold_line_points(
            start_point, end_point, direction, layout_type
        )
        
        # 创建路径
        path = self._create_fold_line_path(path_points)
        
        # 设置画笔
        pen = self._create_line_pen()
        painter.setPen(pen)
        
        # 绘制路径
        painter.drawPath(path)
        
        # 绘制箭头
        self._draw_arrow(painter, path_points[-2] if len(path_points) > 1 else start_point, 
                        end_point, direction)
    
    def _render_curve_line(self, painter: QPainter, parent_card, child_card, layout_type: str):
        """渲染曲线风格连线（二次贝塞尔曲线）"""
        start_point, end_point, direction = self._get_connection_points(
            parent_card, child_card, layout_type
        )
        
        # 计算控制点（参考 simple-mind-map 的 quadraticCurvePath）
        control_point = self._calculate_quadratic_control_point(
            start_point, end_point, direction
        )
        
        # 创建路径
        path = QPainterPath()
        path.moveTo(start_point)
        path.quadTo(control_point, end_point)
        
        # 设置画笔
        pen = self._create_line_pen()
        painter.setPen(pen)
        
        # 绘制路径
        painter.drawPath(path)
        
        # 绘制箭头
        self._draw_arrow(painter, control_point, end_point, direction)
    
    def _render_direct_line(self, painter: QPainter, parent_card, child_card):
        """渲染直连风格连线（直线）"""
        start_point, end_point, direction = self._get_connection_points(
            parent_card, child_card, "mind_map"
        )
        
        # 创建直线路径
        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)
        
        # 设置画笔
        pen = self._create_line_pen()
        painter.setPen(pen)
        
        # 绘制路径
        painter.drawPath(path)
        
        # 绘制箭头
        self._draw_arrow(painter, start_point, end_point, direction)
    
    def _render_bezier_line(self, painter: QPainter, parent_card, child_card):
        """渲染三次贝塞尔曲线连线"""
        start_point, end_point, direction = self._get_connection_points(
            parent_card, child_card, "mind_map"
        )
        
        # 计算控制点（参考 simple-mind-map 的 cubicBezierPath）
        control1, control2 = self._calculate_cubic_bezier_control_points(
            start_point, end_point, direction
        )
        
        # 创建路径
        path = QPainterPath()
        path.moveTo(start_point)
        path.cubicTo(control1, control2, end_point)
        
        # 创建渐变画笔
        gradient = QLinearGradient(start_point, end_point)
        gradient.setColorAt(0, QColor(70, 130, 180, 200))
        gradient.setColorAt(1, QColor(100, 180, 255, 200))
        
        pen = QPen(gradient, self.line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # 绘制路径
        painter.drawPath(path)
        
        # 绘制箭头
        self._draw_arrow(painter, control2, end_point, direction)
    
    def _get_connection_points(self, parent_card, child_card, layout_type: str) -> Tuple[QPointF, QPointF, str]:
        """
        获取连接点（参考 simple-mind-map 的逻辑）
        根据布局类型和节点位置智能选择连接点
        确保使用卡片的实际大小和位置
        """
        # 获取卡片的实际边界矩形（考虑场景坐标）
        parent_rect = parent_card.boundingRect()
        child_rect = child_card.boundingRect()
        
        # 获取卡片在场景中的实际位置
        parent_pos = parent_card.pos()
        child_pos = child_card.pos()
        
        # 计算卡片的实际中心点（在场景坐标中）
        parent_center = QPointF(
            parent_pos.x() + parent_rect.width() / 2,
            parent_pos.y() + parent_rect.height() / 2
        )
        child_center = QPointF(
            child_pos.x() + child_rect.width() / 2,
            child_pos.y() + child_rect.height() / 2
        )
        
        # 获取卡片的实际宽度和高度
        parent_width = parent_rect.width()
        parent_height = parent_rect.height()
        child_width = child_rect.width()
        child_height = child_rect.height()
        
        # 根据布局类型选择连接点
        if layout_type == "mind_map":
            # 思维导图：根据左右方向选择连接点
            if child_center.x() > parent_center.x():
                # 子节点在右侧
                start_point = QPointF(
                    parent_pos.x() + parent_width,  # 父节点右边缘
                    parent_center.y()  # 父节点垂直中心
                )
                end_point = QPointF(
                    child_pos.x(),  # 子节点左边缘
                    child_center.y()  # 子节点垂直中心
                )
                direction = "right"
            else:
                # 子节点在左侧
                start_point = QPointF(
                    parent_pos.x(),  # 父节点左边缘
                    parent_center.y()  # 父节点垂直中心
                )
                end_point = QPointF(
                    child_pos.x() + child_width,  # 子节点右边缘
                    child_center.y()  # 子节点垂直中心
                )
                direction = "left"
        elif layout_type == "logical":
            # 逻辑结构图：类似思维导图
            return self._get_connection_points(parent_card, child_card, "mind_map")
        elif layout_type == "timeline":
            # 时间轴：水平连接
            start_point = QPointF(
                parent_pos.x() + parent_width,  # 父节点右边缘
                parent_center.y()  # 父节点垂直中心
            )
            end_point = QPointF(
                child_pos.x(),  # 子节点左边缘
                child_center.y()  # 子节点垂直中心
            )
            direction = "right"
        elif layout_type == "fishbone":
            # 鱼骨图：根据位置选择
            return self._get_connection_points(parent_card, child_card, "mind_map")
        else:
            # 默认：使用最近的连接点（考虑卡片实际大小）
            # 判断子节点相对于父节点的位置
            dx = child_center.x() - parent_center.x()
            dy = child_center.y() - parent_center.y()
            
            if abs(dx) > abs(dy):
                # 水平方向为主
                if dx > 0:
                    # 子节点在右侧
                    start_point = QPointF(parent_pos.x() + parent_width, parent_center.y())
                    end_point = QPointF(child_pos.x(), child_center.y())
                    direction = "right"
                else:
                    # 子节点在左侧
                    start_point = QPointF(parent_pos.x(), parent_center.y())
                    end_point = QPointF(child_pos.x() + child_width, child_center.y())
                    direction = "left"
            else:
                # 垂直方向为主
                if dy > 0:
                    # 子节点在下侧
                    start_point = QPointF(parent_center.x(), parent_pos.y() + parent_height)
                    end_point = QPointF(child_center.x(), child_pos.y())
                    direction = "bottom"
                else:
                    # 子节点在上侧
                    start_point = QPointF(parent_center.x(), parent_pos.y())
                    end_point = QPointF(child_center.x(), child_pos.y() + child_height)
                    direction = "top"
        
        return start_point, end_point, direction
    
    def _create_fold_line_points(self, start: QPointF, end: QPointF, 
                                direction: str, layout_type: str) -> List[QPointF]:
        """
        创建折线点列表（参考 simple-mind-map 的 createFoldLine）
        根据布局类型和方向创建合适的折线路径
        使用固定长度（线的长度不可变）
        """
        # 固定长度参数（不可变）
        FIXED_HORIZONTAL_LENGTH = 80  # 固定水平长度
        FIXED_VERTICAL_LENGTH = 60    # 固定垂直长度
        
        if layout_type == "mind_map":
            # 思维导图：L型折线（固定长度）
            if direction == "right":
                # 向右：先水平（固定长度），再垂直
                mid_x = start.x() + FIXED_HORIZONTAL_LENGTH
                return [
                    start,
                    QPointF(mid_x, start.y()),
                    QPointF(mid_x, end.y()),
                    end
                ]
            else:  # left
                # 向左：先水平（固定长度），再垂直
                mid_x = start.x() - FIXED_HORIZONTAL_LENGTH
                return [
                    start,
                    QPointF(mid_x, start.y()),
                    QPointF(mid_x, end.y()),
                    end
                ]
        elif layout_type == "logical":
            # 逻辑结构图：类似思维导图，但垂直方向为主
            if direction == "bottom":
                # 向下：先垂直（固定长度），再水平
                mid_y = start.y() + FIXED_VERTICAL_LENGTH
                return [
                    start,
                    QPointF(start.x(), mid_y),
                    QPointF(end.x(), mid_y),
                    end
                ]
            else:
                # 其他方向：使用固定长度
                return self._create_fold_line_points(start, end, direction, "mind_map")
        elif layout_type == "timeline":
            # 时间轴：水平直线（固定长度）
            # 计算方向向量
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                # 使用固定长度
                fixed_length = FIXED_HORIZONTAL_LENGTH
                if dx > 0:
                    # 向右
                    fixed_end = QPointF(start.x() + fixed_length, start.y())
                else:
                    # 向左
                    fixed_end = QPointF(start.x() - fixed_length, start.y())
                return [start, fixed_end]
            return [start, end]
        else:
            # 默认：L型折线（固定长度）
            if abs(end.x() - start.x()) > abs(end.y() - start.y()):
                # 水平方向为主
                mid_x = start.x() + (FIXED_HORIZONTAL_LENGTH if end.x() > start.x() else -FIXED_HORIZONTAL_LENGTH)
                return [
                    start,
                    QPointF(mid_x, start.y()),
                    QPointF(mid_x, end.y()),
                    end
                ]
            else:
                # 垂直方向为主
                mid_y = start.y() + (FIXED_VERTICAL_LENGTH if end.y() > start.y() else -FIXED_VERTICAL_LENGTH)
                return [
                    start,
                    QPointF(start.x(), mid_y),
                    QPointF(end.x(), mid_y),
                    end
                ]
    
    def _create_fold_line_path(self, points: List[QPointF]) -> QPainterPath:
        """
        创建带圆角的折线路径（参考 simple-mind-map 的 createFoldLine）
        """
        if len(points) < 2:
            return QPainterPath()
        
        path = QPainterPath()
        path.moveTo(points[0])
        
        # 如果有3个或更多点，最后一个拐角支持圆角
        if len(points) >= 3 and self.line_radius > 0:
            # 计算圆角
            start = points[-3]
            center = points[-2]
            end = points[-1]
            
            # 检查是否在一条直线上
            is_one_line = (
                abs(start.x() - center.x()) < 1 and abs(center.x() - end.x()) < 1
            ) or (
                abs(start.y() - center.y()) < 1 and abs(center.y() - end.y()) < 1
            )
            
            if not is_one_line:
                # 计算圆角点
                c_start = self._compute_new_point(start, center, self.line_radius)
                c_end = self._compute_new_point(end, center, self.line_radius)
                
                # 绘制到圆角起点
                for i in range(1, len(points) - 2):
                    path.lineTo(points[i])
                
                # 绘制圆角
                path.lineTo(c_start)
                path.quadTo(center, c_end)
                path.lineTo(end)
            else:
                # 在一条直线上，不需要圆角
                for i in range(1, len(points)):
                    path.lineTo(points[i])
        else:
            # 少于3个点，直接连接
            for i in range(1, len(points)):
                path.lineTo(points[i])
        
        return path
    
    def _compute_new_point(self, a: QPointF, b: QPointF, radius: float) -> QPointF:
        """
        计算去除圆角大小后的新点（参考 simple-mind-map 的 computeNewPoint）
        """
        # x坐标相同
        if abs(a.x() - b.x()) < 1:
            if b.y() > a.y():
                return QPointF(b.x(), b.y() - radius)
            else:
                return QPointF(b.x(), b.y() + radius)
        # y坐标相同
        elif abs(a.y() - b.y()) < 1:
            if b.x() > a.x():
                return QPointF(b.x() - radius, b.y())
            else:
                return QPointF(b.x() + radius, b.y())
        else:
            # 计算方向向量
            dx = b.x() - a.x()
            dy = b.y() - a.y()
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
                return QPointF(b.x() - dx * radius, b.y() - dy * radius)
            return b
    
    def _calculate_quadratic_control_point(self, start: QPointF, end: QPointF, 
                                           direction: str) -> QPointF:
        """
        计算二次贝塞尔曲线控制点（参考 simple-mind-map 的 quadraticCurvePath）
        """
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        if direction in ["left", "right"]:
            # 水平方向：控制点在x方向偏移
            cx = start.x() + dx * 0.2
            cy = start.y() + dy * 0.8
        else:
            # 垂直方向：控制点在y方向偏移
            cx = start.x() + dx * 0.8
            cy = start.y() + dy * 0.2
        
        return QPointF(cx, cy)
    
    def _calculate_cubic_bezier_control_points(self, start: QPointF, end: QPointF,
                                              direction: str) -> Tuple[QPointF, QPointF]:
        """
        计算三次贝塞尔曲线控制点（参考 simple-mind-map 的 cubicBezierPath）
        """
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        if direction in ["left", "right"]:
            # 水平方向
            cx1 = start.x() + dx / 2
            cy1 = start.y()
            cx2 = cx1
            cy2 = end.y()
        else:
            # 垂直方向
            cx1 = start.x()
            cy1 = start.y() + dy / 2
            cx2 = end.x()
            cy2 = cy1
        
        return QPointF(cx1, cy1), QPointF(cx2, cy2)
    
    def _create_line_pen(self) -> QPen:
        """创建连线画笔"""
        pen = QPen(self.line_color, self.line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return pen
    
    def _draw_arrow(self, painter: QPainter, control_point: QPointF, 
                   end_point: QPointF, direction: str):
        """绘制箭头"""
        # 计算箭头方向
        if direction == "top":
            arrow_dir = QPointF(0, -1)
        elif direction == "right":
            arrow_dir = QPointF(1, 0)
        elif direction == "bottom":
            arrow_dir = QPointF(0, 1)
        elif direction == "left":
            arrow_dir = QPointF(-1, 0)
        else:
            # 根据控制点和终点计算方向
            dx = end_point.x() - control_point.x()
            dy = end_point.y() - control_point.y()
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                arrow_dir = QPointF(dx / length, dy / length)
            else:
                arrow_dir = QPointF(0, 1)
        
        # 箭头大小
        arrow_size = 10
        
        # 计算箭头的三个点
        perpendicular = QPointF(-arrow_dir.y(), arrow_dir.x())
        
        arrow_point1 = QPointF(
            end_point.x() - arrow_size * arrow_dir.x() + arrow_size * 0.4 * perpendicular.x(),
            end_point.y() - arrow_size * arrow_dir.y() + arrow_size * 0.4 * perpendicular.y()
        )
        arrow_point2 = QPointF(
            end_point.x() - arrow_size * arrow_dir.x() - arrow_size * 0.4 * perpendicular.x(),
            end_point.y() - arrow_size * arrow_dir.y() - arrow_size * 0.4 * perpendicular.y()
        )
        
        # 绘制箭头
        arrow = QPolygonF([end_point, arrow_point1, arrow_point2])
        painter.setBrush(self.line_color)
        painter.setPen(QPen(self.line_color, 1))
        painter.drawPolygon(arrow)
    
    def get_margin_x(self, layer_index: int) -> float:
        """
        获取水平间距（参考 simple-mind-map 的 getMarginX）
        """
        if layer_index == 1:
            return self.default_margin_x * 1.2
        else:
            return self.default_margin_x
    
    def get_margin_y(self, layer_index: int) -> float:
        """
        获取垂直间距（参考 simple-mind-map 的 getMarginY）
        """
        return self.default_margin_y

