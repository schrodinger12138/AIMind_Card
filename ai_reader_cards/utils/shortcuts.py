"""快捷键模块 - 处理剪贴板和快捷键"""

import pyperclip
from PyQt6.QtCore import QTimer


class ClipboardMonitor:
    """剪贴板监控器"""
    
    def __init__(self, callback, interval=500):
        """初始化剪贴板监控器
        
        Args:
            callback: 检测到新内容时的回调函数
            interval: 检测间隔（毫秒）
        """
        self.callback = callback
        self.last_content = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_clipboard)
        self.timer.setInterval(interval)
        self.enabled = False
    
    def start(self):
        """开始监控剪贴板"""
        self.enabled = True
        try:
            self.last_content = pyperclip.paste()
        except:
            self.last_content = ""
        self.timer.start()
    
    def stop(self):
        """停止监控剪贴板"""
        self.enabled = False
        self.timer.stop()
    
    def _check_clipboard(self):
        """检查剪贴板内容"""
        if not self.enabled:
            return
        
        try:
            current_content = pyperclip.paste()
            
            # 如果内容发生变化且不为空
            if current_content and current_content != self.last_content:
                self.last_content = current_content
                # 触发回调
                if self.callback:
                    self.callback(current_content)
        except Exception as e:
            # 忽略剪贴板访问错误
            pass
    
    def get_clipboard_text(self):
        """获取当前剪贴板文本"""
        try:
            return pyperclip.paste()
        except:
            return ""
    
    def set_clipboard_text(self, text):
        """设置剪贴板文本"""
        try:
            pyperclip.copy(text)
        except:
            pass
