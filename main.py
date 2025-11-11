# 文件路径: main.py
"""AI阅读卡片思维导图工具 - 程序入口"""

import sys
import os

# 将当前目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
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