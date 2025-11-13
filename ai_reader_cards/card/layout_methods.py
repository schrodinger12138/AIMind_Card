"""
布局方法实现 - 参考 simple-mind-map 实现所有布局类型
包含：目录组织图、鱼骨图、竖向时间轴等布局的具体实现
"""

from typing import List, Dict
from PyQt6.QtCore import QPointF
import math


class LayoutMethods:
    """布局方法集合 - 补充 enhanced_layout.py 中缺失的方法"""
    
    def __init__(self, margin_x=80, margin_y=40):
        self.margin_x = margin_x
        self.margin_y = margin_y
    
    def compute_catalog_positions(self, node: Dict, root_card):
        """
        计算目录组织图位置（参考 simple-mind-map 的 CatalogOrganization）
        """
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = QPointF(400, 300)
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
                
                layer_index = node['layer_index']
                margin_x = self.margin_x
                
                if parent['card'] == root_card:
                    # 根节点的直接子节点：在根节点下方
                    node['top'] = parent['top'] + parent['height'] + margin_x
                else:
                    # 其他节点：在父节点下方
                    node['top'] = parent['top'] + parent['height'] + margin_x
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self.compute_catalog_positions(child, root_card)
        
        # 计算子节点区域宽度（仅根节点）
        if node['card'] == root_card:
            is_expanded = getattr(node['card'], 'is_expanded', True)
            if is_expanded and node['children']:
                children_area_width = sum(
                    child['card'].CARD_WIDTH for child in node['children']
                )
                margin = self.margin_x
                node['children_area_width'] = (
                    children_area_width + (len(node['children']) + 1) * margin
                )
    
    def compute_catalog_left_top_values(self, node: Dict, root_card):
        """计算目录组织图的left和top值"""
        if not node:
            return
        
        is_expanded = getattr(node['card'], 'is_expanded', True)
        if not is_expanded or not node['children']:
            return
        
        margin_x = self.margin_x
        margin_y = self.margin_y
        
        if node['card'] == root_card:
            # 根节点的子节点：水平排列
            left = node['left'] + node['width'] / 2 - node.get('children_area_width', 0) / 2
            total_left = left + margin_x
            for child in node['children']:
                child['left'] = total_left
                total_left += child['width'] + margin_x
        else:
            # 非根节点的子节点：垂直排列
            total_top = (
                node['top'] + node['height'] + margin_y
            )
            for child in node['children']:
                child['left'] = node['left'] + node['width'] * 0.5
                child['top'] = total_top
                total_top += child['height'] + margin_y
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self.compute_catalog_left_top_values(child, root_card)
    
    def compute_fishbone_positions(self, node: Dict, root_card, fishbone_deg=45):
        """
        计算鱼骨图位置（参考 simple-mind-map 的 Fishbone）
        Args:
            fishbone_deg: 鱼骨图倾斜角度（度）
        """
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = QPointF(400, 300)
            card_width = node['card'].CARD_WIDTH
            card_height = node['card'].CARD_HEIGHT
            node['width'] = card_width
            node['height'] = card_height
            node['left'] = root_center.x() - card_width / 2
            node['top'] = root_center.y() - card_height / 2
        else:
            # 非根节点：根据方向和角度计算位置
            parent = node['parent']
            if parent:
                card_width = node['card'].CARD_WIDTH
                card_height = node['card'].CARD_HEIGHT
                node['width'] = card_width
                node['height'] = card_height
                
                layer_index = node['layer_index']
                margin_x = self.margin_x
                
                # 确定生长方向
                if not node.get('dir'):
                    # 根据索引决定方向（偶数向右，奇数向左）
                    index = parent['children'].index(node)
                    node['dir'] = 'right' if index % 2 == 0 else 'left'
                
                # 计算位置（考虑倾斜角度）
                rad = math.radians(fishbone_deg)
                if node['dir'] == 'right':
                    # 向右上方
                    dx = margin_x * math.cos(rad)
                    dy = -margin_x * math.sin(rad)
                else:
                    # 向左上方
                    dx = -margin_x * math.cos(rad)
                    dy = -margin_x * math.sin(rad)
                
                node['left'] = parent['left'] + parent['width'] / 2 + dx - card_width / 2
                node['top'] = parent['top'] + parent['height'] / 2 + dy - card_height / 2
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self.compute_fishbone_positions(child, root_card, fishbone_deg)
    
    def compute_timeline_positions(self, node: Dict, root_card, horizontal=True):
        """
        计算时间轴位置（参考 simple-mind-map 的 Timeline/VerticalTimeline）
        Args:
            horizontal: True=横向，False=竖向
        """
        if not node:
            return
        
        # 根节点定位在中心
        if node['card'] == root_card:
            root_center = QPointF(400, 300)
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
                
                layer_index = node['layer_index']
                margin = self.margin_x if horizontal else self.margin_y
                
                if horizontal:
                    # 横向：在父节点右侧
                    node['left'] = parent['left'] + parent['width'] + margin
                    node['top'] = parent['top']
                else:
                    # 竖向：在父节点下方或根据方向在左右
                    if not node.get('dir'):
                        index = parent['children'].index(node)
                        node['dir'] = 'right' if index % 2 == 0 else 'left'
                    
                    if node['dir'] == 'right':
                        node['left'] = parent['left'] + parent['width'] + margin
                    else:
                        node['left'] = parent['left'] - margin - card_width
                    node['top'] = parent['top'] + parent['height'] + margin
        
        # 递归处理子节点
        for child in node['children']:
            is_expanded = getattr(child['card'], 'is_expanded', True)
            if is_expanded:
                self.compute_timeline_positions(child, root_card, horizontal)

