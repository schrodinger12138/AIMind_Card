# AI代码分析报告

> 本文档由AI自动分析项目中的Python代码并生成详细报告

## 项目概览

- **分析文件数**: 25
- **分析时间**: AIcard
- **使用模型**: GPT-3.5-turbo

---

## 📄 文件: ai_reader_cards\__init__.py

### 📋 功能总结

该模块用于处理AI阅读卡片与思维导图工具相关功能。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 处理AI阅读卡片
- 生成思维导图

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 🔍 缺少具体的函数或类实现

<details>
<summary>📝 查看源代码</summary>

```python
"""AI阅读卡片与思维导图工具"""
__version__ = "1.0.0"

```
</details>

---

## 📄 文件: ai_reader_cards\ai_api.py

### 📋 功能总结

AI API模块用于调用OpenAI API生成问题/答案卡片。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 调用OpenAI API生成问题/答案卡片
- 解析AI返回的JSON响应
- 设置使用的模型

### 💡 改进建议

- 📝 在异常处理中添加更多详细信息，以便更好地定位问题
- 📝 考虑对API请求进行错误处理和重试机制

### ⚠️ 潜在问题

- 🔍 未处理所有可能的异常情况，可能导致程序崩溃
- 🔍 API请求失败时可能会导致生成卡片失败

<details>
<summary>📝 查看源代码</summary>

```python
"""AI API模块 - 调用OpenAI API生成问题/答案卡片"""

import os
import json
import re
from openai import OpenAI




API_BASE = "https://api.chatanywhere.tech/v1"
OPENAI_API_KEY = "sk-lwkQzJYwYdJwbQ4DaAlM3Ti6pgMCzEgztBjREyOlYFPLPDQP"


class AICardGenerator:
    """AI卡片生成器"""

    def __init__(self, model="gpt-3.5-turbo"):  # ✅ 改成 gpt-3.5-turbo
        api_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
        if not api_key:
            raise RuntimeError("未检测到 OPENAI_API_KEY 环境变量，请先设置API密钥")

        self.client = OpenAI(
            api_key=api_key,
            base_url=API_BASE  # ✅ 加上自定义代理
        )
        self.model = model
    
    def generate_card(self, text_content):
        """从文本内容生成学习卡片
        
        Args:
            text_content: 要转换为卡片的文本内容
            
        Returns:
            dict: 包含title, question, answer的字典
        """
        prompt = f"""请把下面的文本提炼成一个学习卡片，返回JSON格式，包含以下字段：
- title: 一句精简的标题（6-20字）
- question: 一个考察该片段核心概念的问题
- answer: 对问题的简洁回答（不超过150字）

返回内容必须是严格的JSON对象，不要添加任何额外说明。

文本内容：
{text_content}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的知识卡片生成助手，擅长将复杂内容转换为结构化的学习卡片。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result_text = (response.choices[0].message.content or "").strip()
            
            # 解析JSON响应
            card_data = self._parse_json_response(result_text)
            
            # 确保所有必需字段都存在
            card = {
                "title": card_data.get("title", "")[:100],
                "question": card_data.get("question", "")[:200],
                "answer": card_data.get("answer", "")[:500],
                "source_text": text_content[:500]
            }
            
            return card
            
        except Exception as e:
            raise RuntimeError(f"AI卡片生成失败: {str(e)}")
    
    def _parse_json_response(self, response_text):
        """解析AI返回的JSON响应
        
        Args:
            response_text: AI返回的文本
            
        Returns:
            dict: 解析后的JSON对象
        """
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 解析失败，返回默认结构
                return {
                    "title": "解析失败",
                    "question": "AI返回内容无法解析",
                    "answer": response_text[:200]
                }
    
    def set_model(self, model):
        """设置使用的模型
        
        Args:
            model: 模型名称
        """
        self.model = model

```
</details>

---

## 📄 文件: ai_reader_cards\anki_connect.py

### 📋 功能总结

AnkiConnect API 模块 - 用于连接和添加卡片到Anki

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 与 AnkiConnect 插件通信
- 发送API请求到AnkiConnect
- 检查连接状态
- 获取Deck和Note Model名称
- 添加新笔记到Anki

### 💡 改进建议

- 📝 添加更多错误处理机制，提高代码的健壮性
- 📝 考虑增加日志记录功能，便于排查问题
- 📝 优化网络请求部分的性能，减少不必要的数据传输

### ⚠️ 潜在问题

- 🔍 依赖于AnkiConnect插件，插件更新可能导致兼容性问题
- 🔍 部分异常情况下可能会导致程序崩溃，需要更全面的异常处理

<details>
<summary>📝 查看源代码</summary>

```python
"""AnkiConnect API 模块 - 用于连接和添加卡片到Anki"""

import json
import urllib.request
import urllib.error
from PyQt6.QtWidgets import QMessageBox

class AnkiConnector:
    """处理与 AnkiConnect 插件通信的类"""

    def __init__(self, port=8765):
        self.base_url = f"http://127.0.0.1:{port}"

    def _invoke(self, action, **params):
        """
        向AnkiConnect发送API请求
        """
        payload = {
            "action": action,
            "version": 6,
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

    def add_note(self, deck_name, model_name, fields):
        """
        添加一个新笔记 (卡片)

        Args:
            deck_name (str): Deck名称
            model_name (str): Note Model名称
            fields (dict): 字段字典 (例如: {"Front": "Q", "Back": "A"})

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
            "tags": ["AI_MindMap"]
        }
        return self._invoke("addNote", note=note)
```
</details>

---

## 📄 文件: ai_reader_cards\card.py

### 📋 功能总结

定义了连接点图形项和知识卡片类，实现了可视化知识卡片的功能。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 定义了连接点图形项ConnectionPoint，实现了连接点的样式和交互效果。
- 定义了知识卡片类KnowledgeCard，实现了可拖动、可编辑的知识卡片功能。
- 知识卡片包含标题、问题、答案等信息，支持编辑、添加子节点、连接等操作。

### 💡 改进建议

- 📝 在create_text_items方法中，存在注释中提到的代码缺失，需要完善。
- 📝 可以进一步优化知识卡片类的布局和样式，提升用户体验。
- 📝 考虑添加更多交互功能，如拖拽连接、自动布局等，增强可视化效果。

### ⚠️ 潜在问题

- 🔍 部分方法缺少完整的实现，如create_text_items方法中的代码缺失。
- 🔍 可能存在性能瓶颈，特别是在处理大量知识卡片和连接时，需要进行性能优化。
- 🔍 需要注意连接点的位置计算和更新逻辑，确保连接功能的准确性和稳定性。

<details>
<summary>📝 查看源代码</summary>

```python
"""卡片模块 - 定义可视化知识卡片"""

from PyQt6.QtWidgets import (QGraphicsRectItem, QGraphicsTextItem,
                              QGraphicsItem, QGraphicsSceneMouseEvent,
                              QInputDialog, QMessageBox, QMenu,
                              QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QTextEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (QPen, QBrush, QColor, QFont, QPainterPath,
                         QCursor, QAction, QPainter)
class ConnectionPoint(QGraphicsRectItem):
    """连接点图形项"""

    def __init__(self, parent_card, direction):
        super().__init__(-4, -4, 8, 8)  # 8x8像素的连接点
        self.parent_card = parent_card
        self.direction = direction
        self.setBrush(QBrush(QColor(70, 130, 180)))
        self.setPen(QPen(QColor(255, 255, 255), 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.setZValue(100)  # 确保连接点在最上层

    def hoverEnterEvent(self, event):
        """鼠标悬停时改变颜色"""
        self.setBrush(QBrush(QColor(255, 140, 0)))  # 悬停时橙色
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """鼠标离开时恢复颜色"""
        self.setBrush(QBrush(QColor(70, 130, 180)))  # 正常时蓝色
        super().hoverLeaveEvent(event)


"""卡片模块 - 定义可视化知识卡片"""

from PyQt6.QtWidgets import (QGraphicsRectItem, QGraphicsTextItem,
                             QGraphicsItem, QGraphicsSceneMouseEvent,
                             QInputDialog, QMessageBox, QMenu,
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (QPen, QBrush, QColor, QFont, QPainterPath,
                         QCursor, QAction, QPainter)


class CardEditDialog(QDialog):
    """卡片编辑对话框"""
    # ... 保持原有代码不变 ...


class KnowledgeCard(QGraphicsRectItem):
    """知识卡片 - 可拖动、可编辑的卡片"""

    CARD_WIDTH = 280
    CARD_HEIGHT = 180
    HEADER_HEIGHT = 35
    BORDER_RADIUS = 8

    # 定义信号
    request_edit = pyqtSignal(object)  # 请求编辑卡片
    request_add_child = pyqtSignal(object)  # 请求添加子节点
    content_changed = pyqtSignal(object)  # 内容改变信号
    connection_started = pyqtSignal(object, str, QPointF)  # 开始连接信号

    def __init__(self, card_id, title, question, answer, x=0, y=0):
        """初始化卡片"""
        super().__init__(0, 0, self.CARD_WIDTH, self.CARD_HEIGHT)

        self.card_id = card_id
        self.title_text = title
        self.question_text = question
        self.answer_text = answer
        self.parent_card = None
        self.child_cards = []
        self.connections = []  # 存储连接信息
        # 修复：添加 connection_points 初始化
        self.connection_points = {}

        # 设置卡片属性
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # 设置卡片样式
        self.setPen(QPen(QColor(100, 100, 100), 2))
        self.setBrush(QBrush(QColor(255, 255, 255)))

        # 创建文本显示项
        self.create_text_items()

        # 计算连接点位置
        self.update_connection_points()

    def create_text_items(self):
        """创建文本显示项"""
        # 创建标题文本
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(self._truncate_text(self.title_text, 30))
        self.title_item.setPos(10, 5)
        title_font = QFont("Arial", 11, QFont.Weight.Bold)
        self.title_item.setFont(title_font)
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))
        self.title_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # 创建问题文本
        self.question_item = QGraphicsTextItem(self)
        self.question_item.setPlainText("Q: " + self._truncate_text(self.question_text, 60))
        self.question_item.setPos(10, self.HEADER_HEIGHT + 5)
        question_font = QFont("Arial", 9, QFont.Weight.Bold)
        self.question_item.setFont(question_font)
        self.question_item.setDefaultTextColor(QColor(70, 130, 180))
        self.question_item.setTextWidth(self.CARD_WIDTH - 20)
        self.question_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # 创建答案文本
        self.answer_item = QGraphicsTextItem(self)
        self.answer_item.setPlainText("A: " + self._truncate_text(self.answer_text, 120))
        self.answer_item.setPos(10, self.HEADER_HEIGHT + 50)
        answer_font = QFont("Arial", 8)
        self.answer_item.setFont(answer_font)
        self.answer_item.setDefaultTextColor(QColor(60, 60, 60))
        self.answer_item.setTextWidth(self.CARD_WIDTH - 20)
        self.answer_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    # 修复：添加缺失的连接点方法
    def update_connection_points(self):
        """更新连接点位置"""
        self.connection_points = {
            'top': QPointF(self.CARD_WIDTH / 2, 0),
            'right': QPointF(self.CARD_WIDTH, self.CARD_HEIGHT / 2),
            'bottom': QPointF(self.CARD_WIDTH / 2, self.CARD_HEIGHT),
            'left': QPointF(0, self.CARD_HEIGHT / 2)
        }

    def get_connection_point(self, direction):
        """获取指定方向的连接点"""
        if direction in self.connection_points:
            return self.mapToScene(self.connection_points[direction])
        return self.get_center_pos()

    def get_nearest_connection_point(self, target_point):
        """获取距离目标点最近的连接点"""
        local_target = self.mapFromScene(target_point)

        min_distance = float('inf')
        nearest_direction = 'bottom'

        for direction, point in self.connection_points.items():
            distance = (point - local_target).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                nearest_direction = direction

        return nearest_direction, self.get_connection_point(nearest_direction)

    def add_connection(self, from_direction, to_card, to_direction):
        """添加连接关系"""
        connection = {
            'from_direction': from_direction,
            'to_card': to_card,
            'to_direction': to_direction
        }
        self.connections.append(connection)
        to_card.set_parent_card(self)

    def remove_connection(self, to_card):
        """移除连接"""
        self.connections = [conn for conn in self.connections if conn['to_card'] != to_card]
        if to_card in self.child_cards:
            self.child_cards.remove(to_card)
        to_card.set_parent_card(None)

    def get_connections(self):
        """获取所有连接"""
        return self.connections

    # 修复：添加缺失的鼠标事件方法
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在连接点附近
            click_pos = event.pos()
            for direction, point in self.connection_points.items():
                if (point - click_pos).manhattanLength() < 20:  # 点击在连接点附近
                    scene_point = self.mapToScene(point)
                    self.connection_started.emit(self, direction, scene_point)
                    event.accept()
                    return

        super().mousePressEvent(event)

    def _truncate_text(self, text, max_length):
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def set_parent_card(self, parent):
        """设置父卡片"""
        if self.parent_card:
            self.parent_card.child_cards.remove(self)
        self.parent_card = parent
        if parent and self not in parent.child_cards:
            parent.child_cards.append(self)

    def get_center_pos(self):
        """获取卡片中心位置"""
        return QPointF(
            self.pos().x() + self.CARD_WIDTH / 2,
            self.pos().y() + self.CARD_HEIGHT / 2
        )

    def to_dict(self):
        """转换为字典格式用于保存"""
        return {
            "id": self.card_id,
            "title": self.title_text,
            "question": self.question_text,
            "answer": self.answer_text,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "parent_id": self.parent_card.card_id if self.parent_card else None
        }

    def paint(self, painter, option, widget=None):
        """自定义绘制卡片"""
        # 绘制阴影效果
        shadow_rect = QRectF(3, 3, self.CARD_WIDTH, self.CARD_HEIGHT)
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # 绘制主卡片背景
        card_rect = QRectF(0, 0, self.CARD_WIDTH, self.CARD_HEIGHT)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRoundedRect(card_rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # 绘制标题栏背景
        header_rect = QRectF(0, 0, self.CARD_WIDTH, self.HEADER_HEIGHT)
        if self.isSelected():
            painter.setBrush(QBrush(QColor(255, 140, 0)))  # 选中时橙色
        else:
            painter.setBrush(QBrush(QColor(70, 130, 180)))  # 默认蓝色
        painter.setPen(Qt.PenStyle.NoPen)

        # 绘制圆角标题栏
        path = QPainterPath()
        path.moveTo(0, self.HEADER_HEIGHT)
        path.lineTo(0, self.BORDER_RADIUS)
        path.quadTo(0, 0, self.BORDER_RADIUS, 0)
        path.lineTo(self.CARD_WIDTH - self.BORDER_RADIUS, 0)
        path.quadTo(self.CARD_WIDTH, 0, self.CARD_WIDTH, self.BORDER_RADIUS)
        path.lineTo(self.CARD_WIDTH, self.HEADER_HEIGHT)
        path.closeSubpath()
        painter.drawPath(path)

        # 绘制连接点（仅在选中时显示）
        # 绘制连接点（仅在选中时显示）
        if self.isSelected():
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(70, 130, 180), 2))

            for point in self.connection_points.values():
                # 使用QRectF来绘制椭圆
                painter.drawEllipse(QRectF(point.x() - 4, point.y() - 4, 8, 8))


    def itemChange(self, change, value):
        """卡片位置改变时的回调"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # 更新连接点位置
            self.update_connection_points()
            # 通知场景更新连线
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)

    def get_bottom_center(self):
        """获取卡片底部中心位置"""
        return QPointF(
            self.pos().x() + self.CARD_WIDTH / 2,
            self.pos().y() + self.CARD_HEIGHT
        )

    def get_top_center(self):
        """获取卡片顶部中心位置"""
        return QPointF(
            self.pos().x() + self.CARD_WIDTH / 2,
            self.pos().y()
        )
```
</details>

