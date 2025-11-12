"""思维导图模块 - 管理卡片画布与连线"""

import xmind
from xmind.core.const import TOPIC_DETACHED
from xmind.core.markerref import MarkerId

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (QPen, QColor, QPainter, QPainterPath,
                         QPolygonF, QTransform, QLinearGradient)

# 修复：添加正确的导入
from ai_reader_cards.card import KnowledgeCard


class ConnectionLine:
    """连接线类"""

    def __init__(self, from_card, from_direction, to_card, to_direction):
        self.from_card = from_card
        self.from_direction = from_direction
        self.to_card = to_card
        self.to_direction = to_direction

    def get_points(self):
        """获取连接的起点和终点"""
        from_point = self.from_card.get_connection_point(self.from_direction)
        to_point = self.to_card.get_connection_point(self.to_direction)
        return from_point, to_point

class CardSearchTool:
    """卡片搜索工具类"""

    def __init__(self, scene):
        self.scene = scene
        self.search_results = []
        self.current_result_index = -1
        self.original_styles = {}  # 保存原始样式

    def search(self, keyword, search_fields=None):
        """搜索卡片
        Args:
            keyword: 搜索关键词
            search_fields: 搜索字段列表，如 ['title', 'question', 'answer']
        """
        if not keyword:
            return []

        if search_fields is None:
            search_fields = ['title', 'question', 'answer']

        # 恢复之前的结果样式
        self.clear_highlights()

        self.search_results = []
        keyword_lower = keyword.lower()

        for card in self.scene.cards:
            matched = False
            match_data = {}

            # 检查各个字段
            for field in search_fields:
                if hasattr(card, f'{field}_text'):
                    text = getattr(card, f'{field}_text', '').lower()
                    if keyword_lower in text:
                        matched = True
                        match_data[field] = {
                            'text': getattr(card, f'{field}_text', ''),
                            'positions': self._find_match_positions(text, keyword_lower)
                        }

            if matched:
                self.search_results.append((card, match_data))
                # 保存原始样式
                self._save_original_style(card)

        # 高亮显示结果
        self._highlight_results()
        return self.search_results

    def _find_match_positions(self, text, keyword):
        """查找匹配位置"""
        positions = []
        start = 0
        text_lower = text.lower()

        while True:
            pos = text_lower.find(keyword, start)
            if pos == -1:
                break
            positions.append((pos, pos + len(keyword)))
            start = pos + 1

        return positions

    def _save_original_style(self, card):
        """保存卡片原始样式"""
        if card not in self.original_styles:
            self.original_styles[card] = {
                'pen': card.pen(),
                'brush': card.brush(),
                'z_value': card.zValue()
            }

    def _highlight_results(self):
        """高亮显示搜索结果"""
        for card, _ in self.search_results:
            # 设置高亮样式
            highlight_pen = QPen(QColor(255, 215, 0), 3)  # 金色边框
            card.setPen(highlight_pen)
            card.setZValue(100)  # 置于顶层

    def clear_highlights(self):
        """清除高亮显示"""
        for card, original_style in self.original_styles.items():
            card.setPen(original_style['pen'])
            card.setBrush(original_style['brush'])
            card.setZValue(original_style['z_value'])

        self.original_styles.clear()
        self.search_results.clear()
        self.current_result_index = -1

    def navigate_to_next(self):
        """导航到下一个结果"""
        if not self.search_results:
            return None

        self.current_result_index = (self.current_result_index + 1) % len(self.search_results)
        return self._focus_current_result()

    def navigate_to_previous(self):
        """导航到上一个结果"""
        if not self.search_results:
            return None

        self.current_result_index = (self.current_result_index - 1) % len(self.search_results)
        return self._focus_current_result()

    def _focus_current_result(self):
        """聚焦当前结果"""
        if 0 <= self.current_result_index < len(self.search_results):
            card, match_data = self.search_results[self.current_result_index]

            # 确保卡片可见
            if self.scene.views():
                view = self.scene.views()[0]
                view.centerOn(card)

            return card, match_data, self.current_result_index + 1, len(self.search_results)
        return None
