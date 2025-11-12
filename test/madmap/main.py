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