# 代码重构说明

## 重构目标
将Markdown相关功能和Card相关功能分别组织到独立的文件夹中，提高代码的可维护性和可读性。

## 新的目录结构

### `markdown/` 文件夹
包含所有Markdown相关的功能模块：

- **`markdown_viewer.py`** - Markdown查看器（基于QTextEdit，支持Obsidian风格）
- **`markdown_preview.py`** - Markdown预览组件（基于QWebEngineView，支持MathJax）
- **`markdown_translator.py`** - Markdown翻译器
- **`pdf_to_md.py`** - PDF转Markdown转换器
- **`pdf_viewer.py`** - PDF查看器
- **`__init__.py`** - 模块导出

### `card/` 文件夹
包含所有Card相关的功能模块：

- **`card.py`** - 知识卡片类（KnowledgeCard）
- **`mindmap.py`** - 思维导图场景和视图（MindMapScene, MindMapView）
- **`tree_models.py`** - 树形数据模型（TreeNode）
- **`layout_engine.py`** - 布局算法引擎（LayoutEngine）
- **`enhanced_layout.py`** - 增强布局引擎（防重叠等）
- **`fixed_connections.py`** - 固定长度连线系统
- **`professional_connections.py`** - 专业连线管理器
- **`undo_manager.py`** - 撤销/重做管理器
- **`__init__.py`** - 模块导出

## 导入方式

### 使用Markdown功能
```python
from ai_reader_cards.markdown import MarkdownViewer, MarkdownPreview, MarkdownTranslator
from ai_reader_cards.markdown import PDFToMarkdownConverter, PDFViewer
```

### 使用Card功能
```python
from ai_reader_cards.card import KnowledgeCard, MindMapScene, MindMapView
from ai_reader_cards.card import LayoutEngine, TreeNode, UndoManager
from ai_reader_cards.card import FixedConnectionManager, ConnectionManager
```

## 已更新的文件

以下文件的导入路径已更新：
- `ui_components/input_panel.py`
- `ui_components/mindmap_panel.py`
- `ui_components/main_controller.py`
- `ui_main.py`
- `card/mindmap.py`（内部相对导入）
- `card/card.py`（内部相对导入）
- `card/enhanced_layout.py`（内部相对导入）

## 注意事项

1. **相对导入**：`card/` 和 `markdown/` 文件夹内的模块使用相对导入（`from .module import ...`）
2. **外部导入**：其他模块使用绝对导入（`from ai_reader_cards.markdown import ...`）
3. **向后兼容**：通过 `__init__.py` 导出，保持原有的导入方式兼容


