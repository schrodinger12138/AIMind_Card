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