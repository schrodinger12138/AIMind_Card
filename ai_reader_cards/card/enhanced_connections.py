"""
增强的连线样式 - 手绘风格、彩虹线条、流动动画
参考 Simple Mind Map 的连线样式
"""

import math
import random
from PyQt6.QtCore import QPointF, QPropertyAnimation, QEasingCurve, Qt, QTimer
from PyQt6.QtGui import QPainterPath, QPainter, QPen, QBrush, QColor, QLinearGradient, QConicalGradient
from .madmap_based_connections import ProfessionalConnection


class HandDrawnConnection(ProfessionalConnection):
    """手绘风格连线 - 添加随机抖动"""
    
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)
        self.jitter_amount = 3  # 抖动幅度
    
    def update_path(self):
        """更新路径，添加手绘抖动效果"""
        start, end = self.get_connection_points()
        
        # 计算控制点
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # 添加随机抖动
        cp1_x = start.x() + dx * 0.3 + random.uniform(-self.jitter_amount, self.jitter_amount)
        cp1_y = start.y() + dy * 0.3 + random.uniform(-self.jitter_amount, self.jitter_amount)
        cp2_x = start.x() + dx * 0.7 + random.uniform(-self.jitter_amount, self.jitter_amount)
        cp2_y = start.y() + dy * 0.7 + random.uniform(-self.jitter_amount, self.jitter_amount)
        
        # 创建贝塞尔曲线，使用多个控制点模拟手绘效果
        path = QPainterPath()
        path.moveTo(start)
        
        # 使用多个小段模拟手绘
        num_segments = 10
        for i in range(1, num_segments + 1):
            t = i / num_segments
            # 贝塞尔曲线上的点
            x = (1-t)**3 * start.x() + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end.x()
            y = (1-t)**3 * start.y() + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end.y()
            # 添加小抖动
            x += random.uniform(-self.jitter_amount * 0.5, self.jitter_amount * 0.5)
            y += random.uniform(-self.jitter_amount * 0.5, self.jitter_amount * 0.5)
            path.lineTo(QPointF(x, y))
        
        self.path = path
    
    def draw(self, painter):
        """绘制手绘风格连线"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(100, 100, 100), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        # 绘制箭头（父节点 -> 子节点）
        self.draw_arrow(painter)
    
    def draw_arrow(self, painter):
        """绘制箭头（父节点 -> 子节点）"""
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
            
            painter.setBrush(QBrush(QColor(100, 100, 100)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


class RainbowConnection(ProfessionalConnection):
    """彩虹线条 - 使用渐变颜色"""
    
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)
        self.colors = [
            QColor(255, 0, 0),    # 红
            QColor(255, 127, 0),  # 橙
            QColor(255, 255, 0),  # 黄
            QColor(0, 255, 0),    # 绿
            QColor(0, 0, 255),    # 蓝
            QColor(75, 0, 130),   # 靛
            QColor(148, 0, 211),  # 紫
        ]
    
    def update_path(self):
        """更新路径"""
        start, end = self.get_connection_points()
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        cp1 = QPointF(start.x() + dx * 0.3, start.y() + dy * 0.3)
        cp2 = QPointF(start.x() + dx * 0.7, start.y() + dy * 0.7)
        
        path = QPainterPath()
        path.moveTo(start)
        path.cubicTo(cp1, cp2, end)
        
        self.path = path
    
    def draw(self, painter):
        """绘制彩虹线条"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 创建线性渐变
        start, end = self.get_connection_points()
        gradient = QLinearGradient(start, end)
        
        # 根据路径长度分段着色
        num_colors = len(self.colors)
        for i, color in enumerate(self.colors):
            stop = i / (num_colors - 1) if num_colors > 1 else 0
            gradient.setColorAt(stop, color)
        
        pen = QPen(gradient, 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        # 绘制箭头（父节点 -> 子节点）
        self.draw_arrow(painter)
    
    def draw_arrow(self, painter):
        """绘制箭头（父节点 -> 子节点）"""
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
            
            # 使用渐变色填充箭头
            arrow_gradient = QLinearGradient(end, arrow_p1)
            arrow_gradient.setColorAt(0, self.colors[-1])  # 紫色
            arrow_gradient.setColorAt(1, self.colors[0])  # 红色
            painter.setBrush(QBrush(arrow_gradient))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


class AnimatedConnection(ProfessionalConnection):
    """带动画的连线 - 流动效果"""
    
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)
        self.dash_offset = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(50)  # 每50ms更新一次
        self.animation_speed = 2  # 动画速度
    
    def _update_animation(self):
        """更新动画"""
        self.dash_offset += self.animation_speed
        if self.dash_offset > 20:
            self.dash_offset = 0
    
    def update_path(self):
        """更新路径"""
        start, end = self.get_connection_points()
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        cp1 = QPointF(start.x() + dx * 0.3, start.y() + dy * 0.3)
        cp2 = QPointF(start.x() + dx * 0.7, start.y() + dy * 0.7)
        
        path = QPainterPath()
        path.moveTo(start)
        path.cubicTo(cp1, cp2, end)
        
        self.path = path
    
    def draw(self, painter):
        """绘制带动画的连线"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor(70, 130, 180), 3)
        pen.setDashPattern([10, 5])
        pen.setDashOffset(self.dash_offset)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        # 绘制箭头（父节点 -> 子节点）
        self.draw_arrow(painter)
    
    def draw_arrow(self, painter):
        """绘制箭头（父节点 -> 子节点）"""
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
            
            painter.setBrush(QBrush(QColor(70, 130, 180)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)
    
    def stop_animation(self):
        """停止动画"""
        if self.animation_timer:
            self.animation_timer.stop()
