# 文件路径: ai_reader_cards\workers.py
"""工作线程模块"""

from PyQt6.QtCore import QThread, pyqtSignal


class AIWorkerThread(QThread):
    """AI处理工作线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ai_generator, text_content):
        super().__init__()
        self.ai_generator = ai_generator
        self.text_content = text_content

    def run(self):
        """在后台线程中执行AI请求"""
        try:
            card_data = self.ai_generator.generate_card(self.text_content)
            self.finished.emit(card_data)
        except Exception as e:
            self.error.emit(str(e))