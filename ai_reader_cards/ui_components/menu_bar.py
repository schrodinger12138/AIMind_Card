# 文件路径: ai_reader_cards\ui_components\menu_bar.py
"""主菜单栏组件"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence


class MenuBar(QMenuBar):
    """主菜单栏"""

    # 文件菜单信号
    new_requested = pyqtSignal()
    open_requested = pyqtSignal()
    save_requested = pyqtSignal()
    save_as_requested = pyqtSignal()
    export_markdown_requested = pyqtSignal()
    export_xmind_requested = pyqtSignal()
    export_anki_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    # 编辑菜单信号
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    cut_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    paste_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    select_all_requested = pyqtSignal()
    find_requested = pyqtSignal()

    # 视图菜单信号
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()
    zoom_reset_requested = pyqtSignal()
    toggle_toolbar_requested = pyqtSignal(str, bool)  # toolbar_name, visible

    # 工具菜单信号
    connect_ai_requested = pyqtSignal()
    toggle_clipboard_monitor_requested = pyqtSignal(bool)
    toggle_drawing_mode_requested = pyqtSignal(bool)
    toggle_connection_mode_requested = pyqtSignal(bool)

    # 排列菜单信号
    align_left_requested = pyqtSignal()
    align_right_requested = pyqtSignal()
    align_top_requested = pyqtSignal()
    align_bottom_requested = pyqtSignal()
    align_center_h_requested = pyqtSignal()
    align_center_v_requested = pyqtSignal()
    distribute_h_requested = pyqtSignal()
    distribute_v_requested = pyqtSignal()
    arrange_hierarchy_requested = pyqtSignal()

    # 设置菜单信号
    settings_requested = pyqtSignal()
    
    # 布局信号
    layout_requested = pyqtSignal(str)  # layout_name
    
    # 工具菜单信号
    connect_ai_requested = pyqtSignal()
    toggle_clipboard_monitor_requested = pyqtSignal(bool)
    toggle_connection_mode_requested = pyqtSignal(bool)
    
    # 帮助菜单信号
    about_requested = pyqtSignal()
    help_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_menus()

    def init_menus(self):
        """初始化所有菜单"""
        self.create_settings_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_help_menu()

    def create_settings_menu(self):
        """创建设置菜单"""
        settings_menu = self.addMenu("设置(&S)")
        
        # 设置对话框
        settings_action = QAction("设置(&S)...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.settings_requested.emit)
        settings_menu.addAction(settings_action)

    def create_edit_menu(self):
        """创建编辑菜单"""
        edit_menu = self.addMenu("编辑(&E)")

        # 撤销/重做
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo_requested.emit)
        edit_menu.addAction(undo_action)

        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo_requested.emit)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # 剪切/复制/粘贴
        cut_action = QAction("剪切(&T)", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_requested.emit)
        edit_menu.addAction(cut_action)

        copy_action = QAction("复制(&C)", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_requested.emit)
        edit_menu.addAction(copy_action)

        paste_action = QAction("粘贴(&P)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_requested.emit)
        edit_menu.addAction(paste_action)

        delete_action = QAction("删除(&D)", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.delete_requested.emit)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        # 全选/查找
        select_all_action = QAction("全选(&A)", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all_requested.emit)
        edit_menu.addAction(select_all_action)

        find_action = QAction("查找(&F)...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.find_requested.emit)
        edit_menu.addAction(find_action)

    def create_view_menu(self):
        """创建视图菜单 - 包含缩放和布局"""
        view_menu = self.addMenu("视图(&V)")

        # 缩放
        zoom_in_action = QAction("放大(&I)", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in_requested.emit)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("缩小(&O)", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out_requested.emit)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("重置缩放(&R)", self)
        zoom_reset_action.triggered.connect(self.zoom_reset_requested.emit)
        view_menu.addAction(zoom_reset_action)

        view_menu.addSeparator()

        # 布局子菜单
        layout_menu = view_menu.addMenu("布局(&L)")
        
        # 布局选项信号（需要添加）
        self.layout_mind_map_action = QAction("思维导图布局", self)
        self.layout_mind_map_action.triggered.connect(lambda: self.layout_requested.emit("mind_map"))
        layout_menu.addAction(self.layout_mind_map_action)
        
        self.layout_logical_action = QAction("逻辑结构布局", self)
        self.layout_logical_action.triggered.connect(lambda: self.layout_requested.emit("logical"))
        layout_menu.addAction(self.layout_logical_action)
        
        self.layout_timeline_action = QAction("时间轴布局", self)
        self.layout_timeline_action.triggered.connect(lambda: self.layout_requested.emit("timeline"))
        layout_menu.addAction(self.layout_timeline_action)
        
        self.layout_fishbone_action = QAction("鱼骨图布局", self)
        self.layout_fishbone_action.triggered.connect(lambda: self.layout_requested.emit("fishbone"))
        layout_menu.addAction(self.layout_fishbone_action)
        
        self.layout_auto_arrange_action = QAction("自动排列", self)
        self.layout_auto_arrange_action.triggered.connect(lambda: self.layout_requested.emit("auto_arrange"))
        layout_menu.addAction(self.layout_auto_arrange_action)

        view_menu.addSeparator()

        # 工具栏显示/隐藏
        self.toolbar_actions = {}
        toolbars = [
            ("main_toolbar", "主工具栏"),
            ("search_toolbar", "搜索工具栏"),
            ("alignment_toolbar", "对齐工具栏")
        ]

        for toolbar_id, toolbar_name in toolbars:
            action = QAction(f"显示{toolbar_name}", self)
            action.setCheckable(True)
            action.setChecked(False)  # 默认隐藏
            action.triggered.connect(
                lambda checked, tid=toolbar_id: self.toggle_toolbar_requested.emit(tid, checked)
            )
            view_menu.addAction(action)
            self.toolbar_actions[toolbar_id] = action

    def create_tools_menu(self):
        """创建工具菜单"""
        tools_menu = self.addMenu("工具(&T)")

        # AI相关
        connect_ai_action = QAction("连接AI服务...", self)
        connect_ai_action.triggered.connect(self.connect_ai_requested.emit)
        tools_menu.addAction(connect_ai_action)

        # 剪贴板监控
        self.clipboard_action = QAction("启用剪贴板监控", self)
        self.clipboard_action.setCheckable(True)
        self.clipboard_action.triggered.connect(
            lambda checked: self.toggle_clipboard_monitor_requested.emit(checked)
        )
        tools_menu.addAction(self.clipboard_action)

        tools_menu.addSeparator()

        # 连接模式
        self.connection_mode_action = QAction("连接模式", self)
        self.connection_mode_action.setCheckable(True)
        self.connection_mode_action.triggered.connect(
            lambda checked: self.toggle_connection_mode_requested.emit(checked)
        )
        tools_menu.addAction(self.connection_mode_action)

    def create_help_menu(self):
        """创建帮助菜单"""
        help_menu = self.addMenu("帮助(&H)")

        help_action = QAction("使用帮助(&H)", self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.triggered.connect(self.help_requested.emit)
        help_menu.addAction(help_action)

        about_action = QAction("关于(&A)...", self)
        about_action.triggered.connect(self.about_requested.emit)
        help_menu.addAction(about_action)

    def set_toolbar_visibility(self, toolbar_id, visible):
        """设置工具栏可见性"""
        if toolbar_id in self.toolbar_actions:
            self.toolbar_actions[toolbar_id].setChecked(visible)
    
    def set_clipboard_monitor_status(self, monitoring):
        """设置剪贴板监控状态"""
        if monitoring:
            self.clipboard_action.setText("剪贴板监控中...")
        else:
            self.clipboard_action.setText("启用剪贴板监控")
    
    def set_connection_mode_status(self, enabled):
        """设置连接模式状态"""
        self.connection_mode_action.setChecked(enabled)