"""对齐管理器"""

from PyQt6.QtCore import QObject


class AlignmentManager(QObject):
    """管理卡片对齐功能"""

    def __init__(self):
        super().__init__()

    def align_cards(self, cards, align_type):
        """对齐选中的卡片"""
        if len(cards) < 2:
            return False, "请选择至少两张卡片进行对齐"

        if align_type == "left":
            self._align_left(cards)
        elif align_type == "right":
            self._align_right(cards)
        elif align_type == "top":
            self._align_top(cards)
        elif align_type == "bottom":
            self._align_bottom(cards)
        elif align_type == "center_h":
            self._align_center_horizontal(cards)
        elif align_type == "center_v":
            self._align_center_vertical(cards)
        elif align_type == "distribute_h":
            self._distribute_horizontal(cards)
        elif align_type == "distribute_v":
            self._distribute_vertical(cards)

        align_names = {
            "left": "左对齐", "right": "右对齐", "top": "顶对齐",
            "bottom": "底对齐", "center_h": "水平居中", "center_v": "垂直居中",
            "distribute_h": "水平分布", "distribute_v": "垂直分布"
        }
        return True, f"已执行 {align_names.get(align_type, align_type)}"

    def arrange_hierarchy(self, cards):
        """层次排列"""
        if not cards:
            return False, "请选择卡片进行层次排列"

        # 找到可能的根节点
        root_cards = [card for card in cards if not card.parent_card]
        if not root_cards:
            root_card = cards[0]
        else:
            root_card = root_cards[0]

        # 简单的水平排列
        x_spacing = 200
        y_spacing = 150
        start_x = root_card.scenePos().x()
        start_y = root_card.scenePos().y() + y_spacing

        for i, card in enumerate(cards):
            if card != root_card:
                card.setPos(start_x + i * x_spacing, start_y)

        return True, "已按层次结构排列卡片"

    def _align_left(self, cards):
        """左对齐"""
        min_x = min(card.scenePos().x() for card in cards)
        for card in cards:
            card.setPos(min_x, card.scenePos().y())

    def _align_right(self, cards):
        """右对齐"""
        max_x = max(card.scenePos().x() + card.CARD_WIDTH for card in cards)
        for card in cards:
            card.setPos(max_x - card.CARD_WIDTH, card.scenePos().y())

    def _align_top(self, cards):
        """顶对齐"""
        min_y = min(card.scenePos().y() for card in cards)
        for card in cards:
            card.setPos(card.scenePos().x(), min_y)

    def _align_bottom(self, cards):
        """底对齐"""
        max_y = max(card.scenePos().y() + card.CARD_HEIGHT for card in cards)
        for card in cards:
            card.setPos(card.scenePos().x(), max_y - card.CARD_HEIGHT)

    def _align_center_horizontal(self, cards):
        """水平居中对齐"""
        center_y = sum(card.scenePos().y() + card.CARD_HEIGHT / 2 for card in cards) / len(cards)
        for card in cards:
            card.setPos(card.scenePos().x(), center_y - card.CARD_HEIGHT / 2)

    def _align_center_vertical(self, cards):
        """垂直居中对齐"""
        center_x = sum(card.scenePos().x() + card.CARD_WIDTH / 2 for card in cards) / len(cards)
        for card in cards:
            card.setPos(center_x - card.CARD_WIDTH / 2, card.scenePos().y())

    def _distribute_horizontal(self, cards):
        """水平均匀分布"""
        if len(cards) < 3:
            return

        cards_sorted = sorted(cards, key=lambda card: card.scenePos().x())
        leftmost = cards_sorted[0].scenePos().x()
        rightmost = cards_sorted[-1].scenePos().x()

        total_width = rightmost - leftmost
        gap = total_width / (len(cards) - 1)

        for i, card in enumerate(cards_sorted):
            new_x = leftmost + i * gap
            card.setPos(new_x, card.scenePos().y())

    def _distribute_vertical(self, cards):
        """垂直均匀分布"""
        if len(cards) < 3:
            return

        cards_sorted = sorted(cards, key=lambda card: card.scenePos().y())
        topmost = cards_sorted[0].scenePos().y()
        bottommost = cards_sorted[-1].scenePos().y()

        total_height = bottommost - topmost
        gap = total_height / (len(cards) - 1)

        for i, card in enumerate(cards_sorted):
            new_y = topmost + i * gap
            card.setPos(card.scenePos().x(), new_y)