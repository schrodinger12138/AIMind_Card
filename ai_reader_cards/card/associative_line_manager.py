"""
关联线管理器 - 实现跨节点关联线功能
参考 Simple Mind Map 的 AssociativeLine 插件
"""

import math
from PyQt6.QtCore import QPointF, pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsTextItem, QInputDialog


class AssociativeLineItem(QGraphicsPathItem):
    """关联线图形项"""
    
    def __init__(self, from_node, to_node, control_points=None, line_text=""):
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        self.control_points = control_points or []
        self.line_text = line_text
        self.is_active = False
        self.text_item = None
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)  # 在节点下方
        
        self.update_path()
        if self.line_text:
            self.create_text_item()
    
    def update_path(self):
        """更新贝塞尔曲线路径"""
        start_point = self.get_connection_point(self.from_node, self.to_node)
        end_point = self.get_connection_point(self.to_node, self.from_node)
        
        # 计算控制点
        if not self.control_points:
            self.control_points = self.compute_default_control_points(
                start_point, end_point
            )
        
        # 创建贝塞尔曲线
        path = QPainterPath()
        path.moveTo(start_point)
        path.cubicTo(
            self.control_points[0],
            self.control_points[1],
            end_point
        )
        
        self.setPath(path)
        
        # 更新文字位置
        if self.text_item:
            self.update_text_position()
    
    def compute_default_control_points(self, start, end):
        """计算默认控制点"""
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # 控制点偏移
        offset_x = abs(dx) * 0.5
        offset_y = abs(dy) * 0.5
        
        cp1 = QPointF(start.x() + offset_x, start.y())
        cp2 = QPointF(end.x() - offset_x, end.y())
        
        return [cp1, cp2]
    
    def get_connection_point(self, node, target_node):
        """获取节点连接点"""
        # 计算节点边缘连接点
        node_center = node.center_pos()
        target_center = target_node.center_pos()
        
        # 计算方向
        dx = target_center.x() - node_center.x()
        dy = target_center.y() - node_center.y()
        
        # 获取节点边界
        node_rect = node.boundingRect()
        node_pos = node.pos()
        
        # 计算连接点（在节点边缘）
        if abs(dx) > abs(dy):
            # 水平方向
            if dx > 0:
                # 右侧
                return QPointF(
                    node_pos.x() + node_rect.width(),
                    node_center.y()
                )
            else:
                # 左侧
                return QPointF(node_pos.x(), node_center.y())
        else:
            # 垂直方向
            if dy > 0:
                # 下方
                return QPointF(
                    node_center.x(),
                    node_pos.y() + node_rect.height()
                )
            else:
                # 上方
                return QPointF(node_center.x(), node_pos.y())
    
    def paint(self, painter, option, widget):
        """绘制关联线"""
        # 虚线样式
        pen = QPen(QColor(100, 100, 100), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([6, 4])
        
        if self.is_active:
            pen.setColor(QColor(70, 130, 180))
            pen.setWidth(3)
        
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
        
        # 绘制箭头
        self.draw_arrow(painter)
        
        # 绘制控制点（如果激活）
        if self.is_active:
            self.draw_control_points(painter)
    
    def draw_arrow(self, painter):
        """绘制箭头"""
        path = self.path()
        if path.elementCount() < 2:
            return
        
        # 获取路径终点
        end_point = path.pointAtPercent(1.0)
        
        # 计算方向
        t = 0.95
        point_before_end = path.pointAtPercent(t)
        direction = end_point - point_before_end
        
        if direction.manhattanLength() == 0:
            return
        
        angle = math.atan2(direction.y(), direction.x())
        
        # 绘制箭头
        arrow_size = 10
        arrow_p1 = QPointF(
            end_point.x() - arrow_size * math.cos(angle - math.pi / 6),
            end_point.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        arrow_p2 = QPointF(
            end_point.x() - arrow_size * math.cos(angle + math.pi / 6),
            end_point.y() - arrow_size * math.sin(angle + math.pi / 6)
        )
        
        arrow_path = QPainterPath()
        arrow_path.moveTo(end_point)
        arrow_path.lineTo(arrow_p1)
        arrow_path.lineTo(arrow_p2)
        arrow_path.closeSubpath()
        
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPath(arrow_path)
    
    def draw_control_points(self, painter):
        """绘制控制点"""
        for cp in self.control_points:
            painter.setBrush(QBrush(QColor(70, 130, 180)))
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(cp, 6, 6)
    
    def create_text_item(self):
        """创建文字项"""
        if not self.line_text:
            return
        
        if self.text_item:
            if self.scene():
                self.scene().removeItem(self.text_item)
        
        self.text_item = QGraphicsTextItem(self.line_text)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        from PyQt6.QtGui import QFont
        self.text_item.setFont(QFont("Microsoft YaHei", 9))
        
        if self.scene():
            self.scene().addItem(self.text_item)
        
        self.update_text_position()
    
    def update_text_position(self):
        """更新文字位置"""
        if not self.text_item:
            return
        
        path = self.path()
        if path.elementCount() < 2:
            return
        
        # 在路径中点绘制文字
        mid_point = path.pointAtPercent(0.5)
        
        # 计算文字位置（垂直于路径）
        t = 0.5
        point_before = path.pointAtPercent(t - 0.01)
        point_after = path.pointAtPercent(t + 0.01)
        direction = point_after - point_before
        
        # 垂直方向
        perp_angle = math.atan2(direction.y(), direction.x()) + math.pi / 2
        
        # 文字偏移
        text_offset = 15
        text_pos = QPointF(
            mid_point.x() + text_offset * math.cos(perp_angle),
            mid_point.y() + text_offset * math.sin(perp_angle)
        )
        
        self.text_item.setPos(text_pos)
    
    def set_text(self, text):
        """设置文字"""
        self.line_text = text
        if text:
            self.create_text_item()
        elif self.text_item:
            if self.scene():
                self.scene().removeItem(self.text_item)
            self.text_item = None
    
    def mouseDoubleClickEvent(self, event):
        """双击编辑文字"""
        if event.button() == Qt.MouseButton.LeftButton:
            text, ok = QInputDialog.getText(
                None, "编辑关联线文字", "输入文字:", text=self.line_text
            )
            if ok:
                self.set_text(text)
                event.accept()
        else:
            super().mouseDoubleClickEvent(event)


class AssociativeLineManager:
    """关联线管理器"""
    
    def __init__(self, scene):
        self.scene = scene
        self.line_list = []  # [(line_item, from_node, to_node), ...]
        self.active_line = None
        self.is_creating_line = False
        self.creating_start_node = None
        self.creating_line_item = None
    
    def create_line(self, from_node, to_node, control_points=None, line_text=""):
        """创建关联线"""
        # 检查是否已存在
        for line_item, fn, tn in self.line_list:
            if (fn == from_node and tn == to_node) or \
               (fn == to_node and tn == from_node):
                return None
        
        # 创建关联线
        line_item = AssociativeLineItem(from_node, to_node, control_points, line_text)
        self.scene.addItem(line_item)
        
        # 保存到列表
        self.line_list.append((line_item, from_node, to_node))
        
        # 更新节点数据
        self._update_node_data(from_node, to_node)
        
        return line_item
    
    def remove_line(self, line_item):
        """删除关联线"""
        for i, (item, fn, tn) in enumerate(self.line_list):
            if item == line_item:
                # 删除文字项
                if item.text_item:
                    self.scene.removeItem(item.text_item)
                self.scene.removeItem(item)
                self.line_list.pop(i)
                self._remove_from_node_data(fn, tn)
                break
    
    def set_active_line(self, line_item):
        """设置激活的关联线"""
        # 取消之前的激活
        if self.active_line:
            self.active_line.is_active = False
            self.active_line.update()
        
        # 设置新的激活
        self.active_line = line_item
        if line_item:
            line_item.is_active = True
            line_item.update()
    
    def start_creating_line(self, from_node):
        """开始创建关联线"""
        self.is_creating_line = True
        self.creating_start_node = from_node
    
    def update_creating_line(self, mouse_pos):
        """更新正在创建的关联线（跟随鼠标）"""
        if not self.is_creating_line or not self.creating_start_node:
            return
        
        # 创建临时连线（可以在场景的 mouseMoveEvent 中调用）
        # 这里暂时不实现，因为需要实时更新，可以在场景中直接绘制临时路径
        pass
    
    def complete_creating_line(self, to_node):
        """完成创建关联线"""
        if not self.is_creating_line or not self.creating_start_node:
            return
        
        if self.creating_start_node == to_node:
            # 不能连接到自身
            self.cancel_creating_line()
            return
        
        # 创建关联线
        self.create_line(self.creating_start_node, to_node)
        self.cancel_creating_line()
    
    def cancel_creating_line(self):
        """取消创建关联线"""
        if self.creating_line_item:
            self.scene.removeItem(self.creating_line_item)
            self.creating_line_item = None
        self.is_creating_line = False
        self.creating_start_node = None
    
    def _update_node_data(self, from_node, to_node):
        """更新节点数据"""
        # 在CardTreeNode中保存关联线目标
        if hasattr(from_node, 'tree_node'):
            if not hasattr(from_node.tree_node, 'associative_line_targets'):
                from_node.tree_node.associative_line_targets = []
            
            target_id = to_node.tree_node.id
            if target_id not in from_node.tree_node.associative_line_targets:
                from_node.tree_node.associative_line_targets.append(target_id)
    
    def _remove_from_node_data(self, from_node, to_node):
        """从节点数据中移除关联线"""
        if hasattr(from_node, 'tree_node'):
            if hasattr(from_node.tree_node, 'associative_line_targets'):
                target_id = to_node.tree_node.id
                if target_id in from_node.tree_node.associative_line_targets:
                    from_node.tree_node.associative_line_targets.remove(target_id)
    
    def render_all_lines(self):
        """渲染所有关联线"""
        # 清除现有连线
        for line_item, _, _ in self.line_list:
            if line_item.text_item:
                self.scene.removeItem(line_item.text_item)
            self.scene.removeItem(line_item)
        self.line_list.clear()
        
        # 重新创建所有关联线
        for vn in self.scene.visual_nodes:
            if hasattr(vn.tree_node, 'associative_line_targets'):
                for target_id in vn.tree_node.associative_line_targets:
                    target_vn = self.scene.find_node_by_id(target_id)
                    if target_vn:
                        self.create_line(vn, target_vn)
    
    def update_all_lines(self):
        """更新所有关联线路径"""
        for line_item, _, _ in self.line_list:
            line_item.update_path()

