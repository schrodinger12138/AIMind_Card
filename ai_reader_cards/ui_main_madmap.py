"""
基于 madmap 的主窗口 - 整合 AI 生成、Markdown、PDF 等功能
参考 test/madmap/window.py
整合了原有的 UI 组件（菜单栏、工具栏等）
"""

import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsView, QFileDialog, QComboBox, QLabel,
    QSplitter, QStatusBar, QMessageBox
)
from PyQt6.QtGui import QPainter, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer

from ai_reader_cards.card.madmap_based_scene import CardMindMapScene
from ai_reader_cards.card.madmap_based_layout import CardLayoutEngine
from ai_reader_cards.card.madmap_based_nodes import CardVisualNode
from ai_reader_cards.card.madmap_based_models import CardTreeNode

# 导入UI组件
from ai_reader_cards.ui_components.menu_bar import MenuBar
from ai_reader_cards.ui_components.main_toolbar import MainToolbar
from ai_reader_cards.ui_components.input_panel import InputPanel
from ai_reader_cards.ui_components.drawing_toolbar import DrawingToolbar
from ai_reader_cards.ui_components.search_toolbar import SearchToolbar
from ai_reader_cards.ui_components.alignment_toolbar import AlignmentToolbar

# 导入管理器
from ai_reader_cards.ui_components.main_controller import MainController
from ai_reader_cards.ui_components.card_manager import CardManager
from ai_reader_cards.ui_components.search_manager import SearchManager
from ai_reader_cards.ui_components.alignment_manager import AlignmentManager

# 导入其他功能模块
from ai_reader_cards.ai_api import AICardGenerator


