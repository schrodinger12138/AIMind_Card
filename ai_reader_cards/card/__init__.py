"""Card相关功能模块"""
try:
    from .card import KnowledgeCard, CardEditDialog, ConnectionPoint
except ImportError:
    KnowledgeCard = None
    CardEditDialog = None
    ConnectionPoint = None

try:
    from .mindmap import MindMapScene, MindMapView
except ImportError:
    MindMapScene = None
    MindMapView = None

try:
    from .tree_models import TreeNode
except ImportError:
    TreeNode = None

try:
    from .layout_engine import LayoutEngine
except ImportError:
    LayoutEngine = None

try:
    from .enhanced_layout import EnhancedLayoutEngine
except ImportError:
    EnhancedLayoutEngine = None

try:
    from .fixed_connections import FixedLengthConnection, FixedConnectionManager
except ImportError:
    FixedLengthConnection = None
    FixedConnectionManager = None

try:
    from .professional_connections import (
        ConnectionManager, ProfessionalConnection,
        BezierConnection, SmartConnection, GradientConnection
    )
except ImportError:
    ConnectionManager = None
    ProfessionalConnection = None
    BezierConnection = None
    SmartConnection = None
    GradientConnection = None

try:
    from .undo_manager import UndoManager
except ImportError:
    UndoManager = None

__all__ = [
    'KnowledgeCard',
    'CardEditDialog',
    'ConnectionPoint',
    'MindMapScene',
    'MindMapView',
    'TreeNode',
    'LayoutEngine',
    'EnhancedLayoutEngine',
    'FixedLengthConnection',
    'FixedConnectionManager',
    'ConnectionManager',
    'ProfessionalConnection',
    'BezierConnection',
    'SmartConnection',
    'GradientConnection',
    'UndoManager',
]

