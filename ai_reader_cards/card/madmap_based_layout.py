"""
基于 madmap 的布局引擎
参考 test/madmap/layout.py
支持动态节点大小
"""


class CardLayoutEngine:
    """
    卡片布局引擎 - 基于 madmap 的 LayoutEngine
    参考 test/madmap/layout.py
    """
    
    @staticmethod
    def mind_map(root, h_spacing=200, v_spacing=100, visual_nodes=None):
        """左右树形布局（参考 madmap），支持动态节点大小"""
        def get_node_size(node):
            """获取节点实际大小"""
            if visual_nodes:
                for vn in visual_nodes:
                    if vn.tree_node == node:
                        width, height = vn.get_actual_size()
                        return width, height
            # 默认大小
            from .madmap_based_nodes import CardVisualNode
            return CardVisualNode.WIDTH, CardVisualNode.HEIGHT
        
        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            _, node_height = get_node_size(node)
            
            # 根据子节点总高度计算间距
            if node.children:
                total_children_height = sum(get_node_size(c)[1] for c in node.children)
                total_spacing = v_spacing * (len(node.children) - 1)
                total_height = total_children_height + total_spacing
                child_y = y_offset - total_height / 2 + get_node_size(node.children[0])[1] / 2
                
                for c in node.children:
                    _, child_height = get_node_size(c)
                    layout(c, depth + 1, child_y, direction)
                    child_y += child_height + v_spacing

        # 根节点在左侧，所有子节点向右展开
        root.x = 0
        root.y = 0

        # 所有子节点都向右展开（从左到右）
        if root.children:
            total_children_height = sum(get_node_size(c)[1] for c in root.children)
            total_spacing = v_spacing * (len(root.children) - 1)
            total_height = total_children_height + total_spacing
            child_y = -total_height / 2 + get_node_size(root.children[0])[1] / 2
            
            for c in root.children:
                _, child_height = get_node_size(c)
                layout(c, 1, child_y, 1)  # 向右展开
                child_y += child_height + v_spacing

    @staticmethod
    def logical(root, h_spacing=200, v_spacing=120, visual_nodes=None):
        """
        逻辑结构布局：从左到右，父节点 → 子节点
        水平方向：父节点右边 + 固定间距 → 子节点左边
        垂直方向：多个子节点垂直分布
        
        数学公式：
        - 父节点 a：左上角 (ax, ay)，大小 (aw, ah)
        - 子节点 b：左上角 (bx, by)，大小 (bw, bh)
        - 水平：bx = ax + aw + h_spacing
        - 垂直：第一个子节点 by = ay，后续子节点垂直分布
        """
        def get_node_size(node):
            """获取节点实际大小"""
            if visual_nodes:
                for vn in visual_nodes:
                    if vn.tree_node == node:
                        width, height = vn.get_actual_size()
                        return width, height
            from .madmap_based_nodes import CardVisualNode
            return CardVisualNode.WIDTH, CardVisualNode.HEIGHT
        
        def layout(node, parent_x=None, parent_y=None, parent_w=None, parent_h=None):
            """
            递归布局节点
            Args:
                node: 当前节点
                parent_x: 父节点左上角 x（None 表示根节点）
                parent_y: 父节点左上角 y
                parent_w: 父节点宽度
                parent_h: 父节点高度
            """
            # 获取当前节点实际大小
            node_w, node_h = get_node_size(node)
            
            if parent_x is None:
                # 根节点：左上角在 (0, 0)
                node.x = 0
                node.y = 0
            else:
                # 子节点：在父节点右侧
                # 水平方向：父节点右边缘 + 固定间距 = 子节点左边缘
                # bx = ax + aw + h_spacing
                node.x = parent_x + parent_w + h_spacing
                
                # 垂直方向：第一个子节点与父节点顶部对齐
                # 如果有多个子节点，需要垂直分布（这里先简化，后续会调整）
                node.y = parent_y
            
            # 布局子节点
            if node.children:
                # 先计算所有子节点的大小，用于垂直分布
                child_sizes = [get_node_size(c) for c in node.children]
                
                # 第一个子节点：与父节点顶部对齐
                first_child = node.children[0]
                first_child_w, first_child_h = child_sizes[0]
                layout(first_child, node.x, node.y, first_child_w, first_child_h)
                
                # 后续子节点：垂直分布
                current_y = node.y + first_child_h + v_spacing
                for i in range(1, len(node.children)):
                    child = node.children[i]
                    child_w, child_h = child_sizes[i]
                    layout(child, node.x, current_y, child_w, child_h)
                    # 下一个子节点的 y = 当前子节点底部 + 垂直间距
                    current_y += child_h + v_spacing

        # 从根节点开始布局
        layout(root)

    @staticmethod
    def timeline(root, h_spacing=200, visual_nodes=None):
        """时间轴布局，横向排列（参考 madmap），支持动态节点大小"""
        def get_node_size(node):
            """获取节点实际大小"""
            if visual_nodes:
                for vn in visual_nodes:
                    if vn.tree_node == node:
                        width, height = vn.get_actual_size()
                        return width, height
            from .madmap_based_nodes import CardVisualNode
            return CardVisualNode.WIDTH, CardVisualNode.HEIGHT
        
        def layout(node, x_offset=0, y_offset=0):
            node.x = x_offset
            node.y = y_offset
            node_width, _ = get_node_size(node)
            child_x = x_offset + node_width + h_spacing
            
            for i, c in enumerate(node.children):
                _, child_height = get_node_size(c)
                layout(c, child_x, y_offset + (i - len(node.children) // 2) * max(100, child_height + 20))
                child_width, _ = get_node_size(c)
                child_x += child_width + h_spacing

        layout(root)

    @staticmethod
    def fishbone(root, h_spacing=200, v_spacing=100, visual_nodes=None):
        """鱼骨图布局（参考 madmap），支持动态节点大小"""
        def get_node_size(node):
            """获取节点实际大小"""
            if visual_nodes:
                for vn in visual_nodes:
                    if vn.tree_node == node:
                        width, height = vn.get_actual_size()
                        return width, height
            from .madmap_based_nodes import CardVisualNode
            return CardVisualNode.WIDTH, CardVisualNode.HEIGHT
        
        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            _, node_height = get_node_size(node)
            
            for i, c in enumerate(node.children):
                _, child_height = get_node_size(c)
                spacing = max(v_spacing, child_height + 20)
                layout(c, depth + 1, y_offset + (i - len(node.children) // 2) * spacing, direction)

        # 左右对称分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        for c in left_children:
            layout(c, 1, 0, -1)
        for c in right_children:
            layout(c, 1, 0, 1)

    @staticmethod
    def auto_arrange(root, h_spacing=200, v_spacing=120, visual_nodes=None):
        """自动排列避免重叠（参考 madmap），支持动态节点大小"""
        def get_node_size(node):
            """获取节点实际大小"""
            if visual_nodes:
                for vn in visual_nodes:
                    if vn.tree_node == node:
                        width, height = vn.get_actual_size()
                        return width, height
            from .madmap_based_nodes import CardVisualNode
            return CardVisualNode.WIDTH, CardVisualNode.HEIGHT
        
        def get_all_nodes(node):
            """获取所有节点"""
            nodes = [node]
            for child in node.children:
                nodes.extend(get_all_nodes(child))
            return nodes

        def check_overlap(node1, node2):
            """检查两个节点是否重叠（使用实际大小）"""
            w1, h1 = get_node_size(node1)
            w2, h2 = get_node_size(node2)
            return (abs(node1.x - node2.x) < (w1 + w2) / 2 + h_spacing * 0.5 and
                    abs(node1.y - node2.y) < (h1 + h2) / 2 + v_spacing * 0.5)

        def adjust_position(node, all_nodes):
            """调整节点位置避免重叠"""
            w, h = get_node_size(node)
            for other_node in all_nodes:
                if node != other_node and check_overlap(node, other_node):
                    # 如果重叠，向右下方移动
                    node.x += h_spacing * 0.7
                    node.y += v_spacing * 0.7
                    # 递归检查是否还会与其他节点重叠
                    adjust_position(node, all_nodes)
                    break

        # 先应用基本布局（使用动态大小）
        CardLayoutEngine.mind_map(root, h_spacing, v_spacing, visual_nodes)

        # 获取所有节点并检查重叠
        all_nodes = get_all_nodes(root)
        for node in all_nodes:
            adjust_position(node, all_nodes)

