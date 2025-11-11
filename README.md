ai_reader_cards/
├── main.py                 # 程序入口
├── ui_main.py             # 主窗口容器（简化）
├── ui_components/         # UI组件模块
│   ├── __init__.py
│   ├── control_panel.py   # 控制面板
│   ├── input_panel.py     # 输入面板
│   ├── mindmap_panel.py   # 思维导图面板
│   └── drawing_toolbar.py # 绘画工具栏
├── workers.py             # 工作线程
├── ai_api.py
├── card.py
├── mindmap.py
├── pdf_viewer.py
└── utils/
    ├── storage.py
    ├── shortcuts.py
    └── file_utils.py
近期想法
1.增加卡片功能
2.优化UI布局
3.增强PDF阅读体验



AI阅读卡片思维导图工具 v1.0
一个基于PyQt6的桌面应用，集成AI问答、知识卡片化和思维导图可视化的智能学习助手。

🌟 核心功能
1. 🤖 AI智能卡片生成
自动调用OpenAI API将文本内容转换为结构化学习卡片
智能提取标题、问题、答案三部分
支持自定义AI模型（gpt-4o、gpt-4o-mini、gpt-3.5-turbo）
2. 🧠 交互式思维导图画布
可视化知识层级关系，卡片可自由拖动
自动绘制平滑贝塞尔曲线连线和箭头
支持父子节点建立和解除连接
网格背景和阴影效果提升视觉体验
3. ⚡ 高效操作方式
空格键（Space）：快速从输入框生成卡片
剪贴板监控：复制文本自动触发AI卡片生成
Ctrl+滚轮：画布缩放（0.1x ~ 5x）
中键拖动：平移视图
Ctrl+S：保存卡片数据
Ctrl+O：加载卡片数据
4. 💾 数据持久化
自动保存为JSON格式（含卡片位置、层级关系）
支持导出为Markdown格式
窗口关闭时自动保存当前状态
📁 项目结构
ai_reader_cards/
├── main.py                 # 程序入口
├── ai_api.py              # AI接口模块（OpenAI集成）
├── card.py                # 知识卡片类（可视化组件）
├── mindmap.py             # 思维导图场景和视图
├── ui_main.py             # 主窗口界面
└── utils/
    ├── storage.py         # 数据存储与导出
    └── shortcuts.py       # 剪贴板监控

🚀 快速开始
环境要求
Python 3.11+
PyQt6
OpenAI API密钥
安装依赖
pip install PyQt6 pyperclip openai

配置API密钥
设置环境变量：

export OPENAI_API_KEY="your-api-key-here"

或在应用启动后通过界面配置。

运行应用
python main.py

📖 使用指南
基础操作流程
启动应用 → 点击"🔌 连接AI"按钮
输入文本 → 在左侧文本框输入或粘贴内容
生成卡片 → 点击"✨ 生成卡片"或按空格键
拖动组织 → 在思维导图画布中拖动卡片
建立层级 → 选中两张卡片，点击"🔗 连接选中卡片"
保存导出 → 使用"💾 保存"或"📤 导出Markdown"
进阶技巧
剪贴板监控模式
启用"📋 启用剪贴板监控"
在任何应用中复制文本（Ctrl+C）
自动生成卡片到画布
画布操作
缩放：按住Ctrl键，滚动鼠标滚轮
平移：按住鼠标中键拖动
选择卡片：单击卡片
多选：按住Ctrl点击多张卡片
连接管理
创建连接：选中两张卡片 → 点击"🔗 连接选中卡片"
删除连接：选中子卡片 → 点击"❌ 取消连接"
连线显示：自动绘制贝塞尔曲线从父卡片底部到子卡片顶部
🎨 卡片设计
每张卡片包含三部分：

标题栏（蓝色背景）：显示卡片标题，选中时变为橙色
问题区（蓝色文字）：考察核心概念的问题
答案区（黑色文字）：简洁的答案内容
💾 数据格式
JSON格式（保存/加载）
{
  "version": "1.0",
  "created_at": "2025-01-01T12:00:00",
  "cards": [
    {
      "id": 1,
      "title": "卡片标题",
      "question": "问题内容",
      "answer": "答案内容",
      "x": 100,
      "y": 200,
      "parent_id": null
    }
  ]
}

Markdown格式（导出）
## 1. 卡片标题
**问题：** 问题内容
**答案：** 答案内容
---

🔧 技术栈
GUI框架：PyQt6
AI服务：OpenAI API
数据存储：JSON
剪贴板：pyperclip
📝 开发说明
LSP诊断
部分PyQt6类型提示问题属于已知的假阳性，不影响运行：

card.py：QPainter方法类型提示
mindmap.py：QGraphicsScene/View事件类型提示
这些是PyQt6类型存根的局限性，实际运行完全正常。

扩展开发
项目采用模块化设计，便于扩展：

添加新AI模型：修改ai_api.py
自定义卡片样式：修改card.py中的绘制方法
新增导出格式：扩展utils/storage.py
🔮 未来计划
 支持PDF/DOCX文件导入
 语义搜索功能
 多主题界面（夜间模式）
 卡片分组与标签系统
 AI自动关联建议
 导出为FreeMind格式
 云端同步功能
 浏览器插件集成
📄 许可证
本项目为开源学习项目，仅供教育和研究使用。

🙏 致谢
OpenAI - 提供强大的语言模型
Qt Project - 优秀的跨平台GUI框架
Python社区 - 丰富的生态系统
版本：1.0.0
最后更新：2025年11月

如有问题或建议，欢迎提交Is