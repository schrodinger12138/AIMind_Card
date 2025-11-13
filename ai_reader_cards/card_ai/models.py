"""数据模型定义 - 基于madmap，添加问题和答案属性"""
import json
import uuid


class TreeNode:
    def __init__(self, title, question="", answer="", x=0, y=0):
        self.id = str(uuid.uuid4())  # 使用UUID确保唯一性
        self.title = title
        self.question = question  # 问题属性
        self.answer = answer  # 答案属性
        self.parent = None
        self.children = []
        self.x = x
        self.y = y
        self.level = 0  # 节点层级
        
        # 源文本引用（用于跳转）
        self.source_text = ""  # 存储生成卡片时的源文本
        self.source_text_start = -1  # 源文本在文档中的起始位置
        self.source_text_end = -1  # 源文本在文档中的结束位置

    def add_child(self, node):
        node.parent = self
        node.level = self.level + 1
        self.children.append(node)

    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "question": self.question,
            "answer": self.answer,
            "x": self.x,
            "y": self.y,
            "source_text": self.source_text,
            "source_text_start": self.source_text_start,
            "source_text_end": self.source_text_end,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(
            data.get("title", ""),
            data.get("question", ""),
            data.get("answer", ""),
            data.get("x", 0),
            data.get("y", 0)
        )
        node.id = data.get("id", str(uuid.uuid4()))
        node.source_text = data.get("source_text", "")
        node.source_text_start = data.get("source_text_start", -1)
        node.source_text_end = data.get("source_text_end", -1)
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
        new_node = TreeNode(
            self.title,
            self.question,
            self.answer,
            self.x + 20,
            self.y + 20
        )
        new_node.level = self.level
        new_node.source_text = self.source_text
        new_node.source_text_start = self.source_text_start
        new_node.source_text_end = self.source_text_end

        for child in self.children:
            new_child = child.duplicate()
            new_node.add_child(new_child)

        return new_node

