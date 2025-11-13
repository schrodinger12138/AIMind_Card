"""搜索管理器"""

from PyQt6.QtCore import QObject, pyqtSignal


class SearchManager(QObject):
    """管理卡片搜索功能"""

    search_results_updated = pyqtSignal(list, str)  # results, keyword
    navigation_updated = pyqtSignal(int, int)  # current_index, total_results

    def __init__(self):
        super().__init__()
        self.search_results = []
        self.current_result_index = -1
        self.current_keyword = ""

    def search(self, cards, keyword, search_fields=None):
        """搜索卡片"""
        if not keyword:
            return []

        if search_fields is None:
            search_fields = ['title', 'question', 'answer']

        self.search_results = []
        self.current_keyword = keyword
        keyword_lower = keyword.lower()

        for card in cards:
            matched = False
            for field in search_fields:
                if hasattr(card, f'{field}_text'):
                    text = getattr(card, f'{field}_text', '').lower()
                    if keyword_lower in text:
                        matched = True
                        break

            if matched:
                self.search_results.append(card)

        self.search_results_updated.emit(self.search_results, keyword)
        return self.search_results

    def navigate_next(self):
        """导航到下一个结果"""
        if not self.search_results:
            return None

        self.current_result_index = (self.current_result_index + 1) % len(self.search_results)
        self.navigation_updated.emit(self.current_result_index + 1, len(self.search_results))
        return self.search_results[self.current_result_index]

    def navigate_previous(self):
        """导航到上一个结果"""
        if not self.search_results:
            return None

        self.current_result_index = (self.current_result_index - 1) % len(self.search_results)
        self.navigation_updated.emit(self.current_result_index + 1, len(self.search_results))
        return self.search_results[self.current_result_index]

    def clear_search(self):
        """清除搜索"""
        self.search_results.clear()
        self.current_result_index = -1
        self.current_keyword = ""

    def get_current_status(self):
        """获取当前搜索状态"""
        if not self.search_results:
            return 0, 0, self.current_keyword
        return self.current_result_index + 1, len(self.search_results), self.current_keyword