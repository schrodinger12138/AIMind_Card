# AI阅读卡片思维导图工具

一个强大的AI驱动的阅读辅助工具，支持PDF阅读、思维导图生成、Markdown编辑和LaTeX公式渲染。

## ✨ 功能特性

- 📄 **PDF阅读器**：支持PDF文件阅读和文本选择
- 🧠 **思维导图**：自动生成和布局思维导图
- 📝 **Markdown编辑器**：支持实时预览、LaTeX公式、代码高亮
- 🤖 **AI卡片生成**：从选中文本自动生成问题-答案卡片
- 🔗 **智能连线**：自动连接相关卡片
- 🎨 **多种布局**：支持思维导图、逻辑图、时间线等多种布局
- 📤 **导出功能**：支持导出为Markdown、XMind、Anki等格式

## 🚀 快速开始

### 安装

```bash
# 使用虚拟环境（推荐）
setup_venv.bat  # Windows
# 或
./setup_venv.sh  # Linux/Mac

# 启动应用
python main.py
```

### 使用

1. **连接AI**：在工具栏选择AI模型并点击"连接AI"
2. **打开文件**：通过菜单或拖拽打开PDF/Markdown文件
3. **创建卡片**：在阅读区域选中文本，点击"生成卡片"按钮
4. **管理思维导图**：使用工具栏切换布局，拖动卡片调整位置

## 🔬 LaTeX公式渲染

程序启动时会自动加载测试文档，包含各种LaTeX公式示例。

### 支持的公式格式

- **行内公式**：`$E=mc^2$`
- **块级公式**：`$$E=mc^2$$`
- **复杂公式**：支持矩阵、分数、积分、求和等

### 公式语法修正

如果公式无法渲染，检查语法是否正确：

- ❌ `\vec{\lambda}{\mathbf{k}}` → ✅ `\vec{\lambda}_{\mathbf{k}}`
- ❌ `\tau{z}` → ✅ `\tau_{z}`

## 📚 文档

详细文档请查看 `docs/` 目录：
- 安装指南
- 使用说明
- 问题排查
- LaTeX公式渲染说明

## ❓ 常见问题

### PyQt6-WebEngine导入失败？
参考 `docs/archive/INSTALL_WEBENGINE.md`

### LaTeX公式不显示？
参考 `docs/archive/LATEX_FORMULA_TROUBLESHOOTING.md`

### 如何离线使用？
参考 `docs/archive/setup_local_mathjax.md`

## 📝 开发

项目采用模块化设计：
- `ai_reader_cards/card/` - 卡片和思维导图
- `ai_reader_cards/markdown/` - Markdown处理和预览
- `ai_reader_cards/ui_components/` - UI组件

## 📄 许可证

MIT License

---

**提示**：程序启动时会自动加载测试内容，方便测试LaTeX公式渲染功能。
