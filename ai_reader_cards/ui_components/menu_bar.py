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

    # 帮助菜单信号
    about_requested = pyqtSignal()
    help_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_menus()

    def init_menus(self):
        """初始化所有菜单"""
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_arrange_menu()
        self.create_help_menu()

    def create_file_menu(self):
        """创建文件菜单"""
        file_menu = self.addMenu("文件(&F)")

        # 新建
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_requested.emit)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # 打开
        open_action = QAction("打开(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_requested.emit)
        file_menu.addAction(open_action)

        # 保存
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_requested.emit)
        file_menu.addAction(save_action)

        # 另存为
        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as_requested.emit)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # 导出子菜单
        export_menu = file_menu.addMenu("导出(&E)")

        export_markdown_action = QAction("导出为Markdown...", self)
        export_markdown_action.triggered.connect(self.export_markdown_requested.emit)
        export_menu.addAction(export_markdown_action)

        export_xmind_action = QAction("导出为XMind...", self)
        export_xmind_action.triggered.connect(self.export_xmind_requested.emit)
        export_menu.addAction(export_xmind_action)

        export_anki_action = QAction("导出到Anki...", self)
        export_anki_action.triggered.connect(self.export_anki_requested.emit)
        export_menu.addAction(export_anki_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.exit_requested.emit)
        file_menu.addAction(exit_action)

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
        """创建视图菜单"""
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

        # 工具栏显示/隐藏
        self.toolbar_actions = {}
        toolbars = [
            ("main_toolbar", "主工具栏"),
            ("drawing_toolbar", "绘画工具栏"),
            ("search_toolbar", "搜索工具栏"),
            ("alignment_toolbar", "对齐工具栏")
        ]

        for toolbar_id, toolbar_name in toolbars:
            action = QAction(f"显示{toolbar_name}", self)
            action.setCheckable(True)
            action.setChecked(True)
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

        # 模式切换
        self.drawing_mode_action = QAction("绘画模式", self)
        self.drawing_mode_action.setCheckable(True)
        self.drawing_mode_action.triggered.connect(
            lambda checked: self.toggle_drawing_mode_requested.emit(checked)
        )
        tools_menu.addAction(self.drawing_mode_action)

        self.connection_mode_action = QAction("连接模式", self)
        self.connection_mode_action.setCheckable(True)
        self.connection_mode_action.triggered.connect(
            lambda checked: self.toggle_connection_mode_requested.emit(checked)
        )
        tools_menu.addAction(self.connection_mode_action)

    def create_arrange_menu(self):
        """创建排列菜单"""
        arrange_menu = self.addMenu("排列(&A)")

        # 对齐
        align_left_action = QAction("左对齐", self)
        align_left_action.triggered.connect(self.align_left_requested.emit)
        arrange_menu.addAction(align_left_action)

        align_right_action = QAction("右对齐", self)
        align_right_action.triggered.connect(self.align_right_requested.emit)
        arrange_menu.addAction(align_right_action)

        align_top_action = QAction("顶对齐", self)
        align_top_action.triggered.connect(self.align_top_requested.emit)
        arrange_menu.addAction(align_top_action)

        align_bottom_action = QAction("底对齐", self)
        align_bottom_action.triggered.connect(self.align_bottom_requested.emit)
        arrange_menu.addAction(align_bottom_action)

        arrange_menu.addSeparator()

        align_center_h_action = QAction("水平居中", self)
        align_center_h_action.triggered.connect(self.align_center_h_requested.emit)
        arrange_menu.addAction(align_center_h_action)

        align_center_v_action = QAction("垂直居中", self)
        align_center_v_action.triggered.connect(self.align_center_v_requested.emit)
        arrange_menu.addAction(align_center_v_action)

        arrange_menu.addSeparator()

        distribute_h_action = QAction("水平分布", self)
        distribute_h_action.triggered.connect(self.distribute_h_requested.emit)
        arrange_menu.addAction(distribute_h_action)

        distribute_v_action = QAction("垂直分布", self)
        distribute_v_action.triggered.connect(self.distribute_v_requested.emit)
        arrange_menu.addAction(distribute_v_action)

        arrange_menu.addSeparator()

        arrange_hierarchy_action = QAction("层次排列", self)
        arrange_hierarchy_action.triggered.connect(self.arrange_hierarchy_requested.emit)
        arrange_menu.addAction(arrange_hierarchy_action)

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

    def set_clipboard_monitor_status(self, monitoring):
        """设置剪贴板监控状态"""
        if monitoring:
            self.clipboard_action.setText("剪贴板监控中...")
        else:
            self.clipboard_action.setText("启用剪贴板监控")

    def set_drawing_mode_status(self, enabled):
        """设置绘画模式状态"""
        self.drawing_mode_action.setChecked(enabled)

    def set_connection_mode_status(self, enabled):
        """设置连接模式状态"""
        self.connection_mode_action.setChecked(enabled)

    def set_toolbar_visibility(self, toolbar_id, visible):
        """设置工具栏可见性"""
        if toolbar_id in self.toolbar_actions:
            self.toolbar_actions[toolbar_id].setChecked(visible)