class MadMapBasedMainWindow(QMainWindow):
    """
    基于 madmap 的主窗口
    整合 AI 生成、Markdown 预览、PDF 查看等功能
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI卡片思维导图工具 - 基于MadMap")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 初始化管理器
        self.controller = MainController()
        self.card_manager = CardManager()
        self.search_manager = SearchManager()
        self.alignment_manager = AlignmentManager()
        
        # 初始化场景和视图
        self.scene = CardMindMapScene()
        self.view = QGraphicsView(self.scene)
        
        # 初始化UI组件
        self.menu_bar = MenuBar()
        self.main_toolbar = MainToolbar()
        self.input_panel = InputPanel()
        self.drawing_toolbar = DrawingToolbar()
        self.search_toolbar = SearchToolbar()
        self.alignment_toolbar = AlignmentToolbar()
        
        self.root_node = None
        
        # AI 生成器
        self.ai_generator = None
        
        self.init_ui()
        self.connect_signals()
        self.setup_shortcuts()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置菜单栏
        self.setMenuBar(self.menu_bar)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加工具栏（使用QToolBar，默认隐藏）
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.drawing_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.search_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.alignment_toolbar)
        
        # 默认隐藏所有工具栏
        self.main_toolbar.setVisible(False)
        self.drawing_toolbar.setVisible(False)
        self.search_toolbar.setVisible(False)
        self.alignment_toolbar.setVisible(False)
        
        # 创建分割器：左侧输入面板，右侧思维导图
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.input_panel)
        splitter.addWidget(self.view)
        splitter.setSizes([500, 1100])
        main_layout.addWidget(splitter)
        
        # 设置视图属性
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.view.setFocus()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("就绪")
        
        # 加载测试内容（延迟加载，确保UI完全初始化）
        QTimer.singleShot(500, self._load_test_content)
    
    def connect_signals(self):
        """连接所有信号"""
        self._connect_menu_signals()
        self._connect_toolbar_signals()
        self._connect_controller_signals()
        self._connect_ui_signals()
        self._connect_manager_signals()
    
    def _connect_menu_signals(self):
        """连接菜单信号"""
        # 设置菜单
        self.menu_bar.settings_requested.connect(self._show_settings)
        
        # 编辑菜单
        self.menu_bar.undo_requested.connect(self._undo)
        self.menu_bar.redo_requested.connect(self._redo)
        self.menu_bar.cut_requested.connect(lambda: self._handle_text_operation("cut"))
        self.menu_bar.copy_requested.connect(lambda: self._handle_text_operation("copy"))
        self.menu_bar.paste_requested.connect(lambda: self._handle_text_operation("paste"))
        self.menu_bar.delete_requested.connect(self._delete_selected)
        self.menu_bar.select_all_requested.connect(lambda: self._handle_text_operation("select_all"))
        self.menu_bar.find_requested.connect(self._focus_search)
        
        # 视图菜单
        self.menu_bar.zoom_in_requested.connect(self._zoom_in)
        self.menu_bar.zoom_out_requested.connect(self._zoom_out)
        self.menu_bar.zoom_reset_requested.connect(self._zoom_reset)
        self.menu_bar.toggle_toolbar_requested.connect(self._toggle_toolbar)
        self.menu_bar.layout_requested.connect(self._apply_layout_from_menu)
        
        # 工具菜单
        self.menu_bar.connect_ai_requested.connect(self._connect_ai)
        self.menu_bar.toggle_clipboard_monitor_requested.connect(self._toggle_clipboard_monitor)
        self.menu_bar.toggle_connection_mode_requested.connect(self._toggle_connection_mode)
        
        # 帮助菜单
        self.menu_bar.about_requested.connect(self._show_about)
        self.menu_bar.help_requested.connect(self._show_help)
    
    def _connect_toolbar_signals(self):
        """连接工具栏信号"""
        # 主工具栏
        self.main_toolbar.connect_ai_requested.connect(self._connect_ai)
        self.main_toolbar.model_changed.connect(self.controller.on_model_changed)
        self.main_toolbar.open_requested.connect(self._open_file_dialog)
        self.main_toolbar.save_requested.connect(self._save_cards)
        self.main_toolbar.load_requested.connect(self._load_cards)
        self.main_toolbar.toggle_clipboard_monitor_requested.connect(self._toggle_clipboard_monitor)
        self.main_toolbar.clear_canvas_requested.connect(self.clear_canvas)
        self.main_toolbar.export_markdown_requested.connect(self._export_markdown)
        self.main_toolbar.export_xmind_requested.connect(self._export_xmind)
        self.main_toolbar.export_anki_requested.connect(self._export_to_anki)
        self.main_toolbar.apply_layout_requested.connect(self.apply_layout)
        self.main_toolbar.layout_changed.connect(self.change_layout)
        self.main_toolbar.connection_style_changed.connect(self.change_connection_style)
        
        # 搜索工具栏
        self.search_toolbar.search_requested.connect(self._search_cards)
        self.search_toolbar.clear_search_requested.connect(self._clear_search)
        self.search_toolbar.navigate_next_requested.connect(self._navigate_search_next)
        self.search_toolbar.navigate_previous_requested.connect(self._navigate_search_previous)
        
        # 对齐工具栏
        self.alignment_toolbar.alignment_requested.connect(self._handle_alignment_request)
    
    def _connect_controller_signals(self):
        """连接控制器信号"""
        self.controller.status_updated.connect(self.update_status)
        self.controller.card_generated.connect(self.on_card_generated)
        self.controller.generation_error.connect(self.on_generation_error)
    
    def _connect_ui_signals(self):
        """连接UI组件信号"""
        # 输入面板信号
        self.input_panel.generate_card_requested.connect(self.on_generate_card_requested)
        self.input_panel.file_opened.connect(self.on_file_opened)
        
        # 场景信号
        self.scene.jump_to_source_requested.connect(self.on_jump_to_source_requested)
    
    def _connect_manager_signals(self):
        """连接管理器信号"""
        # 搜索管理器
        self.search_manager.search_results_updated.connect(self._on_search_results_updated)
        self.search_manager.navigation_updated.connect(self._on_navigation_updated)
        
        # 对齐管理器
        if hasattr(self.alignment_manager, 'alignment_completed'):
            self.alignment_manager.alignment_completed.connect(self._on_alignment_completed)
    
    def _connect_ai(self):
        """连接AI服务（从菜单/工具栏）"""
        model = self.main_toolbar.get_selected_model() if self.main_toolbar else "gpt-3.5-turbo"
        success, message = self.controller.connect_ai(model)
        if success:
            self.ai_generator = self.controller.ai_generator
            if self.main_toolbar:
                self.main_toolbar.set_ai_connected(model)
            self.update_status(message)
        else:
            QMessageBox.warning(self, "连接失败", message)
            self.update_status(f"AI连接失败: {message}")
    
    def connect_ai(self):
        """连接AI服务（兼容旧方法）"""
        self._connect_ai()
    
    def change_layout(self, layout_name):
        """切换布局"""
        self.scene.set_layout_type(layout_name)
        self.update_status(f"布局已切换: {layout_name}")
    
    def change_connection_style(self, style):
        """切换连线样式"""
        # 映射连线样式（madmap 使用 bezier/smart/gradient）
        style_map = {
            "fixed": "bezier",
            "bezier": "bezier",
            "smart": "smart",
            "gradient": "gradient",
            "default": "bezier"
        }
        madmap_style = style_map.get(style, "bezier")
        self.scene.set_connection_style(madmap_style)
        self.scene.update()
        self.update_status(f"连线样式已切换: {style}")
    
    def apply_layout(self):
        """应用布局算法"""
        self.scene.apply_layout()
        self.update_status("布局已应用")
    
    def on_generate_card_requested(self, text_content):
        """处理生成卡片请求"""
        if not self.ai_generator:
            QMessageBox.warning(self, "未连接AI", "请先连接AI服务")
            return
        
        # 使用控制器生成卡片
        try:
            self.controller.generate_card(text_content)
        except Exception as e:
            QMessageBox.warning(self, "生成失败", str(e))
    
    def on_card_generated(self, card):
        """
        处理卡片生成完成
        card 是 KnowledgeCard 对象，需要转换为 CardTreeNode
        """
        # 从 KnowledgeCard 获取数据
        title = getattr(card, 'title_text', '')
        question = getattr(card, 'question_text', '')
        answer = getattr(card, 'answer_text', '')
        source_text = getattr(card, 'source_text', '')
        source_start = getattr(card, 'source_text_start', -1)
        source_end = getattr(card, 'source_text_end', -1)
        
        # 添加到场景
        visual_node = self.scene.add_card_from_ai(
            title,
            question,
            answer,
            source_text,
            source_start,
            source_end
        )
        
        self.update_status(f"卡片已生成: {title}")
    
    def on_generation_error(self, error_msg):
        """处理生成错误"""
        QMessageBox.warning(self, "生成失败", error_msg)
        self.update_status("卡片生成失败")
    
    def on_file_opened(self, filepath, file_type):
        """处理文件打开"""
        try:
            if file_type == "text":
                content, filename = self.controller.open_text_file(filepath)
            elif file_type == "markdown":
                content, filename = self.controller.open_markdown_file(filepath)
            elif file_type == "pdf":
                content, filename = self.controller.open_pdf_file(filepath)
            else:
                return
            
            # 设置输入面板内容
            if hasattr(self.input_panel, 'text_input'):
                if hasattr(self.input_panel.text_input, 'setPlainText'):
                    self.input_panel.text_input.setPlainText(content)
                elif hasattr(self.input_panel.text_input, 'setText'):
                    self.input_panel.text_input.setText(content)
            
            self.update_status(f"已打开文件: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "打开失败", str(e))
    
    def on_jump_to_source_requested(self, tree_node):
        """处理跳转到源文本请求"""
        if tree_node.source_text and hasattr(self.input_panel, 'text_input'):
            # 在输入面板中高亮源文本
            text_input = self.input_panel.text_input
            if hasattr(text_input, 'setPlainText'):
                text_input.setPlainText(tree_node.source_text)
                # 如果有位置信息，可以滚动到对应位置
                if tree_node.source_text_start >= 0:
                    cursor = text_input.textCursor()
                    cursor.setPosition(tree_node.source_text_start)
                    text_input.setTextCursor(cursor)
                    text_input.ensureCursorVisible()
            self.update_status("已跳转到源文本")
    
    def save_json(self):
        """保存为JSON文件"""
        root_node = self.scene.get_root_node()
        if not root_node:
            QMessageBox.information(self, "提示", "没有可保存的节点")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "保存 JSON", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(root_node.to_dict(), f, ensure_ascii=False, indent=2)
                self.update_status(f"已保存到: {path}")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", str(e))
    
    def load_json(self):
        """从JSON文件加载"""
        path, _ = QFileDialog.getOpenFileName(self, "加载 JSON", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.root_node = CardTreeNode.from_dict(data)
                self.calculate_levels(self.root_node)
                self.refresh_scene()
                self.scene.apply_layout()
                self.update_status(f"已加载: {path}")
            except Exception as e:
                QMessageBox.warning(self, "加载失败", str(e))
    
    def calculate_levels(self, node, level=0):
        """计算节点层级"""
        node.level = level
        for child in node.children:
            self.calculate_levels(child, level + 1)
    
    def refresh_scene(self):
        """刷新场景"""
        self.scene.clear()
        self.scene.visual_nodes.clear()
        
        def add_visual(node):
            vn = CardVisualNode(node)
            self.scene.add_visual_node(vn)
            for c in node.children:
                add_visual(c)
        
        if self.root_node:
            add_visual(self.root_node)
            self.scene.update()
    
    def clear_canvas(self, confirm=True):
        """清空画布"""
        if confirm:
            reply = QMessageBox.question(self, "确认", "确定要清空画布吗？")
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.root_node = None
        self.scene.clear()
        self.scene.visual_nodes.clear()
        self.scene.copied_nodes.clear()
        self.update_status("画布已清空")
    
    # ========== 文件操作相关方法 ==========
    def _open_file_dialog(self):
        """打开文件对话框"""
        self.input_panel._open_file()
    
    def _save_cards(self):
        """保存卡片（使用JSON格式）"""
        root_node = self.scene.get_root_node()
        if not root_node:
            QMessageBox.warning(self, "提示", "画布中没有卡片可保存")
            return
        
        self.save_json()
    
    def _load_cards(self):
        """加载卡片"""
        self.load_json()
    
    def _export_markdown(self):
        """导出Markdown"""
        root_node = self.scene.get_root_node()
        if not root_node:
            QMessageBox.warning(self, "提示", "画布中没有卡片可导出")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "导出为Markdown", "", "Markdown Files (*.md)")
        if path:
            try:
                content = self._convert_tree_to_markdown(root_node)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.update_status(f"已导出到Markdown: {path}")
                QMessageBox.information(self, "成功", f"已成功导出到Markdown文件")
            except Exception as e:
                QMessageBox.warning(self, "导出失败", str(e))
    
    def _export_xmind(self):
        """导出XMind"""
        root_node = self.scene.get_root_node()
        if not root_node:
            QMessageBox.warning(self, "提示", "画布中没有卡片可导出")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "导出为XMind", "", "XMind Files (*.xmind)")
        if path:
            try:
                # 转换为XMind格式（简化版）
                self.update_status("XMind导出功能待实现")
                QMessageBox.information(self, "提示", "XMind导出功能待实现")
            except Exception as e:
                QMessageBox.warning(self, "导出失败", str(e))
    
    def _export_to_anki(self):
        """导出到Anki"""
        root_node = self.scene.get_root_node()
        if not root_node:
            QMessageBox.warning(self, "提示", "画布中没有卡片可导出")
            return
        
        try:
            from ai_reader_cards.utils.anki_connect import AnkiConnector
            connector = AnkiConnector()
            version = connector.check_connection()
            
            if not version:
                QMessageBox.critical(self, "Anki连接失败",
                                    "无法连接到AnkiConnect。请确保：\n"
                                    "1. Anki正在运行\n"
                                    "2. 已安装AnkiConnect插件\n"
                                    "3. AnkiConnect插件已启用")
                return
            
            # 转换节点为卡片并导出
            cards = self._convert_tree_to_cards(root_node)
            success, message = self.controller.export_to_anki(cards)
            if success:
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "导出结果", message)
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出到Anki时发生错误：\n{str(e)}")
    
    def _convert_tree_to_cards(self, node):
        """将树节点转换为KnowledgeCard列表"""
        from ai_reader_cards.card import KnowledgeCard
        cards = []
        
        def walk_tree(n, parent_card=None):
            card = KnowledgeCard(
                card_id=len(cards) + 1,
                title=n.title,
                question=n.question,
                answer=n.answer
            )
            card.source_text = n.source_text
            card.source_text_start = n.source_text_start
            card.source_text_end = n.source_text_end
            if parent_card:
                card.parent_card = parent_card
            cards.append(card)
            
            for child in n.children:
                walk_tree(child, card)
        
        walk_tree(node)
        return cards
    
    def _convert_tree_to_markdown(self, node, level=1):
        """将树节点转换为Markdown格式"""
        lines = []
        
        def walk_tree(n, lvl):
            # 标题
            prefix = "#" * lvl
            lines.append(f"{prefix} {n.title}")
            lines.append("")
            
            # 问题和答案
            if n.question:
                lines.append(f"**问题：** {n.question}")
                lines.append("")
            if n.answer:
                lines.append(f"**答案：** {n.answer}")
                lines.append("")
            
            # 子节点
            for child in n.children:
                walk_tree(child, lvl + 1)
        
        walk_tree(node, level)
        return "\n".join(lines)
    
    # ========== 编辑操作相关方法 ==========
    def _undo(self):
        """撤销（madmap版本暂不支持）"""
        self.update_status("撤销功能待实现")
    
    def _redo(self):
        """重做（madmap版本暂不支持）"""
        self.update_status("重做功能待实现")
    
    def _delete_selected(self):
        """删除选中项"""
        selected_nodes = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if selected_nodes:
            reply = QMessageBox.question(self, "确认删除",
                                        f"确定要删除选中的 {len(selected_nodes)} 个节点吗？")
            if reply == QMessageBox.StandardButton.Yes:
                for node in selected_nodes:
                    self.scene.delete_node(node)
                self.update_status(f"已删除 {len(selected_nodes)} 个节点")
    
    def _handle_text_operation(self, operation):
        """处理文本操作"""
        if hasattr(self.input_panel, 'text_input'):
            text_input = self.input_panel.text_input
            if operation == "copy":
                text_input.copy()
                self.update_status("文本已复制")
            elif operation == "paste":
                text_input.paste()
                self.update_status("文本已粘贴")
            elif operation == "cut":
                text_input.cut()
                self.update_status("文本已剪切")
            elif operation == "select_all":
                text_input.selectAll()
                self.update_status("已全选文本")
    
    # ========== 视图操作相关方法 ==========
    def _zoom_in(self):
        """放大视图"""
        self.view.scale(1.2, 1.2)
        self.update_status("视图已放大")
    
    def _zoom_out(self):
        """缩小视图"""
        self.view.scale(0.8, 0.8)
        self.update_status("视图已缩小")
    
    def _zoom_reset(self):
        """重置缩放"""
        self.view.resetTransform()
        self.update_status("视图缩放已重置")
    
    def _toggle_toolbar(self, toolbar_id, visible):
        """切换工具栏可见性"""
        toolbars = {
            "main_toolbar": self.main_toolbar,
            "drawing_toolbar": self.drawing_toolbar,
            "search_toolbar": self.search_toolbar,
            "alignment_toolbar": self.alignment_toolbar
        }
        
        if toolbar_id in toolbars:
            toolbars[toolbar_id].setVisible(visible)
            status = "显示" if visible else "隐藏"
            self.update_status(f"{status} {toolbar_id}")
    
    def _apply_layout_from_menu(self, layout_name):
        """从菜单应用布局"""
        self.change_layout(layout_name)
        self.apply_layout()
    
    # ========== 设置相关方法 ==========
    def _show_settings(self):
        """显示设置对话框"""
        from ai_reader_cards.ui_components.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()
    
    def _on_settings_saved(self):
        """设置保存后的回调"""
        self.update_status("设置已保存，部分设置需要重启应用生效")
        # 重新初始化AI生成器以应用新配置
        try:
            model = self.main_toolbar.get_selected_model() if self.main_toolbar else "gpt-3.5-turbo"
            self.controller.ai_generator = AICardGenerator(model=model)
            self.ai_generator = self.controller.ai_generator
            self.update_status("AI配置已更新")
        except Exception as e:
            self.update_status(f"更新AI配置失败: {str(e)}")
    
    def _focus_search(self):
        """聚焦到搜索框"""
        if hasattr(self.search_toolbar, 'search_input'):
            self.search_toolbar.search_input.setFocus()
            self.search_toolbar.search_input.selectAll()
            self.update_status("搜索框已聚焦")
    
    # ========== 工具操作相关方法 ==========
    def _toggle_clipboard_monitor(self, checked):
        """切换剪贴板监控"""
        success, message = self.controller.toggle_clipboard_monitor(checked, self._on_clipboard_changed)
        if success:
            self.update_status(message)
        else:
            QMessageBox.warning(self, "操作失败", message)
    
    def _toggle_connection_mode(self, enabled):
        """切换连接模式（madmap版本暂不支持）"""
        self.update_status("连接模式功能待实现")
    
    def _on_clipboard_changed(self, text):
        """剪贴板内容改变"""
        if len(text.strip()) >= 15 and self.controller.ai_generator:
            self.controller.generate_card(text)
            self.update_status("从剪贴板生成卡片中...")
    
    # ========== 搜索相关方法 ==========
    def _search_cards(self, keyword, search_fields=None):
        """搜索卡片"""
        # 获取所有节点
        all_nodes = [vn.tree_node for vn in self.scene.visual_nodes]
        
        # 执行搜索
        results = []
        for node in all_nodes:
            if keyword.lower() in node.title.lower():
                results.append(node)
            elif keyword.lower() in node.question.lower():
                results.append(node)
            elif keyword.lower() in node.answer.lower():
                results.append(node)
        
        # 高亮显示结果
        for vn in self.scene.visual_nodes:
            vn.setSelected(vn.tree_node in results)
        
        if results:
            # 聚焦到第一个结果
            first_vn = next((vn for vn in self.scene.visual_nodes if vn.tree_node == results[0]), None)
            if first_vn:
                self.view.centerOn(first_vn)
            
            self.update_status(f"找到 {len(results)} 个匹配 '{keyword}' 的结果")
        else:
            self.update_status(f"未找到匹配 '{keyword}' 的结果")
    
    def _navigate_search_next(self):
        """导航到下一个搜索结果"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if selected:
            # 找到下一个选中的节点
            all_selected = [vn for vn in self.scene.visual_nodes if vn.isSelected()]
            if all_selected:
                current = selected[0] if selected else None
                if current:
                    try:
                        current_index = all_selected.index(current)
                        next_index = (current_index + 1) % len(all_selected)
                        next_node = all_selected[next_index]
                        self.view.centerOn(next_node)
                        self.update_status(f"导航到结果 {next_index + 1}/{len(all_selected)}")
                    except ValueError:
                        pass
    
    def _navigate_search_previous(self):
        """导航到上一个搜索结果"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if selected:
            all_selected = [vn for vn in self.scene.visual_nodes if vn.isSelected()]
            if all_selected:
                current = selected[0] if selected else None
                if current:
                    try:
                        current_index = all_selected.index(current)
                        prev_index = (current_index - 1) % len(all_selected)
                        prev_node = all_selected[prev_index]
                        self.view.centerOn(prev_node)
                        self.update_status(f"导航到结果 {prev_index + 1}/{len(all_selected)}")
                    except ValueError:
                        pass
    
    def _clear_search(self):
        """清除搜索"""
        for vn in self.scene.visual_nodes:
            vn.setSelected(False)
        if hasattr(self.search_toolbar, 'clear_status'):
            self.search_toolbar.clear_status()
        self.update_status("搜索已清除")
    
    # ========== 对齐相关方法 ==========
    def _handle_alignment_request(self, align_type):
        """处理对齐请求"""
        align_map = {
            "left": self._align_left,
            "right": self._align_right,
            "top": self._align_top,
            "bottom": self._align_bottom,
            "center_h": self._align_center_h,
            "center_v": self._align_center_v
        }
        align_func = align_map.get(align_type)
        if align_func:
            align_func()
    
    def _align_left(self):
        """左对齐"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if len(selected) < 2:
            QMessageBox.warning(self, "提示", "请至少选择2个节点进行对齐")
            return
        
        min_x = min(vn.pos().x() for vn in selected)
        for vn in selected:
            vn.setPos(min_x, vn.pos().y())
        self.scene.update()
        self.update_status("已左对齐")
    
    def _align_right(self):
        """右对齐"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if len(selected) < 2:
            QMessageBox.warning(self, "提示", "请至少选择2个节点进行对齐")
            return
        
        max_x = max(vn.pos().x() + vn.WIDTH for vn in selected)
        for vn in selected:
            vn.setPos(max_x - vn.WIDTH, vn.pos().y())
        self.scene.update()
        self.update_status("已右对齐")
    
    def _align_top(self):
        """上对齐"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if len(selected) < 2:
            QMessageBox.warning(self, "提示", "请至少选择2个节点进行对齐")
            return
        
        min_y = min(vn.pos().y() for vn in selected)
        for vn in selected:
            vn.setPos(vn.pos().x(), min_y)
        self.scene.update()
        self.update_status("已上对齐")
    
    def _align_bottom(self):
        """下对齐"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if len(selected) < 2:
            QMessageBox.warning(self, "提示", "请至少选择2个节点进行对齐")
            return
        
        max_y = max(vn.pos().y() + vn.HEIGHT for vn in selected)
        for vn in selected:
            vn.setPos(vn.pos().x(), max_y - vn.HEIGHT)
        self.scene.update()
        self.update_status("已下对齐")
    
    def _align_center_h(self):
        """水平居中对齐"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if len(selected) < 2:
            QMessageBox.warning(self, "提示", "请至少选择2个节点进行对齐")
            return
        
        center_x = sum(vn.pos().x() + vn.WIDTH / 2 for vn in selected) / len(selected)
        for vn in selected:
            vn.setPos(center_x - vn.WIDTH / 2, vn.pos().y())
        self.scene.update()
        self.update_status("已水平居中对齐")
    
    def _align_center_v(self):
        """垂直居中对齐"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CardVisualNode)]
        if len(selected) < 2:
            QMessageBox.warning(self, "提示", "请至少选择2个节点进行对齐")
            return
        
        center_y = sum(vn.pos().y() + vn.HEIGHT / 2 for vn in selected) / len(selected)
        for vn in selected:
            vn.setPos(vn.pos().x(), center_y - vn.HEIGHT / 2)
        self.scene.update()
        self.update_status("已垂直居中对齐")
    
    # ========== 管理器回调方法 ==========
    def _on_search_results_updated(self, results, keyword):
        """搜索结果更新回调"""
        # 将 KnowledgeCard 转换为 CardTreeNode 进行搜索
        # 注意：这里 results 是 KnowledgeCard 列表，需要适配
        if results:
            # 如果 results 是 KnowledgeCard，需要找到对应的 CardVisualNode
            # 暂时简化处理：直接使用场景中的节点
            all_nodes = [vn.tree_node for vn in self.scene.visual_nodes]
            matched_nodes = []
            
            # 尝试匹配节点（简化版）
            for card in results:
                # 根据卡片标题查找对应的节点
                for node in all_nodes:
                    if hasattr(card, 'title_text') and node.title == card.title_text:
                        matched_nodes.append(node)
                        break
            
            # 高亮显示结果
            for vn in self.scene.visual_nodes:
                vn.setSelected(vn.tree_node in matched_nodes)
            
            if matched_nodes:
                first_vn = next((vn for vn in self.scene.visual_nodes if vn.tree_node == matched_nodes[0]), None)
                if first_vn:
                    self.view.centerOn(first_vn)
                self.update_status(f"找到 {len(matched_nodes)} 个匹配 '{keyword}' 的结果")
            else:
                self.update_status(f"找到 {len(results)} 个匹配 '{keyword}' 的结果（需要适配）")
        else:
            # 清除选择
            for vn in self.scene.visual_nodes:
                vn.setSelected(False)
            self.update_status(f"未找到匹配 '{keyword}' 的结果")
    
    def _on_navigation_updated(self, current_index, total_results):
        """导航更新回调"""
        if hasattr(self.search_toolbar, 'update_status'):
            keyword = self.search_toolbar.search_input.text() if hasattr(self.search_toolbar, 'search_input') else ""
            self.search_toolbar.update_status(current_index, total_results, keyword)
    
    def _on_alignment_completed(self, message):
        """对齐完成回调"""
        self.scene.update()
        self.update_status(message)
    
    # ========== 帮助相关方法 ==========
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于",
            "AI卡片思维导图工具 v1.0 - MadMap版\n\n"
            "一个基于AI的知识管理和思维导图工具。\n"
            "支持从文本和PDF生成学习卡片，并可视化为思维导图。\n\n"
            "功能特点:\n"
            "• AI智能生成学习卡片（包含问题和答案）\n"
            "• 可视化思维导图（基于MadMap）\n"
            "• 支持PDF和文本文件\n"
            "• 导出到Markdown、XMind、Anki\n"
            "• 剪贴板监控自动生成")
    
    def _show_help(self):
        """显示帮助"""
        QMessageBox.information(self, "使用帮助",
            "使用说明:\n\n"
            "1. 连接AI服务后，可以生成学习卡片\n"
            "2. 支持打开文本文件和PDF文件\n"
            "3. 选中文本后按空格键或点击生成卡片按钮\n"
            "4. 在思维导图中可以拖拽、连接卡片\n"
            "5. 支持导出为Markdown、XMind和Anki格式\n\n"
            "快捷键:\n"
            "• Ctrl+O: 打开文件\n"
            "• Ctrl+S: 保存\n"
            "• Ctrl+F: 搜索\n"
            "• Ctrl+C/V/X: 复制/粘贴/剪切\n"
            "• Ctrl+A: 全选\n"
            "• Delete: 删除选中节点\n"
            "• Enter: 添加子节点\n"
            "• Tab: 添加同级节点\n"
            "• Space: 生成卡片")
    
    # ========== 工具方法 ==========
    def setup_shortcuts(self):
        """设置快捷键"""
        # 快捷键已经在各个UI组件中设置
        pass
    
    def _load_test_content(self):
        """加载测试内容"""
        test_markdown = """# LaTeX公式测试文档

