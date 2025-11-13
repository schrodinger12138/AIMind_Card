# 文件路径: ai_reader_cards\ui_main.py (完整版本)
"""重构后的主窗口 - 使用标准菜单栏和工具栏"""

import sys
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt, QTimer

# 导入新的UI组件
from ai_reader_cards.ui_components.menu_bar import MenuBar
from ai_reader_cards.ui_components.main_toolbar import MainToolbar
from ai_reader_cards.ui_components.input_panel import InputPanel
from ai_reader_cards.ui_components.mindmap_panel import MindMapPanel
from ai_reader_cards.ui_components.drawing_toolbar import DrawingToolbar
from ai_reader_cards.ui_components.search_toolbar import SearchToolbar
from ai_reader_cards.ui_components.alignment_toolbar import AlignmentToolbar

# 导入管理器
from ai_reader_cards.ui_components.main_controller import MainController
from ai_reader_cards.ui_components.card_manager import CardManager
from ai_reader_cards.ui_components.search_manager import SearchManager
from ai_reader_cards.ui_components.alignment_manager import AlignmentManager


class MainWindow(QMainWindow):
    """重构后的主窗口 - 使用标准UI布局"""

    def __init__(self):
        super().__init__()

        # 初始化管理器
        self.controller = MainController()
        self.card_manager = CardManager()
        self.search_manager = SearchManager()
        self.alignment_manager = AlignmentManager()

        # 初始化UI组件
        self.menu_bar = MenuBar()
        self.main_toolbar = MainToolbar()
        self.input_panel = InputPanel()
        self.mindmap_panel = MindMapPanel()
        self.drawing_toolbar = DrawingToolbar()
        self.search_toolbar = SearchToolbar()
        self.alignment_toolbar = AlignmentToolbar()

        self.init_ui()
        self.connect_signals()
        self.setup_shortcuts()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("AI阅读卡片思维导图工具 v1.0")
        self.setGeometry(100, 100, 1400, 800)

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
        
        # 默认隐藏所有工具栏（除了主工具栏）
        self.main_toolbar.setVisible(False)  # 主工具栏也默认隐藏
        self.drawing_toolbar.setVisible(False)
        self.search_toolbar.setVisible(False)
        self.alignment_toolbar.setVisible(False)

        # 创建分割器 - 左侧输入面板，右侧思维导图
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.input_panel)
        splitter.addWidget(self.mindmap_panel)
        splitter.setSizes([400, 1000])
        main_layout.addWidget(splitter)

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
        self.main_toolbar.clear_canvas_requested.connect(self._clear_canvas)
        self.main_toolbar.export_markdown_requested.connect(self._export_markdown)
        self.main_toolbar.export_xmind_requested.connect(self._export_xmind)
        self.main_toolbar.export_anki_requested.connect(self._export_to_anki)
        self.main_toolbar.apply_layout_requested.connect(self._apply_layout)
        self.main_toolbar.connection_style_changed.connect(self._change_connection_style)

        # 思维导图面板的绘画功能（已移到面板上方）
        self.mindmap_panel.drawing_mode_toggled.connect(self.mindmap_panel.set_drawing_mode)
        self.mindmap_panel.pen_color_changed.connect(self.mindmap_panel.set_pen_color)
        self.mindmap_panel.pen_width_changed.connect(self.mindmap_panel.set_pen_width)
        self.mindmap_panel.clear_drawings_requested.connect(self.mindmap_panel.clear_drawings)
        self.mindmap_panel.load_cards_requested.connect(self._load_cards)
        
        # 绘画工具栏（如果显示）
        if self.drawing_toolbar:
            self.drawing_toolbar.drawing_mode_toggled.connect(self.mindmap_panel.set_drawing_mode)
            self.drawing_toolbar.pen_color_changed.connect(self.mindmap_panel.set_pen_color)
            self.drawing_toolbar.pen_width_changed.connect(self.mindmap_panel.set_pen_width)
            self.drawing_toolbar.clear_drawings_requested.connect(self.mindmap_panel.clear_drawings)

        # 搜索工具栏
        self.search_toolbar.search_requested.connect(self._search_cards)
        self.search_toolbar.navigate_next_requested.connect(self._navigate_search_next)
        self.search_toolbar.navigate_previous_requested.connect(self._navigate_search_previous)
        self.search_toolbar.clear_search_requested.connect(self._clear_search)

        # 对齐工具栏
        self.alignment_toolbar.alignment_requested.connect(self._align_cards)
        self.alignment_toolbar.arrange_hierarchy_requested.connect(self._arrange_hierarchy)

    def _connect_controller_signals(self):
        """连接控制器信号"""
        self.controller.status_updated.connect(self.update_status)
        self.controller.card_generated.connect(self.mindmap_panel.add_card)
        self.controller.generation_error.connect(self._handle_generation_error)

    def _connect_ui_signals(self):
        """连接UI组件信号"""
        # 输入面板信号
        self.input_panel.file_opened.connect(self._open_file)
        self.input_panel.generate_card_requested.connect(self.controller.generate_card)
        self.input_panel.text_operation_requested.connect(self._handle_text_operation)
        self.input_panel.pdf_dropped.connect(self._handle_pdf_drop)
        self.input_panel.markdown_dropped.connect(self._handle_markdown_drop)
        self.input_panel.translate_requested.connect(self._translate_markdown)

        # 思维导图面板信号
        self.mindmap_panel.link_cards_requested.connect(self._link_selected_cards)
        self.mindmap_panel.unlink_card_requested.connect(self._unlink_selected_card)
        self.mindmap_panel.connection_mode_toggled.connect(self._toggle_connection_mode)
        self.mindmap_panel.delete_connection_requested.connect(self._delete_connection)

    def _connect_manager_signals(self):
        """连接管理器信号"""
        self.card_manager.cards_linked.connect(self._on_cards_linked)
        self.card_manager.card_unlinked.connect(self._on_card_unlinked)
        self.card_manager.connection_deleted.connect(self._on_connection_deleted)

        self.search_manager.search_results_updated.connect(self._on_search_results_updated)
        self.search_manager.navigation_updated.connect(self._on_navigation_updated)

    # 文件操作相关方法
    def _new_file(self):
        """新建文件"""
        reply = QMessageBox.question(self, "确认", "确定要创建新文件吗？未保存的更改将丢失。")
        if reply == QMessageBox.StandardButton.Yes:
            self._clear_canvas(confirm=False)
            self.input_panel._clear_content()
            self.update_status("已创建新文件")

    def _open_file_dialog(self):
        """打开文件对话框"""
        self.input_panel._open_file()

    def _open_file(self, filepath, file_type):
        """打开文件"""
        try:
            if file_type == 'pdf':
                content, filename = self.controller.open_pdf_file(filepath)
            elif file_type == 'markdown':
                content, filename = self.controller.open_markdown_file(filepath)
            else:
                content, filename = self.controller.open_text_file(filepath)

            self.input_panel.set_file_content(content, filename, file_type)
            self.update_status(f"已打开文件: {filename}")
        except Exception as e:
            self._show_message(False, f"无法打开文件:\n{str(e)}")
    
    def _handle_pdf_drop(self, pdf_path):
        """处理PDF拖拽"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox
        
        # 显示转换选项对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF文件处理")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 提示信息
        info_label = QLabel(f"检测到PDF文件:\n{pdf_path}\n\n请选择处理方式：")
        layout.addWidget(info_label)
        
        # 转换选项
        convert_checkbox = QCheckBox("转换为Markdown格式（使用OCR识别）")
        convert_checkbox.setChecked(True)
        layout.addWidget(convert_checkbox)
        
        direct_checkbox = QCheckBox("直接打开PDF（提取文本，不转换）")
        layout.addWidget(direct_checkbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if convert_checkbox.isChecked():
                # 转换为Markdown
                self._convert_pdf_to_markdown(pdf_path)
            elif direct_checkbox.isChecked():
                # 直接打开PDF
                self._open_file(pdf_path, 'pdf')
            else:
                # 默认转换为Markdown
                self._convert_pdf_to_markdown(pdf_path)
    
    def _convert_pdf_to_markdown(self, pdf_path):
        """将PDF转换为Markdown"""
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class PDFConversionThread(QThread):
            """PDF转换线程"""
            progress = pyqtSignal(int, int, str)  # current, total, message
            finished = pyqtSignal(str, str)  # content, filename
            error = pyqtSignal(str)
            
            def __init__(self, pdf_path):
                super().__init__()
                self.pdf_path = pdf_path
            
            def run(self):
                try:
                    from ai_reader_cards.markdown import PDFToMarkdownConverter
                    converter = PDFToMarkdownConverter()
                    
                    def progress_callback(current, total, message):
                        self.progress.emit(current, total, message)
                    
                    content = converter.convert_pdf_to_markdown(
                        self.pdf_path,
                        progress_callback=progress_callback
                    )
                    
                    filename = os.path.basename(self.pdf_path)
                    self.finished.emit(content, filename)
                except Exception as e:
                    self.error.emit(str(e))
        
        # 创建进度对话框
        progress_dialog = QProgressDialog("正在转换PDF...", "取消", 0, 100, self)
        progress_dialog.setWindowTitle("PDF转Markdown")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        
        # 创建转换线程
        thread = PDFConversionThread(pdf_path)
        
        def update_progress(current, total, message):
            if total > 0:
                progress = int((current / total) * 100)
                progress_dialog.setValue(progress)
                progress_dialog.setLabelText(message)
        
        def on_finished(content, filename):
            progress_dialog.close()
            self.input_panel.set_file_content(content, filename, 'markdown')
            self.update_status(f"已转换PDF为Markdown: {filename}")
        
        def on_error(error_msg):
            progress_dialog.close()
            self._show_message(False, f"PDF转换失败:\n{error_msg}")
        
        thread.progress.connect(update_progress)
        thread.finished.connect(on_finished)
        thread.error.connect(on_error)
        
        thread.start()
        progress_dialog.exec()
    
    def _handle_markdown_drop(self, markdown_path):
        """处理Markdown文件拖拽"""
        # 直接打开Markdown文件
        try:
            content, filename = self.controller.open_markdown_file(markdown_path)
            self.input_panel.set_file_content(content, filename, 'markdown')
            self.update_status(f"已打开Markdown文件: {filename}")
        except Exception as e:
            self._show_message(False, f"无法打开Markdown文件:\n{str(e)}")
    
    def _translate_markdown(self, target_language):
        """翻译Markdown内容"""
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import QThread, pyqtSignal
        from ai_reader_cards.markdown import MarkdownTranslator
        
        class TranslationThread(QThread):
            """翻译线程"""
            progress = pyqtSignal(int, int, str)  # current, total, message
            finished = pyqtSignal(str)  # translated_content
            error = pyqtSignal(str)
            
            def __init__(self, content, target_language):
                super().__init__()
                self.content = content
                self.target_language = target_language
            
            def run(self):
                try:
                    translator = MarkdownTranslator()
                    
                    def progress_callback(current, total, message):
                        self.progress.emit(current, total, message)
                    
                    translated = translator.translate_markdown(
                        self.content,
                        self.target_language,
                        progress_callback
                    )
                    self.finished.emit(translated)
                except Exception as e:
                    self.error.emit(str(e))
        
        # 获取当前内容
        content = self.input_panel.get_plain_text()
        if not content:
            QMessageBox.warning(self, "提示", "没有可翻译的内容")
            return
        
        # 创建进度对话框
        progress_dialog = QProgressDialog("正在翻译...", "取消", 0, 100, self)
        progress_dialog.setWindowTitle("Markdown翻译")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        
        # 创建翻译线程
        thread = TranslationThread(content, target_language)
        
        def update_progress(current, total, message):
            if total > 0:
                progress = int((current / total) * 100)
                progress_dialog.setValue(progress)
                progress_dialog.setLabelText(message)
        
        def on_finished(translated_content):
            progress_dialog.close()
            self.input_panel.set_file_content(translated_content, "翻译结果", 'markdown')
            self.update_status(f"翻译完成（目标语言: {target_language}）")
        
        def on_error(error_msg):
            progress_dialog.close()
            self._show_message(False, f"翻译失败:\n{error_msg}")
        
        thread.progress.connect(update_progress)
        thread.finished.connect(on_finished)
        thread.error.connect(on_error)
        
        thread.start()
        progress_dialog.exec()

    def _save_cards(self):
        """保存卡片"""
        cards = self.mindmap_panel.get_all_cards()
        if not cards:
            QMessageBox.warning(self, "提示", "画布中没有卡片可保存")
            return

        success, message = self.controller.save_cards(cards)
        if success:
            self.update_status(message)
        else:
            self._show_message(success, message)

    def _save_cards_as(self):
        """另存为卡片"""
        cards = self.mindmap_panel.get_all_cards()
        if not cards:
            QMessageBox.warning(self, "提示", "画布中没有卡片可保存")
            return

        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "另存为", "cards.json", "JSON文件 (*.json)"
        )
        if filepath:
            try:
                self.controller.storage.save_cards(cards, filepath)
                self.update_status(f"已保存 {len(cards)} 张卡片到: {filepath}")
                QMessageBox.information(self, "成功", f"已保存 {len(cards)} 张卡片")
            except Exception as e:
                self._show_message(False, f"保存失败:\n{str(e)}")

    def _load_cards(self):
        """加载卡片"""
        try:
            result = self.controller.load_cards()
            if result:
                loaded_cards, card_map = result
                self._clear_canvas(confirm=False)

                for card in loaded_cards:
                    self.mindmap_panel.add_card(card)

                self.mindmap_panel.update_scene()
                self.update_status(f"已加载 {len(loaded_cards)} 张卡片")
        except Exception as e:
            self._show_message(False, f"加载失败:\n{str(e)}")

    def _export_markdown(self):
        """导出Markdown"""
        cards = self.mindmap_panel.get_all_cards()
        if not cards:
            QMessageBox.warning(self, "提示", "画布中没有卡片可导出")
            return

        success, message = self.controller.export_markdown(cards)
        self._show_message(success, message)

    def _export_xmind(self):
        """导出XMind"""
        cards = self.mindmap_panel.get_all_cards()
        if not cards:
            QMessageBox.warning(self, "提示", "画布中没有卡片可导出")
            return

        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出为XMind", "mindmap.xmind", "XMind文件 (*.xmind)"
        )
        if filepath:
            try:
                self.mindmap_panel.mindmap_scene.export_to_xmind(filepath)
                self.update_status(f"已导出到XMind: {filepath}")
                QMessageBox.information(self, "成功", f"已成功导出到XMind文件")
            except Exception as e:
                self._show_message(False, f"导出XMind失败:\n{str(e)}")

    def _export_to_anki(self):
        """导出到Anki"""
        try:
            cards = self.mindmap_panel.get_all_cards()
            if not cards:
                QMessageBox.warning(self, "提示", "画布中没有卡片可导出")
                return

            # 检查Anki连接
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

            # 执行导出
            success, message = self.controller.export_to_anki(cards)
            if success:
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "导出结果", message)

        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出到Anki时发生错误：\n{str(e)}")

    # 编辑操作相关方法
    def _undo(self):
        """撤销"""
        self.mindmap_panel.mindmap_scene.undo()
        self.update_status("已撤销")

    def _redo(self):
        """重做"""
        self.mindmap_panel.mindmap_scene.redo()
        self.update_status("已重做")

    def _delete_selected(self):
        """删除选中项"""
        selected_cards = self.mindmap_panel.get_selected_cards()
        if selected_cards:
            reply = QMessageBox.question(self, "确认删除",
                                        f"确定要删除选中的 {len(selected_cards)} 张卡片吗？")
            if reply == QMessageBox.StandardButton.Yes:
                for card in selected_cards:
                    self.mindmap_panel.remove_card(card)
                self.update_status(f"已删除 {len(selected_cards)} 张卡片")

    def _handle_text_operation(self, operation):
        """处理文本操作"""
        text_input = self.input_panel.get_text_input()
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

    # 视图操作相关方法
    def _zoom_in(self):
        """放大视图"""
        self.mindmap_panel.mindmap_view.scale(1.2, 1.2)
        self.update_status("视图已放大")

    def _zoom_out(self):
        """缩小视图"""
        self.mindmap_panel.mindmap_view.scale(0.8, 0.8)
        self.update_status("视图已缩小")

    def _zoom_reset(self):
        """重置缩放"""
        self.mindmap_panel.mindmap_view.resetTransform()
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
            from ai_reader_cards.ai_api import AICardGenerator
            model = self.main_toolbar.get_selected_model() if self.main_toolbar else "gpt-3.5-turbo"
            self.controller.ai_generator = AICardGenerator(model=model)
            self.update_status("AI配置已更新")
        except Exception as e:
            self.update_status(f"更新AI配置失败: {str(e)}")

    def _focus_search(self):
        """聚焦到搜索框"""
        self.search_toolbar.search_input.setFocus()
        self.search_toolbar.search_input.selectAll()
        self.update_status("搜索框已聚焦")

    # 工具操作相关方法
    def _connect_ai(self):
        """连接AI服务"""
        model = self.main_toolbar.get_selected_model()
        success, message = self.controller.connect_ai(model)

        if success:
            if self.main_toolbar:
                self.main_toolbar.set_ai_connected(model)
            self.input_panel.enable_generate_button(True)
            self.update_status(f"AI已连接 - 模型: {model}")
        self._show_message(success, message)

    def _toggle_clipboard_monitor(self, checked):
        """切换剪贴板监控"""
        success, message = self.controller.toggle_clipboard_monitor(checked, self._on_clipboard_changed)
        if success:
            if self.main_toolbar and hasattr(self.main_toolbar, 'set_clipboard_monitor_status'):
                self.main_toolbar.set_clipboard_monitor_status(checked)
        self._show_message(success, message)

    def _toggle_drawing_mode(self, enabled):
        """切换绘画模式"""
        self.drawing_toolbar.drawing_btn.setChecked(enabled)
        self.mindmap_panel.set_drawing_mode(enabled)
        status = "启用" if enabled else "禁用"
        self.update_status(f"{status}绘画模式")

    def _toggle_connection_mode(self, enabled):
        """切换连接模式"""
        self.mindmap_panel.set_connection_mode(enabled)
        status = "启用" if enabled else "禁用"
        self.update_status(f"{status}连接模式")

    # 排列操作相关方法
    def _align_cards(self, align_type):
        """对齐选中的卡片"""
        cards = self.mindmap_panel.get_selected_cards()
        success, message = self.alignment_manager.align_cards(cards, align_type)
        if success:
            self.mindmap_panel.update_scene()
        self._show_message(success, message)

    def _arrange_hierarchy(self):
        """层次排列"""
        cards = self.mindmap_panel.get_selected_cards()
        success, message = self.alignment_manager.arrange_hierarchy(cards)
        if success:
            self.mindmap_panel.update_scene()
        self._show_message(success, message)

    # 卡片管理相关方法
    def _link_selected_cards(self):
        """连接选中的卡片"""
        cards = self.mindmap_panel.get_selected_cards()
        success, message = self.card_manager.link_cards(cards)
        if success:
            self.mindmap_panel.update_scene()
        self._show_message(success, message)

    def _unlink_selected_card(self):
        """取消连接"""
        cards = self.mindmap_panel.get_selected_cards()
        if cards:
            success, message = self.card_manager.unlink_card(cards[0])
            if success:
                self.mindmap_panel.update_scene()
            self._show_message(success, message)

    def _delete_connection(self):
        """删除连接"""
        cards = self.mindmap_panel.get_selected_cards()
        if cards:
            success, message = self.card_manager.delete_connection(cards[0])
            if success:
                self.mindmap_panel.update_scene()
            self._show_message(success, message)

    # 搜索相关方法
    def _search_cards(self, keyword, search_fields):
        """搜索卡片"""
        cards = self.mindmap_panel.get_all_cards()
        self.search_manager.search(cards, keyword, search_fields)

    def _navigate_search_next(self):
        """导航到下一个搜索结果"""
        card = self.search_manager.navigate_next()
        if card:
            self._focus_card(card)

    def _navigate_search_previous(self):
        """导航到上一个搜索结果"""
        card = self.search_manager.navigate_previous()
        if card:
            self._focus_card(card)

    def _clear_search(self):
        """清除搜索"""
        self.search_manager.clear_search()
        for card in self.mindmap_panel.get_all_cards():
            card.setSelected(False)
        self.search_toolbar.clear_status()
        self.update_status("搜索已清除")

    # 帮助相关方法
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于",
            "AI阅读卡片思维导图工具 v1.0\n\n"
            "一个基于AI的知识管理和思维导图工具。\n"
            "支持从文本和PDF生成学习卡片，并可视化为思维导图。\n\n"
            "功能特点:\n"
            "• AI智能生成学习卡片\n"
            "• 可视化思维导图\n"
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
            "• Delete: 删除选中卡片\n"
            "• Space: 生成卡片")

    # 事件处理相关方法
    def _on_clipboard_changed(self, text):
        """剪贴板内容改变"""
        if len(text.strip()) >= 15 and self.controller.ai_generator:
            self.controller.generate_card(text)
            self.update_status("从剪贴板生成卡片中...")

    def _on_cards_linked(self, parent_card, child_card):
        """卡片连接完成"""
        self.update_status(f"已建立连接: {parent_card.title_text} → {child_card.title_text}")

    def _on_card_unlinked(self, card):
        """卡片取消连接"""
        self.update_status(f"已取消卡片连接: {card.title_text}")

    def _on_connection_deleted(self, from_card, to_card):
        """连接已删除"""
        self.update_status(f"已删除连接: {from_card.title_text} → {to_card.title_text}")

    def _on_search_results_updated(self, results, keyword):
        """搜索结果更新"""
        if results:
            # 高亮显示结果
            for card in self.mindmap_panel.get_all_cards():
                card.setSelected(card in results)

            # 聚焦到第一个结果
            if results:
                self._focus_card(results[0])

            current_index, total_results, _ = self.search_manager.get_current_status()
            self.search_toolbar.update_status(current_index, total_results, keyword)
            self.update_status(f"找到 {len(results)} 个匹配 '{keyword}' 的结果")
        else:
            self.search_toolbar.update_status(0, 0, keyword)
            self.update_status(f"未找到匹配 '{keyword}' 的卡片")

    def _on_navigation_updated(self, current_index, total_results):
        """导航更新"""
        current_text = self.search_toolbar.search_input.text()
        self.search_toolbar.update_status(current_index, total_results, current_text)

    def _handle_generation_error(self, error_msg):
        """处理生成错误"""
        self.input_panel.enable_generate_button(True)
        self._show_message(False, f"AI卡片生成失败:\n{error_msg}")

    # 工具方法
    def _focus_card(self, card):
        """聚焦到卡片"""
        view = self.mindmap_panel.mindmap_view
        view.centerOn(card)

    def _clear_canvas(self, confirm=True):
        """清空画布"""
        if confirm:
            reply = QMessageBox.question(self, "确认", "确定要清空画布吗？")
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.mindmap_panel.clear_canvas()
        self.mindmap_panel.clear_drawings()
        self.controller.card_id_counter = 0
        self.update_status("画布已清空")
    
    def _apply_layout(self):
        """应用布局算法（从工具栏）"""
        layout_name = self.main_toolbar.layout_combo.currentText() if self.main_toolbar else "mind_map"
        self.mindmap_panel.apply_layout(layout_name)
        # 更新连线系统的布局类型
        self.mindmap_panel.mindmap_scene.set_layout_type(layout_name)
        self.update_status(f"已应用布局: {layout_name}")
    
    def _apply_layout_from_menu(self, layout_name):
        """从菜单应用布局算法"""
        self.mindmap_panel.apply_layout(layout_name)
        # 更新连线系统的布局类型
        self.mindmap_panel.mindmap_scene.set_layout_type(layout_name)
        self.update_status(f"已应用布局: {layout_name}")
    
    def _change_connection_style(self, style):
        """切换连线样式"""
        self.mindmap_panel.mindmap_scene.set_connection_style(style)
        self.update_status(f"已切换连线样式: {style}")

    def _show_message(self, success, message):
        """显示消息"""
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)

    def setup_shortcuts(self):
        """设置快捷键"""
        # 快捷键已经在各个UI组件中设置
        # 这里可以添加全局快捷键
        pass

    def update_status(self, message):
        """更新状态栏"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"[{timestamp}] {message}")

    def _load_test_content(self):
        """加载测试内容"""
        test_markdown = r"""# LaTeX公式测试文档

这是一个测试文档，用于测试LaTeX公式渲染功能。

## 基本公式

### 行内公式
这是行内公式：$E=mc^2$，还有 $\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$。

### 块级公式

基本公式：
$$E = mc^2$$

积分公式：
$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

微分方程：
$$\frac{\partial u}{\partial t} = \alpha \nabla^2 u$$

泰勒级数：
$$f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n$$

## 复杂公式

### 矩阵
$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
$$

### 量子力学公式
$$\mathcal{L} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi$$

### 你的公式（修正版）
$$H=\varepsilon_{0,\mathbf{k}}+t_{x,\mathbf{k}}\tau_{x}+t_{z,\mathbf{k}}\tau_{z}+\tau_{y}\vec{\lambda}_{\mathbf{k}}\cdot\vec{\sigma}+\tau_{z}\vec{J}\cdot\vec{\sigma}$$

**注意**：原公式中的 `\vec{\lambda}{\mathbf{k}}` 已修正为 `\vec{\lambda}_{\mathbf{k}}`，`\tau{z}` 已修正为 `\tau_{z}`。

## 其他测试

### 分数
$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

### 求和与积分
$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$

$$\int_{0}^{\infty} \frac{\sin(x)}{x} dx = \frac{\pi}{2}$$

### 偏微分
$$\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} = 0$$

## 测试说明

1. 所有公式应该正确渲染
2. 如果公式显示为原始LaTeX代码，说明MathJax未正确加载
3. 如果公式显示错误，检查公式语法是否正确

---
*测试文档 - 用于验证LaTeX公式渲染功能*
"""
        
        # 设置测试内容
        self.input_panel.set_file_content(test_markdown, "测试文档.md", "markdown")
        self.update_status("已加载测试内容")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 询问是否保存
        cards = self.mindmap_panel.get_all_cards()
        if cards:
            reply = QMessageBox.question(
                self,
                "保存确认",
                "是否保存当前的卡片数据？",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.controller.storage.save_cards(cards)
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        self.controller.cleanup()
        event.accept()
