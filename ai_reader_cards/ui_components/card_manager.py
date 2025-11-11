"""卡片管理器"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QInputDialog


class CardManager(QObject):
    """管理卡片的操作"""

    cards_linked = pyqtSignal(object, object)  # parent_card, child_card
    card_unlinked = pyqtSignal(object)  # card
    connection_deleted = pyqtSignal(object, object)  # from_card, to_card

    def __init__(self):
        super().__init__()

    def link_cards(self, cards):
        """连接选中的卡片"""
        if len(cards) != 2:
            return False, "请选择恰好两张卡片"

        parent_card, child_card = cards[0], cards[1]

        # 检查是否形成循环
        if self._would_create_cycle(parent_card, child_card):
            return False, "不能形成循环连接"

        child_card.set_parent_card(parent_card)
        self.cards_linked.emit(parent_card, child_card)
        return True, f"已建立连接: {parent_card.title_text} -> {child_card.title_text}"

    def unlink_card(self, card):
        """取消连接"""
        if not card.parent_card:
            return False, "该卡片没有父节点"

        parent_title = card.parent_card.title_text
        card.set_parent_card(None)
        self.card_unlinked.emit(card)
        return True, f"已取消连接: {parent_title} -> {card.title_text}"

    def delete_connection(self, card):
        """删除选中的连接"""
        connections = card.get_connections()
        if not connections:
            return False, "该卡片没有连接"

        # 显示连接列表供用户选择删除
        connection_list = []
        for conn in connections:
            connection_list.append(f"{conn['from_direction']} -> {conn['to_card'].title_text} ({conn['to_direction']})")

        connection_str, ok = QInputDialog.getItem(
            None, "选择要删除的连接", "连接列表:", connection_list, 0, False
        )

        if ok and connection_str:
            index = connection_list.index(connection_str)
            connection_to_delete = connections[index]
            card.remove_connection(connection_to_delete['to_card'])
            self.connection_deleted.emit(card, connection_to_delete['to_card'])
            return True, f"已删除连接: {card.title_text} -> {connection_to_delete['to_card'].title_text}"

        return False, "取消删除"

    def _would_create_cycle(self, parent, child):
        """检查是否形成循环"""
        # 简单的循环检测：如果child是parent的祖先，则形成循环
        current = parent
        while current:
            if current == child:
                return True
            current = current.parent_card
        return False

    def get_card_hierarchy(self, cards):
        """获取卡片层次结构"""
        root_cards = [card for card in cards if not card.parent_card]
        hierarchy = {}

        for card in root_cards:
            hierarchy[card] = self._get_subtree(card)

        return hierarchy

    def _get_subtree(self, card):
        """获取子树"""
        subtree = {}
        for child in card.child_cards:
            subtree[child] = self._get_subtree(child)
        return subtree