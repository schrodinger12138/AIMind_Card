# PyQt6-WebEngine 安装指南

## 问题说明
如果遇到 "DLL load failed while importing QtWebEngineWidgets: 找不到指定的程序" 错误，通常是因为：
1. PyQt6-WebEngine 安装不完整
2. 缺少必要的系统依赖（Visual C++ Redistributable）
3. PyQt6 和 PyQt6-WebEngine 版本不匹配

## 推荐安装方法（Conda环境）

### 方法1：使用 conda-forge（推荐）
```bash
# 激活conda环境
conda activate ai_cards

# 卸载可能存在的旧版本
pip uninstall PyQt6-WebEngine -y
conda remove pyqtwebengine -y

# 使用conda安装（会自动处理依赖）
conda install -c conda-forge pyqtwebengine -y

# 验证安装
python check_webengine.py
```

### 方法2：使用 pip（如果conda方法失败）
```bash
# 激活conda环境
conda activate ai_cards

# 卸载旧版本
pip uninstall PyQt6-WebEngine PyQt6 -y

# 重新安装PyQt6和PyQt6-WebEngine
pip install PyQt6>=6.0.0
pip install PyQt6-WebEngine>=6.0.0

# 验证安装
python check_webengine.py
```

### 方法3：完整重新安装（如果以上方法都失败）
```bash
# 激活conda环境
conda activate ai_cards

# 完全卸载
pip uninstall PyQt6-WebEngine PyQt6 -y
conda remove pyqtwebengine pyqt -y

# 使用conda安装完整套件
conda install -c conda-forge pyqt pyqtwebengine -y

# 验证安装
python check_webengine.py
```

## 系统依赖（Windows）

如果仍然失败，可能需要安装 Visual C++ Redistributable：
- 下载并安装：https://aka.ms/vs/17/release/vc_redist.x64.exe
- 或者从 Microsoft 官网下载最新版本

## 验证安装

运行诊断脚本：
```bash
conda activate ai_cards
python check_webengine.py
```

如果显示 `[OK] 所有检查通过！`，说明安装成功。

## 常见问题

### Q: 为什么使用conda而不是pip？
A: conda会自动处理系统级依赖，特别是Windows上的DLL依赖，通常更可靠。

### Q: 安装后仍然报错怎么办？
A: 
1. 确认使用的是conda环境中的Python：`where python` 应该指向conda环境
2. 重启终端和应用程序
3. 检查PyQt6和PyQt6-WebEngine版本是否匹配：`pip list | findstr PyQt6`

### Q: 可以同时使用pip和conda安装吗？
A: 不推荐。建议只使用一种方式，优先使用conda。