---

## 📄 文件: ai_reader_cards\hh.py

### 📋 功能总结

将指定目录及其子目录下的所有 .py 文件合并为一个 Markdown 文件，每个文件带有路径标识。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 遍历指定目录及其子目录下的所有 .py 文件
- 将每个文件内容以 Markdown 代码块格式写入输出文件
- 处理异常情况，如无法读取文件

### 💡 改进建议

- 📝 添加参数校验，确保 root_dir 是有效的目录路径
- 📝 考虑增加参数控制是否包含子目录下的 .py 文件
- 📝 优化文件读取方式，避免一次性读取大文件内容

### ⚠️ 潜在问题

- 🔍 在处理大量文件时，可能会占用较多内存，需要注意内存消耗
- 🔍 未处理文件编码问题，可能导致读取失败或乱码

<details>
<summary>📝 查看源代码</summary>

```python
import os

def merge_py_to_markdown(root_dir=None, output_filename="all_code.md"):
    """
    合并指定目录及其子目录下的所有 .py 文件为一个 Markdown 文件。
    每个文件会带有路径标识，并以 Markdown 代码块格式包裹。
    """

    # 若未指定路径，则默认当前脚本所在目录
    if root_dir is None:
        root_dir = os.getcwd()

    # 输出文件路径
    output_file = os.path.join(root_dir, output_filename)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# 合并的 Python 代码文件\n\n")

        # 遍历目录树
        for dirpath, _, filenames in os.walk(root_dir):
            for file in filenames:
                if file.endswith(".py"):
                    filepath = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(filepath, root_dir)

                    # 跳过输出文件自身
                    if os.path.abspath(filepath) == os.path.abspath(output_file):
                        continue

                    out.write(f"# 文件路径: {rel_path}\n")
                    out.write("```python\n")
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"# 无法读取文件: {e}\n")
                    out.write("\n```\n\n---\n\n")

    print(f"✅ 所有 .py 文件内容已合并到: {output_file}")

if __name__ == "__main__":
    merge_py_to_markdown()

```
</details>

---

## 📄 文件: ai_reader_cards\mindmap.py

### 📋 功能总结

{'ConnectionLine': '连接线类，用于表示两个卡片之间的连接关系', 'CardSearchTool': '卡片搜索工具类，用于在场景中搜索卡片并高亮显示搜索结果'}

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 连接线类用于表示卡片之间的连接关系
- 卡片搜索工具类支持关键词搜索和高亮显示搜索结果

### 💡 改进建议

- 📝 在搜索方法中，可以添加对搜索结果为空的处理逻辑
- 📝 在导航到下一个结果方法中，修复返回值错误的问题

### ⚠️ 潜在问题

- 🔍 在搜索方法中，未处理搜索结果为空的情况，可能导致逻辑错误
- 🔍 在导航到下一个结果方法中，返回值应该是当前搜索结果，而非错误的属性名

<details>
<summary>📝 查看源代码</summary>

```python
"""思维导图模块 - 管理卡片画布与连线"""

import xmind
from xmind.core.const import TOPIC_DETACHED
from xmind.core.markerref import MarkerId

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (QPen, QColor, QPainter, QPainterPath,
                         QPolygonF, QTransform, QLinearGradient)

# 修复：添加正确的导入
from ai_reader_cards.card import KnowledgeCard


class ConnectionLine:
    """连接线类"""

    def __init__(self, from_card, from_direction, to_card, to_direction):
        self.from_card = from_card
        self.from_direction = from_direction
        self.to_card = to_card
        self.to_direction = to_direction

    def get_points(self):
        """获取连接的起点和终点"""
        from_point = self.from_card.get_connection_point(self.from_direction)
        to_point = self.to_card.get_connection_point(self.to_direction)
        return from_point, to_point

class CardSearchTool:
    """卡片搜索工具类"""

    def __init__(self, scene):
        self.scene = scene
        self.search_results = []
        self.current_result_index = -1
        self.original_styles = {}  # 保存原始样式

    def search(self, keyword, search_fields=None):
        """搜索卡片
        Args:
            keyword: 搜索关键词
            search_fields: 搜索字段列表，如 ['title', 'question', 'answer']
        """
        if not keyword:
            return []

        if search_fields is None:
            search_fields = ['title', 'question', 'answer']

        # 恢复之前的结果样式
        self.clear_highlights()

        self.search_results = []
        keyword_lower = keyword.lower()

        for card in self.scene.cards:
            matched = False
            match_data = {}

            # 检查各个字段
            for field in search_fields:
                if hasattr(card, f'{field}_text'):
                    text = getattr(card, f'{field}_text', '').lower()
                    if keyword_lower in text:
                        matched = True
                        match_data[field] = {
                            'text': getattr(card, f'{field}_text', ''),
                            'positions': self._find_match_positions(text, keyword_lower)
                        }

            if matched:
                self.search_results.append((card, match_data))
                # 保存原始样式
                self._save_original_style(card)

        # 高亮显示结果
        self._highlight_results()
        return self.search_results

    def _find_match_positions(self, text, keyword):
        """查找匹配位置"""
        positions = []
        start = 0
        text_lower = text.lower()

        while True:
            pos = text_lower.find(keyword, start)
            if pos == -1:
                break
            positions.append((pos, pos + len(keyword)))
            start = pos + 1

        return positions

    def _save_original_style(self, card):
        """保存卡片原始样式"""
        if card not in self.original_styles:
            self.original_styles[card] = {
                'pen': card.pen(),
                'brush': card.brush(),
                'z_value': card.zValue()
            }

    def _highlight_results(self):
        """高亮显示搜索结果"""
        for card, _ in self.search_results:
            # 设置高亮样式
            highlight_pen = QPen(QColor(255, 215, 0), 3)  # 金色边框
            card.setPen(highlight_pen)
            card.setZValue(100)  # 置于顶层

    def clear_highlights(self):
        """清除高亮显示"""
        for card, original_style in self.original_styles.items():
            card.setPen(original_style['pen'])
            card.setBrush(original_style['brush'])
            card.setZValue(original_style['z_value'])

        self.original_styles.clear()
        self.search_results.clear()
        self.current_result_index = -1

    def navigate_to_next(self):
        """导航到下一个结果"""
        if not self.search_results:
            return None

        self.current_result_index = (self.current_result_index + 1) % len(self.search_results)
        return self._focus_current_result()

    def navigate_to_previous(self):
        """导航到上一个结果"""
        if not self.search_results:
            return None

        self.current_result_index = (self.current_result_index - 1) % len(self.search_results)
        return self._focus_current_result()

    def _focus_current_result(self):
        """聚焦当前结果"""
        if 0 <= self.current_result_index < len(self.search_results):
            card, match_data = self.search_results[self.current_result_index]

            # 确保卡片可见
            if self.scene.views():
                view = self.scene.views()[0]
                view.centerOn(card)

            return card, match_data, self.current_result_index + 1, len(self.search_results)
        return None
class CardAlignmentTool:
    """卡片对齐工具类"""

    @staticmethod
    def align_left(cards):
        """左对齐"""
        if not cards or len(cards) < 2:
            return
        min_x = min(card.scenePos().x() for card in cards)
        for card in cards:
            card.setPos(min_x, card.scenePos().y())

    @staticmethod
    def align_right(cards):
        """右对齐"""
        if not cards or len(cards) < 2:
            return
        max_x = max(card.scenePos().x() + card.CARD_WIDTH for card in cards)
        for card in cards:
            card.setPos(max_x - card.CARD_WIDTH, card.scenePos().y())

    @staticmethod
    def align_top(cards):
        """顶对齐"""
        if not cards or len(cards) < 2:
            return
        min_y = min(card.scenePos().y() for card in cards)
        for card in cards:
            card.setPos(card.scenePos().x(), min_y)

    @staticmethod
    def align_bottom(cards):
        """底对齐"""
        if not cards or len(cards) < 2:
            return
        max_y = max(card.scenePos().y() + card.CARD_HEIGHT for card in cards)
        for card in cards:
            card.setPos(card.scenePos().x(), max_y - card.CARD_HEIGHT)

    @staticmethod
    def align_center_horizontal(cards):
        """水平居中对齐"""
        if not cards or len(cards) < 2:
            return
        center_y = sum(card.scenePos().y() + card.CARD_HEIGHT / 2 for card in cards) / len(cards)
        for card in cards:
            card.setPos(card.scenePos().x(), center_y - card.CARD_HEIGHT / 2)

    @staticmethod
    def align_center_vertical(cards):
        """垂直居中对齐"""
        if not cards or len(cards) < 2:
            return
        center_x = sum(card.scenePos().x() + card.CARD_WIDTH / 2 for card in cards) / len(cards)
        for card in cards:
            card.setPos(center_x - card.CARD_WIDTH / 2, card.scenePos().y())

    @staticmethod
    def distribute_horizontal(cards):
        """水平均匀分布"""
        if not cards or len(cards) < 3:
            return

        cards_sorted = sorted(cards, key=lambda card: card.scenePos().x())
        leftmost = cards_sorted[0].scenePos().x()
        rightmost = cards_sorted[-1].scenePos().x()

        total_width = rightmost - leftmost
        gap = total_width / (len(cards) - 1)

        for i, card in enumerate(cards_sorted):
            new_x = leftmost + i * gap
            card.setPos(new_x, card.scenePos().y())

    @staticmethod
    def distribute_vertical(cards):
        """垂直均匀分布"""
        if not cards or len(cards) < 3:
            return

        cards_sorted = sorted(cards, key=lambda card: card.scenePos().y())
        topmost = cards_sorted[0].scenePos().y()
        bottommost = cards_sorted[-1].scenePos().y()

        total_height = bottommost - topmost
        gap = total_height / (len(cards) - 1)

        for i, card in enumerate(cards_sorted):
            new_y = topmost + i * gap
            card.setPos(card.scenePos().x(), new_y)

    @staticmethod
    def arrange_hierarchy(root_card, horizontal_spacing=200, vertical_spacing=150):
        """按层次结构排列卡片"""
        if not root_card:
            return

        def arrange_subtree(card, start_x, start_y, level):
            """递归排列子树"""
            if not card.child_cards:
                return start_x

            current_x = start_x
            for child in card.child_cards:
                # 设置子卡片位置
                child.setPos(current_x, start_y + level * vertical_spacing)
                # 递归排列子卡片的子树
                current_x = arrange_subtree(child, current_x, start_y, level + 1)
                current_x += horizontal_spacing

            return current_x

        # 从根节点开始排列
        root_card.setPos(0, 0)
        arrange_subtree(root_card, -horizontal_spacing, vertical_spacing, 1)


