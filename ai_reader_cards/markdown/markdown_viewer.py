"""Markdown查看器 - 支持公式显示和完整Markdown语法"""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument, QTextCharFormat, QTextCursor
import re
import html

# 尝试导入专业Markdown库
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# 尝试导入代码高亮库
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


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
        """将Markdown转换为HTML（支持数学公式和完整语法）"""
        if not markdown_text:
            return ""
        
        # 如果安装了markdown库，使用专业渲染
        if HAS_MARKDOWN:
            return self._markdown_to_html_professional(markdown_text)
        else:
            return self._markdown_to_html_simple(markdown_text)
    
    def _markdown_to_html_professional(self, markdown_text):
        """使用markdown库进行专业渲染"""
        # 配置Markdown扩展
        extensions = [
            'codehilite',  # 代码高亮
            'fenced_code',  # 围栏代码块
            'tables',  # 表格支持
            'toc',  # 目录
            'nl2br',  # 换行转<br>
            'sane_lists',  # 智能列表
        ]
        
        # 创建Markdown实例
        md = markdown.Markdown(extensions=extensions, extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': HAS_PYGMENTS,
            }
        })
        
        # 转换Markdown为HTML
        html_content = md.convert(markdown_text)
        
        # 处理Obsidian特有语法（在HTML转换后）
        html_content = self._process_obsidian_features(html_content, markdown_text)
        
        # 处理数学公式（在HTML转换后）
        html_content = self._process_math_formulas(html_content)
        
        # 包装在完整HTML文档中
        return self._wrap_html(html_content)
    
    def _markdown_to_html_simple(self, markdown_text):
        """简单Markdown渲染（不使用库）"""
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
        
        # 处理Obsidian特有语法
        html = self._process_obsidian_features(html, markdown_text)
        
        # 处理列表
        html = self._process_lists(html)
        
        # 处理表格
        html = self._process_tables(html)
        
        # 处理引用
        html = self._process_blockquotes(html)
        
        # 处理水平线
        html = re.sub(r'^---+\s*$', '<hr>', html, flags=re.MULTILINE)
        html = re.sub(r'^\*\*\*\s*$', '<hr>', html, flags=re.MULTILINE)
        
        # 处理换行（将单个换行转换为<br>，双换行转换为段落）
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = re.sub(r'\n', '<br>', html)
        html = '<p>' + html + '</p>'
        
        # 处理数学公式
        html = self._process_math_formulas(html)
        
        # 包装在HTML文档中
        return self._wrap_html(html)
    
    def _process_obsidian_features(self, html_content, original_text):
        """处理Obsidian特有语法"""
        # 1. 处理内部链接 [[链接]] 或 [[链接|显示文本]]
        def process_wikilink(match):
            link_content = match.group(1)
            if '|' in link_content:
                link, display = link_content.split('|', 1)
                return f'<a href="#{link}" class="internal-link" data-link="{link}">{display}</a>'
            else:
                return f'<a href="#{link_content}" class="internal-link" data-link="{link_content}">{link_content}</a>'
        
        html_content = re.sub(r'\[\[([^\]]+)\]\]', process_wikilink, html_content)
        
        # 2. 处理标签 #标签
        def process_tag(match):
            tag = match.group(1)
            return f'<span class="tag">#{tag}</span>'
        
        # 标签不能出现在代码块中，需要先保护代码块
        code_blocks = []
        def protect_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        html_content = re.sub(r'<pre>[\s\S]*?</pre>', protect_code, html_content)
        html_content = re.sub(r'<code[^>]*>[\s\S]*?</code>', protect_code, html_content)
        
        # 处理标签（不在代码中的）
        html_content = re.sub(r'#([a-zA-Z0-9_\-/]+)', process_tag, html_content)
        
        # 恢复代码块
        for i, code in enumerate(code_blocks):
            html_content = html_content.replace(f"__CODE_BLOCK_{i}__", code)
        
        # 3. 处理任务列表 - [ ] 和 - [x]
        def process_task_list(match):
            checked = match.group(1).lower() == 'x'
            content = match.group(2)
            checked_attr = 'checked' if checked else ''
            checkbox = f'<input type="checkbox" class="task-checkbox" {checked_attr} disabled>'
            return f'<li class="task-list-item">{checkbox} {content}</li>'
        
        html_content = re.sub(
            r'<li>\[([ xX])\]\s*(.*?)</li>',
            process_task_list,
            html_content
        )
        
        # 4. 处理脚注 [^1] 和 [^1]: 脚注内容
        footnotes = {}
        footnote_pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n\[\^|\n\n|$)'
        for match in re.finditer(footnote_pattern, original_text, re.MULTILINE | re.DOTALL):
            footnote_id = match.group(1)
            footnote_content = match.group(2).strip()
            footnotes[footnote_id] = footnote_content
        
        def process_footnote_ref(match):
            footnote_id = match.group(1)
            if footnote_id in footnotes:
                return f'<sup><a href="#footnote-{footnote_id}" class="footnote-ref" id="footnote-ref-{footnote_id}">[{footnote_id}]</a></sup>'
            return match.group(0)
        
        html_content = re.sub(r'\[\^(\d+)\]', process_footnote_ref, html_content)
        
        # 添加脚注列表
        if footnotes:
            footnote_html = '<div class="footnotes"><hr><ol>'
            for footnote_id, content in sorted(footnotes.items(), key=lambda x: int(x[0])):
                footnote_html += f'<li id="footnote-{footnote_id}">{html.escape(content)} <a href="#footnote-ref-{footnote_id}" class="footnote-backref">↩</a></li>'
            footnote_html += '</ol></div>'
            html_content += footnote_html
        
        # 5. 处理删除线 ~~text~~
        html_content = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', html_content)
        
        # 6. 处理高亮 ==text== (Obsidian特有)
        html_content = re.sub(r'==([^=]+)==', r'<mark class="highlight">\1</mark>', html_content)
        
        return html_content
    
    def _process_math_formulas(self, html_content):
        """处理数学公式"""
        # 处理行内数学公式 $...$（避免与代码冲突）
        # 先保护代码块中的$符号
        code_blocks = []
        def protect_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        html_content = re.sub(r'```[\s\S]*?```', protect_code, html_content)
        html_content = re.sub(r'`[^`]+`', protect_code, html_content)
        
        # 处理行内公式 $...$（非代码中的）
        # 支持多行公式，但限制在合理范围内
        html_content = re.sub(
            r'\$([^$]+?)\$',
            lambda m: f'<span class="math-inline">{html.escape(m.group(1))}</span>',
            html_content,
            flags=re.DOTALL
        )
        
        # 处理块级公式 $$...$$
        html_content = re.sub(
            r'\$\$([\s\S]*?)\$\$',
            lambda m: f'<div class="math-block">{html.escape(m.group(1).strip())}</div>',
            html_content
        )
        
        # 处理LaTeX公式（支持更复杂的格式，如\gamma{mn}）
        # 处理行内公式 \(...\) 和 $...$
        html_content = re.sub(
            r'\\?\(([^)]+)\\?\)',
            lambda m: f'<span class="math-inline">{html.escape(m.group(1))}</span>',
            html_content
        )
        html_content = re.sub(
            r'\\?\[([\s\S]*?)\\?\]',
            lambda m: f'<div class="math-block">{html.escape(m.group(1).strip())}</div>',
            html_content
        )
        
        # 处理带花括号的LaTeX命令，如 \gamma{mn} = -\gamma{nm}
        # 这些已经在之前的$...$处理中包含了，但需要确保正确转义
        
        # 恢复代码块
        for i, code in enumerate(code_blocks):
            html_content = html_content.replace(f"__CODE_BLOCK_{i}__", code)
        
        return html_content
    
    def _process_lists(self, html_content):
        """处理列表（包括任务列表）"""
        lines = html_content.split('\n')
        result = []
        in_list = False
        list_type = None
        
        for line in lines:
            # 任务列表 - [ ] 或 - [x]
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
    
    def _process_tables(self, html_content):
        """处理表格"""
        lines = html_content.split('\n')
        result = []
        in_table = False
        header_processed = False
        
        for i, line in enumerate(lines):
            # 检测表格行（包含|）
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    result.append('<table class="markdown-table">')
                    in_table = True
                    header_processed = False
                
                # 检测分隔行（---）
                if re.match(r'^\|[\s\-:]+\|$', line.strip()):
                    header_processed = True
                    continue
                
                # 处理表格行
                cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                tag = 'th' if not header_processed else 'td'
                row_html = '<tr>' + ''.join([f'<{tag}>{html.escape(cell)}</{tag}>' for cell in cells]) + '</tr>'
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
    
    def _process_blockquotes(self, html_content):
        """处理引用块"""
        lines = html_content.split('\n')
        result = []
        in_quote = False
        
        for line in lines:
            if line.strip().startswith('>'):
                if not in_quote:
                    result.append('<blockquote>')
                    in_quote = True
                content = line.strip()[1:].strip()
                result.append(f'<p>{content}</p>')
            else:
                if in_quote:
                    result.append('</blockquote>')
                    in_quote = False
                result.append(line)
        
        if in_quote:
            result.append('</blockquote>')
        
        return '\n'.join(result)
    
    def _wrap_html(self, html_content):
        """包装HTML内容到完整文档"""
        # 添加代码高亮样式（如果使用Pygments）
        code_style = ""
        if HAS_PYGMENTS:
            formatter = HtmlFormatter(style='default')
            code_style = f"<style>{formatter.get_style_defs('.highlight')}</style>"
        
        full_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
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
                h1 {{ 
                    font-size: 2em; 
                    font-weight: 700; 
                    margin: 1.2em 0 0.8em 0;
                    border-bottom: 2px solid #3a3a3a;
                    padding-bottom: 0.5em;
                    color: #ffffff;
                }}
                h2 {{ 
                    font-size: 1.6em; 
                    font-weight: 600; 
                    margin: 1em 0 0.6em 0;
                    border-bottom: 1px solid #3a3a3a;
                    padding-bottom: 0.4em;
                    color: #ffffff;
                }}
                h3 {{ 
                    font-size: 1.3em; 
                    font-weight: 600; 
                    margin: 0.9em 0 0.5em 0;
                    color: #ffffff;
                }}
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
                a.internal-link:hover {{
                    color: #c4a8ff;
                    border-bottom-color: #c4a8ff;
                }}
                a.footnote-ref {{
                    color: #7aa2f7;
                    border: none;
                    text-decoration: none;
                    font-size: 0.85em;
                    vertical-align: super;
                }}
                a.footnote-backref {{
                    color: #7aa2f7;
                    border: none;
                    text-decoration: none;
                    margin-left: 0.3em;
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
                li.task-list-item .task-checkbox {{
                    margin-right: 0.5em;
                    cursor: pointer;
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
                table.markdown-table tr:hover {{
                    background-color: #2a2a2a;
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
                
                .math-inline {{
                    font-family: 'Times New Roman', 'STIX', 'Computer Modern', serif;
                    font-style: italic;
                    font-size: 1.15em;
                    color: #c7254e;
                    white-space: nowrap;
                }}
                
                .math-block {{
                    font-family: 'Times New Roman', 'STIX', 'Computer Modern', serif;
                    text-align: center;
                    margin: 1.5em 0;
                    padding: 1em;
                    background-color: #2a2a2a;
                    border-left: 4px solid #7aa2f7;
                    font-size: 1.1em;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    border-radius: 0 4px 4px 0;
                }}
                
                img {{
                    max-width: 100%;
                    height: auto;
                    margin: 1.2em 0;
                    display: block;
                    border-radius: 6px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                }}
                
                /* Obsidian特有样式 */
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
                
                .footnotes {{
                    margin-top: 3em;
                    padding-top: 1em;
                    border-top: 1px solid #3a3a3a;
                }}
                
                .footnotes ol {{
                    font-size: 0.9em;
                    color: #a0a0a0;
                }}
                
                .footnotes li {{
                    margin: 0.5em 0;
                }}
            </style>
            {code_style}
        </head>
        <body>
            {html_content}
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
    
    def highlight_text(self, text_to_highlight, start_pos=-1, end_pos=-1):
        """高亮显示文本"""
        if not self._plain_text:
            return
        
        # 如果提供了位置，直接使用
        if start_pos >= 0 and end_pos > start_pos:
            cursor = self.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, self.textCursor().MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
            
            # 设置高亮格式
            if not self._highlight_format:
                from PyQt6.QtGui import QTextCharFormat, QColor
                self._highlight_format = QTextCharFormat()
                self._highlight_format.setBackground(QColor(255, 255, 0))  # 黄色背景
            
            cursor.setCharFormat(self._highlight_format)
            self.setTextCursor(cursor)
            
            # 滚动到高亮位置
            self.ensureCursorVisible()
        else:
            # 搜索文本并高亮
            if text_to_highlight in self._plain_text:
                # 找到第一个匹配位置
                pos = self._plain_text.find(text_to_highlight)
                if pos >= 0:
                    cursor = self.textCursor()
                    cursor.setPosition(pos)
                    cursor.setPosition(pos + len(text_to_highlight), self.textCursor().MoveMode.KeepAnchor)
                    self.setTextCursor(cursor)
                    
                    # 设置高亮格式
                    if not self._highlight_format:
                        from PyQt6.QtGui import QTextCharFormat, QColor
                        self._highlight_format = QTextCharFormat()
                        self._highlight_format.setBackground(QColor(255, 255, 0))  # 黄色背景
                    
                    cursor.setCharFormat(self._highlight_format)
                    self.setTextCursor(cursor)
                    
                    # 滚动到高亮位置
                    self.ensureCursorVisible()

