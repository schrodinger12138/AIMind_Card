"""树形数据模型 - 从 madmap 集成"""
import json
import uuid


class TreeNode:
    """树节点数据模型"""
    
    def __init__(self, title, x=0, y=0):
        self.id = str(uuid.uuid4())  # 使用UUID确保唯一性
        self.title = title
        self.parent = None
        self.children = []
        self.x = x
        self.y = y
        self.level = 0  # 节点层级

    def add_child(self, node):
        """添加子节点"""
        node.parent = self
        node.level = self.level + 1
        self.children.append(node)

    def remove_child(self, node):
        """移除子节点"""
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "level": self.level,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        """从字典创建节点"""
        node = TreeNode(data["title"], data.get("x", 0), data.get("y", 0))
        node.id = data.get("id", str(uuid.uuid4()))
        node.level = data.get("level", 0)
        for child_data in data.get("children", []):
            child_node = TreeNode.from_dict(child_data)
            node.add_child(child_node)
        return node

    def find_node_by_id(self, node_id):
        """根据ID查找节点"""
        if self.id == node_id:
            return self

        for child in self.children:
            found = child.find_node_by_id(node_id)
            if found:
                return found
        return None

    def get_siblings(self):
        """获取同级节点"""
        if self.parent is None:
            return [self]
        return self.parent.children

    def is_descendant_of(self, node):
        """检查当前节点是否是指定节点的后代"""
        current = self
        while current.parent is not None:
            if current.parent == node:
                return True
            current = current.parent
        return False

    def update_levels(self, new_level=0):
        """递归更新节点层级"""
        self.level = new_level
        for child in self.children:
            child.update_levels(new_level + 1)

    def duplicate(self):
        """复制节点及其子树"""
        new_node = TreeNode(self.title, self.x + 20, self.y + 20)
        new_node.level = self.level

        for child in self.children:
            new_child = child.duplicate()
            new_node.add_child(new_child)

        return new_node

