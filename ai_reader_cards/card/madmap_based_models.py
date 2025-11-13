"""
基于 madmap 的数据模型 - 添加问题和答案属性
参考 test/madmap/models.py
"""

import json
import uuid


class CardTreeNode:
    """
    卡片树节点 - 基于 madmap 的 TreeNode，添加问题和答案属性
    """
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
        self.source_text = ""  # 源文本（用于跳转）
        self.source_text_start = -1
        self.source_text_end = -1
        self.note_text = ""  # 笔记文本
        # 关联线相关
        self.associative_line_targets = []  # 关联线目标节点ID列表
        self.associative_line_control_offsets = {}  # 关联线控制点偏移 {target_id: [cp1_offset, cp2_offset]}
        self.associative_line_text = {}  # 关联线文字 {target_id: text}
        # 节点内容相关
        self.image_path = ""  # 图片路径
        self.image_placement = "top"  # 图片位置：top/bottom/left/right

    def add_child(self, node):
        node.parent = self
        node.level = self.level + 1
        self.children.append(node)

    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def to_dict(self):
        """转换为字典（包含问题和答案）"""
        return {
            "id": self.id,
            "title": self.title,
            "question": self.question,
            "answer": self.answer,
            "x": self.x,
            "y": self.y,
            "level": self.level,
            "source_text": self.source_text,
            "source_text_start": self.source_text_start,
            "source_text_end": self.source_text_end,
            "note_text": self.note_text,
            "associative_line_targets": getattr(self, 'associative_line_targets', []),
            "associative_line_control_offsets": getattr(self, 'associative_line_control_offsets', {}),
            "associative_line_text": getattr(self, 'associative_line_text', {}),
            "image_path": getattr(self, 'image_path', ""),
            "image_placement": getattr(self, 'image_placement', "top"),
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        """从字典创建节点"""
        node = CardTreeNode(
            data.get("title", ""),
            data.get("question", ""),
            data.get("answer", ""),
            data.get("x", 0),
            data.get("y", 0)
        )
        node.id = data.get("id", str(uuid.uuid4()))
        node.level = data.get("level", 0)
        node.source_text = data.get("source_text", "")
        node.source_text_start = data.get("source_text_start", -1)
        node.source_text_end = data.get("source_text_end", -1)
        node.note_text = data.get("note_text", "")
        node.associative_line_targets = data.get("associative_line_targets", [])
        node.associative_line_control_offsets = data.get("associative_line_control_offsets", {})
        node.associative_line_text = data.get("associative_line_text", {})
        node.image_path = data.get("image_path", "")
        node.image_placement = data.get("image_placement", "top")
        
        for child_data in data.get("children", []):
            child_node = CardTreeNode.from_dict(child_data)
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
        new_node = CardTreeNode(
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
        new_node.note_text = self.note_text
        new_node.associative_line_targets = self.associative_line_targets.copy() if hasattr(self, 'associative_line_targets') else []
        new_node.associative_line_control_offsets = self.associative_line_control_offsets.copy() if hasattr(self, 'associative_line_control_offsets') else {}
        new_node.associative_line_text = self.associative_line_text.copy() if hasattr(self, 'associative_line_text') else {}
        new_node.image_path = self.image_path if hasattr(self, 'image_path') else ""
        new_node.image_placement = self.image_placement if hasattr(self, 'image_placement') else "top"

        for child in self.children:
            new_child = child.duplicate()
            new_node.add_child(new_child)

        return new_node

