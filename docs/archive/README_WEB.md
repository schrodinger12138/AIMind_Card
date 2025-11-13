# Web版使用说明

## 功能特性

✅ **PDF阅读器**：使用浏览器原生PDF查看器
✅ **思维导图**：右侧面板，使用vis.js渲染
✅ **文本选择**：在PDF中选中文本，点击"创建卡片"生成AI卡片
✅ **双向跳转**：
   - 点击思维导图中的卡片 → 跳转到PDF对应位置
   - 点击PDF中的标记 → 跳转到思维导图中的卡片
✅ **全文翻译**：将PDF全文翻译为中文
✅ **PDF转Markdown**：将PDF转换为Markdown格式
✅ **Markdown模式**：切换到Markdown编辑器，支持实时预览和LaTeX公式

## 安装依赖

```bash
# 激活虚拟环境
venv\Scripts\activate.bat  # Windows
# 或
source venv/bin/activate   # Linux/Mac

# 安装Web依赖
pip install flask flask-cors
```

## 启动Web应用

```bash
python web_app.py
```

然后在浏览器中访问：`http://localhost:5000`

## 使用流程

1. **连接AI**：点击"连接AI"按钮，选择模型
2. **上传PDF**：点击"上传PDF"按钮，选择要阅读的PDF文件
3. **创建卡片**：
   - 在PDF中选中文本
   - 点击弹出的"创建卡片"按钮
   - AI会自动生成问题-答案卡片
4. **查看思维导图**：右侧面板显示所有卡片的关系
5. **跳转**：
   - 点击思维导图中的节点 → 跳转到PDF位置
   - 点击PDF中的黄色标记 → 跳转到对应卡片
6. **翻译/转换**：
   - 点击"全文翻译" → 将PDF翻译为中文Markdown
   - 点击"PDF转Markdown" → 转换为Markdown格式
7. **切换模式**：点击"切换到Markdown"查看/编辑Markdown内容

## 目录结构

```
web/
├── templates/          # HTML模板
│   └── index.html
├── static/            # 静态资源
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
uploads/               # 上传的PDF文件存储目录
web_app.py             # Flask应用入口
```

## 技术栈

- **后端**：Flask + Python
- **前端**：HTML + CSS + JavaScript
- **思维导图**：vis.js
- **PDF查看**：浏览器原生PDF查看器
- **Markdown渲染**：MathJax（LaTeX公式支持）

## 注意事项

1. 首次使用需要连接AI（需要配置API密钥）
2. PDF文件会保存在`uploads/`目录
3. 思维导图数据保存在内存中，刷新页面会丢失（后续可添加持久化）
4. PDF文本选择功能依赖于浏览器PDF查看器的支持

## 开发计划

- [ ] 添加卡片持久化存储
- [ ] 优化PDF文本选择精度
- [ ] 添加更多思维导图布局选项
- [ ] 支持导出思维导图为图片
- [ ] 添加用户认证和会话管理

