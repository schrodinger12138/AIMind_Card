"""
Markdown预览组件 - 完全基于ReText的实现方式
使用 markups 库进行转换，使用 QWebEngineView 显示
"""
import os
from pathlib import Path

# 尝试导入QWebEngineView
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl, QDir, pyqtSignal
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    QWebEngineView = None

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
import re
from functools import lru_cache
import hashlib

# 尝试导入 markups 库（ReText 使用的方式）
try:
    import markups
    from markups import MarkdownMarkup
    HAS_MARKUPS = True
except ImportError:
    HAS_MARKUPS = False
    MarkdownMarkup = None


class MarkdownPreviewReText(QWidget):
    """
    Markdown预览组件 - 完全基于ReText的实现方式
    
    参考 ReText/ReText/tab.py 和 ReText/ReText/webenginepreview.py
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._markdown_text = ""
        self._fileName = None  # 文件路径，用于设置 baseUrl
        self._current_dir = QDir.currentPath()
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._delayed_update)
        self._pending_markdown = None
        
        if not HAS_WEBENGINE:
            self._show_error("QWebEngineView 未安装")
            return
        
        if not HAS_MARKUPS:
            self._show_error("markups 库未安装\n\n请安装: pip install Markups[markdown]")
            return
        
        self.init_ui()
    
    def _show_error(self, message):
        """显示错误信息"""
        layout = QVBoxLayout(self)
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: red; padding: 20px; font-size: 11px;")
        error_label.setWordWrap(True)
        layout.addWidget(error_label)
        self.web_view = None
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建WebEngineView（参考 ReTextWebEnginePreview）
        self.web_view = QWebEngineView()
        
        # 设置WebEngine设置（参考 ReTextWebEnginePreview.__init__）
        settings = self.web_view.settings()
        settings.setDefaultTextEncoding('utf-8')
        settings.setAttribute(
            settings.WebAttribute.LocalContentCanAccessRemoteUrls, 
            True
        )
        
        layout.addWidget(self.web_view)
        
        # 加载空页面
        self._load_html("")
    
    def _preprocess_math_formulas(self, markdown_text):
        """
        预处理数学公式：将 $...$ 转换为 \(...\)（行内公式）
        保留 $$...$$ 作为块级公式
        
        Args:
            markdown_text: 原始 Markdown 文本
            
        Returns:
            处理后的 Markdown 文本
        """
        if not markdown_text:
            return markdown_text
        
        # 先保护 $$...$$ 块级公式，避免被转换
        # 使用临时占位符
        block_placeholders = {}
        placeholder_counter = 0
        
        def replace_block(match):
            nonlocal placeholder_counter
            placeholder = f"__BLOCK_MATH_{placeholder_counter}__"
            block_placeholders[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder
        
        # 匹配 $$...$$（块级公式），但不匹配 $$$...$$$ 或更多 $
        # 使用负向前后查找确保不是 $$$ 的一部分
        text = re.sub(r'(?<!\$)\$\$(?!\$)([^\$]+?)\$\$(?!\$)', replace_block, markdown_text)
        
        # 现在转换 $...$ 为 \(...\)
        # 匹配单个 $...$，但要排除：
        # 1. 已经转义的 \$
        # 2. $$...$$ 块级公式（已经被占位符替换）
        def replace_inline(match):
            content = match.group(1)
            return f'\\({content}\\)'
        
        # 匹配 $...$，但排除：
        # - 前面有反斜杠的 \$（已转义）
        # - 前面或后面有另一个 $ 的（$$...$$ 块级公式）
        text = re.sub(r'(?<!\\)(?<!\$)\$([^\$\n]+?)\$(?!\$)', replace_inline, text)
        
        # 恢复块级公式占位符
        for placeholder, original in block_placeholders.items():
            text = text.replace(placeholder, original)
        
        return text
    
    def set_markdown(self, markdown_text, file_path=None):
        """
        设置Markdown内容并渲染（延迟渲染优化）
        
        Args:
            markdown_text: Markdown文本内容
            file_path: 文件路径（可选，用于设置baseUrl和解析相对路径）
        """
        self._markdown_text = markdown_text
        self._fileName = file_path
        
        if file_path:
            self._current_dir = os.path.dirname(os.path.abspath(file_path))
        else:
            self._current_dir = QDir.currentPath()
        
        # 延迟渲染：停止之前的定时器，重新开始
        self._update_timer.stop()
        self._pending_markdown = markdown_text
        # 延迟500ms渲染，避免频繁更新
        self._update_timer.start(500)
    
    def _delayed_update(self):
        """延迟更新预览"""
        if self._pending_markdown is not None:
            # 转换Markdown为HTML（参考 ReText 的方式）
            html_content = self._convert_markdown_to_html(self._pending_markdown)
            self._load_html(html_content)
            self._pending_markdown = None
    
    @lru_cache(maxsize=32)
    def _convert_markdown_to_html_cached(self, markdown_hash, file_path_hash):
        """
        缓存的Markdown转换（使用哈希值作为键）
        """
        # 这里不应该被直接调用，应该通过 _convert_markdown_to_html
        pass
    
    def _convert_markdown_to_html(self, markdown_text):
        """
        将Markdown转换为HTML（完全按照ReText的方式，带缓存优化）
        
        参考 ReText/ReText/tab.py 的 getHtmlFromConverted 方法
        """
        if not markdown_text:
            return self._get_empty_html()
        
        # 计算缓存键
        markdown_hash = hashlib.md5(markdown_text.encode('utf-8')).hexdigest()
        file_path_hash = hashlib.md5(str(self._fileName or '').encode('utf-8')).hexdigest()
        cache_key = (markdown_hash, file_path_hash)
        
        # 检查缓存（使用简单的字典缓存）
        if not hasattr(self, '_html_cache'):
            self._html_cache = {}
        
        if cache_key in self._html_cache:
            return self._html_cache[cache_key]
        
        try:
            # 预处理：将 $...$ 转换为 \(...\)（行内公式）
            # 但保留 $$...$$ 作为块级公式
            processed_text = self._preprocess_math_formulas(markdown_text)
            
            # 使用 markups 库转换（参考 ReText/converterprocess.py）
            markup = MarkdownMarkup(filename=self._fileName)
            converted = markup.convert(processed_text)
            
            # 获取完整的HTML（参考 ReText/tab.py getHtmlFromConverted）
            # 参考 ReText/tab.py 第176-202行的实现
            headers = ''
            # 添加基本样式（参考 ReText/tab.py 第192-195行）
            style = 'td, th { border: 1px solid #c3c3c3; padding: 0 3px 0 3px; }\n'
            style += 'table { border-collapse: collapse; }\n'
            style += 'img { max-width: 100%; }\n'
            # 优化MathJax加载：延迟渲染
            style += 'script[type="text/x-mathjax-config"] { display: none; }\n'
            headers += '<style type="text/css">\n' + style + '</style>\n'
            # 添加MathJax延迟渲染配置
            mathjax_config = '''
            <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
                tex2jax: {inlineMath: [['$','$'], ['\\\\(','\\\\)']]},
                skipStartupTypeset: true
            });
            </script>
            '''
            headers += mathjax_config
            
            # 获取完整的HTML（参考 ReText/tab.py 第200-202行）
            html = converted.get_whole_html(
                custom_headers=headers,  # 自定义头部（包含样式）
                include_stylesheet=True,  # 包含样式表
                fallback_title='Markdown Preview',  # 默认标题
                webenv=True  # Web环境模式
            )
            
            # 添加延迟渲染脚本
            html = html.replace('</body>', '''
            <script>
            // 延迟渲染MathJax
            if (typeof MathJax !== 'undefined') {
                setTimeout(function() {
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
                }, 100);
            }
            </script>
            </body>''')
            
            # 缓存结果（限制缓存大小）
            if len(self._html_cache) > 50:
                # 删除最旧的缓存项
                oldest_key = next(iter(self._html_cache))
                del self._html_cache[oldest_key]
            self._html_cache[cache_key] = html
            
            return html
            
        except Exception as e:
            # 如果转换失败，返回错误信息
            import traceback
            error_detail = traceback.format_exc()
            error_html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>转换错误</title>
            </head>
            <body>
                <p style="color: red; font-weight: bold;">Markdown转换失败</p>
                <p style="color: #666;">错误信息: {str(e)}</p>
                <p style="color: #666;">请确保已安装 markups 库: pip install Markups[markdown]</p>
                <details>
                    <summary>详细错误信息</summary>
                    <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">{error_detail}</pre>
                </details>
            </body>
            </html>
            """
            return error_html
    
    def _get_empty_html(self):
        """返回空的HTML文档"""
        return """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Markdown Preview</title>
        </head>
        <body>
            <p style="color: #888;">等待输入Markdown内容...</p>
        </body>
        </html>
        """
    
    def _load_html(self, html_content):
        """
        加载HTML内容到WebEngineView
        
        参考 ReText/ReText/tab.py 的 updatePreviewBox 方法
        """
        if not self.web_view:
            return
        
        # 设置字体（参考 ReText/tab.py updatePreviewBox）
        # 这里可以设置预览字体，暂时使用默认
        
        # 设置HTML内容（参考 ReText/tab.py updatePreviewBox）
        # 重要：必须提供 baseUrl，否则 QWebView 会拒绝显示图片等外部对象
        if self._fileName:
            baseUrl = QUrl.fromLocalFile(self._fileName)
        else:
            baseUrl = QUrl.fromLocalFile(self._current_dir)
        
        # 使用 setHtml 方法（参考 ReText/tab.py 第254行）
        self.web_view.setHtml(html_content, baseUrl)
    
    def set_file_path(self, file_path):
        """
        设置文件路径（用于更新baseUrl）
        
        Args:
            file_path: 文件路径
        """
        self._fileName = file_path
        if file_path:
            self._current_dir = os.path.dirname(os.path.abspath(file_path))
        else:
            self._current_dir = QDir.currentPath()
        
        # 如果已有内容，重新加载以更新baseUrl
        if self._markdown_text:
            html_content = self._convert_markdown_to_html(self._markdown_text)
            self._load_html(html_content)
    
    def get_plain_text(self):
        """获取当前Markdown文本"""
        return self._markdown_text
    
    def set_font(self, font):
        """
        设置预览字体
        
        参考 ReText/ReText/webenginepreview.py 的 setFont 方法
        """
        if not self.web_view:
            return
        
        settings = self.web_view.settings()
        settings.setFontFamily(
            settings.FontFamily.StandardFont,
            font.family()
        )
        from PyQt6.QtGui import QFontInfo
        settings.setFontSize(
            settings.FontSize.DefaultFontSize,
            QFontInfo(font).pixelSize()
        )

