"""设置对话框 - API密钥和代理配置"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QComboBox, QTextEdit, QGroupBox,
    QMessageBox, QTabWidget, QWidget, QFormLayout, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from ai_reader_cards.config_manager import get_config_manager

# 导入配置
try:
    from ai_reader_cards.config import COMMON_PROXIES, AVAILABLE_MODELS
except ImportError:
    COMMON_PROXIES = {}
    AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]


class SettingsDialog(QDialog):
    """设置对话框"""
    
    settings_saved = pyqtSignal()  # 设置保存信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.config = get_config_manager()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tabs = QTabWidget()
        
        # API设置选项卡
        api_tab = self.create_api_tab()
        tabs.addTab(api_tab, "API设置")
        
        # 代理设置选项卡
        proxy_tab = self.create_proxy_tab()
        tabs.addTab(proxy_tab, "代理设置")
        
        # 其他设置选项卡
        other_tab = self.create_other_tab()
        tabs.addTab(other_tab, "其他设置")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_api_tab(self):
        """创建API设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # OpenAI API密钥
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入OpenAI API密钥或从环境变量读取")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("OpenAI API密钥:", self.api_key_edit)
        
        # API Base URL
        self.api_base_edit = QLineEdit()
        self.api_base_edit.setPlaceholderText("https://api.chatanywhere.tech/v1")
        layout.addRow("OpenAI API Base URL:", self.api_base_edit)
        
        # DeepSeek API密钥
        self.deepseek_api_key_edit = QLineEdit()
        self.deepseek_api_key_edit.setPlaceholderText("输入DeepSeek API密钥（可选）")
        self.deepseek_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("DeepSeek API密钥:", self.deepseek_api_key_edit)
        
        # DeepSeek API Base URL
        self.deepseek_api_base_edit = QLineEdit()
        self.deepseek_api_base_edit.setPlaceholderText("https://api.deepseek.com/v1/chat/completions")
        layout.addRow("DeepSeek API Base URL:", self.deepseek_api_base_edit)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS)
        layout.addRow("默认模型:", self.model_combo)
        
        # 提示信息
        hint_label = QLabel(
            "提示：\n"
            "1. API密钥可以从环境变量 OPENAI_API_KEY 读取\n"
            "2. 如果留空，将使用环境变量中的值\n"
            "3. API Base URL 用于指定API服务地址"
        )
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addRow("", hint_label)
        
        return widget
    
    def create_proxy_tab(self):
        """创建代理设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 启用代理
        self.use_proxy_checkbox = QCheckBox("启用代理")
        self.use_proxy_checkbox.toggled.connect(self.on_proxy_enabled_changed)
        layout.addWidget(self.use_proxy_checkbox)
        
        # 常见代理配置
        common_group = QGroupBox("常见代理配置（可直接选择）")
        common_layout = QVBoxLayout()
        
        self.common_proxy_combo = QComboBox()
        self.common_proxy_combo.addItem("-- 选择常见配置 --", None)
        for key, proxy_info in COMMON_PROXIES.items():
            self.common_proxy_combo.addItem(proxy_info["name"], key)
        self.common_proxy_combo.currentIndexChanged.connect(self.on_common_proxy_selected)
        common_layout.addWidget(self.common_proxy_combo)
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        # 自定义代理配置
        custom_group = QGroupBox("自定义代理配置")
        custom_layout = QFormLayout()
        
        # HTTP代理
        self.http_proxy_edit = QLineEdit()
        self.http_proxy_edit.setPlaceholderText("例如: socks5h://localhost:11284 或 http://127.0.0.1:7890")
        custom_layout.addRow("HTTP代理:", self.http_proxy_edit)
        
        # HTTPS代理
        self.https_proxy_edit = QLineEdit()
        self.https_proxy_edit.setPlaceholderText("例如: socks5h://localhost:11284 或 http://127.0.0.1:7890")
        custom_layout.addRow("HTTPS代理:", self.https_proxy_edit)
        
        # 快速粘贴按钮
        paste_layout = QHBoxLayout()
        paste_btn = QPushButton("📋 粘贴代理配置")
        paste_btn.clicked.connect(self.paste_proxy_config)
        paste_layout.addWidget(paste_btn)
        paste_layout.addStretch()
        custom_layout.addRow("", paste_layout)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # 使用场景
        scenario_group = QGroupBox("代理使用场景")
        scenario_layout = QVBoxLayout()
        
        self.translate_checkbox = QCheckBox("翻译时使用代理")
        self.translate_checkbox.setChecked(True)
        scenario_layout.addWidget(self.translate_checkbox)
        
        self.api_checkbox = QCheckBox("API请求时使用代理")
        self.api_checkbox.setChecked(True)
        scenario_layout.addWidget(self.api_checkbox)
        
        scenario_group.setLayout(scenario_layout)
        layout.addWidget(scenario_group)
        
        # 提示信息
        hint_label = QLabel(
            "提示：\n"
            "1. 支持 socks5h:// 和 http:// 协议\n"
            "2. 可以直接粘贴完整的代理配置\n"
            "3. 格式: socks5h://localhost:11284 或 http://127.0.0.1:7890"
        )
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(hint_label)
        
        layout.addStretch()
        
        return widget
    
    def create_other_tab(self):
        """创建其他设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 翻译设置
        self.default_language_combo = QComboBox()
        self.default_language_combo.addItems(["中文 (zh)", "英文 (en)", "日文 (ja)", "韩文 (ko)"])
        layout.addRow("默认翻译语言:", self.default_language_combo)
        
        # 布局设置
        self.default_layout_combo = QComboBox()
        self.default_layout_combo.addItems(["mind_map", "logical", "timeline", "fishbone", "auto_arrange"])
        layout.addRow("默认布局:", self.default_layout_combo)
        
        # 连线样式
        self.default_connection_combo = QComboBox()
        self.default_connection_combo.addItems(["fixed", "bezier", "smart", "gradient"])
        layout.addRow("默认连线样式:", self.default_connection_combo)
        
        return widget
    
    def on_proxy_enabled_changed(self, enabled):
        """代理启用状态改变"""
        self.http_proxy_edit.setEnabled(enabled)
        self.https_proxy_edit.setEnabled(enabled)
        self.common_proxy_combo.setEnabled(enabled)
        self.translate_checkbox.setEnabled(enabled)
        self.api_checkbox.setEnabled(enabled)
    
    def on_common_proxy_selected(self, index):
        """选择常见代理配置"""
        if index > 0:
            proxy_key = self.common_proxy_combo.currentData()
            if proxy_key and proxy_key in COMMON_PROXIES:
                proxy_info = COMMON_PROXIES[proxy_key]
                self.http_proxy_edit.setText(proxy_info["http"])
                self.https_proxy_edit.setText(proxy_info["https"])
                self.use_proxy_checkbox.setChecked(True)
    
    def paste_proxy_config(self):
        """粘贴代理配置"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if text:
            # 尝试解析粘贴的文本
            # 支持格式: socks5h://localhost:11284 或 http://127.0.0.1:7890
            if "://" in text:
                # 如果包含协议，直接使用
                if "socks5h" in text or "socks5" in text:
                    self.http_proxy_edit.setText(text)
                    self.https_proxy_edit.setText(text)
                elif "http" in text:
                    self.http_proxy_edit.setText(text)
                    self.https_proxy_edit.setText(text)
                self.use_proxy_checkbox.setChecked(True)
                QMessageBox.information(self, "成功", "已粘贴代理配置")
            else:
                # 尝试作为端口号处理
                try:
                    port = int(text.strip())
                    proxy_url = f"socks5h://localhost:{port}"
                    self.http_proxy_edit.setText(proxy_url)
                    self.https_proxy_edit.setText(proxy_url)
                    self.use_proxy_checkbox.setChecked(True)
                    QMessageBox.information(self, "成功", f"已设置代理端口: {port}")
                except ValueError:
                    QMessageBox.warning(self, "提示", "无法识别代理配置格式，请手动输入")
    
    def load_settings(self):
        """加载设置"""
        # 加载API设置
        api_key = self.config.get("api.openai_api_key", "")
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        self.api_key_edit.setText(api_key)
        
        self.api_base_edit.setText(self.config.get("api.openai_base_url", "https://api.chatanywhere.tech/v1"))
        self.model_combo.setCurrentText(self.config.get("api.model", "gpt-3.5-turbo"))
        
        # 加载DeepSeek API设置
        deepseek_api_key = self.config.get("api.deepseek_api_key", "")
        if not deepseek_api_key:
            deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.deepseek_api_key_edit.setText(deepseek_api_key)
        self.deepseek_api_base_edit.setText(self.config.get("api.deepseek_base_url", "https://api.deepseek.com/v1/chat/completions"))
        
        # 加载代理设置
        use_proxy = self.config.get("proxy.use_proxy", False)
        self.use_proxy_checkbox.setChecked(use_proxy)
        
        proxies = self.config.get("proxy.proxies", {})
        self.http_proxy_edit.setText(proxies.get("http", "") or "")
        self.https_proxy_edit.setText(proxies.get("https", "") or "")
        
        when_to_use = self.config.get("proxy.when_to_use_proxy", [])
        self.translate_checkbox.setChecked("translate" in when_to_use)
        self.api_checkbox.setChecked("api_request" in when_to_use)
        
        # 加载其他设置
        default_lang = self.config.get("translation.default_target_language", "zh")
        lang_text = {"zh": "中文 (zh)", "en": "英文 (en)", "ja": "日文 (ja)", "ko": "韩文 (ko)"}.get(default_lang, "中文 (zh)")
        index = self.default_language_combo.findText(lang_text)
        if index >= 0:
            self.default_language_combo.setCurrentIndex(index)
        
        self.default_layout_combo.setCurrentText(self.config.get("layout.default", "mind_map"))
        self.default_connection_combo.setCurrentText(self.config.get("connection.default", "fixed"))
        
        # 更新UI状态
        self.on_proxy_enabled_changed(use_proxy)
    
    def save_settings(self):
        """保存设置"""
        # 保存API设置
        api_key = self.api_key_edit.text().strip()
        if api_key:
            self.config.set("api.openai_api_key", api_key)
        
        # 保存DeepSeek API设置
        deepseek_api_key = self.deepseek_api_key_edit.text().strip()
        if deepseek_api_key:
            self.config.set("api.deepseek_api_key", deepseek_api_key)
        
        deepseek_base_url = self.deepseek_api_base_edit.text().strip()
        if deepseek_base_url:
            self.config.set("api.deepseek_base_url", deepseek_base_url)
        
        api_base = self.api_base_edit.text().strip()
        if api_base:
            self.config.set("api.openai_base_url", api_base)
        
        self.config.set("api.model", self.model_combo.currentText())
        
        # 保存代理设置
        use_proxy = self.use_proxy_checkbox.isChecked()
        self.config.set("proxy.use_proxy", use_proxy)
        
        proxies = {
            "http": self.http_proxy_edit.text().strip() or None,
            "https": self.https_proxy_edit.text().strip() or None
        }
        self.config.set("proxy.proxies", proxies)
        
        when_to_use = []
        if self.translate_checkbox.isChecked():
            when_to_use.append("translate")
        if self.api_checkbox.isChecked():
            when_to_use.append("api_request")
        self.config.set("proxy.when_to_use_proxy", when_to_use)
        
        # 保存其他设置
        lang_code = self.default_language_combo.currentText().split("(")[1].split(")")[0]
        self.config.set("translation.default_target_language", lang_code)
        self.config.set("layout.default", self.default_layout_combo.currentText())
        self.config.set("connection.default", self.default_connection_combo.currentText())
        
        # 保存到文件
        self.config.save_config()
        
        # 发送信号
        self.settings_saved.emit()
        
        QMessageBox.information(self, "成功", "设置已保存")
        self.accept()

