# 文件路径: main.py
# -*- coding: utf-8 -*-
"""AI阅读卡片思维导图工具 - 程序入口"""

import sys
import os

# 设置输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 将当前目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 显示环境信息
conda_env = os.environ.get('CONDA_DEFAULT_ENV', '未检测到')
venv_path = os.environ.get('VIRTUAL_ENV', '未检测到')
print(f"当前conda环境: {conda_env}")
print(f"虚拟环境: {venv_path}")
print(f"Python路径: {sys.executable}")

from PyQt6.QtWidgets import QApplication

# 尝试导入Qt WebEngine（用于诊断）
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print("[OK] PyQt6-WebEngine 导入成功")
except ImportError as e:
    print(f"[FAIL] PyQt6-WebEngine 导入失败: {e}")
    print("提示: 请确保在正确的环境中运行程序")
    print("  1. 使用虚拟环境: 运行 setup_venv.bat 创建环境，然后使用 run_with_venv.bat")
    print("  2. 使用conda环境: conda activate ai_cards")
    print("  3. 如果DLL错误，可能需要安装 Visual C++ Redistributable")

from ai_reader_cards.ui_main import MainWindow


def main():
    """程序入口函数"""
    # 创建Qt应用
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("AI阅读卡片思维导图工具")
    app.setOrganizationName("AI Reading Cards")
    app.setApplicationVersion("1.0.0")

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()