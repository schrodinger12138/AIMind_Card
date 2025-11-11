# 文件路径: ai_reader_cards\ui_components\__init__.py (更新版本)
"""UI组件包"""

from .menu_bar import MenuBar
from .main_toolbar import MainToolbar
from .control_panel import ControlPanel  # 保留，但可能不再使用
from .input_panel import InputPanel
from .mindmap_panel import MindMapPanel
from .drawing_toolbar import DrawingToolbar
from .search_toolbar import SearchToolbar
from .alignment_toolbar import AlignmentToolbar

# 管理器
from .main_controller import MainController
from .card_manager import CardManager
from .search_manager import SearchManager
from .alignment_manager import AlignmentManager

__all__ = [
    'MenuBar',
    'MainToolbar',
    'ControlPanel',
    'InputPanel',
    'MindMapPanel',
    'DrawingToolbar',
    'SearchToolbar',
    'AlignmentToolbar',
    'MainController',
    'CardManager',
    'SearchManager',
    'AlignmentManager'
]