"""主窗口业务逻辑控制器"""

import os
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt6.QtCore import QObject, pyqtSignal

from ai_reader_cards.workers import AIWorkerThread
from ai_reader_cards.ai_api import AICardGenerator
from ai_reader_cards.card import KnowledgeCard
from ai_reader_cards.utils.storage import CardStorage
from ai_reader_cards.utils.shortcuts import ClipboardMonitor


class MainController(QObject):
    """处理主窗口业务逻辑"""

    # 状态信号
    status_updated = pyqtSignal(str)
    card_generated = pyqtSignal(object)
    generation_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.card_id_counter = 0
        self.ai_generator = None
        self.storage = CardStorage()
        self.current_worker = None
        self.clipboard_monitor = None

        # 连接管理
        self.connection_mode = False

    def connect_ai(self, model):
        """连接AI服务"""
        try:
            self.ai_generator = AICardGenerator(model=model)
            self.status_updated.emit(f"AI已连接 - 模型: {model}")
            return True, f"已成功连接到OpenAI API\n模型: {model}"
        except Exception as e:
            return False, f"无法连接到AI服务:\n{str(e)}"

    def on_model_changed(self, model):
        """模型改变"""
        if self.ai_generator:
            self.ai_generator.set_model(model)
            self.status_updated.emit(f"模型已切换: {model}")

    def open_text_file(self, filepath):
        """打开文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            filename = os.path.basename(filepath)
            self.status_updated.emit(f"已打开文本文件: {filename}")
            return content, filename
        except Exception as e:
            raise Exception(f"无法打开文本文件:\n{str(e)}")

    def open_pdf_file(self, filepath):
        """打开PDF文件"""
        try:
            import fitz
            doc = fitz.open(filepath) if hasattr(fitz, 'open') else fitz.Document(filepath)
            text_content = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += f"\n--- 第 {page_num + 1} 页 ---\n"
                text_content += page.get_text()
            doc.close()

            filename = os.path.basename(filepath)
            self.status_updated.emit(f"已打开PDF文件: {filename}")
            return text_content, filename
        except Exception as e:
            raise Exception(f"无法打开PDF文件:\n{str(e)}")

    def generate_card(self, text_content):
        """生成卡片"""
        if not self.ai_generator:
            raise Exception("请先连接AI服务")

        if len(text_content) < 10:
            raise Exception("文本过短，请输入至少10个字符")

        self.status_updated.emit("AI正在生成卡片...")

        # 创建工作线程
        self.current_worker = AIWorkerThread(self.ai_generator, text_content)
        self.current_worker.finished.connect(self._on_card_generated)
        self.current_worker.error.connect(self._on_generation_error)
        self.current_worker.start()

    def _on_card_generated(self, card_data):
        """卡片生成完成"""
        import random
        self.card_id_counter += 1

        card = KnowledgeCard(
            card_id=self.card_id_counter,
            title=card_data["title"],
            question=card_data["question"],
            answer=card_data["answer"],
            x=random.randint(-500, 500),
            y=random.randint(-300, 300)
        )

        self.card_generated.emit(card)
        self.status_updated.emit(f"卡片已生成: {card_data['title']}")
        self.auto_save()

    def _on_generation_error(self, error_msg):
        """卡片生成错误"""
        self.generation_error.emit(error_msg)
        self.status_updated.emit("卡片生成失败")

    def toggle_clipboard_monitor(self, enabled, callback):
        """切换剪贴板监控"""
        if enabled:
            if not self.ai_generator:
                return False, "请先连接AI服务"

            self.clipboard_monitor = ClipboardMonitor(callback)
            self.clipboard_monitor.start()
            self.status_updated.emit("剪贴板监控已启动")
            return True, "剪贴板监控已启动"
        else:
            if self.clipboard_monitor:
                self.clipboard_monitor.stop()
            self.status_updated.emit("剪贴板监控已停止")
            return True, "剪贴板监控已停止"

    def save_cards(self, cards):
        """保存卡片"""
        if not cards:
            return False, "画布中没有卡片"

        filepath, _ = QFileDialog.getSaveFileName(None, "保存卡片数据", "cards.json", "JSON文件 (*.json)")
        if filepath:
            self.storage.save_cards(cards, filepath)
            self.status_updated.emit(f"已保存 {len(cards)} 张卡片")
            return True, f"已保存 {len(cards)} 张卡片"
        return False, "取消保存"

    def load_cards(self):
        """加载卡片"""
        filepath, _ = QFileDialog.getOpenFileName(None, "加载卡片数据", "", "JSON文件 (*.json)")
        if not filepath:
            return None

        try:
            cards_data = self.storage.load_cards(filepath)
            loaded_cards = []
            card_map = {}

            for data in cards_data:
                self.card_id_counter = max(self.card_id_counter, data.get("id", 0))
                card = KnowledgeCard(
                    card_id=data["id"],
                    title=data["title"],
                    question=data["question"],
                    answer=data["answer"],
                    x=data.get("x", 0),
                    y=data.get("y", 0)
                )
                loaded_cards.append(card)
                card_map[data["id"]] = card

            # 重建父子关系
            for data in cards_data:
                if data.get("parent_id") and data["id"] in card_map and data["parent_id"] in card_map:
                    card_map[data["id"]].set_parent_card(card_map[data["parent_id"]])

            self.status_updated.emit(f"已加载 {len(cards_data)} 张卡片")
            return loaded_cards, card_map

        except Exception as e:
            raise Exception(f"无法加载卡片数据:\n{str(e)}")

    def export_markdown(self, cards):
        """导出Markdown"""
        if not cards:
            return False, "画布中没有卡片"

        filepath, _ = QFileDialog.getSaveFileName(None, "导出为Markdown", "cards.md", "Markdown文件 (*.md)")
        if filepath:
            self.storage.export_as_markdown(cards, filepath)
            self.status_updated.emit(f"已导出 {len(cards)} 张卡片")
            return True, f"已导出 {len(cards)} 张卡片"
        return False, "取消导出"

    def export_to_anki(self, cards):
        """导出卡片到Anki"""
        if not cards:
            return False, "画布中没有卡片"

        try:
            from ai_reader_cards.anki_connect import AnkiConnector
            connector = AnkiConnector()

            # 检查连接
            version = connector.check_connection()
            if not version:
                return False, "无法连接到Anki。请确保Anki正在运行且AnkiConnect插件已安装。"

            # 执行导出
            added, skipped, errors = connector.export_cards_to_anki(cards)

            if errors == 0:
                message = f"成功导出 {added} 张新卡片到Anki"
                if skipped > 0:
                    message += f"，跳过 {skipped} 张已存在卡片"
                self.status_updated.emit(message)
                return True, message
            else:
                message = f"导出完成：成功 {added}，跳过 {skipped}，错误 {errors}"
                self.status_updated.emit(message)
                return False, message

        except Exception as e:
            error_msg = f"导出到Anki失败: {str(e)}"
            self.status_updated.emit(error_msg)
            return False, error_msg

    def auto_save(self, cards=None):
        """自动保存"""
        # 这个方法需要在实际使用时传入cards参数
        pass

    def cleanup(self):
        """清理资源"""
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()