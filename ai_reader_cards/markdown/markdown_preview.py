"""Markdown预览组件 - 基于QWebEngineView，支持MathJax公式渲染"""
import os
import re
import base64
from io import BytesIO
from pathlib import Path

# 尝试导入QWebEngineView
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl, pyqtSignal
    HAS_WEBENGINE = True
    WEBENGINE_ERROR = None
except ImportError as e:
    HAS_WEBENGINE = False
    QWebEngineView = None
    WEBENGINE_ERROR = str(e)
except Exception as e:
    # 捕获其他可能的错误（如缺少依赖）
    HAS_WEBENGINE = False
    QWebEngineView = None
    WEBENGINE_ERROR = f"导入错误: {type(e).__name__}: {str(e)}"

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer

# 尝试导入Markdown库
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# 尝试导入Pygments
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

# 尝试导入Matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # 使用非交互式后端
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# 尝试导入Pillow
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class MarkdownPreview(QWidget):
    """Markdown预览组件 - 使用QWebEngineView渲染HTML"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._markdown_text = ""
        self._base_path = None  # 用于解析相对路径图片
        
        if not HAS_WEBENGINE:
            # 如果没有QWebEngineView，显示错误信息
            layout = QVBoxLayout(self)
            error_msg = (
                "QWebEngineView 未安装或导入失败。\n\n"
                "请安装 PyQt6-WebEngine:\n"
                "  pip install PyQt6-WebEngine\n"
                "或使用 conda:\n"
                "  conda install -c conda-forge pyqtwebengine\n\n"
            )
            if WEBENGINE_ERROR:
                error_msg += f"错误详情: {WEBENGINE_ERROR}\n\n"
            error_msg += (
                "提示: 如果已安装但仍显示此错误，请确认：\n"
                "1. 使用的是正确的Python环境（conda环境）\n"
                "2. 已重启应用程序\n"
                "3. PyQt6和PyQt6-WebEngine版本兼容"
            )
            error_label = QLabel(error_msg)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; padding: 20px; font-size: 11px;")
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
            self.web_view = None
            return
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建WebEngineView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # 加载空页面
        self._load_html("")
    
    def set_markdown(self, markdown_text, base_path=None):
        """设置Markdown内容并渲染"""
        self._markdown_text = markdown_text
        self._base_path = base_path
        
        html_content = self._markdown_to_html(markdown_text)
        self._load_html(html_content)
    
    def _markdown_to_html(self, markdown_text):
        """将Markdown转换为HTML（支持MathJax）"""
        if not markdown_text:
            return self._create_html_template("")
        
        # 处理图片路径（包括base64图片）
        markdown_text = self._process_images(markdown_text)
        
        # 保护代码块（避免处理代码中的$符号）
        code_blocks = []
        def protect_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        # 先保护代码块
        protected_text = re.sub(r'```[\s\S]*?```', protect_code, markdown_text)
        protected_text = re.sub(r'`[^`]+`', protect_code, protected_text)
        
        # 转换Markdown为HTML（公式会保留为$$...$$格式）
        if HAS_MARKDOWN:
            html_content = self._convert_with_markdown(protected_text)
        else:
            html_content = self._convert_simple(protected_text)
        
        # 恢复代码块
        for i, code in enumerate(code_blocks):
            html_content = html_content.replace(f"__CODE_BLOCK_{i}__", code)
        
        # 处理LaTeX公式（在HTML中直接处理，参考afdaf.py）
        html_content = self._process_math_in_html(html_content)
        
        return self._create_html_template(html_content)
    
    def _process_images(self, markdown_text):
        """处理图片路径和base64图片"""
        # 处理base64图片（已处理，直接返回）
        # 处理相对路径图片
        if self._base_path:
            def replace_image_path(match):
                alt_text = match.group(1)
                img_path = match.group(2)
                
                # 如果是base64图片，直接返回
                if img_path.startswith('data:image'):
                    return match.group(0)
                
                # 处理相对路径
                if not os.path.isabs(img_path):
                    if self._base_path:
                        full_path = os.path.join(os.path.dirname(self._base_path), img_path)
                        if os.path.exists(full_path):
                            # 转换为file:// URL
                            abs_path = os.path.abspath(full_path)
                            try:
                                from PyQt6.QtCore import QUrl
                                img_path = QUrl.fromLocalFile(abs_path).toString()
                            except ImportError:
                                # 如果QUrl不可用，使用file://协议
                                img_path = f"file:///{abs_path.replace(os.sep, '/')}"
                
                return f'![{alt_text}]({img_path})'
            
            markdown_text = re.sub(
                r'!\[([^\]]*)\]\(([^)]+)\)',
                replace_image_path,
                markdown_text
            )
        
        return markdown_text
    
    def _process_math_in_html(self, html_content):
        """在HTML中直接处理LaTeX公式（参考afdaf.py的简单方法）"""
        # 保护代码块中的内容
        code_blocks = []
        def protect_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        html_content = re.sub(r'<pre>[\s\S]*?</pre>', protect_code, html_content, flags=re.DOTALL)
        html_content = re.sub(r'<code[^>]*>[\s\S]*?</code>', protect_code, html_content, flags=re.DOTALL)
        
        # 处理被HTML转义的$符号
        html_content = html_content.replace('&amp;#36;', '$')
        html_content = html_content.replace('&#36;', '$')
        
        def process_display_math(match):
            """处理块级公式 $$...$$"""
            math_content = match.group(1).strip()
            # 移除可能被Markdown添加的<p>标签和多余的空白
            math_content = re.sub(r'^<p[^>]*>|</p>$', '', math_content, flags=re.IGNORECASE).strip()
            # 清理HTML实体
            math_content = math_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            return f'<div class="math-display">$${math_content}$$</div>'
        
        # 先处理块级公式 $$...$$（支持多行）
        # 匹配可能被包装的块级公式
        html_content = re.sub(
            r'<p[^>]*>\s*\$\$([\s\S]*?)\$\$\s*</p>',
            process_display_math,
            html_content,
            flags=re.DOTALL
        )
        # 匹配未包装的块级公式
        html_content = re.sub(
            r'(?<!<div[^>]*>)\$\$([\s\S]*?)\$\$(?!</div>)',
            lambda m: f'<div class="math-display">$${m.group(1).strip()}$$</div>',
            html_content,
            flags=re.DOTALL
        )
        
        def process_inline_math(match):
            """处理行内公式 $...$"""
            math_content = match.group(1).strip()
            # 清理HTML实体
            math_content = math_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            return f'<span class="math-inline">${math_content}$</span>'
        
        # 处理行内公式 $...$（不在代码块和已处理的块级公式中）
        # 避免匹配已经被处理的公式和代码块
        html_content = re.sub(
            r'(?<!<span[^>]*>)(?<!<div[^>]*>)(?<!\$)\$(?!\$)([^$\n<]+?)\$(?!\$)(?!</span>)(?!</div>)',
            process_inline_math,
            html_content
        )
        
        # 恢复代码块
        for i, code in enumerate(code_blocks):
            html_content = html_content.replace(f"__CODE_BLOCK_{i}__", code)
        
        return html_content
    
    def _get_mathjax_script(self):
        """获取MathJax脚本（使用MathJax 2.7.7，参考afdaf.py的成功实现）"""
        # 使用MathJax 2.7.7（与afdaf.py保持一致，确保兼容性）
        return '''<script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>'''
    
    def _convert_with_markdown(self, markdown_text):
        """使用markdown库转换"""
        extensions = [
            'codehilite',
            'fenced_code',
            'tables',
            'toc',
            'nl2br',
            'sane_lists',
        ]
        
        md = markdown.Markdown(extensions=extensions, extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': HAS_PYGMENTS,
            }
        })
        
        html_content = md.convert(markdown_text)
        
        # 处理Obsidian特性
        html_content = self._process_obsidian_features(html_content, markdown_text)
        
        return html_content
    
    def _convert_simple(self, markdown_text):
        """简单Markdown转换（不使用库）"""
        html = markdown_text
        
        # 处理标题
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        
        # 处理代码块
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            lambda m: f'<pre><code class="language-{m.group(1) or ""}">{m.group(2)}</code></pre>',
            html,
            flags=re.DOTALL
        )
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # 处理链接
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # 处理图片
        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html)
        
        # 处理列表
        html = self._process_lists_simple(html)
        
        # 处理表格
        html = self._process_tables_simple(html)
        
        # 处理引用
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # 处理分割线
        html = re.sub(r'^---+\s*$', '<hr>', html, flags=re.MULTILINE)
        
        return html
    
    def _process_lists_simple(self, html):
        """处理列表"""
        lines = html.split('\n')
        result = []
        in_list = False
        list_type = None
        
        for line in lines:
            # 任务列表
            task_match = re.match(r'^[-*+]\s+\[([ xX])\]\s+(.+)$', line)
            if task_match:
                checked = task_match.group(1).lower() == 'x'
                content = task_match.group(2)
                checked_attr = 'checked' if checked else ''
                checkbox = f'<input type="checkbox" class="task-checkbox" {checked_attr} disabled>'
                if not in_list or list_type != 'ul':
                    if in_list:
                        result.append('</ol>' if list_type == 'ol' else '</ul>')
                    result.append('<ul class="task-list">')
                    in_list = True
                    list_type = 'ul'
                result.append(f'<li class="task-list-item">{checkbox} {content}</li>')
            # 有序列表
            elif re.match(r'^\d+\.\s+', line):
                if not in_list or list_type != 'ol':
                    if in_list:
                        result.append('</ul>' if list_type == 'ul' else '</ol>')
                    result.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                content = re.sub(r'^\d+\.\s+', '', line)
                result.append(f'<li>{content}</li>')
            # 无序列表
            elif re.match(r'^[-*+]\s+', line):
                if not in_list or list_type != 'ul':
                    if in_list:
                        result.append('</ol>' if list_type == 'ol' else '</ul>')
                    result.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                content = re.sub(r'^[-*+]\s+', '', line)
                result.append(f'<li>{content}</li>')
            else:
                if in_list:
                    result.append('</ol>' if list_type == 'ol' else '</ul>')
                    in_list = False
                    list_type = None
                result.append(line)
        
        if in_list:
            result.append('</ol>' if list_type == 'ol' else '</ul>')
        
        return '\n'.join(result)
    
    def _process_tables_simple(self, html):
        """处理表格"""
        lines = html.split('\n')
        result = []
        in_table = False
        header_processed = False
        
        for line in lines:
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    result.append('<table class="markdown-table">')
                    in_table = True
                    header_processed = False
                
                if re.match(r'^\|[\s\-:]+\|$', line.strip()):
                    header_processed = True
                    continue
                
                cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                tag = 'th' if not header_processed else 'td'
                row_html = '<tr>' + ''.join([f'<{tag}>{cell}</{tag}>' for cell in cells]) + '</tr>'
                result.append(row_html)
                
                if not header_processed:
                    header_processed = True
            else:
                if in_table:
                    result.append('</table>')
                    in_table = False
                    header_processed = False
                result.append(line)
        
        if in_table:
            result.append('</table>')
        
        return '\n'.join(result)
    
    def _process_obsidian_features(self, html_content, original_text):
        """处理Obsidian特有语法"""
        # 内部链接
        html_content = re.sub(
            r'\[\[([^\]]+)\]\]',
            lambda m: f'<a href="#{m.group(1)}" class="internal-link">{m.group(1)}</a>',
            html_content
        )
        
        # 标签
        code_blocks = []
        def protect_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        html_content = re.sub(r'<pre>[\s\S]*?</pre>', protect_code, html_content)
        html_content = re.sub(r'<code[^>]*>[\s\S]*?</code>', protect_code, html_content)
        
        html_content = re.sub(
            r'#([a-zA-Z0-9_\-/]+)',
            lambda m: f'<span class="tag">#{m.group(1)}</span>',
            html_content
        )
        
        for i, code in enumerate(code_blocks):
            html_content = html_content.replace(f"__CODE_BLOCK_{i}__", code)
        
        # 删除线
        html_content = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', html_content)
        
        # 高亮
        html_content = re.sub(r'==([^=]+)==', r'<mark class="highlight">\1</mark>', html_content)
        
        return html_content
    
    def _create_html_template(self, content):
        """创建完整的HTML模板（包含MathJax）"""
        # Pygments样式
        code_style = ""
        if HAS_PYGMENTS:
            formatter = HtmlFormatter(style='monokai', noclasses=False)
            code_style = f"<style>{formatter.get_style_defs('.highlight')}</style>"
        
        # 尝试使用本地MathJax，如果不存在则使用CDN
        mathjax_script = self._get_mathjax_script()
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Preview</title>
    
    <!-- MathJax 2.7.7 (参考afdaf.py的成功实现) -->
    {mathjax_script}
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
            font-size: 15px;
            line-height: 1.7;
            padding: 20px 40px;
            color: #dcddde;
            background-color: #1e1e1e;
            max-width: 900px;
            margin: 0 auto;
        }}
        
        h1 {{ font-size: 2em; font-weight: 700; margin: 1.2em 0 0.8em 0; border-bottom: 2px solid #3a3a3a; padding-bottom: 0.5em; color: #ffffff; }}
        h2 {{ font-size: 1.6em; font-weight: 600; margin: 1em 0 0.6em 0; border-bottom: 1px solid #3a3a3a; padding-bottom: 0.4em; color: #ffffff; }}
        h3 {{ font-size: 1.3em; font-weight: 600; margin: 0.9em 0 0.5em 0; color: #ffffff; }}
        h4 {{ font-size: 1.15em; font-weight: 600; margin: 0.8em 0 0.4em 0; color: #ffffff; }}
        h5 {{ font-size: 1.05em; font-weight: 600; margin: 0.7em 0 0.3em 0; color: #e0e0e0; }}
        h6 {{ font-size: 1em; font-weight: 600; margin: 0.6em 0 0.3em 0; color: #d0d0d0; }}
        
        code {{
            background-color: #2d2d2d;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: #e06c75;
            border: 1px solid #3a3a3a;
        }}
        
        pre {{
            background-color: #2d2d2d;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #3a3a3a;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #abb2bf;
            border: none;
        }}
        
        a {{
            color: #7aa2f7;
            text-decoration: none;
            border-bottom: 1px solid #7aa2f7;
        }}
        
        a:hover {{
            color: #9ab8ff;
            border-bottom-color: #9ab8ff;
        }}
        
        a.internal-link {{
            color: #bb9af7;
            border-bottom: 1px solid #bb9af7;
            font-weight: 500;
        }}
        
        ul, ol {{
            margin: 0.8em 0;
            padding-left: 2em;
        }}
        
        li {{
            margin: 0.4em 0;
            line-height: 1.7;
        }}
        
        li.task-list-item {{
            list-style: none;
            margin-left: -1.5em;
        }}
        
        table.markdown-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.2em 0;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        table.markdown-table th {{
            background-color: #2d2d2d;
            font-weight: 600;
            padding: 12px;
            text-align: left;
            border: 1px solid #3a3a3a;
            color: #ffffff;
        }}
        
        table.markdown-table td {{
            padding: 12px;
            border: 1px solid #3a3a3a;
        }}
        
        table.markdown-table tr:nth-child(even) {{
            background-color: #252525;
        }}
        
        blockquote {{
            border-left: 4px solid #7aa2f7;
            margin: 1.2em 0;
            padding: 0.8em 1.2em;
            background-color: #2a2a2a;
            color: #a0a0a0;
            font-style: italic;
            border-radius: 0 4px 4px 0;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #3a3a3a;
            margin: 2em 0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            margin: 1.2em 0;
            display: block;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }}
        
        .tag {{
            background-color: #2d2d2d;
            color: #7aa2f7;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: 500;
            border: 1px solid #3a3a3a;
            margin: 0 2px;
        }}
        
        mark.highlight {{
            background-color: #ffd700;
            color: #000;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        
        del {{
            text-decoration: line-through;
            color: #888;
            opacity: 0.7;
        }}
        
        /* MathJax样式调整 */
        .MathJax {{
            color: #dcddde !important;
        }}
        
        .math-display {{
            margin: 1.5em 0;
            text-align: center;
            overflow-x: auto;
        }}
        
        .math-inline {{
            display: inline;
        }}
        
        /* 确保MathJax渲染的公式可见 */
        .MathJax_SVG, .MathJax_SVG_Display {{
            max-width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
        }}
    </style>
    {code_style}
</head>
<body>
    {content}
    <script>
        // MathJax 2.7.7 渲染方式（参考afdaf.py的成功实现）
        if (typeof MathJax !== 'undefined') {{
            MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
        }} else {{
            // 如果MathJax还未加载，等待加载完成后再渲染
            window.addEventListener('load', function() {{
                if (typeof MathJax !== 'undefined') {{
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
                }}
            }});
        }}
    </script>
</body>
</html>"""
        return html
    
    def _load_html(self, html_content):
        """加载HTML内容到WebEngineView"""
        if not self.web_view:
            return
        
        # 使用data URL加载HTML
        html_data = html_content.encode('utf-8')
        data_url = f"data:text/html;charset=utf-8;base64,{base64.b64encode(html_data).decode('utf-8')}"
        self.web_view.setHtml(html_content, baseUrl=QUrl("file:///"))
        
        # 延迟触发MathJax渲染（确保MathJax已加载）
        # 参考afdaf.py的实现方式
        QTimer.singleShot(500, self._trigger_mathjax_render)
    
    def _trigger_mathjax_render(self):
        """触发MathJax渲染（MathJax 2.7.7方式）"""
        if not self.web_view:
            return
        
        # 使用JavaScript触发MathJax渲染
        js_code = """
        if (typeof MathJax !== 'undefined' && MathJax.Hub) {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
        } else {
            // 如果MathJax还未加载，等待一段时间后重试
            setTimeout(function() {
                if (typeof MathJax !== 'undefined' && MathJax.Hub) {
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
                }
            }, 1000);
        }
        """
        self.web_view.page().runJavaScript(js_code)
    
    def export_to_html(self, filepath):
        """导出为HTML文件"""
        html_content = self._markdown_to_html(self._markdown_text)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"导出HTML失败: {e}")
            return False
    
    def export_to_pdf(self, filepath):
        """导出为PDF文件"""
        try:
            # 尝试使用weasyprint
            try:
                import weasyprint
                html_content = self._markdown_to_html(self._markdown_text)
                weasyprint.HTML(string=html_content).write_pdf(filepath)
                return True
            except ImportError:
                pass
            
            # 尝试使用pypandoc
            try:
                import pypandoc
                pypandoc.convert_file(
                    self._markdown_text,
                    'pdf',
                    format='markdown',
                    outputfile=filepath
                )
                return True
            except ImportError:
                pass
            
            # 如果都没有，使用QWebEngineView的打印功能
            if self.web_view:
                # 需要异步处理
                def print_to_pdf():
                    self.web_view.printToPdf(filepath)
                
                QTimer.singleShot(1000, print_to_pdf)
                return True
            
            return False
        except Exception as e:
            print(f"导出PDF失败: {e}")
            return False


def plot_to_base64(fig=None):
    """将Matplotlib图表转换为base64字符串"""
    if not HAS_MATPLOTLIB:
        return None
    
    if fig is None:
        fig = plt.gcf()
    
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    return f"data:image/png;base64,{data}"


def create_chart_markdown(x_data, y_data, title="Chart", xlabel="X", ylabel="Y"):
    """创建包含图表的Markdown字符串"""
    if not HAS_MATPLOTLIB:
        return ""
    
    plt.figure(figsize=(8, 6))
    plt.plot(x_data, y_data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    
    img_data = plot_to_base64()
    plt.close()
    
    if img_data:
        return f"![{title}]({img_data})"
    return ""