这是一个测试文档，用于测试LaTeX公式渲染功能。

## 基本公式

### 行内公式
这是行内公式：$E=mc^2$，还有 $\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$。

### 块级公式

基本公式：
$$E = mc^2$$

积分公式：
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

微分方程：
$$\\frac{\\partial u}{\\partial t} = \\alpha \\nabla^2 u$$

## 复杂公式

### 量子力学公式
$$H=\\varepsilon_{0,\\mathbf{k}}+t_{x,\\mathbf{k}}\\tau_{x}+t_{z,\\mathbf{k}}\\tau_{z}+\\tau_{y}\\vec{\\lambda}_{\\mathbf{k}}\\cdot\\vec{\\sigma}+\\tau_{z}\\vec{J}\\cdot\\vec{\\sigma}$$

测试文档 - 用于验证LaTeX公式渲染功能
"""
        if hasattr(self.input_panel, 'text_input'):
            if hasattr(self.input_panel.text_input, 'setPlainText'):
                self.input_panel.text_input.setPlainText(test_markdown)
            elif hasattr(self.input_panel.text_input, 'setText'):
                self.input_panel.text_input.setText(test_markdown)
    
    def update_status(self, message):
        """更新状态栏"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"[{timestamp}] {message}")
    
    def keyPressEvent(self, event: QKeyEvent):
        """窗口级别的键盘事件处理"""
        # 将键盘事件传递给场景
        self.scene.keyPressEvent(event)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MadMapBasedMainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

