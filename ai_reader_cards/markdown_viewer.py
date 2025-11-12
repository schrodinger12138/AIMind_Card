"""Markdown查看器 - 支持公式显示"""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument, QTextCharFormat, QTextCursor
import re


class MarkdownViewer(QTextEdit):
    """支持Markdown和数学公式的文本查看器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)  # 允许编辑以便复制文本
        self.setAcceptRichText(True)
        self._plain_text = ""  # 保存原始纯文本
        # 启用HTML渲染以支持公式
        self.setHtml("")
    
    def set_markdown_content(self, markdown_text):
        """设置Markdown内容并渲染"""
        self._plain_text = markdown_text  # 保存原始文本
        html_content = self._markdown_to_html(markdown_text)
        self.setHtml(html_content)
    
    def toPlainText(self):
        """获取纯文本内容"""
        return self._plain_text
    
    def _markdown_to_html(self, markdown_text):
        """将Markdown转换为HTML（支持数学公式）"""
        if not markdown_text:
            return ""
        
        html = markdown_text
        
        # 处理行内数学公式 $...$
        html = re.sub(
            r'\$([^$]+)\$',
            r'<span style="font-family: \'Times New Roman\', serif; font-style: italic;">\1</span>',
            html
        )
        
        # 处理块级数学公式 $$...$$
        html = re.sub(
            r'\$\$([^$]+)\$\$',
            r'<div style="text-align: center; margin: 10px 0; font-family: \'Times New Roman\', serif; font-size: 14px;">\1</div>',
            html,
            flags=re.DOTALL
        )
        
        # 处理LaTeX公式（更完整的支持）
        # 行内公式 \(...\) 或 $...$
        html = re.sub(
            r'\\?\(([^)]+)\\?\)',
            r'<span style="font-family: \'Times New Roman\', serif; font-style: italic;">\1</span>',
            html
        )
        
        # 块级公式 \[...\] 或 $$...$$
        html = re.sub(
            r'\\?\[([^\]]+)\\?\]',
            r'<div style="text-align: center; margin: 10px 0; font-family: \'Times New Roman\', serif; font-size: 14px;">\1</div>',
            html,
            flags=re.DOTALL
        )
        
        # 处理标题
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 处理粗体 **text** 或 __text__
        html = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'__([^_]+)__', r'<b>\1</b>', html)
        
        # 处理斜体 *text* 或 _text_
        html = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', html)
        html = re.sub(r'_([^_]+)_', r'<i>\1</i>', html)
        
        # 处理代码块 ```
        html = re.sub(
            r'```([^`]+)```',
            r'<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace;">\1</pre>',
            html,
            flags=re.DOTALL
        )
        
        # 处理行内代码 `code`
        html = re.sub(
            r'`([^`]+)`',
            r'<code style="background-color: #f5f5f5; padding: 2px 4px; border-radius: 2px; font-family: monospace;">\1</code>',
            html
        )
        
        # 处理链接 [text](url)
        html = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" style="color: #0066cc;">\1</a>',
            html
        )
        
        # 处理换行（将单个换行转换为<br>，双换行转换为段落）
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = re.sub(r'\n', '<br>', html)
        html = '<p>' + html + '</p>'
        
        # 包装在HTML文档中
        full_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.6;
                    padding: 10px;
                }}
                h1 {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                h2 {{ font-size: 20px; font-weight: bold; margin: 8px 0; }}
                h3 {{ font-size: 16px; font-weight: bold; margin: 6px 0; }}
                code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 2px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return full_html
    
    def set_plain_text(self, text):
        """设置纯文本（兼容原有接口）"""
        self._plain_text = text
        self.setPlainText(text)
    
    def setPlainText(self, text):
        """设置纯文本"""
        self._plain_text = text
        super().setPlainText(text)

