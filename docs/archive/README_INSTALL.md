# 安装说明

## 快速安装（推荐）

### Windows用户
双击运行 `install_requirements.bat`，脚本会自动：
1. 激活或创建conda环境 `ai_cards`
2. 使用conda安装PyQt6和PyQt6-WebEngine（避免DLL问题）
3. 安装其他Python依赖

### Linux/Mac用户
```bash
chmod +x install_requirements.sh
./install_requirements.sh
```

## 手动安装

### 1. 创建conda环境（如果还没有）
```bash
conda create -n ai_cards python=3.10 -y
conda activate ai_cards
```

### 2. 安装PyQt6和PyQt6-WebEngine（重要！）

**推荐方式（使用conda，避免Windows DLL问题）：**
```bash
conda install -c conda-forge pyqt pyqtwebengine -y
```

**备选方式（使用pip）：**
```bash
pip install PyQt6>=6.0.0 PyQt6-WebEngine>=6.0.0
```

### 3. 安装其他依赖
```bash
pip install -r requirements.txt
```

### 4. 验证安装
```bash
python check_webengine.py
```

## 使用environment.yml（推荐用于新环境）

```bash
conda env create -f environment.yml
conda activate ai_cards
```

## 常见问题

### Q: Windows上出现"DLL load failed"错误？
A: 使用conda安装PyQt6-WebEngine而不是pip：
```bash
conda install -c conda-forge pyqtwebengine -y
```

### Q: 如何确认安装成功？
A: 运行 `python check_webengine.py`，应该看到所有检查项都显示 `[OK]`

### Q: 可以更新依赖吗？
A: 可以，但建议先备份环境：
```bash
conda update -c conda-forge pyqt pyqtwebengine
pip install --upgrade -r requirements.txt
```

## 依赖列表

### 核心依赖
- **PyQt6** >= 6.0.0 - GUI框架
- **PyQt6-WebEngine** >= 6.0.0 - Web引擎（用于Markdown预览）

### AI相关
- **openai** >= 1.0.0 - OpenAI API客户端

### 文件处理
- **PyMuPDF** >= 1.23.0 - PDF处理
- **Pillow** >= 10.0.0 - 图像处理

### Markdown相关
- **markdown** >= 3.4.0 - Markdown解析
- **Pygments** >= 2.15.0 - 代码高亮

### 工具库
- **pyperclip** >= 1.8.0 - 剪贴板操作
- **requests** >= 2.31.0 - HTTP请求
- **tqdm** >= 4.66.0 - 进度条
- **matplotlib** >= 3.7.0 - 图表绘制
- **weasyprint** >= 60.0 - PDF导出
- **jinja2** >= 3.1.0 - 模板引擎

