"""AnkiConnect API 模块 - 用于连接和添加卡片到Anki"""

import json
import urllib.request
import urllib.error
import os
from PyQt6.QtWidgets import QMessageBox

class AnkiConnector:
    """处理与 AnkiConnect 插件通信的类"""

    def __init__(self, port=8765):
        self.base_url = f"http://127.0.0.1:{port}"
        self.ANKI_CONNECT_VERSION = 6

    def _invoke(self, action, **params):
        """
        向AnkiConnect发送API请求
        """
        payload = {
            "action": action,
            "version": self.ANKI_CONNECT_VERSION,
            "params": params
        }
        payload_data = json.dumps(payload).encode('utf-8')

        try:
            req = urllib.request.Request(self.base_url, data=payload_data)
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                result = json.loads(response_data)

                if result.get("error"):
                    raise Exception(result["error"])

                return result.get("result")

        except urllib.error.URLError as e:
            # Anki未打开或插件未安装
            raise Exception("无法连接到 AnkiConnect。请确保:\n"
                            "1. Anki 正在运行。\n"
                            "2. AnkiConnect 插件已安装并激活。\n"
                            f"3. AnkiConnect 正在 {self.base_url} 监听。")
        except Exception as e:
            # 其他错误 (例如：JSON解析、API错误)
            raise Exception(f"Anki API 请求失败: {str(e)}")

    def check_connection(self):
        """检查AnkiConnect连接并返回版本号"""
        try:
            version = self._invoke("version")
            return version
        except Exception as e:
            QMessageBox.critical(None, "Anki连接失败", str(e))
            return None

    def get_deck_names(self):
        """获取所有Deck的名称"""
        return self._invoke("deckNames")

    def get_model_names(self):
        """获取所有Note Model的名称"""
        return self._invoke("modelNames")

    def add_note(self, deck_name, model_name, fields, tags=None):
        """
        添加一个新笔记 (卡片)

        Args:
            deck_name (str): Deck名称
            model_name (str): Note Model名称
            fields (dict): 字段字典 (例如: {"Front": "Q", "Back": "A"})
            tags (list): 标签列表

        Returns:
            int: 新笔记的ID
        """
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "options": {
                "allowDuplicate": False
            },
            "tags": tags or ["AI_MindMap"]
        }
        return self._invoke("addNote", note=note)

    def create_deck(self, deck_name):
        """创建牌组"""
        try:
            self._invoke("createDeck", deck=deck_name)
            return True
        except Exception as e:
            print(f"创建牌组时出错：{e}")
            return False

    def find_existing_notes(self, deck_name, id_tag_prefix="id_"):
        """查找已存在的笔记ID

        Args:
            deck_name: 牌组名称
            id_tag_prefix: ID标签前缀

        Returns:
            set: 已存在的卡片ID集合
        """
        try:
            # 查找所有包含ID标签的笔记
            query = f"deck:{deck_name} tag:{id_tag_prefix}*"
            note_ids = self._invoke("findNotes", query=query)

            existing_ids = set()
            for note_id in note_ids:
                # 获取笔记信息
                note_info = self._invoke("notesInfo", notes=[note_id])
                if note_info and len(note_info) > 0:
                    tags = note_info[0].get("tags", [])
                    # 提取ID标签
                    for tag in tags:
                        if tag.startswith(id_tag_prefix):
                            try:
                                card_id = int(tag[len(id_tag_prefix):])
                                existing_ids.add(card_id)
                            except ValueError:
                                continue
            return existing_ids
        except Exception as e:
            print(f"查找现有笔记时出错: {e}")
            return set()

    def sanitize_tag(self, s):
        """清理标签字符串"""
        return "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(s))[:50]

    def export_cards_to_anki(self, cards, deck_name="AI_MindMap_Import"):
        """导出卡片到Anki，只导出新卡片

        Args:
            cards: 卡片对象列表
            deck_name: Anki牌组名称

        Returns:
            tuple: (成功数量, 跳过数量, 错误数量)
        """
        try:
            # 检查连接
            if not self.check_connection():
                raise Exception("无法连接到Anki")

            # 创建牌组
            self.create_deck(deck_name)

            # 获取已存在的卡片ID
            existing_ids = self.find_existing_notes(deck_name)
            print(f"找到 {len(existing_ids)} 个已存在的卡片")

            added, skipped, errors = 0, 0, 0

            for card in cards:
                # 检查卡片是否已存在
                if card.card_id in existing_ids:
                    print(f"⚠️ 跳过重复卡片：{card.title_text} (id={card.card_id})")
                    skipped += 1
                    continue

                # 准备卡片内容 - 修复属性访问
                front = f"<b>{card.title_text}</b><br><br>{card.question_text}"
                back = card.answer_text

                # 准备标签
                tags = ["imported_mindmap"]
                if card.card_id:
                    tags.append(f"id_{card.card_id}")
                tags.append(self.sanitize_tag(card.title_text))

                try:
                    note_id = self.add_note(
                        deck_name,
                        "Basic",  # 使用Basic笔记类型
                        {"Front": front, "Back": back},
                        tags
                    )
                    print(f"✅ 已添加卡片：{card.title_text} (note_id={note_id}, card_id={card.card_id})")
                    added += 1
                except Exception as e:
                    msg = str(e).lower()
                    if "duplicate" in msg:
                        print(f"⚠️ 跳过重复卡片：{card.title_text}")
                        skipped += 1
                    else:
                        print(f"❌ 添加失败：{card.title_text} -> {e}")
                        errors += 1

            print(f"📊 导出完成：共 {len(cards)} 张 | 成功 {added} | 跳过 {skipped} | 错误 {errors}")
            return added, skipped, errors

        except Exception as e:
            raise Exception(f"导出到Anki失败: {str(e)}")