class CardAlignmentTool:
    """卡片对齐工具类"""

    @staticmethod
    def align_left(cards):
        """左对齐"""
        if not cards or len(cards) < 2:
            return
        min_x = min(card.scenePos().x() for card in cards)
        for card in cards:
            card.setPos(min_x, card.scenePos().y())

    @staticmethod
    def align_right(cards):
        """右对齐"""
        if not cards or len(cards) < 2:
            return
        max_x = max(card.scenePos().x() + card.CARD_WIDTH for card in cards)
        for card in cards:
            card.setPos(max_x - card.CARD_WIDTH, card.scenePos().y())

    @staticmethod
    def align_top(cards):
        """顶对齐"""
        if not cards or len(cards) < 2:
            return
        min_y = min(card.scenePos().y() for card in cards)
        for card in cards:
            card.setPos(card.scenePos().x(), min_y)

    @staticmethod
    def align_bottom(cards):
        """底对齐"""
        if not cards or len(cards) < 2:
            return
        max_y = max(card.scenePos().y() + card.CARD_HEIGHT for card in cards)
        for card in cards:
            card.setPos(card.scenePos().x(), max_y - card.CARD_HEIGHT)

    @staticmethod
    def align_center_horizontal(cards):
        """水平居中对齐"""
        if not cards or len(cards) < 2:
            return
        center_y = sum(card.scenePos().y() + card.CARD_HEIGHT / 2 for card in cards) / len(cards)
        for card in cards:
            card.setPos(card.scenePos().x(), center_y - card.CARD_HEIGHT / 2)

    @staticmethod
    def align_center_vertical(cards):
        """垂直居中对齐"""
        if not cards or len(cards) < 2:
            return
        center_x = sum(card.scenePos().x() + card.CARD_WIDTH / 2 for card in cards) / len(cards)
        for card in cards:
            card.setPos(center_x - card.CARD_WIDTH / 2, card.scenePos().y())

    @staticmethod
    def distribute_horizontal(cards):
        """水平均匀分布"""
        if not cards or len(cards) < 3:
            return

        cards_sorted = sorted(cards, key=lambda card: card.scenePos().x())
        leftmost = cards_sorted[0].scenePos().x()
        rightmost = cards_sorted[-1].scenePos().x()

        total_width = rightmost - leftmost
        gap = total_width / (len(cards) - 1)

        for i, card in enumerate(cards_sorted):
            new_x = leftmost + i * gap
            card.setPos(new_x, card.scenePos().y())

    @staticmethod
    def distribute_vertical(cards):
        """垂直均匀分布"""
        if not cards or len(cards) < 3:
            return

        cards_sorted = sorted(cards, key=lambda card: card.scenePos().y())
        topmost = cards_sorted[0].scenePos().y()
        bottommost = cards_sorted[-1].scenePos().y()

        total_height = bottommost - topmost
        gap = total_height / (len(cards) - 1)

        for i, card in enumerate(cards_sorted):
            new_y = topmost + i * gap
            card.setPos(card.scenePos().x(), new_y)

    @staticmethod
    def arrange_hierarchy(root_card, horizontal_spacing=200, vertical_spacing=150):
        """按层次结构排列卡片"""
        if not root_card:
            return

        def arrange_subtree(card, start_x, start_y, level):
            """递归排列子树"""
            if not card.child_cards:
                return start_x

            current_x = start_x
            for child in card.child_cards:
                # 设置子卡片位置
                child.setPos(current_x, start_y + level * vertical_spacing)
                # 递归排列子卡片的子树
                current_x = arrange_subtree(child, current_x, start_y, level + 1)
                current_x += horizontal_spacing

            return current_x

        # 从根节点开始排列
        root_card.setPos(0, 0)
        arrange_subtree(root_card, -horizontal_spacing, vertical_spacing, 1)


