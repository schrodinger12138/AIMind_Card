"""
节点图标支持 - 内置图标库
参考 Simple Mind Map 的图标系统
"""

from PyQt6.QtCore import QSize, Qt, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QGraphicsPixmapItem


class IconManager:
    """图标管理器"""
    
    # 内置图标库（使用 Unicode 符号）
    ICON_LIBRARIES = {
        'business': {
            'briefcase': '💼',
            'chart': '📊',
            'money': '💰',
            'target': '🎯',
            'trophy': '🏆',
            'lightbulb': '💡',
        },
        'education': {
            'book': '📚',
            'graduation': '🎓',
            'school': '🏫',
            'pencil': '✏️',
            'notebook': '📓',
            'microscope': '🔬',
        },
        'tools': {
            'wrench': '🔧',
            'hammer': '🔨',
            'screwdriver': '🪛',
            'gear': '⚙️',
            'toolbox': '🧰',
        },
        'communication': {
            'phone': '📞',
            'email': '📧',
            'message': '💬',
            'chat': '💭',
            'megaphone': '📢',
        },
        'time': {
            'clock': '🕐',
            'calendar': '📅',
            'alarm': '⏰',
            'stopwatch': '⏱️',
        },
        'status': {
            'check': '✅',
            'cross': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'star': '⭐',
            'heart': '❤️',
        },
        'location': {
            'pin': '📍',
            'map': '🗺️',
            'globe': '🌍',
            'building': '🏢',
        },
        'food': {
            'apple': '🍎',
            'coffee': '☕',
            'pizza': '🍕',
            'cake': '🎂',
        },
        'travel': {
            'car': '🚗',
            'plane': '✈️',
            'train': '🚂',
            'ship': '🚢',
        },
        'medical': {
            'hospital': '🏥',
            'pill': '💊',
            'heartbeat': '💓',
            'stethoscope': '🩺',
        },
    }
    
    @classmethod
    def get_icon(cls, category, name):
        """获取图标（返回 Unicode 字符）"""
        if category in cls.ICON_LIBRARIES:
            if name in cls.ICON_LIBRARIES[category]:
                return cls.ICON_LIBRARIES[category][name]
        return None
    
    @classmethod
    def get_all_categories(cls):
        """获取所有图标分类"""
        return list(cls.ICON_LIBRARIES.keys())
    
    @classmethod
    def get_icons_in_category(cls, category):
        """获取指定分类下的所有图标"""
        if category in cls.ICON_LIBRARIES:
            return cls.ICON_LIBRARIES[category]
        return {}
    
    @classmethod
    def create_icon_pixmap(cls, icon_char, size=24, color=None):
        """创建图标像素图"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置字体
        font = QFont("Segoe UI Emoji", size - 4)
        painter.setFont(font)
        
        # 设置颜色（如果指定）
        if color:
            painter.setPen(QPen(color))
        else:
            painter.setPen(QPen(QColor(0, 0, 0)))
        
        # 绘制图标
        painter.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, icon_char)
        painter.end()
        
        return pixmap

