# 合并的 Python 代码文件

# 文件路径: AIREADME.py
```python
import os
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

class CodeAnalyzer:
    """代码分析器"""

    def __init__(self, model="gpt-3.5-turbo"):
        api_key = os.environ.get("OPENAI_API_KEY", "sk-lwkQzJYwYdJwbQ4DaAlM3Ti6pgMCzEgztBjREyOlYFPLPDQP")
        if not api_key:
            raise RuntimeError("未检测到 OPENAI_API_KEY 环境变量，请先设置API密钥")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.chatanywhere.tech/v1"
        )
        self.model = model
        self.lock = threading.Lock()
    
    def analyze_code(self, file_path, code_content):
        """分析Python代码
        
        Args:
            file_path: 文件路径
            code_content: 代码内容
            
        Returns:
            dict: 包含分析结果的字典
        """
        prompt = f"""请分析以下Python代码，提供详细的分析报告。代码来自文件: {file_path}

请按照以下结构返回JSON格式的分析结果：
- function_summary: 主要函数/方法的简要说明
- key_features: 代码的核心功能特性（列表形式）
- complexity_analysis: 代码复杂度分析（简单/中等/复杂）
- improvement_suggestions: 改进建议（列表形式）
- potential_issues: 潜在问题或风险点（列表形式）

代码内容：
{code_content[:4000]}  # 限制内容长度
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码分析专家，擅长分析Python代码的结构、功能和优化点。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            result_text = (response.choices[0].message.content or "").strip()
            
            # 解析JSON响应
            analysis_data = self._parse_json_response(result_text)
            
            # 构建分析结果
            analysis_result = {
                "file_path": file_path,
                "function_summary": analysis_data.get("function_summary", "无总结"),
                "key_features": analysis_data.get("key_features", []),
                "complexity_analysis": analysis_data.get("complexity_analysis", "未知"),
                "improvement_suggestions": analysis_data.get("improvement_suggestions", []),
                "potential_issues": analysis_data.get("potential_issues", [])
            }
            
            with self.lock:
                print(f"✅ 已完成分析: {file_path}")
            
            return analysis_result
            
        except Exception as e:
            with self.lock:
                print(f"❌ 分析失败 {file_path}: {str(e)}")
            
            return {
                "file_path": file_path,
                "function_summary": f"分析失败: {str(e)}",
                "key_features": [],
                "complexity_analysis": "未知",
                "improvement_suggestions": [],
                "potential_issues": []
            }
    
    def _parse_json_response(self, response_text):
        """解析AI返回的JSON响应"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return {
                    "function_summary": "JSON解析失败",
                    "key_features": ["无法解析AI响应"],
                    "complexity_analysis": "未知",
                    "improvement_suggestions": ["检查AI响应格式"],
                    "potential_issues": ["AI响应格式异常"]
                }

def merge_py_to_markdown(root_dir, max_workers=3):
    """合并Python文件并生成代码分析报告（多线程版本）"""
    
    # 初始化代码分析器
    analyzer = CodeAnalyzer()
    
    # 目标 Markdown 文件路径
    output_dir = os.path.join(root_dir, "")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "AI_code_analysis.md")

    # 收集所有Python文件
    python_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if os.path.abspath(dirpath) == os.path.abspath(output_dir):
            continue
        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                rel_path = os.path.relpath(filepath, root_dir)
                python_files.append((rel_path, filepath))

    print(f"🔍 找到 {len(python_files)} 个Python文件，开始分析...")

    # 多线程分析文件
    analysis_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_file = {}
        for rel_path, filepath in python_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    code_content = f.read()
                
                # 跳过空文件或过小的文件
                if len(code_content.strip()) < 10:
                    continue
                
                # 提交分析任务
                future = executor.submit(analyzer.analyze_code, rel_path, code_content)
                future_to_file[future] = (rel_path, filepath, code_content)
                
            except Exception as e:
                print(f"❌ 读取文件失败 {rel_path}: {e}")

        # 收集完成的任务
        for future in as_completed(future_to_file):
            rel_path, filepath, code_content = future_to_file[future]
            try:
                result = future.result()
                analysis_results.append((rel_path, filepath, code_content, result))
            except Exception as e:
                print(f"❌ 任务执行失败 {rel_path}: {e}")

    # 按文件路径排序结果
    analysis_results.sort(key=lambda x: x[0])

    # 生成Markdown报告
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# AI代码分析报告\n\n")
        out.write("> 本文档由AI自动分析项目中的Python代码并生成详细报告\n\n")
        out.write(f"## 项目概览\n\n")
        out.write(f"- **分析文件数**: {len(analysis_results)}\n")
        out.write(f"- **分析时间**: {os.path.basename(root_dir)}\n")
        out.write(f"- **使用模型**: GPT-3.5-turbo\n\n")
        out.write("---\n\n")

        for rel_path, filepath, code_content, analysis in analysis_results:
            out.write(f"## 📄 文件: {rel_path}\n\n")
            
            # 功能总结
            out.write(f"### 📋 功能总结\n\n")
            out.write(f"{analysis['function_summary']}\n\n")
            
            # 复杂度分析
            out.write(f"### 🎯 复杂度分析\n\n")
            complexity = analysis['complexity_analysis']
            complexity_emoji = "🟢" if "简单" in complexity else "🟡" if "中等" in complexity else "🔴"
            out.write(f"{complexity_emoji} **{complexity}**\n\n")
            
            # 核心特性
            out.write(f"### ✨ 核心特性\n\n")
            features = analysis['key_features']
            if features:
                for feature in features:
                    out.write(f"- {feature}\n")
            else:
                out.write("- 无明确特性标识\n")
            out.write("\n")
            
            # 改进建议
            out.write(f"### 💡 改进建议\n\n")
            suggestions = analysis['improvement_suggestions']
            if suggestions:
                for suggestion in suggestions:
                    out.write(f"- 📝 {suggestion}\n")
            else:
                out.write("- 暂无改进建议\n")
            out.write("\n")
            
            # 潜在问题
            out.write(f"### ⚠️ 潜在问题\n\n")
            issues = analysis['potential_issues']
            if issues:
                for issue in issues:
                    out.write(f"- 🔍 {issue}\n")
            else:
                out.write("- 未发现明显问题\n")
            out.write("\n")
            
            # 源代码（可折叠）
            out.write("<details>\n<summary>📝 查看源代码</summary>\n\n")
            out.write("```python\n")
            out.write(code_content)
            out.write("\n```\n")
            out.write("</details>\n\n")
            
            out.write("---\n\n")

    print(f"✅ AI代码分析报告已生成: {output_file}")
    print(f"📊 成功分析 {len(analysis_results)} 个文件")

