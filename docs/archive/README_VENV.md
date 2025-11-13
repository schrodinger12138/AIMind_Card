# 虚拟环境使用指南

## 快速开始

### Windows用户

1. **创建虚拟环境并安装依赖**
   ```bash
   setup_venv.bat
   ```
   这个脚本会：
   - 在当前目录创建 `venv` 虚拟环境
   - 安装所有依赖包
   - 验证安装

2. **运行程序**
   ```bash
   run_with_venv.bat
   ```
   或者手动激活：
   ```bash
   venv\Scripts\activate.bat
   python main.py
   ```

### Linux/Mac用户

1. **创建虚拟环境并安装依赖**
   ```bash
   chmod +x setup_venv.sh
   ./setup_venv.sh
   ```

2. **运行程序**
   ```bash
   source venv/bin/activate
   python main.py
   ```

## 手动操作

### 创建虚拟环境
```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### 激活虚拟环境
```bash
# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 退出虚拟环境
```bash
deactivate
```

## 注意事项

1. **PyQt6-WebEngine DLL问题**
   - 如果遇到 "DLL load failed" 错误，可能需要安装 Visual C++ Redistributable
   - 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 或者尝试使用conda环境（conda会自动处理依赖）

2. **虚拟环境位置**
   - 虚拟环境创建在当前目录的 `venv` 文件夹中
   - 不要将 `venv` 文件夹提交到版本控制系统（已在.gitignore中）

3. **更新依赖**
   ```bash
   # 激活虚拟环境后
   pip install --upgrade -r requirements.txt
   ```

## 故障排除

### 问题：虚拟环境创建失败
- 确保Python版本 >= 3.8
- 检查是否有足够的磁盘空间
- 确保有写入权限

### 问题：pip安装失败
- 检查网络连接
- 尝试使用国内镜像源：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 问题：PyQt6-WebEngine导入失败
- 尝试重新安装：
  ```bash
  pip uninstall PyQt6-WebEngine -y
  pip install PyQt6-WebEngine
  ```
- 如果仍然失败，考虑使用conda环境