class MindMapScene(QGraphicsScene):
    """思维导图场景 - 支持绘画功能"""

    # 添加连接相关信号
    connection_started = pyqtSignal(object, str, QPointF)  # 卡片，方向，位置

    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.cards = []
        self.root_card = None  # 根节点卡片

        # 连线相关属性
        self.connecting = False
        self.connection_start_card = None
        self.connection_start_direction = None
        self.temp_connection_line = None
        self.temp_end_point = None

        # 绘画相关属性
        self.drawing = False
        self.last_point = QPointF()
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3
        self.current_path_item = None
        self.drawing_mode = False
        self.drawn_paths = []  # 存储所有绘画路径

        # 修复：正确初始化工具类
        self.alignment_tool = CardAlignmentTool()
        self.search_tool = CardSearchTool(self)

    # 修复：添加缺失的方法
    def start_connection(self, from_card, from_direction, start_point):
        """开始创建连接"""
        self.connecting = True
        self.connection_start_card = from_card
        self.connection_start_direction = from_direction
        self.temp_end_point = start_point

        # 创建临时连线
        pen = QPen(QColor(255, 140, 0), 2, Qt.PenStyle.DashLine)
        self.temp_connection_line = self.addLine(
            start_point.x(), start_point.y(),
            start_point.x(), start_point.y(),
            pen
        )

    def clear_drawings(self):
        """清除所有绘画"""
        # 移除所有绘画路径
        for path in self.drawn_paths:
            self.removeItem(path)
        self.drawn_paths.clear()
        self.update()

    def update_connection(self, end_point):
        """更新临时连接线"""
        if self.connecting and self.temp_connection_line:
            start_point = self.connection_start_card.get_connection_point(
                self.connection_start_direction
            )
            self.temp_connection_line.setLine(
                start_point.x(), start_point.y(),
                end_point.x(), end_point.y()
            )
            self.temp_end_point = end_point

    def finish_connection(self, to_card, to_direction):
        """完成连接创建"""
        if self.connecting and self.connection_start_card and to_card:
            # 检查是否连接到自身
            if self.connection_start_card == to_card:
                self.cancel_connection()
                return False

            # 创建连接
            self.connection_start_card.add_connection(
                self.connection_start_direction,
                to_card,
                to_direction
            )

            # 更新场景
            self.removeItem(self.temp_connection_line)
            self.connecting = False
            self.connection_start_card = None
            self.connection_start_direction = None
            self.temp_connection_line = None
            self.temp_end_point = None

            self.update()
            return True

        self.cancel_connection()
        return False

    def cancel_connection(self):
        """取消连接创建"""
        if self.temp_connection_line:
            self.removeItem(self.temp_connection_line)
        self.connecting = False
        self.connection_start_card = None
        self.connection_start_direction = None
        self.temp_connection_line = None
        self.temp_end_point = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.connecting:
            # 更新临时连接线
            self.update_connection(event.scenePos())
            event.accept()
        elif self.drawing and self.drawing_mode and self.current_path_item is not None:
            current_point = event.scenePos()
            self.current_path.lineTo(current_point)
            self.current_path_item.setPath(self.current_path)
            self.last_point = current_point
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.connecting and event.button() == Qt.MouseButton.LeftButton:
            # 检查是否释放到卡片上
            items = self.items(event.scenePos())
            for item in items:
                if isinstance(item, KnowledgeCard) and item != self.connection_start_card:
                    # 找到最近的连接点
                    direction, point = item.get_nearest_connection_point(
                        self.connection_start_card.get_center_pos()
                    )
                    self.finish_connection(item, direction)
                    event.accept()
                    return

            # 如果没有释放到卡片上，取消连接
            self.cancel_connection()
            event.accept()
        elif self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.current_path_item = None
            self.current_path = None
            event.accept()

        super().mouseReleaseEvent(event)

    # 修复：添加缺失的卡片管理方法
    def add_card(self, card):
        """添加卡片到场景"""
        self.addItem(card)
        self.cards.append(card)

        # 连接卡片的连接信号
        if hasattr(card, 'connection_started'):
            card.connection_started.connect(self.start_connection)

    def remove_card(self, card):
        """从场景移除卡片"""
        if card in self.cards:
            self.cards.remove(card)
        self.removeItem(card)

    def get_all_cards(self):
        """获取所有卡片"""
        return self.cards

    def get_selected_cards(self):
        """获取选中的卡片"""
        return [item for item in self.selectedItems() if isinstance(item, KnowledgeCard)]

    def clear_canvas(self):
        """清空画布"""
        for card in self.cards[:]:
            self.remove_card(card)
        self.cards.clear()

    def export_to_xmind(self, filename):
        """导出到XMind文件"""
        self.workbook = xmind.load(filename)
        self.sheet = self.workbook.getPrimarySheet()
        self.sheet.setTitle("思维导图")

        # 如果有根节点卡片，从根节点开始导出
        if self.root_card:
            root_topic = self.sheet.getRootTopic()
            root_topic.setTitle(self.root_card.get_question())  # 使用问题作为标题

            # 添加答案作为备注
            if self.root_card.get_answer():
                root_topic.setTitle(f"{self.root_card.get_question()}\nA: {self.root_card.get_answer()}")

            # 递归添加子节点
            self._add_card_to_xmind(self.root_card, root_topic)

        # 保存文件
        xmind.save(self.workbook, path=filename)

    def import_from_xmind(self, filename):
        """从XMind文件导入"""
        from ai_reader_cards.card import Card  # 导入Card类

        self.workbook = xmind.load(filename)
        self.sheet = self.workbook.getPrimarySheet()
        root_topic = self.sheet.getRootTopic()

        # 清除现有卡片
        for card in self.cards:
            self.removeItem(card)
        self.cards.clear()

        # 创建根节点卡片
        title = root_topic.getTitle()
        # 分离问题和答案
        if "\nA: " in title:
            question, answer = title.split("\nA: ", 1)
        else:
            question = title
            answer = ""

        self.root_card = Card(question, answer)
        self.root_card.setPos(0, 0)  # 根节点放在中心
        self.addItem(self.root_card)
        self.cards.append(self.root_card)

        # 递归导入子节点
        self._import_topics_from_xmind(root_topic, self.root_card)

    def _add_card_to_xmind(self, card, parent_topic):
        """递归将卡片添加到XMind主题中"""
        # 处理子卡片
        for child_card in card.child_cards:
            sub_topic = parent_topic.addSubTopic()
            sub_topic.setTitle(child_card.get_question())

            # 添加答案作为备注
            if child_card.get_answer():
                sub_topic.setTitle(f"{child_card.get_question()}\nA: {child_card.get_answer()}")

            # 递归处理子节点
            self._add_card_to_xmind(child_card, sub_topic)

    def _import_topics_from_xmind(self, topic, parent_card):
        """递归从XMind主题导入卡片"""
        from ai_reader_cards.card import Card  # 导入Card类

        # 获取子主题
        for sub_topic in topic.getSubTopics():
            title = sub_topic.getTitle()
            # 分离问题和答案
            if "\nA: " in title:
                question, answer = title.split("\nA: ", 1)
            else:
                question = title
                answer = ""

            # 创建新卡片
            child_card = Card(question, answer)

            # 设置卡片位置（相对于父卡片）
            offset_x = len(parent_card.child_cards) * 200  # 水平偏移
            offset_y = 150  # 垂直偏移
            child_card.setPos(parent_card.pos().x() + offset_x,
                            parent_card.pos().y() + offset_y)

            # 添加到场景
            self.addItem(child_card)
            self.cards.append(child_card)

            # 建立父子关系
            parent_card.add_child(child_card)
            child_card.set_parent(parent_card)

            # 递归处理子主题
            self._import_topics_from_xmind(sub_topic, child_card)

    def add_card(self, card):
        """添加卡片到场景"""
        self.addItem(card)
        self.cards.append(card)

    def remove_card(self, card):
        """从场景移除卡片"""
        if card in self.cards:
            self.cards.remove(card)
        self.removeItem(card)

    def get_all_cards(self):
        """获取所有卡片"""
        return self.cards

    def drawBackground(self, painter, rect):
        """绘制网格背景"""
        super().drawBackground(painter, rect)

        # 绘制淡灰色网格
        painter.setPen(QPen(QColor(240, 240, 240), 0.5))

        grid_size = 50
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # 绘制垂直线
        x = left
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += grid_size

        # 绘制水平线
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += grid_size

    def drawForeground(self, painter, rect):
        """绘制前景（连线）"""
        super().drawForeground(painter, rect)

        # 绘制所有父子连线
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for card in self.cards:
            if card.parent_card:
                self._draw_smart_connection(painter, card.parent_card, card)

    def _draw_smart_connection(self, painter, parent_card, child_card):
        """绘制智能连接线 - 自动选择最近的连接点"""

        # 获取最近的连接点对
        parent_direction, parent_point = parent_card.get_nearest_connection_point(
            child_card.get_center_pos()
        )
        child_direction, child_point = child_card.get_nearest_connection_point(
            parent_card.get_center_pos()
        )

        # 创建贝塞尔曲线路径
        path = QPainterPath()
        path.moveTo(parent_point)

        # 根据连接方向计算控制点
        control1, control2 = self._calculate_control_points(
            parent_point, parent_direction,
            child_point, child_direction
        )

        # 绘制三次贝塞尔曲线
        path.cubicTo(control1, control2, child_point)

        # 创建渐变画笔
        gradient = QLinearGradient(parent_point, child_point)
        gradient.setColorAt(0, QColor(70, 130, 180, 200))
        gradient.setColorAt(1, QColor(100, 180, 255, 200))

        # 设置画笔
        pen = QPen(gradient, 2.5)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # 绘制路径
        painter.drawPath(path)

        # 绘制优雅的箭头
        self._draw_elegant_arrow(painter, control2, child_point, child_direction)

    def _calculate_control_points(self, start_point, start_direction, end_point, end_direction):
        """根据连接方向计算贝塞尔曲线控制点"""

        # 计算基础偏移量
        dx = abs(end_point.x() - start_point.x())
        dy = abs(end_point.y() - start_point.y())
        base_offset = min(max(dx, dy) * 0.3, 150)

        # 根据起始方向计算第一个控制点
        if start_direction == 'top':
            control1 = QPointF(start_point.x(), start_point.y() - base_offset)
        elif start_direction == 'right':
            control1 = QPointF(start_point.x() + base_offset, start_point.y())
        elif start_direction == 'bottom':
            control1 = QPointF(start_point.x(), start_point.y() + base_offset)
        elif start_direction == 'left':
            control1 = QPointF(start_point.x() - base_offset, start_point.y())
        else:
            control1 = QPointF(start_point.x(), start_point.y() + base_offset)

        # 根据结束方向计算第二个控制点
        if end_direction == 'top':
            control2 = QPointF(end_point.x(), end_point.y() - base_offset)
        elif end_direction == 'right':
            control2 = QPointF(end_point.x() + base_offset, end_point.y())
        elif end_direction == 'bottom':
            control2 = QPointF(end_point.x(), end_point.y() + base_offset)
        elif end_direction == 'left':
            control2 = QPointF(end_point.x() - base_offset, end_point.y())
        else:
            control2 = QPointF(end_point.x(), end_point.y() - base_offset)

        return control1, control2

    def _draw_elegant_arrow(self, painter, control_point, end_point, direction):
        """绘制优雅的箭头（考虑连接方向）"""

        # 计算箭头方向向量
        if direction == 'top':
            arrow_dir = QPointF(0, -1)
        elif direction == 'right':
            arrow_dir = QPointF(1, 0)
        elif direction == 'bottom':
            arrow_dir = QPointF(0, 1)
        elif direction == 'left':
            arrow_dir = QPointF(-1, 0)
        else:
            # 默认向下
            arrow_dir = QPointF(0, 1)

        # 箭头大小
        arrow_size = 12

        # 计算箭头的三个点
        perpendicular = QPointF(-arrow_dir.y(), arrow_dir.x())  # 垂直向量

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
        gradient = QLinearGradient(end_point, arrow_point1)
        gradient.setColorAt(0, QColor(100, 180, 255))
        gradient.setColorAt(1, QColor(70, 130, 180))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(70, 130, 180), 1))
        painter.drawPolygon(arrow)

    def itemChange(self, change, value):
        """检测卡片位置变化"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            moved_card = self.focusItem()
            if isinstance(moved_card, KnowledgeCard):
                for card in self.cards:
                    if card != moved_card and card.collidesWithItem(moved_card):
                        moved_card.set_parent_card(card)
                        card.add_child_card(moved_card)
                        break
        return super().itemChange(change, value)


class MindMapView(QGraphicsView):
    """思维导图视图 - 支持缩放、平移"""

    def __init__(self, scene):
        super().__init__(scene)

        # 设置视图属性
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.scale_factor = 1.0
        self.is_panning = False
        self.last_pan_point = QPointF()

    def wheelEvent(self, event):
        """鼠标滚轮缩放"""
        # Ctrl+滚轮进行缩放
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # 获取滚轮滚动方向
            delta = event.angleDelta().y()

            # 计算缩放因子
            if delta > 0:
                factor = 1.15
            else:
                factor = 1 / 1.15

            # 限制缩放范围
            new_scale = self.scale_factor * factor
            if 0.1 <= new_scale <= 5.0:
                self.scale(factor, factor)
                self.scale_factor = new_scale
        else:
            # 普通滚轮滚动
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 中键拖动平移
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_panning:
            # 平移视图
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)