def analyze_single_file(file_path):
    """单独分析一个Python文件"""
    analyzer = CodeAnalyzer()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        print(f"正在分析: {file_path}")
        result = analyzer.analyze_code(file_path, code_content)
        
        print(f"\n📄 文件: {file_path}")
        print(f"📋 功能总结: {result['function_summary']}")
        print(f"🎯 复杂度: {result['complexity_analysis']}")
        print(f"✨ 核心特性: {', '.join(result['key_features'][:3])}")
        print(f"💡 改进建议: {', '.join(result['improvement_suggestions'][:2])}")
        print(f"⚠️ 潜在问题: {', '.join(result['potential_issues'][:2])}")
        print("-" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ 分析文件 {file_path} 时出错: {e}")
        return None

# 使用方法
if __name__ == "__main__":
    root = r"E:\onedrive\OneDrive - bupt.edu.cn\AIcard"  # ← 修改为你的主目录路径
    
    # 生成完整的AI代码分析报告（多线程，3个worker）
    merge_py_to_markdown(root, max_workers=3)
    
    # 如果需要单独分析某个文件，可以使用：
    # single_file = r"C:\Users\anyon\pythonProject\example.py"
    # analyze_single_file(single_file)
```

---

# 文件路径: anki_test.py
```python
import os
import json
import requests

ANKI_CONNECT_URL = "http://localhost:8765"
ANKI_CONNECT_VERSION = 6

def invoke(action, params=None):
    payload = {
        "action": action,
        "version": ANKI_CONNECT_VERSION,
        "params": params or {}
    }
    r = requests.post(ANKI_CONNECT_URL, json=payload)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data["result"]

def find_json_file():
    """在当前目录及子目录下查找 JSON 文件"""
    for root, _, files in os.walk("."):
        for f in files:
            if f.lower() == "card.json":
                return os.path.join(root, f)
        for f in files:
            if f.lower().endswith(".json"):
                return os.path.join(root, f)
    return None

def create_deck(deck_name):
    try:
        invoke("createDeck", {"deck": deck_name})
    except Exception as e:
        print(f"创建牌组时出错：{e}")

def add_note(deck_name, front, back, tags=None):
    note = {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {"Front": front, "Back": back},
        "options": {"allowDuplicate": False},
        "tags": tags or []
    }
    return invoke("addNote", {"note": note})

def sanitize_tag(s):
    return "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(s))[:50]

def main():
    json_path = find_json_file()
    if not json_path:
        print("❌ 未找到任何 JSON 文件，请将 card.json 放在当前目录或子目录下。")
        return

    print(f"✅ 找到 JSON 文件：{json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards = data.get("cards", [])
    if not cards:
        print("❌ JSON 文件中未找到 'cards' 列表。")
        return

    deck_name = "card_json_import"
    create_deck(deck_name)

    added, skipped, errors = 0, 0, 0

    for c in cards:
        title = c.get("title", "")
        q = c.get("question", "")
        a = c.get("answer", "")
        front = f"<b>{title}</b><br><br>{q}" if title else q
        back = a
        tags = ["imported_json"]
        if c.get("id"):
            tags.append(f"id_{c['id']}")
        tags.append(sanitize_tag(title))

        try:
            note_id = add_note(deck_name, front, back, tags)
            print(f"✅ 已添加卡片：{title} (note_id={note_id})")
            added += 1
        except Exception as e:
            msg = str(e).lower()
            if "duplicate" in msg:
                print(f"⚠️ 跳过重复卡片：{title}")
                skipped += 1
            else:
                print(f"❌ 添加失败：{title} -> {e}")
                errors += 1

    print(f"\n📊 导入完成：共 {len(cards)} 张 | 成功 {added} | 跳过 {skipped} | 错误 {errors}")

if __name__ == "__main__":
    main()

```

---

# 文件路径: hh.py
```python
import os

def merge_py_to_markdown(root_dir=None, output_filename="all_code.md"):
    """
    合并指定目录及其子目录下的所有 .py 文件为一个 Markdown 文件。
    忽略 test 文件夹及其子目录。
    每个文件会带有路径标识，并以 Markdown 代码块格式包裹。
    """

    if root_dir is None:
        root_dir = os.getcwd()

    output_file = os.path.join(root_dir, output_filename)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# 合并的 Python 代码文件\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # 过滤掉 test 目录
            if "test111" in dirpath.split(os.sep):
                continue

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

---

# 文件路径: test.py
```python
#!/usr/bin/env python3
"""
MindMap/Tree布局演示 - 专业版连线功能（修正版）
功能：
- 节点树数据模型，可序列化 JSON
- 多布局算法: mind_map, logical, timeline, fishbone
- 专业连线绘制：贝塞尔曲线、渐变色彩、智能避让
- 节点拖拽 + 自动排列
- 保存/加载 JSON
"""

import sys
import json
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QFileDialog, QComboBox, QLabel, QSlider, QGraphicsItem
)
from PyQt6.QtCore import Qt, QPointF, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainterPath, QPainter, QLinearGradient, QRadialGradient
)


# -------------------------
# 数据模型
# -------------------------
class TreeNode:
    def __init__(self, title, x=0, y=0):
        self.id = id(self)
        self.title = title
        self.parent = None
        self.children = []
        self.x = x
        self.y = y
        self.level = 0  # 节点层级

    def add_child(self, node):
        node.parent = self
        node.level = self.level + 1
        self.children.append(node)

    def to_dict(self):
        return {
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["title"], data.get("x", 0), data.get("y", 0))
        for child_data in data.get("children", []):
            child_node = TreeNode.from_dict(child_data)
            node.add_child(child_node)
        return node


# -------------------------
# 专业连线管理器
# -------------------------
class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.animation_enabled = True

    def create_connection(self, parent_node, child_node, connection_type="bezier"):
        """创建专业连线（parent_node / child_node 应为 VisualNode 实例）"""
        if connection_type == "bezier":
            return BezierConnection(parent_node, child_node)
        elif connection_type == "smart":
            return SmartConnection(parent_node, child_node)
        elif connection_type == "gradient":
            return GradientConnection(parent_node, child_node)
        else:
            return BezierConnection(parent_node, child_node)

    def update_all_connections(self):
        """更新所有连线（若需要缓存可用）"""
        for connection in self.connections:
            connection.update_path()


# -------------------------
# 专业连线基类
# -------------------------
class ProfessionalConnection:
    def __init__(self, parent_node: QGraphicsRectItem, child_node: QGraphicsRectItem):
        self.parent_node = parent_node
        self.child_node = child_node
        self.path = QPainterPath()
        self.animation = None

    def get_connection_points(self):
        """计算连接点位置（基于 visual node 的 center 与矩形边界）"""
        # 使用 VisualNode 的 center_pos() 方法（若传入的是 VisualNode）
        parent_center = self.parent_node.center_pos() if hasattr(self.parent_node, "center_pos") else QPointF(
            self.parent_node.pos().x(), self.parent_node.pos().y()
        )
        child_center = self.child_node.center_pos() if hasattr(self.child_node, "center_pos") else QPointF(
            self.child_node.pos().x(), self.child_node.pos().y()
        )

        # 获取宽高（支持 VisualNode 常量或取 boundingRect）
        try:
            pw = self.parent_node.WIDTH
            ph = self.parent_node.HEIGHT
        except Exception:
            br = self.parent_node.boundingRect()
            pw, ph = br.width(), br.height()

        try:
            cw = self.child_node.WIDTH
            ch = self.child_node.HEIGHT
        except Exception:
            br2 = self.child_node.boundingRect()
            cw, ch = br2.width(), br2.height()

        dx = child_center.x() - parent_center.x()
        dy = child_center.y() - parent_center.y()

        # 计算连接点（在矩形边界上，简化为水平或垂直方向连接）
        if abs(dx) > abs(dy):  # 水平方向为主
            if dx > 0:  # 子在父右侧
                start = QPointF(parent_center.x() + pw / 2, parent_center.y())
                end = QPointF(child_center.x() - cw / 2, child_center.y())
            else:  # 子在父左侧
                start = QPointF(parent_center.x() - pw / 2, parent_center.y())
                end = QPointF(child_center.x() + cw / 2, child_center.y())
        else:  # 垂直方向为主
            if dy > 0:  # 子在父下方
                start = QPointF(parent_center.x(), parent_center.y() + ph / 2)
                end = QPointF(child_center.x(), child_center.y() - ch / 2)
            else:  # 子在父上方
                start = QPointF(parent_center.x(), parent_center.y() - ph / 2)
                end = QPointF(child_center.x(), child_center.y() + ch / 2)

        return start, end

    def update_path(self):
        """更新连线路径 - 子类实现"""
        raise NotImplementedError

    def draw(self, painter: QPainter):
        """绘制连线 - 子类实现"""
        raise NotImplementedError


# -------------------------
# 贝塞尔曲线连线
# -------------------------
class BezierConnection(ProfessionalConnection):
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)
        self.curve_strength = 0.3

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 计算控制点
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        control1 = QPointF(start.x() + dx * self.curve_strength, start.y())
        control2 = QPointF(end.x() - dx * self.curve_strength, end.y())

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        pen = QPen(QColor(70, 130, 180), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)

        # 绘制箭头
        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            # 计算箭头位置（在路径的末端）
            arrow_size = 12
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            painter.setBrush(QBrush(QColor(70, 130, 180)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


# -------------------------
# 智能连线（自动避让）
# -------------------------
class SmartConnection(ProfessionalConnection):
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 智能路径：避免直线交叉，添加中间控制点
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2

        # 根据节点层级调整曲线（尝试读取 child_node 的 TreeNode 层级）
        curve_offset = 0
        if hasattr(self.child_node, "tree_node"):
            curve_offset = 50 * max(0, (self.child_node.tree_node.level - 1))
        else:
            curve_offset = 50

        control1 = QPointF(mid_x, start.y())
        control2 = QPointF(mid_x, end.y())

        # 如果节点在同一侧，添加偏移避免重叠
        if abs(start.x() - end.x()) < 100:
            control1.setX(control1.x() + curve_offset)
            control2.setX(control2.x() + curve_offset)

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        # 根据层级设置不同颜色（尝试读取 child_node 层级）
        level = 1
        if hasattr(self.child_node, "tree_node"):
            level = max(1, self.child_node.tree_node.level)

        level_colors = [
            QColor(70, 130, 180),  # 第1级
            QColor(65, 105, 225),  # 第2级
            QColor(135, 206, 250),  # 第3级
            QColor(173, 216, 230)  # 第4级
        ]

        color_index = min(level - 1, len(level_colors) - 1)
        pen_color = level_colors[color_index]

        pen = QPen(pen_color, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        # pen.setDashPattern([3.0, 2.0])  # PyQt6 支持 setDashPattern，但也可使用样式
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)

        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        # 复用 Bezier 箭头实现（简化）
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 10
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            painter.setBrush(QBrush(QColor(65, 105, 225)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


# -------------------------
# 渐变连线
# -------------------------
class GradientConnection(ProfessionalConnection):
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 创建平滑的贝塞尔曲线
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        control1 = QPointF(start.x() + dx * 0.5, start.y())
        control2 = QPointF(end.x() - dx * 0.5, end.y())

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        start, end = self.get_connection_points()

        # 创建渐变画笔
        gradient = QLinearGradient(start, end)
        gradient.setColorAt(0, QColor(255, 105, 97))  # 珊瑚红
        gradient.setColorAt(0.5, QColor(255, 180, 128))  # 浅橙色
        gradient.setColorAt(1, QColor(119, 221, 119))  # 浅绿色

        pen = QPen(QBrush(gradient), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)

        # 渐变箭头
        self.draw_gradient_arrow(painter)

    def draw_gradient_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 14
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            # 箭头渐变
            arrow_gradient = QRadialGradient(end, arrow_size)
            arrow_gradient.setColorAt(0, QColor(119, 221, 119))
            arrow_gradient.setColorAt(1, QColor(255, 105, 97))

            painter.setBrush(QBrush(arrow_gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
            painter.drawPath(arrow_path)


# -------------------------
# 场景 + 专业连线绘制
# -------------------------
class ProfessionalMindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-2000, -2000, 4000, 4000)
        self.visual_nodes = []
        self.connection_manager = ConnectionManager()
        self.connection_style = "bezier"  # 默认连线样式

    def add_visual_node(self, visual_node: 'VisualNode'):
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)

    def set_connection_style(self, style):
        """设置连线样式"""
        self.connection_style = style
        self.update()

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """绘制专业连线"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        connections = []
        for vn in self.visual_nodes:
            node = vn.tree_node
            for child in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node == child), None)
                if child_vn:
                    connection = self.connection_manager.create_connection(vn, child_vn, self.connection_style)
                    connection.update_path()
                    connections.append(connection)

        # 绘制所有连线（在前景层）
        for connection in connections:
            connection.draw(painter)


# -------------------------
# 增强的可视化节点
# -------------------------
class VisualNode(QGraphicsRectItem):
    WIDTH = 160
    HEIGHT = 90

    def __init__(self, tree_node: TreeNode):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # 根据层级设置不同样式
        self.setup_style()

        # 文本
        self.text_item = QGraphicsTextItem(self.tree_node.title, self)
        self.text_item.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.text_item.setDefaultTextColor(self.get_text_color())
        self.text_item.setTextWidth(self.WIDTH - 20)
        self.text_item.setPos(10, 10)

    def setup_style(self):
        """根据节点层级设置样式"""
        level_styles = [
            (QColor(74, 124, 89), QColor(173, 223, 173), 2.5),  # 根节点
            (QColor(49, 99, 149), QColor(173, 216, 230), 2.0),  # 第1级
            (QColor(149, 99, 49), QColor(255, 218, 185), 1.5),  # 第2级
            (QColor(99, 99, 99), QColor(240, 240, 240), 1.0)  # 其他级别
        ]

        level_index = min(self.tree_node.level, len(level_styles) - 1)
        border_color, fill_color, border_width = level_styles[level_index]

        # 设置渐变填充
        gradient = QLinearGradient(0, 0, 0, self.HEIGHT)
        gradient.setColorAt(0, fill_color.lighter(120))
        gradient.setColorAt(1, fill_color.darker(110))

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(border_color, border_width))

        # 圆角效果（这里仍使用矩形，但可扩展为绘制圆角）
        self.setRect(0, 0, self.WIDTH, self.HEIGHT)

    def get_text_color(self):
        """根据背景色返回合适的文字颜色"""
        level_colors = [
            QColor(255, 255, 255),  # 根节点 - 白色文字
            QColor(0, 0, 0),  # 第1级 - 黑色文字
            QColor(0, 0, 0),  # 第2级 - 黑色文字
            QColor(80, 80, 80)  # 其他级别 - 深灰色
        ]
        return level_colors[min(self.tree_node.level, len(level_colors) - 1)]

    def itemChange(self, change, value):
        # 当节点位置改变时，同步 TreeNode 的 x,y 并让场景更新连线
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x() + self.WIDTH / 2, self.pos().y() + self.HEIGHT / 2)


# -------------------------
# 布局算法
# -------------------------
class LayoutEngine:
    @staticmethod
    def mind_map(root: TreeNode, h_spacing=200, v_spacing=100):
        """左右树形布局"""

        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            child_y = y_offset - v_spacing * (len(node.children) - 1) / 2
            for c in node.children:
                layout(c, depth + 1, child_y, direction)
                child_y += v_spacing

        # 根节点在中间，左右分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        root.x = 0
        root.y = 0

        # 布局左侧子节点
        left_y = -v_spacing * (len(left_children) - 1) / 2
        for c in left_children:
            layout(c, 1, left_y, -1)  # 向左
            left_y += v_spacing

        # 布局右侧子节点
        right_y = -v_spacing * (len(right_children) - 1) / 2
        for c in right_children:
            layout(c, 1, right_y, 1)  # 向右
            right_y += v_spacing

    @staticmethod
    def logical(root: TreeNode, h_spacing=200, v_spacing=120):
        """自上而下逻辑结构布局"""

        def layout(node, depth=0, x_offset=0):
            node.x = x_offset
            node.y = depth * v_spacing
            if node.children:
                child_x = x_offset - (len(node.children) - 1) * h_spacing / 2
                for c in node.children:
                    layout(c, depth + 1, child_x)
                    child_x += h_spacing

        layout(root)

    @staticmethod
    def timeline(root: TreeNode, h_spacing=200):
        """时间轴布局，横向排列"""

        def layout(node, x_offset=0, y_offset=0):
            node.x = x_offset
            node.y = y_offset
            child_x = x_offset + h_spacing
            for i, c in enumerate(node.children):
                layout(c, child_x, y_offset + (i - len(node.children) // 2) * 100)
                child_x += h_spacing

        layout(root)

    @staticmethod
    def fishbone(root: TreeNode, h_spacing=200, v_spacing=100):
        """鱼骨图布局"""

        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            for i, c in enumerate(node.children):
                layout(c, depth + 1, y_offset + (i - len(node.children) // 2) * v_spacing, direction)

        # 左右对称分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        for c in left_children:
            layout(c, 1, 0, -1)
        for c in right_children:
            layout(c, 1, 0, 1)


# -------------------------
# 主窗口
# -------------------------
class ProfessionalMindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("专业思维导图 - 高级连线演示")
        self.resize(1400, 900)
        self.root_node = None
        self.scene = ProfessionalMindMapScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 专业控制面板
        control = QHBoxLayout()

        # 布局选择
        control.addWidget(QLabel("布局算法:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["mind_map", "logical", "timeline", "fishbone"])
        control.addWidget(self.layout_combo)

        # 连线样式选择
        control.addWidget(QLabel("连线样式:"))
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["bezier", "smart", "gradient"])
        self.connection_combo.currentTextChanged.connect(self.change_connection_style)
        control.addWidget(self.connection_combo)

        # 功能按钮
        add_btn = QPushButton("生成示例树")
        add_btn.clicked.connect(self.create_sample_tree)
        control.addWidget(add_btn)

        save_btn = QPushButton("保存 JSON")
        save_btn.clicked.connect(self.save_json)
        control.addWidget(save_btn)

        load_btn = QPushButton("加载 JSON")
        load_btn.clicked.connect(self.load_json)
        control.addWidget(load_btn)

        clear_btn = QPushButton("清空画布")
        clear_btn.clicked.connect(self.clear_canvas)
        control.addWidget(clear_btn)

        layout.addLayout(control)
        layout.addWidget(self.view)

        # 设置视图属性
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def change_connection_style(self, style):
        """切换连线样式"""
        self.scene.set_connection_style(style)
        self.scene.update()

    def create_sample_tree(self):
        """创建专业示例树"""
        self.root_node = TreeNode("核心主题")
        self.root_node.level = 0

        # 第一级节点
        topics = ["战略规划", "产品设计", "技术架构", "市场营销", "运营管理"]
        for i, topic in enumerate(topics):
            child = TreeNode(topic)
            self.root_node.add_child(child)

            # 第二级节点
            sub_topics = []
            if topic == "战略规划":
                sub_topics = ["市场分析", "竞争策略", "目标设定", "资源分配"]
            elif topic == "产品设计":
                sub_topics = ["用户研究", "功能规划", "原型设计", "用户体验"]
            elif topic == "技术架构":
                sub_topics = ["前端技术", "后端服务", "数据库设计", "部署方案"]
            elif topic == "市场营销":
                sub_topics = ["品牌建设", "渠道策略", "内容营销", "数据分析"]
            else:
                sub_topics = ["流程优化", "团队管理", "绩效评估", "风险控制"]

            for sub_topic in sub_topics:
                sub_child = TreeNode(sub_topic)
                child.add_child(sub_child)

                # 第三级节点（部分节点）
                if sub_topic in ["用户研究", "功能规划", "前端技术", "后端服务"]:
                    details = ["需求收集", "方案评估", "实施计划", "验收标准"]
                    for detail in details[:2]:  # 只添加前两个细节
                        detail_node = TreeNode(detail)
                        sub_child.add_child(detail_node)

        self.apply_layout()
        self.refresh_scene()

    def apply_layout(self):
        if not self.root_node:
            return
        layout_name = self.layout_combo.currentText()
        engine = LayoutEngine
        # 动态调用布局函数
        func = getattr(engine, layout_name, None)
        if func:
            func(self.root_node)

    def refresh_scene(self):
        self.scene.clear()
        self.scene.visual_nodes.clear()

        def add_visual(node):
            vn = VisualNode(node)
            self.scene.add_visual_node(vn)
            for c in node.children:
                add_visual(c)

        if self.root_node:
            add_visual(self.root_node)
            self.scene.update()

    def save_json(self):
        if not self.root_node:
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.root_node.to_dict(), f, ensure_ascii=False, indent=2)

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "加载 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.root_node = TreeNode.from_dict(data)
            # 重新计算层级
            self.calculate_levels(self.root_node)
            self.apply_layout()
            self.refresh_scene()

    def calculate_levels(self, node, level=0):
        """计算节点层级"""
        node.level = level
        for child in node.children:
            self.calculate_levels(child, level + 1)

    def clear_canvas(self):
        """清空画布"""
        self.root_node = None
        self.scene.clear()
        self.scene.visual_nodes.clear()


# -------------------------
# 主函数
# -------------------------
def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    win = ProfessionalMindMapWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

```

---

# 文件路径: test1buju.py
```python
#!/usr/bin/env python3
"""
MindMap/Tree布局演示
支持：
- 节点树数据模型，可序列化 JSON
- 多布局算法: mindMap, logical, timeline, fishbone
- 父子连线绘制
- 节点拖拽 + 自动排列
- 保存/加载 JSON
"""

import sys, json, random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QFileDialog, QComboBox
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QPainter


# -------------------------
# 数据模型
# -------------------------
class TreeNode:
    def __init__(self, title, x=0, y=0):
        self.id = id(self)
        self.title = title
        self.parent = None
        self.children = []
        self.x = x
        self.y = y

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def to_dict(self):
        return {
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["title"], data.get("x",0), data.get("y",0))
        for child_data in data.get("children", []):
            child_node = TreeNode.from_dict(child_data)
            node.add_child(child_node)
        return node


# -------------------------
# 可视化节点
# -------------------------
class VisualNode(QGraphicsRectItem):
    WIDTH = 150
    HEIGHT = 80

    def __init__(self, tree_node: TreeNode):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setBrush(QBrush(QColor(255,255,255)))
        self.setPen(QPen(QColor(100,100,100), 2))

        # 文本
        self.text_item = QGraphicsTextItem(self.tree_node.title, self)
        self.text_item.setFont(QFont("Arial", 10))
        self.text_item.setDefaultTextColor(QColor(0,0,0))
        self.text_item.setPos(10,10)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x() + self.WIDTH/2, self.pos().y() + self.HEIGHT/2)


# -------------------------
# 布局算法
# -------------------------
class LayoutEngine:
    @staticmethod
    def mind_map(root: TreeNode, h_spacing=200, v_spacing=100):
        """左右树形布局"""
        def layout(node, depth=0, y_offset=0):
            node.x = depth * h_spacing
            node.y = y_offset
            child_y = y_offset - v_spacing*(len(node.children)-1)/2
            for c in node.children:
                layout(c, depth+1, child_y)
                child_y += v_spacing
        layout(root)

    @staticmethod
    def logical(root: TreeNode, h_spacing=200, v_spacing=120):
        """自上而下逻辑结构布局"""
        def layout(node, depth=0, x_offset=0):
            node.x = x_offset
            node.y = depth * v_spacing
            child_x = x_offset - (len(node.children)-1)*h_spacing/2
            for c in node.children:
                layout(c, depth+1, child_x)
                child_x += h_spacing
        layout(root)

    @staticmethod
    def timeline(root: TreeNode, h_spacing=200):
        """时间轴布局，横向排列"""
        def layout(node, x_offset=0):
            node.x = x_offset
            node.y = 0
            child_x = x_offset + h_spacing
            for c in node.children:
                layout(c, child_x)
                child_x += h_spacing
        layout(root)

    @staticmethod
    def fishbone(root: TreeNode, h_spacing=200, v_spacing=100):
        """鱼骨图布局"""
        def layout(node, depth=0, y_offset=0):
            node.x = depth*h_spacing
            node.y = y_offset
            for i, c in enumerate(node.children):
                layout(c, depth+1, y_offset + (i - len(node.children)//2)*v_spacing)
        layout(root)


# -------------------------
# 场景 + 绘制连线
# -------------------------
class MindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-1000,-1000,2000,2000)
        self.visual_nodes = []

    def add_visual_node(self, visual_node: VisualNode):
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)

    def drawForeground(self, painter: QPainter, rect):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(70,130,180), 2)
        painter.setPen(pen)
        for vn in self.visual_nodes:
            node = vn.tree_node
            for c in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node==c), None)
                if child_vn:
                    MindMapScene.draw_connection(painter, vn.center_pos(), child_vn.center_pos())

    @staticmethod
    def draw_connection(painter, start, end):
        path = QPainterPath()
        mid_x = (start.x() + end.x())/2
        path.moveTo(start)
        path.lineTo(mid_x, start.y())
        path.lineTo(mid_x, end.y())
        path.lineTo(end)
        painter.drawPath(path)


# -------------------------
# 主窗口
# -------------------------
class MindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python MindMap Demo")
        self.resize(1200, 800)
        self.root_node = None
        self.scene = MindMapScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        control = QHBoxLayout()
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["mind_map","logical","timeline","fishbone"])
        control.addWidget(self.layout_combo)

        add_btn = QPushButton("生成示例树")
        add_btn.clicked.connect(self.create_sample_tree)
        control.addWidget(add_btn)

        save_btn = QPushButton("保存 JSON")
        save_btn.clicked.connect(self.save_json)
        control.addWidget(save_btn)

        load_btn = QPushButton("加载 JSON")
        load_btn.clicked.connect(self.load_json)
        control.addWidget(load_btn)

        layout.addLayout(control)
        layout.addWidget(self.view)

    def create_sample_tree(self):
        # 创建示例树
        self.root_node = TreeNode("根节点")
        for i in range(3):
            child = TreeNode(f"子节点{i+1}")
            self.root_node.add_child(child)
            for j in range(2):
                child.add_child(TreeNode(f"孙节点{i+1}-{j+1}"))
        self.apply_layout()
        self.refresh_scene()

    def apply_layout(self):
        if not self.root_node:
            return
        layout_name = self.layout_combo.currentText()
        engine = LayoutEngine
        getattr(engine, layout_name)(self.root_node)

    def refresh_scene(self):
        self.scene.clear()
        self.scene.visual_nodes.clear()
        def add_visual(node):
            vn = VisualNode(node)
            self.scene.add_visual_node(vn)
            for c in node.children:
                add_visual(c)
        add_visual(self.root_node)

    def save_json(self):
        if not self.root_node:
            return
        path,_ = QFileDialog.getSaveFileName(self,"保存 JSON","","JSON Files (*.json)")
        if path:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(self.root_node.to_dict(), f, ensure_ascii=False, indent=2)

    def load_json(self):
        path,_ = QFileDialog.getOpenFileName(self,"加载 JSON","","JSON Files (*.json)")
        if path:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
            self.root_node = TreeNode.from_dict(data)
            self.apply_layout()
            self.refresh_scene()


# -------------------------
# 主函数
# -------------------------
def main():
    app = QApplication(sys.argv)
    win = MindMapWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

```

---

# 文件路径: madmap\connections.py
```python
"""专业连线管理器"""
import math
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath, QPainter, QPen, QBrush, QColor, QLinearGradient, QRadialGradient
from PyQt6.QtCore import Qt

class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.animation_enabled = True

    def create_connection(self, parent_node, child_node, connection_type="bezier"):
        """创建专业连线"""
        if connection_type == "bezier":
            return BezierConnection(parent_node, child_node)
        elif connection_type == "smart":
            return SmartConnection(parent_node, child_node)
        elif connection_type == "gradient":
            return GradientConnection(parent_node, child_node)
        else:
            return BezierConnection(parent_node, child_node)

    def update_all_connections(self):
        """更新所有连线"""
        for connection in self.connections:
            connection.update_path()


class ProfessionalConnection:
    """专业连线基类"""
    def __init__(self, parent_node, child_node):
        self.parent_node = parent_node
        self.child_node = child_node
        self.path = QPainterPath()
        self.animation = None

    def get_connection_points(self):
        """计算连接点位置"""
        parent_center = self.parent_node.center_pos() if hasattr(self.parent_node, "center_pos") else QPointF(
            self.parent_node.pos().x(), self.parent_node.pos().y()
        )
        child_center = self.child_node.center_pos() if hasattr(self.child_node, "center_pos") else QPointF(
            self.child_node.pos().x(), self.child_node.pos().y()
        )

        # 获取宽高
        try:
            pw = self.parent_node.WIDTH
            ph = self.parent_node.HEIGHT
        except Exception:
            br = self.parent_node.boundingRect()
            pw, ph = br.width(), br.height()

        try:
            cw = self.child_node.WIDTH
            ch = self.child_node.HEIGHT
        except Exception:
            br2 = self.child_node.boundingRect()
            cw, ch = br2.width(), br2.height()

        dx = child_center.x() - parent_center.x()
        dy = child_center.y() - parent_center.y()

        # 计算连接点
        if abs(dx) > abs(dy):  # 水平方向为主
            if dx > 0:  # 子在父右侧
                start = QPointF(parent_center.x() + pw / 2, parent_center.y())
                end = QPointF(child_center.x() - cw / 2, child_center.y())
            else:  # 子在父左侧
                start = QPointF(parent_center.x() - pw / 2, parent_center.y())
                end = QPointF(child_center.x() + cw / 2, child_center.y())
        else:  # 垂直方向为主
            if dy > 0:  # 子在父下方
                start = QPointF(parent_center.x(), parent_center.y() + ph / 2)
                end = QPointF(child_center.x(), child_center.y() - ch / 2)
            else:  # 子在父上方
                start = QPointF(parent_center.x(), parent_center.y() - ph / 2)
                end = QPointF(child_center.x(), child_center.y() + ch / 2)

        return start, end

    def update_path(self):
        """更新连线路径 - 子类实现"""
        raise NotImplementedError

    def draw(self, painter: QPainter):
        """绘制连线 - 子类实现"""
        raise NotImplementedError


class BezierConnection(ProfessionalConnection):
    """贝塞尔曲线连线"""
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)
        self.curve_strength = 0.3

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 计算控制点
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        control1 = QPointF(start.x() + dx * self.curve_strength, start.y())
        control2 = QPointF(end.x() - dx * self.curve_strength, end.y())

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        pen = QPen(QColor(70, 130, 180), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 12
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            painter.setBrush(QBrush(QColor(70, 130, 180)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


class SmartConnection(ProfessionalConnection):
    """智能连线（自动避让）"""
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 智能路径：避免直线交叉，添加中间控制点
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2

        # 根据节点层级调整曲线
        curve_offset = 0
        if hasattr(self.child_node, "tree_node"):
            curve_offset = 50 * max(0, (self.child_node.tree_node.level - 1))
        else:
            curve_offset = 50

        control1 = QPointF(mid_x, start.y())
        control2 = QPointF(mid_x, end.y())

        # 如果节点在同一侧，添加偏移避免重叠
        if abs(start.x() - end.x()) < 100:
            control1.setX(control1.x() + curve_offset)
            control2.setX(control2.x() + curve_offset)

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        # 根据层级设置不同颜色
        level = 1
        if hasattr(self.child_node, "tree_node"):
            level = max(1, self.child_node.tree_node.level)

        level_colors = [
            QColor(70, 130, 180),  # 第1级
            QColor(65, 105, 225),  # 第2级
            QColor(135, 206, 250),  # 第3级
            QColor(173, 216, 230)  # 第4级
        ]

        color_index = min(level - 1, len(level_colors) - 1)
        pen_color = level_colors[color_index]

        pen = QPen(pen_color, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        self.draw_arrow(painter)

    def draw_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 10
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            painter.setBrush(QBrush(QColor(65, 105, 225)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(arrow_path)


class GradientConnection(ProfessionalConnection):
    """渐变连线"""
    def __init__(self, parent_node, child_node):
        super().__init__(parent_node, child_node)

    def update_path(self):
        start, end = self.get_connection_points()

        self.path = QPainterPath()
        self.path.moveTo(start)

        # 创建平滑的贝塞尔曲线
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        control1 = QPointF(start.x() + dx * 0.5, start.y())
        control2 = QPointF(end.x() - dx * 0.5, end.y())

        self.path.cubicTo(control1, control2, end)

    def draw(self, painter: QPainter):
        start, end = self.get_connection_points()

        # 创建渐变画笔
        gradient = QLinearGradient(start, end)
        gradient.setColorAt(0, QColor(255, 105, 97))  # 珊瑚红
        gradient.setColorAt(0.5, QColor(255, 180, 128))  # 浅橙色
        gradient.setColorAt(1, QColor(119, 221, 119))  # 浅绿色

        pen = QPen(QBrush(gradient), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path)
        self.draw_gradient_arrow(painter)

    def draw_gradient_arrow(self, painter: QPainter):
        start, end = self.get_connection_points()
        direction = end - start
        if direction.manhattanLength() > 0:
            arrow_size = 14
            angle = math.atan2(direction.y(), direction.x())

            arrow_p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            arrow_p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )

            arrow_path = QPainterPath()
            arrow_path.moveTo(end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.closeSubpath()

            # 箭头渐变
            arrow_gradient = QRadialGradient(end, arrow_size)
            arrow_gradient.setColorAt(0, QColor(119, 221, 119))
            arrow_gradient.setColorAt(1, QColor(255, 105, 97))

            painter.setBrush(QBrush(arrow_gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
            painter.drawPath(arrow_path)
```

---

# 文件路径: madmap\layout.py
```python
"""布局算法"""


class LayoutEngine:
    @staticmethod
    def mind_map(root, h_spacing=200, v_spacing=100):
        """左右树形布局"""

        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            child_y = y_offset - v_spacing * (len(node.children) - 1) / 2
            for c in node.children:
                layout(c, depth + 1, child_y, direction)
                child_y += v_spacing

        # 根节点在中间，左右分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        root.x = 0
        root.y = 0

        # 布局左侧子节点
        left_y = -v_spacing * (len(left_children) - 1) / 2
        for c in left_children:
            layout(c, 1, left_y, -1)  # 向左
            left_y += v_spacing

        # 布局右侧子节点
        right_y = -v_spacing * (len(right_children) - 1) / 2
        for c in right_children:
            layout(c, 1, right_y, 1)  # 向右
            right_y += v_spacing

    @staticmethod
    def logical(root, h_spacing=200, v_spacing=120):
        """自上而下逻辑结构布局"""

        def layout(node, depth=0, x_offset=0):
            node.x = x_offset
            node.y = depth * v_spacing
            if node.children:
                child_x = x_offset - (len(node.children) - 1) * h_spacing / 2
                for c in node.children:
                    layout(c, depth + 1, child_x)
                    child_x += h_spacing

        layout(root)

    @staticmethod
    def timeline(root, h_spacing=200):
        """时间轴布局，横向排列"""

        def layout(node, x_offset=0, y_offset=0):
            node.x = x_offset
            node.y = y_offset
            child_x = x_offset + h_spacing
            for i, c in enumerate(node.children):
                layout(c, child_x, y_offset + (i - len(node.children) // 2) * 100)
                child_x += h_spacing

        layout(root)

    @staticmethod
    def fishbone(root, h_spacing=200, v_spacing=100):
        """鱼骨图布局"""

        def layout(node, depth=0, y_offset=0, direction=1):
            node.x = depth * h_spacing * direction
            node.y = y_offset
            for i, c in enumerate(node.children):
                layout(c, depth + 1, y_offset + (i - len(node.children) // 2) * v_spacing, direction)

        # 左右对称分布
        left_children = [c for i, c in enumerate(root.children) if i % 2 == 0]
        right_children = [c for i, c in enumerate(root.children) if i % 2 == 1]

        for c in left_children:
            layout(c, 1, 0, -1)
        for c in right_children:
            layout(c, 1, 0, 1)

    @staticmethod
    def auto_arrange(root, h_spacing=200, v_spacing=120):
        """自动排列避免重叠"""

        def get_all_nodes(node):
            """获取所有节点"""
            nodes = [node]
            for child in node.children:
                nodes.extend(get_all_nodes(child))
            return nodes

        def check_overlap(node1, node2):
            """检查两个节点是否重叠"""
            return (abs(node1.x - node2.x) < h_spacing and
                    abs(node1.y - node2.y) < v_spacing)

        def adjust_position(node, all_nodes):
            """调整节点位置避免重叠"""
            for other_node in all_nodes:
                if node != other_node and check_overlap(node, other_node):
                    # 如果重叠，向右下方移动
                    node.x += h_spacing * 0.7
                    node.y += v_spacing * 0.7
                    # 递归检查是否还会与其他节点重叠
                    adjust_position(node, all_nodes)
                    break

        # 先应用基本布局
        LayoutEngine.mind_map(root, h_spacing, v_spacing)

        # 获取所有节点并检查重叠
        all_nodes = get_all_nodes(root)
        for node in all_nodes:
            adjust_position(node, all_nodes)
```

---

# 文件路径: madmap\main.py
```python
#!/usr/bin/env python3
"""
MindMap/Tree布局演示 - 专业版连线功能（重构版）
功能：
- 模块化代码结构
- 节点防重叠自动排列
- 键盘快捷键操作
- 双击编辑节点
- 空白处创建节点
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter
from window import ProfessionalMindMapWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = ProfessionalMindMapWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

# 文件路径: madmap\models.py
```python
"""数据模型定义"""
import json


class TreeNode:
    def __init__(self, title, x=0, y=0):
        self.id = id(self)
        self.title = title
        self.parent = None
        self.children = []
        self.x = x
        self.y = y
        self.level = 0  # 节点层级

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
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["title"], data.get("x", 0), data.get("y", 0))
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
```

---

# 文件路径: madmap\nodes.py
```python
"""可视化节点定义"""
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QInputDialog
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QLinearGradient
from models import TreeNode

class VisualNode(QGraphicsRectItem):
    WIDTH = 160
    HEIGHT = 90

    def __init__(self, tree_node: TreeNode):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # 根据层级设置不同样式
        self.setup_style()

        # 文本
        self.text_item = QGraphicsTextItem(self.tree_node.title, self)
        self.text_item.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.text_item.setDefaultTextColor(self.get_text_color())
        self.text_item.setTextWidth(self.WIDTH - 20)
        self.text_item.setPos(10, 10)

    def setup_style(self):
        """根据节点层级设置样式"""
        level_styles = [
            (QColor(74, 124, 89), QColor(173, 223, 173), 2.5),  # 根节点
            (QColor(49, 99, 149), QColor(173, 216, 230), 2.0),  # 第1级
            (QColor(149, 99, 49), QColor(255, 218, 185), 1.5),  # 第2级
            (QColor(99, 99, 99), QColor(240, 240, 240), 1.0)  # 其他级别
        ]

        level_index = min(self.tree_node.level, len(level_styles) - 1)
        border_color, fill_color, border_width = level_styles[level_index]

        # 设置渐变填充
        gradient = QLinearGradient(0, 0, 0, self.HEIGHT)
        gradient.setColorAt(0, fill_color.lighter(120))
        gradient.setColorAt(1, fill_color.darker(110))

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(border_color, border_width))
        self.setRect(0, 0, self.WIDTH, self.HEIGHT)

    def get_text_color(self):
        """根据背景色返回合适的文字颜色"""
        level_colors = [
            QColor(255, 255, 255),  # 根节点 - 白色文字
            QColor(0, 0, 0),  # 第1级 - 黑色文字
            QColor(0, 0, 0),  # 第2级 - 黑色文字
            QColor(80, 80, 80)  # 其他级别 - 深灰色
        ]
        return level_colors[min(self.tree_node.level, len(level_colors) - 1)]

    def itemChange(self, change, value):
        # 当节点位置改变时，同步 TreeNode 的 x,y 并让场景更新连线
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x() + self.WIDTH / 2, self.pos().y() + self.HEIGHT / 2)

    def mouseDoubleClickEvent(self, event):
        """双击编辑节点标题"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.edit_title()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def edit_title(self):
        """编辑节点标题"""
        new_title, ok = QInputDialog.getText(
            None,
            "编辑节点标题",
            "请输入新标题:",
            text=self.tree_node.title
        )
        if ok and new_title:
            self.tree_node.title = new_title
            self.text_item.setPlainText(new_title)
            if self.scene():
                self.scene().update()

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 回车键 - 添加子节点
            self.add_child_node()
            event.accept()
        elif event.key() == Qt.Key.Key_Tab:
            # Tab键 - 添加同级节点
            self.add_sibling_node()
            event.accept()
        else:
            super().keyPressEvent(event)

    def add_child_node(self):
        """添加子节点"""
        child_node = TreeNode("新子节点")
        self.tree_node.add_child(child_node)

        # 计算新节点位置（避免重叠）
        new_x = self.tree_node.x + 200
        new_y = self.tree_node.y + len(self.tree_node.children) * 120

        child_node.x = new_x
        child_node.y = new_y

        # 添加到场景
        if self.scene():
            visual_child = VisualNode(child_node)
            self.scene().add_visual_node(visual_child)
            self.scene().update()

            # 设置新节点为选中状态
            self.scene().clearSelection()
            visual_child.setSelected(True)
            visual_child.setFocus()

    def add_sibling_node(self):
        """添加同级节点"""
        if self.tree_node.parent:
            sibling_node = TreeNode("新同级节点")
            self.tree_node.parent.add_child(sibling_node)

            # 计算新节点位置
            siblings = self.tree_node.parent.children
            index = siblings.index(self.tree_node)

            # 放在当前节点右侧
            sibling_node.x = self.tree_node.x + 200
            sibling_node.y = self.tree_node.y

            # 添加到场景
            if self.scene():
                visual_sibling = VisualNode(sibling_node)
                self.scene().add_visual_node(visual_sibling)
                self.scene().update()

                # 设置新节点为选中状态
                self.scene().clearSelection()
                visual_sibling.setSelected(True)
                visual_sibling.setFocus()
        else:
            # 如果是根节点，不能添加同级节点
            print("根节点不能添加同级节点")
```

---

# 文件路径: madmap\scene.py
```python
"""图形场景定义"""
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPainter
from connections import ConnectionManager
from nodes import VisualNode
from models import TreeNode

class ProfessionalMindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__(-2000, -2000, 4000, 4000)
        self.visual_nodes = []
        self.connection_manager = ConnectionManager()
        self.connection_style = "bezier"  # 默认连线样式

    def add_visual_node(self, visual_node: VisualNode):
        self.addItem(visual_node)
        self.visual_nodes.append(visual_node)

    def set_connection_style(self, style):
        """设置连线样式"""
        self.connection_style = style
        self.update()

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """绘制专业连线"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        connections = []
        for vn in self.visual_nodes:
            node = vn.tree_node
            for child in node.children:
                child_vn = next((v for v in self.visual_nodes if v.tree_node == child), None)
                if child_vn:
                    connection = self.connection_manager.create_connection(vn, child_vn, self.connection_style)
                    connection.update_path()
                    connections.append(connection)

        # 绘制所有连线
        for connection in connections:
            connection.draw(painter)

    def mouseDoubleClickEvent(self, event):
        """空白处双击创建新节点"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取点击位置
            scene_pos = event.scenePos()

            # 创建新节点
            new_node = TreeNode("新节点", scene_pos.x(), scene_pos.y())

            # 添加到场景
            visual_node = VisualNode(new_node)
            self.add_visual_node(visual_node)

            # 如果没有根节点，设置为根节点
            if not any(vn.tree_node.level == 0 for vn in self.visual_nodes):
                new_node.level = 0

            self.update()

            # 设置新节点为选中状态
            self.clearSelection()
            visual_node.setSelected(True)
            visual_node.setFocus()

            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
```

---

# 文件路径: madmap\visual.py
```python
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QPointF

class VisualNode(QGraphicsRectItem):
    WIDTH = 160
    HEIGHT = 90

    def __init__(self, tree_node):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.tree_node = tree_node
        self.setPos(tree_node.x, tree_node.y)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.text_item = QGraphicsTextItem(tree_node.title, self)
        self.text_item.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.text_item.setTextWidth(self.WIDTH - 20)
        self.text_item.setPos(10, 10)
        self.update_style()

    def update_style(self):
        """根据层级设置样式"""
        color_map = [QColor(74,124,89), QColor(49,99,149), QColor(149,99,49), QColor(99,99,99)]
        fill = color_map[min(self.tree_node.level, len(color_map)-1)]
        gradient = QBrush(fill)
        self.setBrush(gradient)
        self.setPen(QPen(QColor(0,0,0), 2))

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.tree_node.x = self.pos().x()
            self.tree_node.y = self.pos().y()
            if self.scene():
                self.scene().update_connections()
        return super().itemChange(change, value)

    def center_pos(self):
        return QPointF(self.pos().x()+self.WIDTH/2, self.pos().y()+self.HEIGHT/2)

```

---

# 文件路径: madmap\window.py
```python
"""主窗口定义"""
import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsView, QFileDialog, QComboBox, QLabel
)
from PyQt6.QtGui import QPainter
from scene import ProfessionalMindMapScene
from layout import LayoutEngine
from nodes import VisualNode
from models import TreeNode

class ProfessionalMindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("专业思维导图 - 高级连线演示")
        self.resize(1400, 900)
        self.root_node = None
        self.scene = ProfessionalMindMapScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 专业控制面板
        control = QHBoxLayout()

        # 布局选择
        control.addWidget(QLabel("布局算法:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["mind_map", "logical", "timeline", "fishbone", "auto_arrange"])
        control.addWidget(self.layout_combo)

        # 连线样式选择
        control.addWidget(QLabel("连线样式:"))
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["bezier", "smart", "gradient"])
        self.connection_combo.currentTextChanged.connect(self.change_connection_style)
        control.addWidget(self.connection_combo)

        # 功能按钮
        layout_btn = QPushButton("应用布局")
        layout_btn.clicked.connect(self.apply_layout)
        control.addWidget(layout_btn)

        add_btn = QPushButton("生成示例树")
        add_btn.clicked.connect(self.create_sample_tree)
        control.addWidget(add_btn)

        save_btn = QPushButton("保存 JSON")
        save_btn.clicked.connect(self.save_json)
        control.addWidget(save_btn)

        load_btn = QPushButton("加载 JSON")
        load_btn.clicked.connect(self.load_json)
        control.addWidget(load_btn)

        clear_btn = QPushButton("清空画布")
        clear_btn.clicked.connect(self.clear_canvas)
        control.addWidget(clear_btn)

        # 添加键盘快捷键说明
        help_label = QLabel("快捷键: Enter-添加子节点 | Tab-添加同级节点 | 双击-编辑标题")
        control.addWidget(help_label)

        layout.addLayout(control)
        layout.addWidget(self.view)

        # 设置视图属性
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setFocus()

    def change_connection_style(self, style):
        """切换连线样式"""
        self.scene.set_connection_style(style)
        self.scene.update()

    def apply_layout(self):
        """应用布局算法"""
        if not self.root_node:
            return
        layout_name = self.layout_combo.currentText()
        engine = LayoutEngine
        func = getattr(engine, layout_name, None)
        if func:
            func(self.root_node)
            self.refresh_scene()

    def create_sample_tree(self):
        """创建专业示例树"""
        self.root_node = TreeNode("核心主题")
        self.root_node.level = 0

        # 第一级节点
        topics = ["战略规划", "产品设计", "技术架构", "市场营销", "运营管理"]
        for i, topic in enumerate(topics):
            child = TreeNode(topic)
            self.root_node.add_child(child)

            # 第二级节点
            sub_topics = []
            if topic == "战略规划":
                sub_topics = ["市场分析", "竞争策略", "目标设定", "资源分配"]
            elif topic == "产品设计":
                sub_topics = ["用户研究", "功能规划", "原型设计", "用户体验"]
            elif topic == "技术架构":
                sub_topics = ["前端技术", "后端服务", "数据库设计", "部署方案"]
            elif topic == "市场营销":
                sub_topics = ["品牌建设", "渠道策略", "内容营销", "数据分析"]
            else:
                sub_topics = ["流程优化", "团队管理", "绩效评估", "风险控制"]

            for sub_topic in sub_topics:
                sub_child = TreeNode(sub_topic)
                child.add_child(sub_child)

                # 第三级节点（部分节点）
                if sub_topic in ["用户研究", "功能规划", "前端技术", "后端服务"]:
                    details = ["需求收集", "方案评估", "实施计划", "验收标准"]
                    for detail in details[:2]:
                        detail_node = TreeNode(detail)
                        sub_child.add_child(detail_node)

        self.apply_layout()
        self.refresh_scene()

    def refresh_scene(self):
        """刷新场景"""
        self.scene.clear()
        self.scene.visual_nodes.clear()

        def add_visual(node):
            vn = VisualNode(node)
            self.scene.add_visual_node(vn)
            for c in node.children:
                add_visual(c)

        if self.root_node:
            add_visual(self.root_node)
            self.scene.update()

    def save_json(self):
        """保存为JSON文件"""
        if not self.root_node:
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.root_node.to_dict(), f, ensure_ascii=False, indent=2)

    def load_json(self):
        """从JSON文件加载"""
        path, _ = QFileDialog.getOpenFileName(self, "加载 JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.root_node = TreeNode.from_dict(data)
            self.calculate_levels(self.root_node)
            self.apply_layout()
            self.refresh_scene()

    def calculate_levels(self, node, level=0):
        """计算节点层级"""
        node.level = level
        for child in node.children:
            self.calculate_levels(child, level + 1)

    def clear_canvas(self):
        """清空画布"""
        self.root_node = None
        self.scene.clear()
        self.scene.visual_nodes.clear()
```

---