class MindMapScene(QGraphicsScene):
    """思维导图场景 - 支持绘画功能"""

    # 添加连接相关信号
    connection_started = pyqtSignal(object, str, QPointF)  # 卡片，方向，位置

    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.cards = []
        self.root_card = None  # 根节点卡片

        # 连线相关属性
        self.connecting = False
        self.connection_start_card = None
        self.connection_start_direction = None
        self.temp_connection_line = None
        self.temp_end_point = None

        # 绘画相关属性
        self.drawing = False
        self.last_point = QPointF()
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3
        self.current_path_item = None
        self.drawing_mode = False
        self.drawn_paths = []  # 存储所有绘画路径

        # 修复：正确初始化工具类
        self.alignment_tool = CardAlignmentTool()
        self.search_tool = CardSearchTool(self)

    # 修复：添加缺失的方法
    def start_connection(self, from_card, from_direction, start_point):
        """开始创建连接"""
        self.connecting = True
        self.connection_start_card = from_card
        self.connection_start_direction = from_direction
        self.temp_end_point = start_point

        # 创建临时连线
        pen = QPen(QColor(255, 140, 0), 2, Qt.PenStyle.DashLine)
        self.temp_connection_line = self.addLine(
            start_point.x(), start_point.y(),
            start_point.x(), start_point.y(),
            pen
        )

    def clear_drawings(self):
        """清除所有绘画"""
        # 移除所有绘画路径
        for path in self.drawn_paths:
            self.removeItem(path)
        self.drawn_paths.clear()
        self.update()

    def update_connection(self, end_point):
        """更新临时连接线"""
        if self.connecting and self.temp_connection_line:
            start_point = self.connection_start_card.get_connection_point(
                self.connection_start_direction
            )
            self.temp_connection_line.setLine(
                start_point.x(), start_point.y(),
                end_point.x(), end_point.y()
            )
            self.temp_end_point = end_point

    def finish_connection(self, to_card, to_direction):
        """完成连接创建"""
        if self.connecting and self.connection_start_card and to_card:
            # 检查是否连接到自身
            if self.connection_start_card == to_card:
                self.cancel_connection()
                return False

            # 创建连接
            self.connection_start_card.add_connection(
                self.connection_start_direction,
                to_card,
                to_direction
            )

            # 更新场景
            self.removeItem(self.temp_connection_line)
            self.connecting = False
            self.connection_start_card = None
            self.connection_start_direction = None
            self.temp_connection_line = None
            self.temp_end_point = None

            self.update()
            return True

        self.cancel_connection()
        return False

    def cancel_connection(self):
        """取消连接创建"""
        if self.temp_connection_line:
            self.removeItem(self.temp_connection_line)
        self.connecting = False
        self.connection_start_card = None
        self.connection_start_direction = None
        self.temp_connection_line = None
        self.temp_end_point = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.connecting:
            # 更新临时连接线
            self.update_connection(event.scenePos())
            event.accept()
        elif self.drawing and self.drawing_mode and self.current_path_item is not None:
            current_point = event.scenePos()
            self.current_path.lineTo(current_point)
            self.current_path_item.setPath(self.current_path)
            self.last_point = current_point
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.connecting and event.button() == Qt.MouseButton.LeftButton:
            # 检查是否释放到卡片上
            items = self.items(event.scenePos())
            for item in items:
                if isinstance(item, KnowledgeCard) and item != self.connection_start_card:
                    # 找到最近的连接点
                    direction, point = item.get_nearest_connection_point(
                        self.connection_start_card.get_center_pos()
                    )
                    self.finish_connection(item, direction)
                    event.accept()
                    return

            # 如果没有释放到卡片上，取消连接
            self.cancel_connection()
            event.accept()
        elif self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.current_path_item = None
            self.current_path = None
            event.accept()

        super().mouseReleaseEvent(event)

    # 修复：添加缺失的卡片管理方法
    def add_card(self, card):
        """添加卡片到场景"""
        self.addItem(card)
        self.cards.append(card)

        # 连接卡片的连接信号
        if hasattr(card, 'connection_started'):
            card.connection_started.connect(self.start_connection)

    def remove_card(self, card):
        """从场景移除卡片"""
        if card in self.cards:
            self.cards.remove(card)
        self.removeItem(card)

    def get_all_cards(self):
        """获取所有卡片"""
        return self.cards

    def get_selected_cards(self):
        """获取选中的卡片"""
        return [item for item in self.selectedItems() if isinstance(item, KnowledgeCard)]

    def clear_canvas(self):
        """清空画布"""
        for card in self.cards[:]:
            self.remove_card(card)
        self.cards.clear()

    def export_to_xmind(self, filename):
        """导出到XMind文件"""
        self.workbook = xmind.load(filename)
        self.sheet = self.workbook.getPrimarySheet()
        self.sheet.setTitle("思维导图")

        # 如果有根节点卡片，从根节点开始导出
        if self.root_card:
            root_topic = self.sheet.getRootTopic()
            root_topic.setTitle(self.root_card.get_question())  # 使用问题作为标题

            # 添加答案作为备注
            if self.root_card.get_answer():
                root_topic.setTitle(f"{self.root_card.get_question()}\nA: {self.root_card.get_answer()}")

            # 递归添加子节点
            self._add_card_to_xmind(self.root_card, root_topic)

        # 保存文件
        xmind.save(self.workbook, path=filename)

    def import_from_xmind(self, filename):
        """从XMind文件导入"""
        from ai_reader_cards.card import Card  # 导入Card类

        self.workbook = xmind.load(filename)
        self.sheet = self.workbook.getPrimarySheet()
        root_topic = self.sheet.getRootTopic()

        # 清除现有卡片
        for card in self.cards:
            self.removeItem(card)
        self.cards.clear()

        # 创建根节点卡片
        title = root_topic.getTitle()
        # 分离问题和答案
        if "\nA: " in title:
            question, answer = title.split("\nA: ", 1)
        else:
            question = title
            answer = ""

        self.root_card = Card(question, answer)
        self.root_card.setPos(0, 0)  # 根节点放在中心
        self.addItem(self.root_card)
        self.cards.append(self.root_card)

        # 递归导入子节点
        self._import_topics_from_xmind(root_topic, self.root_card)

    def _add_card_to_xmind(self, card, parent_topic):
        """递归将卡片添加到XMind主题中"""
        # 处理子卡片
        for child_card in card.child_cards:
            sub_topic = parent_topic.addSubTopic()
            sub_topic.setTitle(child_card.get_question())

            # 添加答案作为备注
            if child_card.get_answer():
                sub_topic.setTitle(f"{child_card.get_question()}\nA: {child_card.get_answer()}")

            # 递归处理子节点
            self._add_card_to_xmind(child_card, sub_topic)

    def _import_topics_from_xmind(self, topic, parent_card):
        """递归从XMind主题导入卡片"""
        from ai_reader_cards.card import Card  # 导入Card类

        # 获取子主题
        for sub_topic in topic.getSubTopics():
            title = sub_topic.getTitle()
            # 分离问题和答案
            if "\nA: " in title:
                question, answer = title.split("\nA: ", 1)
            else:
                question = title
                answer = ""

            # 创建新卡片
            child_card = Card(question, answer)

            # 设置卡片位置（相对于父卡片）
            offset_x = len(parent_card.child_cards) * 200  # 水平偏移
            offset_y = 150  # 垂直偏移
            child_card.setPos(parent_card.pos().x() + offset_x,
                            parent_card.pos().y() + offset_y)

            # 添加到场景
            self.addItem(child_card)
            self.cards.append(child_card)

            # 建立父子关系
            parent_card.add_child(child_card)
            child_card.set_parent(parent_card)

            # 递归处理子主题
            self._import_topics_from_xmind(sub_topic, child_card)

    def add_card(self, card):
        """添加卡片到场景"""
        self.addItem(card)
        self.cards.append(card)

    def remove_card(self, card):
        """从场景移除卡片"""
        if card in self.cards:
            self.cards.remove(card)
        self.removeItem(card)

    def get_all_cards(self):
        """获取所有卡片"""
        return self.cards

    def drawBackground(self, painter, rect):
        """绘制网格背景"""
        super().drawBackground(painter, rect)

        # 绘制淡灰色网格
        painter.setPen(QPen(QColor(240, 240, 240), 0.5))

        grid_size = 50
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # 绘制垂直线
        x = left
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += grid_size

        # 绘制水平线
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += grid_size

    def drawForeground(self, painter, rect):
        """绘制前景（连线）"""
        super().drawForeground(painter, rect)

        # 绘制所有父子连线
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for card in self.cards:
            if card.parent_card:
                self._draw_smart_connection(painter, card.parent_card, card)

    def _draw_smart_connection(self, painter, parent_card, child_card):
        """绘制智能连接线 - 自动选择最近的连接点"""

        # 获取最近的连接点对
        parent_direction, parent_point = parent_card.get_nearest_connection_point(
            child_card.get_center_pos()
        )
        child_direction, child_point = child_card.get_nearest_connection_point(
            parent_card.get_center_pos()
        )

        # 创建贝塞尔曲线路径
        path = QPainterPath()
        path.moveTo(parent_point)

        # 根据连接方向计算控制点
        control1, control2 = self._calculate_control_points(
            parent_point, parent_direction,
            child_point, child_direction
        )

        # 绘制三次贝塞尔曲线
        path.cubicTo(control1, control2, child_point)

        # 创建渐变画笔
        gradient = QLinearGradient(parent_point, child_point)
        gradient.setColorAt(0, QColor(70, 130, 180, 200))
        gradient.setColorAt(1, QColor(100, 180, 255, 200))

        # 设置画笔
        pen = QPen(gradient, 2.5)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # 绘制路径
        painter.drawPath(path)

        # 绘制优雅的箭头
        self._draw_elegant_arrow(painter, control2, child_point, child_direction)

    def _calculate_control_points(self, start_point, start_direction, end_point, end_direction):
        """根据连接方向计算贝塞尔曲线控制点"""

        # 计算基础偏移量
        dx = abs(end_point.x() - start_point.x())
        dy = abs(end_point.y() - start_point.y())
        base_offset = min(max(dx, dy) * 0.3, 150)

        # 根据起始方向计算第一个控制点
        if start_direction == 'top':
            control1 = QPointF(start_point.x(), start_point.y() - base_offset)
        elif start_direction == 'right':
            control1 = QPointF(start_point.x() + base_offset, start_point.y())
        elif start_direction == 'bottom':
            control1 = QPointF(start_point.x(), start_point.y() + base_offset)
        elif start_direction == 'left':
            control1 = QPointF(start_point.x() - base_offset, start_point.y())
        else:
            control1 = QPointF(start_point.x(), start_point.y() + base_offset)

        # 根据结束方向计算第二个控制点
        if end_direction == 'top':
            control2 = QPointF(end_point.x(), end_point.y() - base_offset)
        elif end_direction == 'right':
            control2 = QPointF(end_point.x() + base_offset, end_point.y())
        elif end_direction == 'bottom':
            control2 = QPointF(end_point.x(), end_point.y() + base_offset)
        elif end_direction == 'left':
            control2 = QPointF(end_point.x() - base_offset, end_point.y())
        else:
            control2 = QPointF(end_point.x(), end_point.y() - base_offset)

        return control1, control2

    def _draw_elegant_arrow(self, painter, control_point, end_point, direction):
        """绘制优雅的箭头（考虑连接方向）"""

        # 计算箭头方向向量
        if direction == 'top':
            arrow_dir = QPointF(0, -1)
        elif direction == 'right':
            arrow_dir = QPointF(1, 0)
        elif direction == 'bottom':
            arrow_dir = QPointF(0, 1)
        elif direction == 'left':
            arrow_dir = QPointF(-1, 0)
        else:
            # 默认向下
            arrow_dir = QPointF(0, 1)

        # 箭头大小
        arrow_size = 12

        # 计算箭头的三个点
        perpendicular = QPointF(-arrow_dir.y(), arrow_dir.x())  # 垂直向量

        arrow_point1 = QPointF(
            end_point.x() - arrow_size * arrow_dir.x() + arrow_size * 0.4 * perpendicular.x(),
            end_point.y() - arrow_size * arrow_dir.y() + arrow_size * 0.4 * perpendicular.y()
        )
        arrow_point2 = QPointF(
            end_point.x() - arrow_size * arrow_dir.x() - arrow_size * 0.4 * perpendicular.x(),
            end_point.y() - arrow_size * arrow_dir.y() - arrow_size * 0.4 * perpendicular.y()
        )

        # 绘制箭头
        arrow = QPolygonF([end_point, arrow_point1, arrow_point2])
        gradient = QLinearGradient(end_point, arrow_point1)
        gradient.setColorAt(0, QColor(100, 180, 255))
        gradient.setColorAt(1, QColor(70, 130, 180))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(70, 130, 180), 1))
        painter.drawPolygon(arrow)

    def itemChange(self, change, value):
        """检测卡片位置变化"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            moved_card = self.focusItem()
            if isinstance(moved_card, KnowledgeCard):
                for card in self.cards:
                    if card != moved_card and card.collidesWithItem(moved_card):
                        moved_card.set_parent_card(card)
                        card.add_child_card(moved_card)
                        break
        return super().itemChange(change, value)


class MindMapView(QGraphicsView):
    """思维导图视图 - 支持缩放、平移"""

    def __init__(self, scene):
        super().__init__(scene)

        # 设置视图属性
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.scale_factor = 1.0
        self.is_panning = False
        self.last_pan_point = QPointF()

    def wheelEvent(self, event):
        """鼠标滚轮缩放"""
        # Ctrl+滚轮进行缩放
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # 获取滚轮滚动方向
            delta = event.angleDelta().y()

            # 计算缩放因子
            if delta > 0:
                factor = 1.15
            else:
                factor = 1 / 1.15

            # 限制缩放范围
            new_scale = self.scale_factor * factor
            if 0.1 <= new_scale <= 5.0:
                self.scale(factor, factor)
                self.scale_factor = new_scale
        else:
            # 普通滚轮滚动
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 中键拖动平移
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_panning:
            # 平移视图
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
```
</details>

---

## 📄 文件: ai_reader_cards\pdf_viwer.py

### 📋 功能总结

PDFViewer类实现了一个独立的PDF阅读器组件，包括打开PDF文件、翻页、缩放、文本提取等功能。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 打开PDF文件
- 翻页功能
- 缩放功能
- 文本提取
- 拖放PDF文件到界面

### 💡 改进建议

- 📝 添加PDF文件加载进度提示
- 📝 优化文本提取的性能
- 📝 增加对更多PDF格式的支持
- 📝 改进界面交互体验

### ⚠️ 潜在问题

- 🔍 拖放文件的逻辑可能存在问题，需要进一步测试和验证
- 🔍 文本提取区域的最大高度可能需要调整，以适应更多文本内容

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\pdf_viewer.py
"""PDF阅读器模块 - 独立的PDF查看功能"""

import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QScrollArea, QTextEdit,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage


class PDFViewer(QWidget):
    """独立的PDF阅读器组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 200
        self.current_filepath = ""

        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 控制栏
        control_layout = QHBoxLayout()

        self.open_btn = QPushButton("📄 打开PDF")
        self.open_btn.clicked.connect(self.open_pdf)
        control_layout.addWidget(self.open_btn)

        control_layout.addWidget(QLabel("页码:"))
        self.page_spin = QComboBox()
        self.page_spin.currentTextChanged.connect(self.on_page_changed)
        control_layout.addWidget(self.page_spin)

        control_layout.addWidget(QLabel("缩放:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["100%", "150%", "200%", "250%", "300%"])
        self.zoom_combo.setCurrentText("200%")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_changed)
        control_layout.addWidget(self.zoom_combo)

        self.prev_btn = QPushButton("◀ 上一页")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        control_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("下一页 ▶")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        control_layout.addWidget(self.next_btn)

        # 文件信息标签
        self.file_info_label = QLabel("未打开文件")
        self.file_info_label.setStyleSheet("color: gray; font-size: 11px;")
        control_layout.addWidget(self.file_info_label)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # PDF显示区域
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setMinimumSize(600, 800)
        self.pdf_label.setText("请打开PDF文件\n\n支持拖放PDF文件到此区域")
        self.pdf_label.setStyleSheet("""
            border: 2px dashed #ccc; 
            background-color: #f5f5f5; 
            padding: 20px; 
            color: #666;
            font-size: 14px;
        """)
        self.pdf_label.setAcceptDrops(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.pdf_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 文本提取区域
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("提取的文本:"))

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("PDF文本内容将显示在这里...")
        self.text_area.setMaximumHeight(150)
        text_layout.addWidget(self.text_area)

        layout.addLayout(text_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.create_card_btn = QPushButton("📝 从选中文本创建卡片")
        self.create_card_btn.clicked.connect(self.create_card_from_text)
        self.create_card_btn.setEnabled(False)
        button_layout.addWidget(self.create_card_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def dragEnterEvent(self, event):
        """拖放进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()
                self.pdf_label.setStyleSheet("""
                    border: 2px dashed #0078d7; 
                    background-color: #e3f2fd; 
                    padding: 20px; 
                    color: #666;
                    font-size: 14px;
                """)

    def dragLeaveEvent(self, event):
        """拖放离开事件"""
        self.pdf_label.setStyleSheet("""
            border: 2px dashed #ccc; 
            background-color: #f5f5f5; 
            padding: 20px; 
            color: #666;
            font-size: 14px;
        """)

    def dropEvent(self, event):
        """拖放释放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            filepath = urls[0].toLocalFile()
            if filepath.lower().endswith('.pdf'):
                self.open_pdf_file(filepath)
                self.pdf_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
                event.acceptProposedAction()

    def open_pdf(self):
        """打开PDF文件"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "打开PDF文件", "", "PDF文件 (*.pdf)"
        )

        if filepath:
            self.open_pdf_file(filepath)

    def open_pdf_file(self, filepath):
        """打开PDF文件的具体实现"""
        try:
            # 关闭之前打开的文档
            self.close_document()

            self.doc = fitz.open(filepath)
            self.current_filepath = filepath
            self.total_pages = len(self.doc)
            self.current_page = 0

            # 更新页码选择
            self.page_spin.clear()
            self.page_spin.addItems([str(i + 1) for i in range(self.total_pages)])

            # 启用控件
            self.prev_btn.setEnabled(self.total_pages > 1)
            self.next_btn.setEnabled(self.total_pages > 1)
            self.create_card_btn.setEnabled(True)

            # 更新文件信息
            filename = os.path.basename(filepath)
            self.file_info_label.setText(f"{filename} (共{self.total_pages}页)")

            # 显示第一页
            self.display_page(0)

            # 发送打开成功信号
            if hasattr(self.parent(), 'on_pdf_opened'):
                self.parent().on_pdf_opened(filepath)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开PDF文件:\n{str(e)}")

    def display_page(self, page_num):
        """显示指定页面"""
        if not self.doc:
            return

        if page_num < 0 or page_num >= self.total_pages:
            return

        self.current_page = page_num

        try:
            page = self.doc.load_page(page_num)

            # 渲染页面为图像
            zoom = self.zoom_level / 100
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # 转换为QImage
            img_data = pix.tobytes("ppm")
            qimage = QImage()
            qimage.loadFromData(img_data, "PPM")

            # 显示图像
            pixmap = QPixmap.fromImage(qimage)
            self.pdf_label.setPixmap(pixmap)
            self.pdf_label.setText("")
            self.pdf_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")

        except Exception as e:
            self.pdf_label.setText(f"无法显示页面: {str(e)}")
            self.pdf_label.setStyleSheet("border: 1px solid #ccc; background-color: #fff0f0;")
            return

        # 更新页码
        self.page_spin.setCurrentText(str(page_num + 1))

        # 提取文本
        try:
            page = self.doc.load_page(page_num)
            text = page.get_text()
            self.text_area.setPlainText(text)
        except Exception as e:
            self.text_area.setPlainText(f"无法提取文本: {str(e)}")

    def on_page_changed(self, page_text):
        """页码改变"""
        if page_text and self.doc:
            try:
                page_num = int(page_text) - 1
                if 0 <= page_num < self.total_pages:
                    self.display_page(page_num)
            except ValueError:
                pass

    def on_zoom_changed(self, zoom_text):
        """缩放改变"""
        try:
            self.zoom_level = int(zoom_text.replace('%', ''))
            if self.doc:
                self.display_page(self.current_page)
        except ValueError:
            pass

    def prev_page(self):
        """上一页"""
        if self.current_page > 0 and self.doc:
            self.display_page(self.current_page - 1)

    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages - 1 and self.doc:
            self.display_page(self.current_page + 1)

    def create_card_from_text(self):
        """从选中文本创建卡片"""
        selected_text = self.text_area.textCursor().selectedText()
        if not selected_text:
            selected_text = self.text_area.toPlainText()[:500]

        if selected_text.strip():
            # 发送创建卡片信号
            if hasattr(self.parent(), 'create_card_from_text'):
                self.parent().create_card_from_text(selected_text, self.current_page + 1)

    def close_document(self):
        """安全关闭文档"""
        if self.doc:
            try:
                self.doc.close()
            except:
                pass
            self.doc = None

    def get_current_text(self):
        """获取当前文本内容"""
        return self.text_area.toPlainText()

    def get_selected_text(self):
        """获取选中的文本"""
        return self.text_area.textCursor().selectedText()

    def is_pdf_loaded(self):
        """检查是否有PDF加载"""
        return self.doc is not None and not self.doc.is_closed


class PDFTabWidget(QWidget):
    """PDF标签页组件 - 整合PDF阅读器和相关功能"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_viewer = PDFViewer(self)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.addWidget(self.pdf_viewer)

    def open_pdf_file(self, filepath):
        """打开PDF文件"""
        self.pdf_viewer.open_pdf_file(filepath)

    def close_document(self):
        """关闭文档"""
        self.pdf_viewer.close_document()

    def on_pdf_opened(self, filepath):
        """PDF打开成功回调"""
        # 可以在这里添加额外的处理逻辑
        pass

    def create_card_from_text(self, text, page_num):
        """创建卡片回调"""
        # 转发到父窗口
        if hasattr(self.parent(), 'create_card_from_pdf_text'):
            self.parent().create_card_from_pdf_text(text, page_num)
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\__init__.py

### 📋 功能总结

该代码文件定义了UI组件包中的各个UI组件类以及新增的管理器类，并限制了对外暴露的内容。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 定义了多个UI组件类，如控制面板(ControlPanel)、输入面板(InputPanel)等
- 新增了管理器类，如主控制器(MainController)、卡片管理器(CardManager)等
- 通过__all__限制了对外暴露的内容，提高了代码的封装性

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 未发现明显问题

<details>
<summary>📝 查看源代码</summary>

```python
"""UI组件包"""

from .control_panel import ControlPanel
from .input_panel import InputPanel
from .mindmap_panel import MindMapPanel
from .drawing_toolbar import DrawingToolbar
from .search_toolbar import SearchToolbar
from .alignment_toolbar import AlignmentToolbar

# 新增管理器
from .main_controller import MainController
from .card_manager import CardManager
from .search_manager import SearchManager
from .alignment_manager import AlignmentManager

__all__ = [
    'ControlPanel',
    'InputPanel',
    'MindMapPanel',
    'DrawingToolbar',
    'SearchToolbar',
    'AlignmentToolbar',
    'MainController',
    'CardManager',
    'SearchManager',
    'AlignmentManager'
]
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\alignment_manager.py

### 📋 功能总结

该代码文件实现了一个对齐管理器，用于对卡片进行不同类型的对齐操作和层次排列。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 对齐选中的卡片
- 层次排列卡片
- 左对齐、右对齐、顶对齐、底对齐、水平居中、垂直居中、水平分布、垂直分布功能实现

### 💡 改进建议

- 📝 在_align_left、_align_right、_align_top、_align_bottom、_align_center_horizontal、_align_center_vertical、_distribute_horizontal、_distribute_vertical等方法中，应该添加参数检查和异常处理，以提高代码的健壮性。
- 📝 可以考虑优化水平和垂直分布的算法，使得分布更加均匀和美观。

### ⚠️ 潜在问题

- 🔍 在_align_left、_align_right、_align_top、_align_bottom、_align_center_horizontal、_align_center_vertical、_distribute_horizontal、_distribute_vertical等方法中，未对输入参数进行有效性检查，可能导致程序在特定情况下出现错误。
- 🔍 在_align_left、_align_right、_align_top、_align_bottom、_align_center_horizontal、_align_center_vertical、_distribute_horizontal、_distribute_vertical等方法中，未处理边界情况，可能导致卡片位置计算错误。

<details>
<summary>📝 查看源代码</summary>

```python
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
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\alignment_toolbar.py

### 📋 功能总结

该代码定义了一个对齐工具栏组件AlignmentToolbar，提供了对齐和排列功能的按钮，并通过信号与槽机制实现对齐操作的触发。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 定义了对齐工具栏组件AlignmentToolbar
- 提供了多个对齐和排列功能的按钮
- 通过信号与槽机制实现对齐操作的触发

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 未发现明显问题

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\ui_components\alignment_toolbar.py
"""对齐工具栏组件"""

from PyQt6.QtWidgets import QToolBar, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal


class AlignmentToolbar(QToolBar):
    """对齐工具栏"""

    alignment_requested = pyqtSignal(str)  # align_type
    arrange_hierarchy_requested = pyqtSignal()

    def __init__(self):
        super().__init__("对齐工具")
        self.setMovable(False)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 对齐按钮
        self.addWidget(QLabel("对齐:"))

        left_btn = QPushButton("左对齐")
        left_btn.clicked.connect(lambda: self.alignment_requested.emit("left"))
        self.addWidget(left_btn)

        right_btn = QPushButton("右对齐")
        right_btn.clicked.connect(lambda: self.alignment_requested.emit("right"))
        self.addWidget(right_btn)

        top_btn = QPushButton("顶对齐")
        top_btn.clicked.connect(lambda: self.alignment_requested.emit("top"))
        self.addWidget(top_btn)

        bottom_btn = QPushButton("底对齐")
        bottom_btn.clicked.connect(lambda: self.alignment_requested.emit("bottom"))
        self.addWidget(bottom_btn)

        self.addSeparator()

        center_h_btn = QPushButton("水平居中")
        center_h_btn.clicked.connect(lambda: self.alignment_requested.emit("center_h"))
        self.addWidget(center_h_btn)

        center_v_btn = QPushButton("垂直居中")
        center_v_btn.clicked.connect(lambda: self.alignment_requested.emit("center_v"))
        self.addWidget(center_v_btn)

        self.addSeparator()

        distribute_h_btn = QPushButton("水平分布")
        distribute_h_btn.clicked.connect(lambda: self.alignment_requested.emit("distribute_h"))
        self.addWidget(distribute_h_btn)

        distribute_v_btn = QPushButton("垂直分布")
        distribute_v_btn.clicked.connect(lambda: self.alignment_requested.emit("distribute_v"))
        self.addWidget(distribute_v_btn)

        self.addSeparator()

        # 层次排列
        hierarchy_btn = QPushButton("层次排列")
        hierarchy_btn.clicked.connect(self.arrange_hierarchy_requested.emit)
        self.addWidget(hierarchy_btn)
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\card_manager.py

### 📋 功能总结

{'link_cards': '连接选中的卡片', 'unlink_card': '取消连接', 'delete_connection': '删除选中的连接', 'get_card_hierarchy': '获取卡片层次结构'}

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 连接卡片
- 取消连接
- 删除连接
- 获取卡片层次结构

### 💡 改进建议

- 📝 考虑增加更多的输入验证，如确保连接的唯一性
- 📝 优化连接列表的显示和交互方式

### ⚠️ 潜在问题

- 🔍 循环检测算法可能存在性能问题，特别是在大型卡片结构中
- 🔍 连接列表的选择方式可能不够直观，用户体验有待改进

<details>
<summary>📝 查看源代码</summary>

```python
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
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\control_panel.py

### 📋 功能总结

该代码定义了一个控制面板组件 ControlPanel，提供了与AI模型连接、剪贴板监控、XMind导入导出等功能相关的信号和操作。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 定义了多个信号用于通知主窗口各种操作
- 提供了创建控制面板布局的方法 create_panel()
- 包含了与模型选择、AI连接、剪贴板监控、XMind导入导出等功能相关的操作方法

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 🔍 部分按钮点击事件使用 lambda 表达式，可读性较差，考虑改为普通方法
- 🔍 部分方法未提供错误处理或异常捕获，可能导致程序崩溃

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\ui_components\control_panel.py
"""控制面板组件"""

from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QLabel,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import QObject, pyqtSignal


class ControlPanel(QObject):
    """顶部控制面板

    设计为信号/布局提供者：
    - 调用 `create_panel()` 返回一个 QLayout，主窗口负责把它加入主布局。
    - 这样避免将 ControlPanel 实现成 QWidget，但仍可复用布局与信号。
    """

    # 在类级别定义信号
    ai_connected = pyqtSignal()
    model_changed = pyqtSignal(str)
    clipboard_monitor_toggled = pyqtSignal(bool)
    save_requested = pyqtSignal()
    load_requested = pyqtSignal()
    export_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    # XMind相关信号
    import_xmind_requested = pyqtSignal()
    export_xmind_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.model_combo = None
        self.connect_btn = None
        self.monitor_btn = None
        self.import_xmind_btn = None
        self.export_xmind_btn = None

    def create_panel(self):
        """创建控制面板并返回布局（QLayout）。"""
        # 模型选择
        self.layout.addWidget(QLabel("AI模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        self.layout.addWidget(self.model_combo)

        # 连接AI按钮
        self.connect_btn = QPushButton("🔌 连接AI")
        self.connect_btn.clicked.connect(self._connect_ai)
        self.layout.addWidget(self.connect_btn)

        self.layout.addStretch()

        # 剪贴板监控开关
        self.monitor_btn = QPushButton("📋 启用剪贴板监控")
        self.monitor_btn.setCheckable(True)
        # 使用 lambda 包装 emit 以避免在连接时立即执行
        self.monitor_btn.toggled.connect(lambda checked: self.clipboard_monitor_toggled.emit(checked))
        self.layout.addWidget(self.monitor_btn)

        # XMind导入导出按钮
        self.import_xmind_btn = QPushButton("📥 导入XMind")
        self.import_xmind_btn.clicked.connect(lambda: self.import_xmind_requested.emit())
        self.layout.addWidget(self.import_xmind_btn)

        self.export_xmind_btn = QPushButton("📤 导出XMind")
        self.export_xmind_btn.clicked.connect(lambda: self.export_xmind_requested.emit())
        self.layout.addWidget(self.export_xmind_btn)

        # 保存按钮
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(lambda: self.save_requested.emit())
        self.layout.addWidget(save_btn)

        # 加载按钮
        load_btn = QPushButton("📁 加载")
        load_btn.clicked.connect(lambda: self.load_requested.emit())
        self.layout.addWidget(load_btn)

        # 导出按钮
        export_btn = QPushButton("📤 导出Markdown")
        export_btn.clicked.connect(lambda: self.export_requested.emit())
        self.layout.addWidget(export_btn)

        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空画布")
        clear_btn.clicked.connect(lambda: self.clear_requested.emit())
        self.layout.addWidget(clear_btn)

        return self.layout

    def _on_model_changed(self, model):
        """模型改变回调"""
        self.model_changed.emit(model)

    def _connect_ai(self):
        """连接AI服务"""
        self.ai_connected.emit()

    def set_ai_connected(self, model):
        """设置AI连接状态"""
        if self.connect_btn:
            self.connect_btn.setText("✅ AI已连接")
            self.connect_btn.setEnabled(False)
        if self.model_combo:
            self.model_combo.setEnabled(False)

    def get_selected_model(self):
        """获取选中的模型"""
        return self.model_combo.currentText() if self.model_combo else None

    def set_clipboard_monitor_status(self, monitoring):
        """设置剪贴板监控状态"""
        if monitoring:
            self.monitor_btn.setText("📋 剪贴板监控中...")
        else:
            self.monitor_btn.setText("📋 启用剪贴板监控")
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\drawing_toolbar.py

### 📋 功能总结

该代码定义了一个绘画工具栏组件 DrawingToolbar，用于控制绘画模式、画笔颜色、画笔粗细等功能。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 绘画模式开关
- 颜色选择
- 画笔粗细调整
- 清除绘画功能

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 未发现明显问题

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\ui_components\drawing_toolbar.py
"""绘画工具栏组件"""

from PyQt6.QtWidgets import QToolBar, QPushButton, QLabel, QSpinBox, QColorDialog
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor


class DrawingToolbar(QToolBar):
    """绘画工具栏"""

    drawing_mode_toggled = pyqtSignal(bool)
    pen_color_changed = pyqtSignal(QColor)
    pen_width_changed = pyqtSignal(int)
    clear_drawings_requested = pyqtSignal()

    def __init__(self):
        super().__init__("绘画工具")
        self.drawing_btn = None
        self.color_btn = None
        self.pen_size_spin = None
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 3

        self.setMovable(False)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 绘画模式开关
        self.drawing_btn = QPushButton("🎨 绘画模式")
        self.drawing_btn.setCheckable(True)
        self.drawing_btn.toggled.connect(self.drawing_mode_toggled.emit)
        self.addWidget(self.drawing_btn)

        self.addSeparator()

        # 颜色选择
        self.color_btn = QPushButton("颜色")
        self.color_btn.clicked.connect(self._choose_pen_color)
        self.color_btn.setStyleSheet(f"background-color: {self.pen_color.name()};")
        self.addWidget(self.color_btn)

        # 画笔粗细
        self.addWidget(QLabel("画笔粗细:"))
        self.pen_size_spin = QSpinBox()
        self.pen_size_spin.setRange(1, 20)
        self.pen_size_spin.setValue(self.pen_width)
        self.pen_size_spin.valueChanged.connect(self.pen_width_changed.emit)
        self.addWidget(self.pen_size_spin)

        self.addSeparator()

        # 清除绘画
        clear_drawing_btn = QPushButton("🧹 清除绘画")
        clear_drawing_btn.clicked.connect(self.clear_drawings_requested.emit)
        self.addWidget(clear_drawing_btn)

    def _choose_pen_color(self):
        """选择画笔颜色"""
        color = QColorDialog.getColor(self.pen_color, self, "选择画笔颜色")
        if color.isValid():
            self.pen_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.pen_color_changed.emit(color)

    def toggle_drawing_mode(self):
        """切换绘画模式"""
        self.drawing_btn.toggle()
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\input_panel.py

### 📋 功能总结

该代码定义了一个文件输入面板组件，用于打开文件、显示文件内容并支持文本操作和生成卡片功能。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 打开文件功能
- 清空内容功能
- 从选中文本生成卡片功能
- 文本操作功能（复制、粘贴、剪切、全选）

### 💡 改进建议

- 📝 添加文件保存功能，让用户可以保存编辑后的文件内容。
- 📝 增加文件类型过滤功能，只允许打开特定类型的文件。
- 📝 优化生成卡片功能，提供更多样式和选项。

### ⚠️ 潜在问题

- 🔍 在_generate_card_from_selection方法中，存在未完整的代码片段，可能会导致程序运行时出错。需要补充完整。
- 🔍 UI界面可能需要进一步优化，提升用户体验。

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\ui_components\input_panel.py
"""输入面板组件"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QMessageBox)
from PyQt6.QtCore import pyqtSignal


class InputPanel(QWidget):
    """文件输入面板"""

    file_opened = pyqtSignal(str, str)  # filepath, file_type
    generate_card_requested = pyqtSignal(str)
    text_operation_requested = pyqtSignal(str)  # copy, paste, cut, select_all

    def __init__(self):
        super().__init__()
        self.text_input = None
        self.file_info_label = None
        self.generate_btn = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题和文件控制栏
        title_layout = QHBoxLayout()
        title = QLabel("📚 文件阅读区")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        title_layout.addWidget(title)

        # 文件操作按钮
        open_file_btn = QPushButton("📂 打开文件")
        open_file_btn.clicked.connect(self._open_file)
        title_layout.addWidget(open_file_btn)

        clear_file_btn = QPushButton("🗑️ 清空")
        clear_file_btn.clicked.connect(self._clear_content)
        title_layout.addWidget(clear_file_btn)

        title_layout.addStretch()

        # 文件信息标签
        self.file_info_label = QLabel("未打开文件")
        self.file_info_label.setStyleSheet("color: gray; font-size: 11px;")
        title_layout.addWidget(self.file_info_label)

        layout.addLayout(title_layout)

        # 文本显示和编辑区域
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "文件内容将显示在这里...\n\n"
            "支持的操作：\n"
            "1. 打开文本文件(.txt)、PDF文件(.pdf)\n"
            "2. 支持复制(Ctrl+C)、粘贴(Ctrl+V)、剪切(Ctrl+X)\n"
            "3. 选中文本后按空格键快速生成卡片\n"
            "4. 支持查找(Ctrl+F)、全选(Ctrl+A)"
        )
        layout.addWidget(self.text_input)

        # 文本操作工具栏
        text_toolbar = QHBoxLayout()

        copy_btn = QPushButton("📋 复制")
        copy_btn.clicked.connect(lambda: self.text_operation_requested.emit("copy"))
        text_toolbar.addWidget(copy_btn)

        paste_btn = QPushButton("📄 粘贴")
        paste_btn.clicked.connect(lambda: self.text_operation_requested.emit("paste"))
        text_toolbar.addWidget(paste_btn)

        cut_btn = QPushButton("✂️ 剪切")
        cut_btn.clicked.connect(lambda: self.text_operation_requested.emit("cut"))
        text_toolbar.addWidget(cut_btn)

        select_all_btn = QPushButton("🔍 全选")
        select_all_btn.clicked.connect(lambda: self.text_operation_requested.emit("select_all"))
        text_toolbar.addWidget(select_all_btn)

        text_toolbar.addStretch()
        layout.addLayout(text_toolbar)

        # 生成卡片按钮
        self.generate_btn = QPushButton("✨ 从选中文本生成卡片 (Space)")
        self.generate_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        self.generate_btn.clicked.connect(self._generate_card_from_selection)
        self.generate_btn.setEnabled(False)
        layout.addWidget(self.generate_btn)

    def _open_file(self):
        """打开文件"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            "",
            "文本文件 (*.txt);;PDF文件 (*.pdf);;所有文件 (*.*)"
        )

        if filepath:
            if filepath.lower().endswith('.pdf'):
                self.file_opened.emit(filepath, 'pdf')
            else:
                self.file_opened.emit(filepath, 'text')

    def _clear_content(self):
        """清空内容"""
        self.text_input.clear()
        self.file_info_label.setText("未打开文件")
        self.generate_btn.setEnabled(False)

    def _generate_card_from_selection(self):
        """从选中文本生成卡片"""
        cursor = self.text_input.textCursor()
        if cursor.hasSelection():
            # 使用选中文本
            text = cursor.selectedText()
        else:
            # 如果没有选中文本，使用全部文本（限制长度）
            text = self.text_input.toPlainText()[:1000]
            if not text:
                QMessageBox.warning(self, "提示", "请先打开文件或输入文本内容")
                return

        if len(text) < 10:
            QMessageBox.warning(self, "提示", "文本过短，请输入至少10个字符")
            return

        self.generate_card_requested.emit(text)

    def set_file_content(self, content, filename, file_type):
        """设置文件内容"""
        self.text_input.setPlainText(content)
        if file_type == 'pdf':
            self.file_info_label.setText(f"PDF文件: {filename}")
        else:
            self.file_info_label.setText(f"文本文件: {filename}")
        self.generate_btn.setEnabled(True)

    def enable_generate_button(self, enabled):
        """启用/禁用生成按钮"""
        self.generate_btn.setEnabled(enabled)

    def get_text_input(self):
        """获取文本输入框"""
        return self.text_input
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\main_controller.py

### 📋 功能总结

主窗口业务逻辑控制器，处理连接AI服务、打开文本/PDF文件、生成卡片等功能

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 连接AI服务
- 打开文本文件
- 打开PDF文件
- 生成卡片
- 切换剪贴板监控

### 💡 改进建议

- 📝 添加更多错误处理机制，提高代码的健壮性
- 📝 优化代码结构，提高可读性和可维护性
- 📝 增加日志记录功能，方便排查问题

### ⚠️ 潜在问题

- 🔍 部分函数缺乏详细的错误处理，可能导致程序崩溃
- 🔍 部分函数存在较长的代码块，可考虑拆分为更小的函数以提高可读性

<details>
<summary>📝 查看源代码</summary>

```python
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

    def auto_save(self, cards=None):
        """自动保存"""
        # 这个方法需要在实际使用时传入cards参数
        pass

    def cleanup(self):
        """清理资源"""
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\mindmap_panel.py

### 📋 功能总结

该代码定义了一个思维导图面板组件，用于展示和操作思维导图，包括添加、移除卡片、设置连接模式、清空画布等功能。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 初始化思维导图面板UI
- 添加、移除卡片到场景
- 获取所有卡片和选中的卡片
- 设置连接模式、绘画模式、画笔颜色和宽度
- 清空画布和绘画内容

### 💡 改进建议

- 📝 考虑添加撤销操作功能，以便用户可以撤销上一步的操作
- 📝 增加保存和加载思维导图的功能，提高用户体验

### ⚠️ 潜在问题

- 🔍 在清空画布时，使用了列表切片[:]来遍历所有卡片并移除，可能存在潜在的性能问题，可以考虑优化移除逻辑

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\ui_components\mindmap_panel.py
"""思维导图面板组件"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal

# 修复导入路径
from ai_reader_cards.mindmap import MindMapScene, MindMapView
from ai_reader_cards.card import KnowledgeCard


class MindMapPanel(QWidget):
    """思维导图面板"""

    link_cards_requested = pyqtSignal()
    unlink_card_requested = pyqtSignal()
    connection_mode_toggled = pyqtSignal(bool)
    delete_connection_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mindmap_scene = None
        self.mindmap_view = None
        self.connection_mode_btn = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel("🧠 思维导图画布")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        title_layout.addWidget(title)

        hint = QLabel("提示: Ctrl+滚轮缩放 | 中键拖动平移 | 拖动连接点创建连线 | 一个点可连接多个子节点")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        title_layout.addWidget(hint)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 思维导图视图
        self.mindmap_scene = MindMapScene()
        self.mindmap_view = MindMapView(self.mindmap_scene)
        layout.addWidget(self.mindmap_view)

        # 画布操作按钮
        canvas_controls = QHBoxLayout()

        # 连接模式切换按钮
        self.connection_mode_btn = QPushButton("🔗 连接模式")
        self.connection_mode_btn.setCheckable(True)
        self.connection_mode_btn.toggled.connect(self.connection_mode_toggled.emit)
        canvas_controls.addWidget(self.connection_mode_btn)

        link_btn = QPushButton("🔗 连接选中卡片")
        link_btn.clicked.connect(self.link_cards_requested.emit)
        canvas_controls.addWidget(link_btn)

        unlink_btn = QPushButton("❌ 取消连接")
        unlink_btn.clicked.connect(self.unlink_card_requested.emit)
        canvas_controls.addWidget(unlink_btn)

        delete_connection_btn = QPushButton("🗑️ 删除连接")
        delete_connection_btn.clicked.connect(self.delete_connection_requested.emit)
        canvas_controls.addWidget(delete_connection_btn)

        canvas_controls.addStretch()
        layout.addLayout(canvas_controls)

    def set_connection_mode(self, enabled):
        """设置连接模式"""
        self.connection_mode_btn.setChecked(enabled)

    def add_card(self, card):
        """添加卡片到场景"""
        self.mindmap_scene.add_card(card)

    def remove_card(self, card):
        """从场景移除卡片"""
        self.mindmap_scene.remove_card(card)

    def get_all_cards(self):
        """获取所有卡片"""
        return self.mindmap_scene.get_all_cards()

    def get_selected_cards(self):
        """获取选中的卡片"""
        selected_items = self.mindmap_scene.selectedItems()
        return [item for item in selected_items if isinstance(item, KnowledgeCard)]

    def clear_canvas(self):
        """清空画布"""
        for card in self.mindmap_scene.get_all_cards()[:]:
            self.mindmap_scene.remove_card(card)

    def update_scene(self):
        """更新场景"""
        self.mindmap_scene.update()

    def set_drawing_mode(self, enabled):
        """设置绘画模式"""
        self.mindmap_scene.set_drawing_mode(enabled)

    def set_pen_color(self, color):
        """设置画笔颜色"""
        self.mindmap_scene.set_pen_color(color)

    def set_pen_width(self, width):
        """设置画笔宽度"""
        self.mindmap_scene.set_pen_width(width)

    def clear_drawings(self):
        """清除所有绘画"""
        self.mindmap_scene.clear_drawings()
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\search_manager.py

### 📋 功能总结

该代码文件定义了一个搜索管理器类 SearchManager，用于管理卡片搜索功能。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 搜索卡片功能
- 导航到下一个/上一个搜索结果
- 清除搜索结果
- 获取当前搜索状态

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 未发现明显问题

<details>
<summary>📝 查看源代码</summary>

```python
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
```
</details>

---

## 📄 文件: ai_reader_cards\ui_components\search_toolbar.py

### 📋 功能总结

搜索工具栏组件，包含搜索功能、导航功能和状态更新功能。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 搜索功能，支持关键词搜索和选择搜索字段
- 导航功能，支持上一个和下一个操作
- 状态更新功能，显示搜索结果数量和当前索引

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 未发现明显问题

<details>
<summary>📝 查看源代码</summary>

```python
# 文件路径: ai_reader_cards\ui_components\search_toolbar.py
"""搜索工具栏组件"""

from PyQt6.QtWidgets import (QToolBar, QLineEdit, QPushButton, QLabel,
                             QComboBox, QCheckBox, QHBoxLayout, QWidget)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence


class SearchToolbar(QToolBar):
    """搜索工具栏"""

    search_requested = pyqtSignal(str, list)  # keyword, fields
    navigate_next_requested = pyqtSignal()
    navigate_previous_requested = pyqtSignal()
    clear_search_requested = pyqtSignal()

    def __init__(self):
        super().__init__("搜索工具")
        self.search_input = None
        self.fields_combo = None
        self.case_sensitive_check = None
        self.status_label = None

        self.setMovable(False)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 搜索输入框
        self.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索卡片...")
        self.search_input.setMaximumWidth(200)
        self.search_input.returnPressed.connect(self._on_search)
        self.addWidget(self.search_input)

        # 搜索字段选择
        self.addWidget(QLabel("搜索字段:"))
        self.fields_combo = QComboBox()
        self.fields_combo.addItems(["全部", "标题", "问题", "答案", "标题+问题", "问题+答案"])
        self.addWidget(self.fields_combo)

        # 搜索按钮
        search_btn = QPushButton("🔍 搜索")
        search_btn.clicked.connect(self._on_search)
        self.addWidget(search_btn)

        self.addSeparator()

        # 导航按钮
        prev_btn = QPushButton("◀ 上一个")
        prev_btn.clicked.connect(self.navigate_previous_requested.emit)
        self.addWidget(prev_btn)

        next_btn = QPushButton("下一个 ▶")
        next_btn.clicked.connect(self.navigate_next_requested.emit)
        self.addWidget(next_btn)

        self.addSeparator()

        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.addWidget(self.status_label)

        self.addSeparator()

        # 清除搜索按钮
        clear_btn = QPushButton("清除搜索")
        clear_btn.clicked.connect(self.clear_search_requested.emit)
        self.addWidget(clear_btn)

    def _on_search(self):
        """执行搜索"""
        keyword = self.search_input.text().strip()
        if not keyword:
            return

        # 解析搜索字段
        fields_option = self.fields_combo.currentText()
        if fields_option == "全部":
            search_fields = ['title', 'question', 'answer']
        elif fields_option == "标题":
            search_fields = ['title']
        elif fields_option == "问题":
            search_fields = ['question']
        elif fields_option == "答案":
            search_fields = ['answer']
        elif fields_option == "标题+问题":
            search_fields = ['title', 'question']
        elif fields_option == "问题+答案":
            search_fields = ['question', 'answer']
        else:
            search_fields = ['title', 'question', 'answer']

        self.search_requested.emit(keyword, search_fields)

    def update_status(self, current_index, total_results, keyword):
        """更新搜索状态"""
        if total_results == 0:
            self.status_label.setText(f"未找到 '{keyword}'")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
        else:
            self.status_label.setText(f"找到 {total_results} 个结果 - 当前: {current_index}/{total_results}")
            self.status_label.setStyleSheet("color: green; font-size: 11px;")

    def clear_status(self):
        """清除状态"""
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.search_input.clear()

    def set_search_text(self, text):
        """设置搜索文本"""
        self.search_input.setText(text)
```
</details>

---

## 📄 文件: ai_reader_cards\ui_main.py

### 📋 功能总结

重构后的主窗口，包含各种UI组件和管理器的初始化，连接信号等操作。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 初始化用户界面
- 连接各种信号
- 管理器和UI组件的初始化

### 💡 改进建议

- 📝 完善代码注释，特别是在一些未完成的地方添加注释说明
- 📝 完善异常处理机制，确保程序的稳定性

### ⚠️ 潜在问题

- 🔍 部分代码未完成，如input_panel的内容长度限制部分
- 🔍 可能存在信号连接错误或遗漏的情况，需要仔细检查

<details>
<summary>📝 查看源代码</summary>

```python
"""重构后的主窗口 - 简化版本"""

import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QStatusBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QStatusBar, QMessageBox
# 导入组件
from ai_reader_cards.ui_components.control_panel import ControlPanel
from ai_reader_cards.ui_components.input_panel import InputPanel
from ai_reader_cards.ui_components.mindmap_panel import MindMapPanel
from ai_reader_cards.ui_components.drawing_toolbar import DrawingToolbar
from ai_reader_cards.ui_components.search_toolbar import SearchToolbar
from ai_reader_cards.ui_components.alignment_toolbar import AlignmentToolbar

# 导入管理器
from ai_reader_cards.ui_components.main_controller import MainController
from ai_reader_cards.ui_components.card_manager import CardManager
from ai_reader_cards.ui_components.search_manager import SearchManager
from ai_reader_cards.ui_components.alignment_manager import AlignmentManager


class MainWindow(QMainWindow):
    """重构后的主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化管理器
        self.controller = MainController()
        self.card_manager = CardManager()
        self.search_manager = SearchManager()
        self.alignment_manager = AlignmentManager()

        # 初始化UI组件
        self.control_panel = ControlPanel()
        self.input_panel = InputPanel()
        self.mindmap_panel = MindMapPanel()
        self.drawing_toolbar = DrawingToolbar()
        self.search_toolbar = SearchToolbar()
        self.alignment_toolbar = AlignmentToolbar()

        self.init_ui()
        self.connect_signals()
        self.setup_shortcuts()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("AI阅读卡片思维导图工具 v1.0")
        self.setGeometry(100, 100, 1400, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 添加工具栏
        main_layout.addWidget(self.drawing_toolbar)
        main_layout.addWidget(self.search_toolbar)
        main_layout.addWidget(self.alignment_toolbar)

        # 添加控制面板
        control_layout = self.control_panel.create_panel()
        main_layout.addLayout(control_layout)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.input_panel)
        splitter.addWidget(self.mindmap_panel)
        splitter.setSizes([400, 1000])
        main_layout.addWidget(splitter)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("就绪")

    def connect_signals(self):
        """连接所有信号"""
        self._connect_controller_signals()
        self._connect_ui_signals()
        self._connect_manager_signals()

    def _connect_controller_signals(self):
        """连接控制器信号"""
        self.controller.status_updated.connect(self.update_status)
        self.controller.card_generated.connect(self.mindmap_panel.add_card)
        self.controller.generation_error.connect(self._handle_generation_error)

    def _connect_ui_signals(self):
        """连接UI组件信号"""
        # 控制面板信号
        self.control_panel.ai_connected.connect(self._connect_ai)
        self.control_panel.model_changed.connect(self.controller.on_model_changed)
        self.control_panel.clipboard_monitor_toggled.connect(self._toggle_clipboard_monitor)
        self.control_panel.save_requested.connect(self._save_cards)
        self.control_panel.load_requested.connect(self._load_cards)
        self.control_panel.export_requested.connect(self._export_markdown)
        self.control_panel.clear_requested.connect(self._clear_canvas)
        self.control_panel.import_xmind_requested.connect(self._import_xmind)
        self.control_panel.export_xmind_requested.connect(self._export_xmind)

        # 输入面板信号
        self.input_panel.file_opened.connect(self._open_file)
        self.input_panel.generate_card_requested.connect(self.controller.generate_card)
        self.input_panel.text_operation_requested.connect(self._handle_text_operation)

        # 思维导图面板信号
        self.mindmap_panel.link_cards_requested.connect(self._link_selected_cards)
        self.mindmap_panel.unlink_card_requested.connect(self._unlink_selected_card)
        self.mindmap_panel.connection_mode_toggled.connect(self._toggle_connection_mode)
        self.mindmap_panel.delete_connection_requested.connect(self._delete_connection)

        # 绘画工具栏信号
        self.drawing_toolbar.drawing_mode_toggled.connect(self.mindmap_panel.set_drawing_mode)
        self.drawing_toolbar.pen_color_changed.connect(self.mindmap_panel.set_pen_color)
        self.drawing_toolbar.pen_width_changed.connect(self.mindmap_panel.set_pen_width)
        self.drawing_toolbar.clear_drawings_requested.connect(self.mindmap_panel.clear_drawings)

        # 搜索工具栏信号
        self.search_toolbar.search_requested.connect(self._search_cards)
        self.search_toolbar.navigate_next_requested.connect(self._navigate_search_next)
        self.search_toolbar.navigate_previous_requested.connect(self._navigate_search_previous)
        self.search_toolbar.clear_search_requested.connect(self._clear_search)

        # 对齐工具栏信号
        self.alignment_toolbar.alignment_requested.connect(self._align_cards)
        self.alignment_toolbar.arrange_hierarchy_requested.connect(self._arrange_hierarchy)

    def _connect_manager_signals(self):
        """连接管理器信号"""
        self.card_manager.cards_linked.connect(self._on_cards_linked)
        self.card_manager.card_unlinked.connect(self._on_card_unlinked)
        self.card_manager.connection_deleted.connect(self._on_connection_deleted)

        self.search_manager.search_results_updated.connect(self._on_search_results_updated)
        self.search_manager.navigation_updated.connect(self._on_navigation_updated)

    def setup_shortcuts(self):
        """设置快捷键"""
        # 原有的快捷键设置...
        pass

    # 业务方法 - 委托给相应的管理器
    def _connect_ai(self):
        """连接AI服务"""
        model = self.control_panel.get_selected_model()
        success, message = self.controller.connect_ai(model)

        if success:
            self.control_panel.set_ai_connected(model)
            self.input_panel.enable_generate_button(True)
        self._show_message(success, message)

    def _toggle_clipboard_monitor(self, checked):
        """切换剪贴板监控"""
        success, message = self.controller.toggle_clipboard_monitor(checked, self._on_clipboard_changed)
        if success:
            self.control_panel.set_clipboard_monitor_status(checked)
        self._show_message(success, message)

    def _open_file(self, filepath, file_type):
        """打开文件"""
        try:
            if file_type == 'pdf':
                content, filename = self.controller.open_pdf_file(filepath)
            else:
                content, filename = self.controller.open_text_file(filepath)

            self.input_panel.set_file_content(content, filename, file_type)
        except Exception as e:
            self._show_message(False, str(e))

    def _save_cards(self):
        """保存卡片"""
        cards = self.mindmap_panel.get_all_cards()
        success, message = self.controller.save_cards(cards)
        self._show_message(success, message)

    def _load_cards(self):
        """加载卡片"""
        try:
            result = self.controller.load_cards()
            if result:
                loaded_cards, card_map = result
                self._clear_canvas(confirm=False)

                for card in loaded_cards:
                    self.mindmap_panel.add_card(card)

                self.mindmap_panel.update_scene()
        except Exception as e:
            self._show_message(False, str(e))

    def _export_markdown(self):
        """导出Markdown"""
        cards = self.mindmap_panel.get_all_cards()
        success, message = self.controller.export_markdown(cards)
        self._show_message(success, message)

    def _link_selected_cards(self):
        """连接选中的卡片"""
        cards = self.mindmap_panel.get_selected_cards()
        success, message = self.card_manager.link_cards(cards)
        if success:
            self.mindmap_panel.update_scene()
        self._show_message(success, message)

    def _unlink_selected_card(self):
        """取消连接"""
        cards = self.mindmap_panel.get_selected_cards()
        if cards:
            success, message = self.card_manager.unlink_card(cards[0])
            if success:
                self.mindmap_panel.update_scene()
            self._show_message(success, message)

    def _delete_connection(self):
        """删除连接"""
        cards = self.mindmap_panel.get_selected_cards()
        if cards:
            success, message = self.card_manager.delete_connection(cards[0])
            if success:
                self.mindmap_panel.update_scene()
            self._show_message(success, message)

    def _search_cards(self, keyword, search_fields):
        """搜索卡片"""
        cards = self.mindmap_panel.get_all_cards()
        self.search_manager.search(cards, keyword, search_fields)

    def _navigate_search_next(self):
        """导航到下一个搜索结果"""
        card = self.search_manager.navigate_next()
        if card:
            self._focus_card(card)

    def _navigate_search_previous(self):
        """导航到上一个搜索结果"""
        card = self.search_manager.navigate_previous()
        if card:
            self._focus_card(card)

    def _align_cards(self, align_type):
        """对齐选中的卡片"""
        cards = self.mindmap_panel.get_selected_cards()
        success, message = self.alignment_manager.align_cards(cards, align_type)
        self._show_message(success, message)

    def _arrange_hierarchy(self):
        """层次排列"""
        cards = self.mindmap_panel.get_selected_cards()
        success, message = self.alignment_manager.arrange_hierarchy(cards)
        self._show_message(success, message)

    # 事件处理方法
    def _on_clipboard_changed(self, text):
        """剪贴板内容改变"""
        if len(text.strip()) >= 15 and self.controller.ai_generator:
            self.controller.generate_card(text)

    def _on_cards_linked(self, parent_card, child_card):
        """卡片连接完成"""
        self.update_status(f"已建立连接: {parent_card.title_text} -> {child_card.title_text}")

    def _on_card_unlinked(self, card):
        """卡片取消连接"""
        self.update_status(f"已取消卡片连接: {card.title_text}")

    def _on_connection_deleted(self, from_card, to_card):
        """连接已删除"""
        self.update_status(f"已删除连接: {from_card.title_text} -> {to_card.title_text}")

    def _on_search_results_updated(self, results, keyword):
        """搜索结果更新"""
        if results:
            # 高亮显示结果
            for card in self.mindmap_panel.get_all_cards():
                card.setSelected(card in results)

            # 聚焦到第一个结果
            if results:
                self._focus_card(results[0])

            current_index, total_results, _ = self.search_manager.get_current_status()
            self.search_toolbar.update_status(current_index, total_results, keyword)
            self.update_status(f"找到 {len(results)} 个匹配结果")
        else:
            self.search_toolbar.update_status(0, 0, keyword)
            self.update_status(f"未找到匹配 '{keyword}' 的卡片")

    def _on_navigation_updated(self, current_index, total_results):
        """导航更新"""
        current_text = self.search_toolbar.search_input.text()
        self.search_toolbar.update_status(current_index, total_results, current_text)

    def _focus_card(self, card):
        """聚焦到卡片"""
        view = self.mindmap_panel.mindmap_view
        view.centerOn(card)

    def _clear_search(self):
        """清除搜索"""
        self.search_manager.clear_search()
        for card in self.mindmap_panel.get_all_cards():
            card.setSelected(False)
        self.search_toolbar.clear_status()
        self.update_status("搜索已清除")

    def _toggle_connection_mode(self, enabled):
        """切换连接模式"""
        self.mindmap_panel.set_connection_mode(enabled)
        status = "连接模式已启用 - 点击卡片连接点开始创建连接" if enabled else "连接模式已禁用"
        self.update_status(status)

    def _handle_text_operation(self, operation):
        """处理文本操作"""
        text_input = self.input_panel.get_text_input()
        if operation == "copy":
            text_input.copy()
            self.update_status("文本已复制")
        elif operation == "paste":
            text_input.paste()
            self.update_status("文本已粘贴")
        elif operation == "cut":
            text_input.cut()
            self.update_status("文本已剪切")
        elif operation == "select_all":
            text_input.selectAll()
            self.update_status("已全选文本")

    def _handle_generation_error(self, error_msg):
        """处理生成错误"""
        self.input_panel.enable_generate_button(True)
        self._show_message(False, f"AI卡片生成失败:\n{error_msg}")

    def _clear_canvas(self, confirm=True):
        """清空画布"""
        if confirm:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "确认", "确定要清空画布吗？")
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.mindmap_panel.clear_canvas()
        self.mindmap_panel.clear_drawings()
        self.controller.card_id_counter = 0
        self.update_status("画布已清空")

    def _import_xmind(self):
        """导入XMind文件"""
        # XMind导入逻辑...
        pass

    def _export_xmind(self):
        """导出到XMind文件"""
        # XMind导出逻辑...
        pass

    def _show_message(self, success, message):
        """显示消息"""
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)

    def update_status(self, message):
        """更新状态栏"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"[{timestamp}] {message}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        cards = self.mindmap_panel.get_all_cards()
        if cards:
            self.controller.storage.save_cards(cards)
        self.controller.cleanup()
        event.accept()
```
</details>

---

## 📄 文件: ai_reader_cards\utils\__init__.py

### 📋 功能总结

该代码文件主要用于导入工具模块，包括文件读取工具和其他自定义工具类。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 导入文件读取工具类FileReader
- 限制导出的内容为FileReader、CardStorage和ClipboardMonitor

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 未发现明显问题

<details>
<summary>📝 查看源代码</summary>

```python
"""工具模块"""
"""工具模块"""
from .file_utils import FileReader

__all__ = ['FileReader', 'CardStorage', 'ClipboardMonitor']
```
</details>

---

## 📄 文件: ai_reader_cards\utils\file_utils.py

### 📋 功能总结

文件工具模块，支持多种文件格式的读取，包括文本文件和PDF文件。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 支持读取多种文件格式，包括文本文件和PDF文件
- 提供文件格式过滤器
- 处理不同编码的文本文件

### 💡 改进建议

- 📝 增加更多文件格式的支持，如Excel、图片等
- 📝 优化文本文件读取时的编码处理逻辑

### ⚠️ 潜在问题

- 🔍 对于不支持的文件格式，没有明确的处理方式
- 🔍 部分异常处理可能过于宽泛，需要更具体的异常处理

<details>
<summary>📝 查看源代码</summary>

```python
"""文件工具模块 - 处理各种文件格式的读取"""

import os
import tempfile
from pathlib import Path


class FileReader:
    """文件阅读器 - 支持多种文件格式"""

    @staticmethod
    def read_file(filepath):
        """读取文件内容

        Args:
            filepath: 文件路径

        Returns:
            tuple: (成功与否, 内容或错误信息, 文件类型)
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return False, "文件不存在", None

        try:
            if filepath.suffix.lower() == '.pdf':
                return FileReader._read_pdf(filepath)
            elif filepath.suffix.lower() in ['.txt', '.md', '.json', '.py', '.html', '.css', '.js']:
                return FileReader._read_text(filepath)
            else:
                # 尝试作为文本文件读取
                return FileReader._read_text(filepath)

        except Exception as e:
            return False, f"读取文件失败: {str(e)}", None

    @staticmethod
    def _read_text(filepath):
        """读取文本文件"""
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    return True, content, 'text'
                except UnicodeDecodeError:
                    continue
            return False, "无法解码文件内容", None
        except Exception as e:
            return False, f"读取文本文件失败: {str(e)}", None

    @staticmethod
    def _read_pdf(filepath):
        """读取PDF文件"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(filepath)
            text_content = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += f"\n--- 第 {page_num + 1} 页 ---\n"
                text_content += page.get_text()

            doc.close()
            return True, text_content, 'pdf'

        except ImportError:
            return False, "请安装PyMuPDF库: pip install PyMuPDF", None
        except Exception as e:
            return False, f"读取PDF文件失败: {str(e)}", None

    @staticmethod
    def get_supported_formats():
        """获取支持的文件格式"""
        return {
            '文本文件': ['.txt', '.md', '.json', '.xml', '.csv'],
            '代码文件': ['.py', '.java', '.cpp', '.c', '.h', '.js', '.html', '.css'],
            'PDF文件': ['.pdf'],
            '所有文件': ['*']
        }

    @staticmethod
    def create_file_filter():
        """创建文件过滤器"""
        formats = FileReader.get_supported_formats()
        filters = []
        for desc, exts in formats.items():
            if desc != '所有文件':
                filter_str = f"{desc} ({' '.join(f'*{ext}' for ext in exts)})"
                filters.append(filter_str)
        filters.append("所有文件 (*.*)")
        return ";;".join(filters)
```
</details>

---

## 📄 文件: ai_reader_cards\utils\shortcuts.py

### 📋 功能总结

这段代码定义了一个剪贴板监控器类，用于监控剪贴板内容的变化并触发回调函数。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 监控剪贴板内容变化
- 设置和获取剪贴板文本
- 处理剪贴板访问异常

### 💡 改进建议

- 📝 添加日志记录，以便更好地追踪剪贴板内容的变化和异常情况
- 📝 考虑增加对剪贴板内容变化的历史记录功能，便于用户查看之前的内容

### ⚠️ 潜在问题

- 🔍 剪贴板访问异常处理过于简单，可能会导致隐藏的问题未被发现
- 🔍 未处理剪贴板内容长度限制，可能会导致内容被截断

<details>
<summary>📝 查看源代码</summary>

```python
"""快捷键模块 - 处理剪贴板和快捷键"""

import pyperclip
from PyQt6.QtCore import QTimer


class ClipboardMonitor:
    """剪贴板监控器"""
    
    def __init__(self, callback, interval=500):
        """初始化剪贴板监控器
        
        Args:
            callback: 检测到新内容时的回调函数
            interval: 检测间隔（毫秒）
        """
        self.callback = callback
        self.last_content = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_clipboard)
        self.timer.setInterval(interval)
        self.enabled = False
    
    def start(self):
        """开始监控剪贴板"""
        self.enabled = True
        try:
            self.last_content = pyperclip.paste()
        except:
            self.last_content = ""
        self.timer.start()
    
    def stop(self):
        """停止监控剪贴板"""
        self.enabled = False
        self.timer.stop()
    
    def _check_clipboard(self):
        """检查剪贴板内容"""
        if not self.enabled:
            return
        
        try:
            current_content = pyperclip.paste()
            
            # 如果内容发生变化且不为空
            if current_content and current_content != self.last_content:
                self.last_content = current_content
                # 触发回调
                if self.callback:
                    self.callback(current_content)
        except Exception as e:
            # 忽略剪贴板访问错误
            pass
    
    def get_clipboard_text(self):
        """获取当前剪贴板文本"""
        try:
            return pyperclip.paste()
        except:
            return ""
    
    def set_clipboard_text(self, text):
        """设置剪贴板文本"""
        try:
            pyperclip.copy(text)
        except:
            pass

```
</details>

---

## 📄 文件: ai_reader_cards\utils\storage.py

### 📋 功能总结

这段代码实现了卡片数据的存储和加载功能，包括保存卡片数据到JSON文件、从JSON文件加载卡片数据、导出卡片为Markdown格式以及获取最近保存的文件列表。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 保存卡片数据到JSON文件
- 从JSON文件加载卡片数据
- 导出卡片为Markdown格式
- 获取最近保存的文件列表

### 💡 改进建议

- 📝 可以添加数据校验功能，确保保存和加载的数据格式正确。
- 📝 考虑增加日志记录功能，方便追踪存储和加载过程中的问题。

### ⚠️ 潜在问题

- 🔍 在保存和加载数据时，没有对数据进行校验，可能导致格式不正确的数据被处理。
- 🔍 文件路径的处理可能存在潜在的安全风险，建议增加路径验证机制。

<details>
<summary>📝 查看源代码</summary>

```python
"""数据存储模块 - 保存和加载卡片数据"""

import json
from pathlib import Path
from datetime import datetime


class CardStorage:
    """卡片数据存储管理器"""
    
    def __init__(self, storage_dir="data"):
        """初始化存储管理器
        
        Args:
            storage_dir: 数据存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.default_file = self.storage_dir / "cards.json"
    
    def save_cards(self, cards, filepath=None):
        """保存卡片数据到JSON文件
        
        Args:
            cards: 卡片对象列表
            filepath: 保存路径，默认为cards.json
        """
        if filepath is None:
            filepath = self.default_file
        else:
            filepath = Path(filepath)
        
        # 转换卡片为字典列表
        cards_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "cards": [card.to_dict() for card in cards]
        }
        
        # 保存到JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cards_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_cards(self, filepath=None):
        """从JSON文件加载卡片数据
        
        Args:
            filepath: 加载路径，默认为cards.json
            
        Returns:
            list: 卡片数据字典列表
        """
        if filepath is None:
            filepath = self.default_file
        else:
            filepath = Path(filepath)
        
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 返回卡片数据列表
        if isinstance(data, dict) and "cards" in data:
            return data["cards"]
        else:
            # 兼容旧格式
            return data if isinstance(data, list) else []
    
    def export_as_markdown(self, cards, filepath):
        """导出卡片为Markdown格式
        
        Args:
            cards: 卡片对象列表
            filepath: 导出路径
        """
        filepath = Path(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# 知识卡片导出\n\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"卡片总数: {len(cards)}\n\n")
            f.write("---\n\n")
            
            for idx, card in enumerate(cards, 1):
                card_dict = card.to_dict()
                f.write(f"## {idx}. {card_dict['title']}\n\n")
                f.write(f"**问题：** {card_dict['question']}\n\n")
                f.write(f"**答案：** {card_dict['answer']}\n\n")
                
                if card_dict.get('parent_id'):
                    f.write(f"*父卡片ID: {card_dict['parent_id']}*\n\n")
                
                f.write("---\n\n")
        
        return filepath
    
    def get_recent_files(self, limit=10):
        """获取最近保存的文件列表
        
        Args:
            limit: 返回文件数量限制
            
        Returns:
            list: 文件路径列表
        """
        if not self.storage_dir.exists():
            return []
        
        files = list(self.storage_dir.glob("*.json"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return files[:limit]

```
</details>

---

## 📄 文件: ai_reader_cards\workers.py

### 📋 功能总结

该代码定义了一个AIWorkerThread类，用于在后台线程中执行AI请求，并通过信号将结果返回。

### 🎯 复杂度分析

🟢 **简单**

### ✨ 核心特性

- 使用QThread实现后台工作线程
- 通过信号机制将处理结果返回给主线程

### 💡 改进建议

- 暂无改进建议

### ⚠️ 潜在问题

- 🔍 异常处理仅简单地将异常信息传递给主线程，可能需要更详细的错误处理机制

<details>
<summary>📝 查看源代码</summary>

```python
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
```
</details>

---

## 📄 文件: ai_reader_cards\xmind_preview.py

### 📋 功能总结

该代码文件实现了一个简单的 xmind 预览功能，包括生成示例 xmind 文件、加载解析树结构以及在 PyQt6 窗口中绘制简单的树状预览。

### 🎯 复杂度分析

🟡 **中等**

### ✨ 核心特性

- 生成简单的 xmind 文件用于演示
- 加载并解析 xmind 树结构
- 使用 PyQt6 绘制简单的树状预览

### 💡 改进建议

- 📝 完善 draw_tree 方法的实现，确保绘制树状结构的完整性和美观性
- 📝 添加错误处理机制，提高代码的健壮性
- 📝 考虑优化布局算法，提高绘制性能

### ⚠️ 潜在问题

- 🔍 部分方法实现中未处理异常情况，可能导致程序崩溃
- 🔍 绘制树状结构时可能存在布局不美观的问题
- 🔍 代码中缺少注释，可读性较差

<details>
<summary>📝 查看源代码</summary>

```python
"""
xmind_preview.py

功能：
- 使用 xmind 库生成一个 sample.xmind（示例结构）
- 从 .xmind 加载并解析树结构
- 在 PyQt6 窗口中用 QGraphicsView 绘制简单树状预览

注意：
- 这只是一个轻量的可视化预览；不是完整 WYSIWYG 编辑器。
- 如果你的环境是 Windows，也可以替换掉打开文件的方式（示例中已做跨平台处理）。
"""

import sys
import os
from collections import defaultdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem
)
from PyQt6.QtCore import QRectF, Qt, QPointF, QUrl
from PyQt6.QtGui import QBrush, QColor, QDesktopServices
import xmind

# ---------- xmind helper functions ----------

def create_sample_xmind(path="sample.xmind"):
    """生成一个简单的 xmind 文件用于演示"""
    wb = xmind.load(path)  # 如果不存在，会创建
    sheet = wb.getPrimarySheet()
    sheet.setTitle("Demo Sheet")
    root = sheet.getRootTopic()
    root.setTitle("Root Node")

    # 添加一些子节点（示例）
    for i in range(3):
        t = root.addSubTopic()
        t.setTitle(f"Branch {i+1}")
        # 每个分支添加子节点
        for j in range(2):
            s = t.addSubTopic()
            s.setTitle(f"Item {i+1}.{j+1}")
    xmind.save(wb, path)
    return path

def topic_get_children(topic):
    """安全地获取子节点（不同 xmind 包可能方法名或返回结构不同，做兼容）"""
    # 常见 API：getSubTopics() / getSubTopic() / getChildren()
    for meth in ("getSubTopics", "getSubTopic", "getChildren", "get_sub_topics"):
        if hasattr(topic, meth):
            children = getattr(topic, meth)()
            # 有的实现返回 dict 或 None，统一为 list
            if children is None:
                return []
            if isinstance(children, dict):
                # dict -> values
                return list(children.values())
            if isinstance(children, (list, tuple)):
                return list(children)
            # else try to iterate
            try:
                return list(children)
            except Exception:
                return []
    # 有的实现用 topic.subTopics
    if hasattr(topic, "subTopics"):
        st = getattr(topic, "subTopics")
        return list(st) if st else []
    return []

def topic_get_title(topic):
    """兼容取 title 的方法名"""
    for meth in ("getTitle", "get_title", "getTopicTitle", "title"):
        if hasattr(topic, meth):
            val = getattr(topic, meth)
            return val() if callable(val) else val
    # 直接访问属性 name/text
    for attr in ("title", "text", "name"):
        if hasattr(topic, attr):
            val = getattr(topic, attr)
            return val() if callable(val) else val
    return "Untitled"

def build_tree_from_topic(topic):
    """把 xmind 的 topic 转成 dict 树结构"""
    node = {"title": topic_get_title(topic), "obj": topic, "children": []}
    for c in topic_get_children(topic):
        node["children"].append(build_tree_from_topic(c))
    return node

# ---------- simple tree layout ----------

def layout_tree(root_node, x_spacing=150, y_spacing=80):
    """
    为每个节点分配 (x, y) 坐标
    简单策略：按层分配 y，横向均匀分布
    返回： dict: node -> QPointF
    """
    levels = defaultdict(list)
    def dfs(n, depth=0):
        levels[depth].append(n)
        for ch in n["children"]:
            dfs(ch, depth+1)
    dfs(root_node, 0)

    positions = {}
    # 对每一层，横向安排
    for depth, nodes in levels.items():
        count = len(nodes)
        # 中心对齐：将 x 从 -w ... +w
        total_width = (count - 1) * x_spacing
        for i, node in enumerate(nodes):
            x = i * x_spacing - total_width / 2
            y = depth * y_spacing
            positions[id(node)] = QPointF(x, y)
    return positions

# ---------- PyQt Graphics ----------

class XMindPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints())  # basic
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.node_items = {}  # id(node) -> rect/text

    def draw_tree(self, root_node):
        self.scene.clear()
        positions = layout_tree(root_node)
        # draw nodes
        for node in collect_nodes(root_node):
            pos = positions.get(id(node), QPointF(0,0))
            # rectangle
            rect = QGraphicsRectItem(QRectF(pos.x()-60, pos.y()-20, 120, 40))
            rect.setBrush(QBrush(QColor(240, 248, 255)))
            rect.setPen(Qt.GlobalColor.black)
            text = QGraphicsTextItem(node["title"])
            text.setTextWidth(110)
            text.setPos(pos.x()-55, pos.y()-18)
            self.scene.addItem(rect)
            self.scene.addItem(text)
            self.node_items[id(node)] = (rect, text)
        # draw lines
        def draw_lines(parent):
            for ch in parent["children"]:
                p = positions.get(id(parent), QPointF(0,0))
                c = positions.get(id(ch), QPointF(0,0))
                # simple straight line
                self.scene.addLine(p.x(), p.y()+20, c.x(), c.y()-20)
                draw_lines(ch)
        draw_lines(root_node)
        # adjust scene rect
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

def collect_nodes(root):
    out = []
    def dfs(n):
        out.append(n)
        for ch in n["children"]:
            dfs(ch)
    dfs(root)
    return out

# ---------- Main Window ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XMind PyQt Preview Demo")
        self.resize(900, 600)

        central = QWidget()
        vbox = QVBoxLayout()

        btn_create = QPushButton("Create sample.xmind")
        btn_create.clicked.connect(self.on_create)
        btn_load = QPushButton("Load .xmind and Preview")
        btn_load.clicked.connect(self.on_load)
        btn_open = QPushButton("Open sample.xmind with system default app")
        btn_open.clicked.connect(self.on_open_file)

        vbox.addWidget(btn_create)
        vbox.addWidget(btn_load)
        vbox.addWidget(btn_open)

        self.preview = XMindPreviewWidget()
        vbox.addWidget(self.preview)

        central.setLayout(vbox)
        self.setCentralWidget(central)

        # default path
        self.xmind_path = os.path.abspath("sample.xmind")

    def on_create(self):
        path = create_sample_xmind(self.xmind_path)
        self.statusBar().showMessage(f"Created: {path}")

    def on_load(self):
        # allow user to choose file
        p, _ = QFileDialog.getOpenFileName(self, "Open .xmind", os.getcwd(), "XMind files (*.xmind)")
        if not p:
            return
        try:
            wb = xmind.load(p)
            sheet = wb.getPrimarySheet()
            root = sheet.getRootTopic()
            tree = build_tree_from_topic(root)
            self.preview.draw_tree(tree)
            self.statusBar().showMessage(f"Loaded and rendered: {p}")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading xmind: {e}")

    def on_open_file(self):
        if os.path.exists(self.xmind_path):
            url = QUrl.fromLocalFile(self.xmind_path)
            QDesktopServices.openUrl(url)  # cross platform open with default app
        else:
            self.statusBar().showMessage("sample.xmind not found. Create it first.")

# ---------- run ----------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

```
</details>

---

