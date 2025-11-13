"""
增强的布局算法 - 参考 simple-mind-map 实现
支持自动节点定位、避免重叠、多种布局类型
"""

from typing import List, Dict, Tuple, Optional
from PyQt6.QtCore import QPointF, QRectF
import math


class EnhancedLayoutEngine:
    """增强的布局引擎 - 参考 simple-mind-map 的布局算法"""
    
    # 布局类型常量（参考 simple-mind-map）
    LAYOUT_MIND_MAP = "mind_map"  # 思维导图
    LAYOUT_LOGICAL_LEFT = "logical_left"  # 向左逻辑结构图
    LAYOUT_LOGICAL_RIGHT = "logical_right"  # 向右逻辑结构图
    LAYOUT_ORGANIZATION = "organization"  # 组织结构图
    LAYOUT_CATALOG = "catalog"  # 目录组织图
    LAYOUT_TIMELINE = "timeline"  # 横向时间轴
    LAYOUT_TIMELINE_VERTICAL = "timeline_vertical"  # 竖向时间轴
    LAYOUT_FISHBONE = "fishbone"  # 鱼骨图
    LAYOUT_FISHBONE2 = "fishbone2"  # 带鱼头鱼尾的鱼骨图
    
    # 生长方向常量
    GROW_DIR_LEFT = "left"
    GROW_DIR_RIGHT = "right"
    GROW_DIR_TOP = "top"
    GROW_DIR_BOTTOM = "bottom"
    
    def __init__(self, margin_x=80, margin_y=40):
        """
        初始化布局引擎
        Args:
            margin_x: 水平间距
            margin_y: 垂直间距
        """
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.root_node_center = None
    
    def layout_nodes(self, root_card, cards: List, layout_type: str = LAYOUT_MIND_MAP) -> Dict:
        """
        布局节点（参考 simple-mind-map 的 doLayout）
        支持所有布局类型
        Args:
            root_card: 根节点卡片
            cards: 所有卡片列表
            layout_type: 布局类型
        Returns:
            布局结果字典
        """
        if layout_type == self.LAYOUT_MIND_MAP:
            return self._layout_mind_map(root_card, cards)
        elif layout_type in [self.LAYOUT_LOGICAL_LEFT, self.LAYOUT_LOGICAL_RIGHT]:
            return self._layout_logical(root_card, cards, layout_type == self.LAYOUT_LOGICAL_LEFT)
        elif layout_type == self.LAYOUT_ORGANIZATION:
            return self._layout_organization(root_card, cards)
        elif layout_type == self.LAYOUT_CATALOG:
            return self._layout_catalog(root_card, cards)
        elif layout_type == self.LAYOUT_TIMELINE:
            return self._layout_timeline(root_card, cards)
        elif layout_type == self.LAYOUT_TIMELINE_VERTICAL:
            return self._layout_timeline_vertical(root_card, cards)
        elif layout_type in [self.LAYOUT_FISHBONE, self.LAYOUT_FISHBONE2]:
            return self._layout_fishbone(root_card, cards, layout_type == self.LAYOUT_FISHBONE2)
        else:
            return self._layout_mind_map(root_card, cards)
    
    def _layout_mind_map(self, root_card, cards: List) -> Dict:
        """
        思维导图布局（参考 simple-mind-map 的 MindMap.doLayout）
        """
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 第一步：计算基础值（left, width, height）
        self._compute_base_values(node_tree, root_card)
        
        # 第二步：计算top值
        self._compute_top_values(node_tree, root_card)
        
        # 第三步：调整top值（避免重叠）
        self._adjust_top_values(node_tree, root_card)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _build_node_tree(self, root_card, cards: List) -> Dict:
        """构建节点树结构"""
        # 创建节点映射
        node_map = {}
        for card in cards:
            node_map[card.card_id] = {
                'card': card,
                'children': [],
                'parent': None,
                'layer_index': 0,
                'dir': None,  # 生长方向
                'left': 0,
                'top': 0,
                'width': card.CARD_WIDTH,
                'height': card.CARD_HEIGHT,
                'left_children_area_height': 0,
                'right_children_area_height': 0,
            }
        
        # 构建父子关系
        for card in cards:
            if card.parent_card:
                parent_id = card.parent_card.card_id
                child_id = card.card_id
                if parent_id in node_map and child_id in node_map:
                    node_map[parent_id]['children'].append(node_map[child_id])
                    node_map[child_id]['parent'] = node_map[parent_id]
        
        # 计算层级
        root_node = node_map.get(root_card.card_id)
        if root_node:
            self._compute_layer_indices(root_node, 0)
        
        return root_node if root_node else {}
    
    def _compute_layer_indices(self, node: Dict, layer_index: int):
        """计算节点层级"""
        node['layer_index'] = layer_index
        for child in node['children']:
            self._compute_layer_indices(child, layer_index + 1)
    
    def _compute_base_values(self, node: Dict, root_card):
        """
        计算基础值（参考 simple-mind-map 的 computedBaseValue）
        遍历节点树，计算left、width、height
        """
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = self.root_node_center or QPointF(400, 300)
            # 确保使用卡片的实际大小
            card_width = node['card'].CARD_WIDTH
            card_height = node['card'].CARD_HEIGHT
            node['width'] = card_width
            node['height'] = card_height
            node['left'] = root_center.x() - card_width / 2
            node['top'] = root_center.y() - card_height / 2
            node['dir'] = None
        else:
            # 非根节点：根据父节点和方向计算位置
            parent = node['parent']
            if parent:
                # 确保使用卡片的实际大小
                card_width = node['card'].CARD_WIDTH
                card_height = node['card'].CARD_HEIGHT
                node['width'] = card_width
                node['height'] = card_height
                
                # 确定生长方向
                if not node['dir']:
                    # 根据索引决定方向（偶数向右，奇数向左）
                    index = parent['children'].index(node)
                    node['dir'] = self.GROW_DIR_RIGHT if index % 2 == 0 else self.GROW_DIR_LEFT
                
                # 计算left位置（确保不会重叠）
                layer_index = node['layer_index']
                margin_x = self._get_margin_x(layer_index)
                
                if node['dir'] == self.GROW_DIR_RIGHT:
                    # 确保有足够的间距，避免重叠
                    node['left'] = parent['left'] + parent['width'] + max(margin_x, 10)
                else:
                    # 确保有足够的间距，避免重叠
                    node['left'] = parent['left'] - max(margin_x, 10) - card_width
        
        # 递归处理子节点
        for child in node['children']:
            # 默认展开所有节点（可以根据需要添加展开/收起功能）
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_base_values(child, root_card)
        
        # 返回时计算子节点区域高度
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if is_expanded:
            self._compute_children_area_height(node)
    
    def _compute_children_area_height(self, node: Dict):
        """
        计算子节点区域高度（参考 simple-mind-map 的逻辑）
        """
        if not node['children']:
            node['left_children_area_height'] = 0
            node['right_children_area_height'] = 0
            return
        
        left_children_area_height = 0
        right_children_area_height = 0
        left_count = 0
        right_count = 0
        
        for child in node['children']:
            if child['dir'] == self.GROW_DIR_LEFT:
                left_count += 1
                left_children_area_height += child['height']
            else:
                right_count += 1
                right_children_area_height += child['height']
        
        layer_index = node['layer_index']
        margin_y = self._get_margin_y(layer_index + 1)
        
        node['left_children_area_height'] = (
            left_children_area_height + (left_count + 1) * margin_y
        )
        node['right_children_area_height'] = (
            right_children_area_height + (right_count + 1) * margin_y
        )
    
    def _compute_top_values(self, node: Dict, root_card):
        """
        计算top值（参考 simple-mind-map 的 computedTopValue）
        确保使用卡片的实际高度
        """
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded:
            return
        
        if not node['children']:
            return
        
        layer_index = node['layer_index']
        margin_y = max(self._get_margin_y(layer_index + 1), 10)  # 最小间距10
        
        # 使用实际卡片高度
        node_height = node['card'].CARD_HEIGHT
        base_top = node['top'] + node_height / 2 + margin_y
        
        # 第一个子节点的top值 = 节点中心的top值 - 子节点高度之和的一半
        left_total_top = base_top - node['left_children_area_height'] / 2
        right_total_top = base_top - node['right_children_area_height'] / 2
        
        for child in node['children']:
            # 使用实际卡片高度
            child_height = child['card'].CARD_HEIGHT
            child['height'] = child_height  # 确保高度正确
            
            if child['dir'] == self.GROW_DIR_LEFT:
                child['top'] = left_total_top
                left_total_top += child_height + margin_y
            else:
                child['top'] = right_total_top
                right_total_top += child_height + margin_y
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_top_values(child, root_card)
    
    def _adjust_top_values(self, node: Dict, root_card):
        """
        调整top值，避免重叠（参考 simple-mind-map 的 adjustTopValue）
        确保考虑卡片的实际大小
        """
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded:
            return
        
        if not node['children']:
            return
        
        # 检查子节点之间是否有重叠（考虑实际卡片大小）
        for i in range(len(node['children']) - 1):
            current = node['children'][i]
            next_node = node['children'][i + 1]
            
            # 只调整同方向的节点
            if current['dir'] != next_node['dir']:
                continue
            
            # 确保使用实际卡片高度
            current_height = current['card'].CARD_HEIGHT
            next_height = next_node['card'].CARD_HEIGHT
            
            # 检查重叠（考虑实际高度）
            current_bottom = current['top'] + current_height
            next_top = next_node['top']
            
            # 添加最小间距
            min_margin = 10  # 最小间距，避免卡片紧贴
            
            if current_bottom + min_margin > next_top:
                # 有重叠或间距不足，调整下一个节点的位置
                overlap = current_bottom + min_margin - next_top
                margin_y = max(self._get_margin_y(node['layer_index'] + 1), min_margin)
                next_node['top'] = current_bottom + margin_y
                
                # 递归调整后续节点
                self._adjust_siblings(next_node, overlap + margin_y - min_margin)
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._adjust_top_values(child, root_card)
    
    def _adjust_siblings(self, node: Dict, add_height: float):
        """调整兄弟节点位置"""
        parent = node['parent']
        if not parent:
            return
        
        # 找到当前节点在父节点子节点列表中的位置
        try:
            index = parent['children'].index(node)
        except ValueError:
            return
        
        # 调整后续同方向的兄弟节点
        for i in range(index + 1, len(parent['children'])):
            sibling = parent['children'][i]
            if sibling['dir'] == node['dir']:
                sibling['top'] += add_height
    
    def _apply_layout_to_cards(self, node: Dict, root_card, cards: List, positions: Dict):
        """将布局结果应用到卡片"""
        if not node:
            return
        
        card = node['card']
        positions[card.card_id] = QPointF(node['left'], node['top'])
        
        # 递归处理子节点
        for child in node['children']:
            self._apply_layout_to_cards(child, root_card, cards, positions)
    
    def _layout_logical(self, root_card, cards: List, use_left: bool = False) -> Dict:
        """
        逻辑结构图布局（参考 simple-mind-map 的 LogicalStructure）
        Args:
            use_left: True=向左，False=向右
        """
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 第一步：计算基础值（left, width, height）
        self._compute_logical_base_values(node_tree, root_card, use_left)
        
        # 第二步：计算top值
        self._compute_logical_top_values(node_tree, root_card)
        
        # 第三步：调整top值（避免重叠）
        self._adjust_logical_top_values(node_tree, root_card)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _compute_logical_base_values(self, node: Dict, root_card, use_left: bool):
        """计算逻辑结构图的基础值（参考 LogicalStructure.computedBaseValue）"""
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = self.root_node_center or QPointF(400, 300)
            card_width = node['card'].CARD_WIDTH
            card_height = node['card'].CARD_HEIGHT
            node['width'] = card_width
            node['height'] = card_height
            node['left'] = root_center.x() - card_width / 2
            node['top'] = root_center.y() - card_height / 2
        else:
            # 非根节点：根据方向定位到父节点左侧或右侧
            parent = node['parent']
            if parent:
                card_width = node['card'].CARD_WIDTH
                card_height = node['card'].CARD_HEIGHT
                node['width'] = card_width
                node['height'] = card_height
                
                layer_index = node['layer_index']
                margin_x = self._get_margin_x(layer_index)
                
                if use_left:
                    # 向左
                    node['left'] = parent['left'] - margin_x - card_width
                else:
                    # 向右
                    node['left'] = parent['left'] + parent['width'] + margin_x
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_logical_base_values(child, root_card, use_left)
        
        # 计算子节点区域高度
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if is_expanded:
            self._compute_children_area_height(node)
    
    def _compute_logical_top_values(self, node: Dict, root_card):
        """计算逻辑结构图的top值（参考 LogicalStructure.computedTopValue）"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        layer_index = node['layer_index']
        margin_y = max(self._get_margin_y(layer_index + 1), 10)
        node_height = node['card'].CARD_HEIGHT
        
        # 第一个子节点的top值 = 节点中心的top值 - 子节点高度之和的一半
        top = node['top'] + node_height / 2 - node['left_children_area_height'] / 2
        total_top = top + margin_y
        
        for child in node['children']:
            child_height = child['card'].CARD_HEIGHT
            child['height'] = child_height
            child['top'] = total_top
            total_top += child_height + margin_y
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_logical_top_values(child, root_card)
    
    def _adjust_logical_top_values(self, node: Dict, root_card):
        """调整逻辑结构图的top值（避免重叠）"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        # 检查子节点重叠
        for i in range(len(node['children']) - 1):
            current = node['children'][i]
            next_node = node['children'][i + 1]
            
            current_height = current['card'].CARD_HEIGHT
            next_height = next_node['card'].CARD_HEIGHT
            current_bottom = current['top'] + current_height
            next_top = next_node['top']
            min_margin = 10
            
            if current_bottom + min_margin > next_top:
                overlap = current_bottom + min_margin - next_top
                margin_y = max(self._get_margin_y(node['layer_index'] + 1), min_margin)
                next_node['top'] = current_bottom + margin_y
                self._adjust_siblings(next_node, overlap + margin_y - min_margin)
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._adjust_logical_top_values(child, root_card)
    
    def _layout_timeline(self, root_card, cards: List) -> Dict:
        """
        横向时间轴布局（参考 simple-mind-map 的 Timeline）
        """
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 计算基础值和位置
        self._compute_timeline_base_values(node_tree, root_card)
        self._compute_timeline_left_top_values(node_tree, root_card)
        self._adjust_timeline_left_top_values(node_tree, root_card)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _compute_timeline_base_values(self, node: Dict, root_card):
        """计算时间轴的基础值（参考 Timeline.computedBaseValue）"""
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = self.root_node_center or QPointF(400, 300)
            card_width = node['card'].CARD_WIDTH
            card_height = node['card'].CARD_HEIGHT
            node['width'] = card_width
            node['height'] = card_height
            node['left'] = root_center.x() - card_width / 2
            node['top'] = root_center.y() - card_height / 2
        else:
            # 非根节点
            parent = node['parent']
            if parent:
                card_width = node['card'].CARD_WIDTH
                card_height = node['card'].CARD_HEIGHT
                node['width'] = card_width
                node['height'] = card_height
                
                # 如果是根节点的子节点，垂直对齐
                if parent['card'] == root_card:
                    node['top'] = parent['top'] + (parent['height'] - card_height) / 2
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_timeline_base_values(child, root_card)
    
    def _compute_timeline_left_top_values(self, node: Dict, root_card):
        """计算时间轴的left和top值（参考 Timeline.computedLeftTopValue）"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        layer_index = node['layer_index']
        margin_x = self._get_margin_x(layer_index + 1)
        margin_y = self._get_margin_y(layer_index + 1)
        
        if node['card'] == root_card:
            # 根节点的子节点：水平排列
            left = node['left'] + node['width']
            total_left = left + margin_x
            
            for child in node['children']:
                child['left'] = total_left
                total_left += child['width'] + margin_x
        else:
            # 非根节点的子节点：在父节点下方
            total_top = node['top'] + node['height'] + margin_y
            
            for child in node['children']:
                child['left'] = node['left'] + node['width'] * 0.5
                child['top'] = total_top
                total_top += child['height'] + margin_y
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_timeline_left_top_values(child, root_card)
    
    def _adjust_timeline_left_top_values(self, node: Dict, root_card):
        """调整时间轴的位置（避免重叠）"""
        # 时间轴布局的重叠调整逻辑
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded:
            return
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._adjust_timeline_left_top_values(child, root_card)
    
    def _layout_timeline_vertical(self, root_card, cards: List) -> Dict:
        """
        竖向时间轴布局（参考 simple-mind-map 的 VerticalTimeline）
        """
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 计算基础值和位置
        self._compute_vertical_timeline_base_values(node_tree, root_card)
        self._compute_vertical_timeline_top_values(node_tree, root_card)
        self._adjust_vertical_timeline_left_top_values(node_tree, root_card)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _compute_vertical_timeline_base_values(self, node: Dict, root_card):
        """计算竖向时间轴的基础值"""
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = self.root_node_center or QPointF(400, 300)
            card_width = node['card'].CARD_WIDTH
            card_height = node['card'].CARD_HEIGHT
            node['width'] = card_width
            node['height'] = card_height
            node['left'] = root_center.x() - card_width / 2
            node['top'] = root_center.y() - card_height / 2
        else:
            # 非根节点：定位到父节点右侧
            parent = node['parent']
            if parent:
                card_width = node['card'].CARD_WIDTH
                card_height = node['card'].CARD_HEIGHT
                node['width'] = card_width
                node['height'] = card_height
                
                layer_index = node['layer_index']
                margin_x = self._get_margin_x(layer_index)
                
                node['left'] = parent['left'] + parent['width'] + margin_x
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_vertical_timeline_base_values(child, root_card)
    
    def _compute_vertical_timeline_top_values(self, node: Dict, root_card):
        """计算竖向时间轴的top值"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        layer_index = node['layer_index']
        margin_y = max(self._get_margin_y(layer_index + 1), 10)
        node_height = node['card'].CARD_HEIGHT
        
        # 第一个子节点的top值 = 节点中心的top值 - 子节点高度之和的一半
        top = node['top'] + node_height / 2
        total_top = top + margin_y
        
        for child in node['children']:
            child_height = child['card'].CARD_HEIGHT
            child['height'] = child_height
            child['top'] = total_top
            total_top += child_height + margin_y
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_vertical_timeline_top_values(child, root_card)
    
    def _adjust_vertical_timeline_left_top_values(self, node: Dict, root_card):
        """调整竖向时间轴的位置（避免重叠）"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded:
            return
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._adjust_vertical_timeline_left_top_values(child, root_card)
    
    def _layout_fishbone(self, root_card, cards: List, is_fishbone2: bool = False) -> Dict:
        """
        鱼骨图布局（参考 simple-mind-map 的 Fishbone）
        """
        from .layout_methods import LayoutMethods
        layout_methods = LayoutMethods(self.margin_x, self.margin_y)
        
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 应用鱼骨图布局算法（默认45度角）
        layout_methods.compute_fishbone_positions(node_tree, root_card, fishbone_deg=45)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _layout_catalog(self, root_card, cards: List) -> Dict:
        """
        目录组织图布局（参考 simple-mind-map 的 CatalogOrganization）
        """
        from .layout_methods import LayoutMethods
        layout_methods = LayoutMethods(self.margin_x, self.margin_y)
        
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 应用目录组织图布局算法
        layout_methods.compute_catalog_positions(node_tree, root_card)
        layout_methods.compute_catalog_left_top_values(node_tree, root_card)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _layout_organization(self, root_card, cards: List) -> Dict:
        """
        组织结构图布局（参考 simple-mind-map 的 OrganizationStructure）
        自上而下生长
        """
        # 构建节点树
        node_tree = self._build_node_tree(root_card, cards)
        
        # 第一步：计算基础值（top, width, height）
        self._compute_organization_base_values(node_tree, root_card)
        
        # 第二步：计算left值
        self._compute_organization_left_values(node_tree, root_card)
        
        # 第三步：调整left值（避免重叠）
        self._adjust_organization_left_values(node_tree, root_card)
        
        # 应用布局结果到卡片
        positions = {}
        self._apply_layout_to_cards(node_tree, root_card, cards, positions)
        
        return positions
    
    def _compute_organization_base_values(self, node: Dict, root_card):
        """计算组织结构图的基础值（参考 OrganizationStructure.computedBaseValue）"""
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = self.root_node_center or QPointF(400, 300)
            card_width = node['card'].CARD_WIDTH
            card_height = node['card'].CARD_HEIGHT
            node['width'] = card_width
            node['height'] = card_height
            node['left'] = root_center.x() - card_width / 2
            node['top'] = root_center.y() - card_height / 2
        else:
            # 非根节点：定位到父节点下方
            parent = node['parent']
            if parent:
                card_width = node['card'].CARD_WIDTH
                card_height = node['card'].CARD_HEIGHT
                node['width'] = card_width
                node['height'] = card_height
                
                layer_index = node['layer_index']
                margin_x = self._get_margin_x(layer_index)
                
                node['top'] = parent['top'] + parent['height'] + margin_x
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_organization_base_values(child, root_card)
        
        # 计算子节点区域宽度
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if is_expanded:
            self._compute_organization_children_area_width(node)
    
    def _compute_organization_children_area_width(self, node: Dict):
        """计算子节点区域宽度（参考 OrganizationStructure）"""
        if not node['children']:
            node['children_area_width'] = 0
            return
        
        children_area_width = sum(child['card'].CARD_WIDTH for child in node['children'])
        layer_index = node['layer_index']
        margin_y = self._get_margin_y(layer_index + 1)
        
        node['children_area_width'] = (
            children_area_width + (len(node['children']) + 1) * margin_y
        )
    
    def _compute_organization_left_values(self, node: Dict, root_card):
        """计算组织结构图的left值（参考 OrganizationStructure.computedLeftValue）"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        layer_index = node['layer_index']
        margin_x = self._get_margin_y(layer_index + 1)  # 注意：这里用margin_y作为水平间距
        
        # 第一个子节点的left值 = 节点中心的left值 - 子节点宽度之和的一半
        left = node['left'] + node['width'] / 2 - node['children_area_width'] / 2
        total_left = left + margin_x
        
        for child in node['children']:
            child['left'] = total_left
            total_left += child['width'] + margin_x
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._compute_organization_left_values(child, root_card)
    
    def _adjust_organization_left_values(self, node: Dict, root_card):
        """调整组织结构图的left值（避免重叠）"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        # 检查子节点重叠（水平方向）
        for i in range(len(node['children']) - 1):
            current = node['children'][i]
            next_node = node['children'][i + 1]
            
            current_width = current['card'].CARD_WIDTH
            next_width = next_node['card'].CARD_WIDTH
            current_right = current['left'] + current_width
            next_left = next_node['left']
            min_margin = 10
            
            if current_right + min_margin > next_left:
                overlap = current_right + min_margin - next_left
                margin_x = max(self._get_margin_y(node['layer_index'] + 1), min_margin)
                next_node['left'] = current_right + margin_x
                # 调整后续节点
                for j in range(i + 2, len(node['children'])):
                    node['children'][j]['left'] += overlap + margin_x - min_margin
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self._adjust_organization_left_values(child, root_card)
    
    def _get_margin_x(self, layer_index: int) -> float:
        """获取水平间距（参考 simple-mind-map 的 getMarginX）"""
        if layer_index == 1:
            return self.margin_x * 1.2
        else:
            return self.margin_x
    
    def _get_margin_y(self, layer_index: int) -> float:
        """获取垂直间距（参考 simple-mind-map 的 getMarginY）"""
        return self.margin_y
    
    def set_root_center(self, center: QPointF):
        """设置根节点中心位置"""
        self.root_node_center = center
